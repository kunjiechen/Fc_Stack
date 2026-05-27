"""CLI entry point — single planned SRS path + full workflow deliverables.

Default behaviour: one invocation produces the SRS plus all process artefacts
(source index, extraction records, derivation matrix, open items, gate check,
review record, CHECK list, operation steps) in a single output directory.

Use --emit only to override the output format (srs-html, srs-docx) or to
inspect pipeline intermediates (features-markdown, candidates-markdown, …).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .bundle import RequirementBundleBuilder
from .builder import RequirementBuilder
from .cache_support import cache_key, cached_stage, dependency_fingerprint
from .candidate_mapping import RequirementCandidateMapper, RequirementCandidateMarkdownRenderer
from .candidate_pruner import CandidatePruningMarkdownRenderer, RequirementCandidatePruner
from .emit_support import dispatch_final_emit, emit_text
from .feature_extraction import FeatureExtractionMarkdownRenderer, FeatureExtractor
from .filenames import (
    check_list_doc,
    derivation_doc,
    gate_report_doc,
    next_step_message_doc,
    open_items_doc,
    operation_steps_doc,
    post_generation_guide_doc,
    review_doc,
    source_extract_doc,
    source_index_doc,
    srs_doc,
    trace_matrix_doc,
)
from .gate_check import GateChecker, render_gate_check_markdown
from .open_items import OpenItemsCollector, render_open_items_markdown
from .operation_checklist import (
    render_check_list_markdown,
    render_operation_steps_markdown,
    render_post_generation_guidance_markdown,
    render_post_generation_reply,
    render_review_record_markdown,
)
from .parser import MarkdownStructureParser
from .pipeline_support import enrich_engineering_requirements, load_constraints, overview_from_features
from .raw_requirements import (
    RawInputLoader,
    RawRequirementCoverageAnalyzer,
    RawRequirementExtractor,
    RawRequirementMarkdownRenderer,
    RawRequirementSemanticConverter,
    merge_requirements,
)
from .requirement_planner import RequirementPlanner, RequirementPlanningMarkdownRenderer
from .review_guide import ReviewGuideBuilder, render_review_guide_markdown
from .rules import RequirementRuleEngine
from .session_state import SessionStore, render_final_review_record
from .source_index import (
    DerivationMatrixGenerator,
    ExtractRecordGenerator,
    SourceIndexGenerator,
)
from .srs import (
    ensure_default_engineering_requirements,
    MarkdownSrsRenderer,
    SrsStructureGenerator,
)
from .traceability import TraceabilityMarkdownRenderer, TraceabilityPipeline, load_trace_mapping
from .workflow import FixLoopEngine


# ---------------------------------------------------------------------------
# Emit choices
# ---------------------------------------------------------------------------
# Only format variants and pipeline-inspection emits are user-selectable.
# Process artefacts (source-index, gate-check, …) are always produced.
_FORMAT_EMITS = ("srs-markdown", "srs-html", "srs-docx")
_INSPECT_EMITS = (
    "features-markdown",
    "candidates-markdown",
    "pruning-markdown",
    "planning-markdown",
    "rawreq-markdown",
    "rawreq-json",
    "review-guide-markdown",
)
_JSON_EMITS = (
    "traceability", "coverage", "raw-coverage", "verification",
    "aspice", "impact",
)
_BUNDLE_EMITS = (
    "requirement-bundle", "requirement-bundle-json",
    "architecture-seed", "test-seed", "bundle-validation",
    "traceability-markdown",
)
_WORKFLOW_EMITS = (
    "source-index",
    "extract-records",
    "open-items",
    "gate-check",
    "review-record",
    "check-list",
    "operation-steps",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SRS + full workflow deliverables from datasheet / raw requirements."
    )
    parser.add_argument("input", type=Path, help="Requirements input datasheet file or input directory")
    parser.add_argument("--module", default="FC", help="Module name used in requirement IDs")
    parser.add_argument(
        "--constraints", "--requirement-doc", dest="constraints", type=Path,
        help="Project requirement document / constraint Markdown file.",
    )
    parser.add_argument(
        "--tests", type=Path,
        help="Optional verification/test trace mapping file",
    )
    parser.add_argument(
        "--raw-input", type=Path,
        help="Original development requirement input file (dialog/txt/excel).",
    )
    parser.add_argument(
        "--raw-input-type",
        choices=("auto", "dialog", "txt", "excel"), default="auto",
        help="Source type for --raw-input (default: auto).",
    )
    parser.add_argument(
        "--changed", default="",
        help="Comma-separated SRS requirement IDs for change impact analysis",
    )
    parser.add_argument(
        "--source-root", type=Path,
        help="Optional project source root for bundle source-grounding.",
    )
    parser.add_argument(
        "--emit",
        choices=_FORMAT_EMITS + _INSPECT_EMITS + _JSON_EMITS + _BUNDLE_EMITS + _WORKFLOW_EMITS,
        help="Emit a single artefact instead of the default full-workflow directory.",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        help="Output directory for full-workflow deliverables (default: <input-root>/Output/<MODULE>/Doc/SRS).",
    )
    parser.add_argument(
        "--output", type=Path,
        help="Single-file output path (only meaningful with --emit).",
    )
    parser.add_argument(
        "--with-intermediates", action="store_true",
        help="Write intermediate Markdown artefacts to --intermediate-dir.",
    )
    parser.add_argument(
        "--intermediate-dir", type=Path, default=Path("Output/intermediate"),
        help="Directory for --with-intermediates outputs.",
    )
    parser.add_argument(
        "--cache-dir", type=Path, default=Path(".cache/fc_requirement_workbench"),
        help="Cache directory for parser/extraction/planning stages.",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Disable local cache reuse.",
    )
    parser.add_argument(
        "--mode", choices=("full", "loop", "review"), default="full",
        help="Workflow mode: full=single pass (default), loop=fix-iterate, review=generate+guided-review.",
    )
    parser.add_argument(
        "--fix-input", type=Path,
        help="YAML/JSON fix input file for --mode loop (modifications + open-item closures).",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Print summary JSON only; suppress the human-readable next-step message.",
    )
    args = parser.parse_args()

    resolved = _resolve_requirement_inputs(
        input_path=args.input,
        raw_input=args.raw_input,
        requirement_doc=args.constraints,
    )
    args.input = resolved["datasheet"]
    args.raw_input = resolved["raw_input"]
    args.constraints = resolved["requirement_doc"]
    input_root = resolved["input_root"]

    cache_dir = args.cache_dir
    use_cache = not args.no_cache
    current_dependency_fingerprint = dependency_fingerprint(__file__)

    # ---- Planned SRS pipeline ----
    parsed = cached_stage(cache_dir, "parsed",
        cache_key(args.input, args.module, "parsed", current_dependency_fingerprint),
        lambda: MarkdownStructureParser().parse_file(args.input), enabled=use_cache)

    features = cached_stage(cache_dir, "features",
        cache_key(args.input, args.module, "features", current_dependency_fingerprint),
        lambda: FeatureExtractor(module=args.module).extract(parsed), enabled=use_cache)

    if args.emit == "features-markdown":
        return emit_text(FeatureExtractionMarkdownRenderer().render(features, args.module), args.output)

    candidates = cached_stage(cache_dir, "candidates",
        cache_key(args.input, args.module, "candidates", current_dependency_fingerprint),
        lambda: RequirementCandidateMapper(module=args.module).map(features), enabled=use_cache)

    if args.emit == "candidates-markdown":
        return emit_text(RequirementCandidateMarkdownRenderer().render(candidates, args.module), args.output)

    pruning = cached_stage(cache_dir, "pruning",
        cache_key(args.input, args.module, "pruning", current_dependency_fingerprint),
        lambda: RequirementCandidatePruner().prune(candidates), enabled=use_cache)

    if args.emit == "pruning-markdown":
        return emit_text(CandidatePruningMarkdownRenderer().render(pruning, args.module), args.output)

    planning = cached_stage(cache_dir, "planning",
        cache_key(args.input, args.module, "planning", current_dependency_fingerprint),
        lambda: RequirementPlanner(module=args.module).plan(pruning), enabled=use_cache)

    if args.emit == "planning-markdown":
        return emit_text(RequirementPlanningMarkdownRenderer().render(planning), args.output)

    if args.with_intermediates:
        _write_intermediates(module=args.module, output_dir=args.intermediate_dir,
                             features=features, candidates=candidates, pruning=pruning, planning=planning)

    # ---- Raw requirements ----
    constraints = load_constraints(args.constraints)
    raw_document = None
    raw_semantic_requirements: list[Any] = []
    if args.raw_input:
        raw_input = RawInputLoader().load(args.raw_input, source_type=args.raw_input_type)
        raw_document = RawRequirementExtractor().extract(raw_input, module=args.module)
        raw_semantic_requirements = RawRequirementSemanticConverter().convert(raw_document)
        if args.emit == "rawreq-markdown":
            return emit_text(RawRequirementMarkdownRenderer().render(raw_document), args.output)
        if args.emit == "rawreq-json":
            return emit_text(json.dumps(raw_document.to_dict(), ensure_ascii=False, indent=2) + "\n", args.output)

    planned_requirements = merge_requirements(planning.requirements, raw_semantic_requirements)
    findings = RequirementRuleEngine().validate(planned_requirements, constraints)

    builder_module = (raw_document.module_name if raw_document and raw_document.module_name else args.module)
    safety_level = raw_document.safety_level if raw_document else "QM"
    engineering = RequirementBuilder(module=builder_module).build(planned_requirements, findings)
    engineering = enrich_engineering_requirements(engineering, module=builder_module, raw_document=raw_document)
    engineering = ensure_default_engineering_requirements(engineering, builder_module)

    srs_document = SrsStructureGenerator().build_document(
        engineering, module=builder_module, findings=findings,
        overview=overview_from_features(features, builder_module, safety_level),
    )

    traceability = TraceabilityPipeline().build(engineering, tests=load_trace_mapping(args.tests))
    raw_coverage_detail = (
        RawRequirementCoverageAnalyzer().build_detail(raw_document, engineering)
        if raw_document is not None else None
    )
    requirement_bundle = RequirementBundleBuilder().build(
        module=builder_module, input_document=str(args.input),
        engineering_requirements=engineering, findings=findings,
        traceability=traceability, raw_document=raw_document,
        raw_coverage_detail=raw_coverage_detail, source_root=args.source_root,
    )

    # ---- Review guide (needs gate check, handles itself before dispatch) ----
    if args.emit == "review-guide-markdown":
        collector = OpenItemsCollector()
        open_items = collector.collect(engineering, findings, builder_module)
        checker = GateChecker(
            module=builder_module,
            source_count=0,
            has_raw_requirements=raw_document is not None,
            has_datasheet=True,
            has_project_constraints=args.constraints is not None,
        )
        open_item_dicts = [oi.__dict__ if hasattr(oi, '__dict__') else oi for oi in open_items]
        gate_reports = checker.check_all(engineering, findings, open_item_dicts)
        guide = ReviewGuideBuilder().build(builder_module, engineering, gate_reports, round_number=1)
        return emit_text(render_review_guide_markdown(guide), args.output)

    # ---- Single-emit fast path ----
    if args.emit:
        return dispatch_final_emit(
            emit=args.emit, output=args.output,
            srs_document=srs_document, requirement_bundle=requirement_bundle,
            traceability=traceability, raw_document=raw_document,
            raw_coverage_detail=raw_coverage_detail,
            planned_requirements=planned_requirements,
            module=args.module, changed=args.changed,
            engineering_reqs=engineering,
            findings=findings,
            input_file=str(args.input),
            has_raw_requirements=raw_document is not None,
            has_project_constraints=args.constraints is not None,
            has_datasheet=True,
            feature_groups=[fg.to_dict() if hasattr(fg, "to_dict") else fg for fg in features],
        )

    # ---- Default: full-workflow deliverables ----
    output_dir = args.output_dir or input_root / "Output" / builder_module / "Doc" / "SRS"
    output_dir.mkdir(parents=True, exist_ok=True)
    module = builder_module
    has_raw = raw_document is not None

    # --- Phase 1: Source index + extract records ---
    datasheet_chapters = _collect_datasheet_chapters(parsed)
    source_gen = SourceIndexGenerator(module=module)
    source_entries = source_gen.generate(
        input_file=str(args.input),
        datasheet_chapters=datasheet_chapters,
        has_raw_requirements=has_raw,
        has_project_constraints=args.constraints is not None,
    )
    (output_dir / source_index_doc(module)).write_text(
        source_gen.render_markdown(source_entries, module), encoding="utf-8")

    feature_dicts = [fg.to_dict() if hasattr(fg, 'to_dict') else fg for fg in features]
    extract_gen = ExtractRecordGenerator()
    extract_records = extract_gen.generate_from_features(feature_dicts, source_entries, module)
    (output_dir / source_extract_doc(module)).write_text(
        extract_gen.render_markdown(extract_records, module), encoding="utf-8")

    # --- Phase 2: SRS + derivation + open items ---
    srs_md = MarkdownSrsRenderer().render(srs_document)
    (output_dir / srs_doc(module)).write_text(srs_md, encoding="utf-8")

    deriv_gen = DerivationMatrixGenerator()
    deriv_records = deriv_gen.generate(extract_records, engineering, module)
    (output_dir / derivation_doc(module)).write_text(
        deriv_gen.render_markdown(deriv_records, module), encoding="utf-8")

    collector = OpenItemsCollector()
    open_items = collector.collect(engineering, findings, module)
    (output_dir / open_items_doc(module)).write_text(
        render_open_items_markdown(open_items, module), encoding="utf-8")

    # --- Phase 3: Gate check ---
    (output_dir / trace_matrix_doc(module)).write_text(
        TraceabilityMarkdownRenderer().render(
            traceability,
            module=module,
            raw_document=raw_document,
            raw_coverage=raw_coverage_detail,
        ),
        encoding="utf-8",
    )

    checker = GateChecker(
        module=module,
        source_count=len(source_entries),
        has_raw_requirements=has_raw,
        has_datasheet=True,
        has_project_constraints=args.constraints is not None,
    )
    open_item_dicts = [oi.__dict__ if hasattr(oi, '__dict__') else oi for oi in open_items]
    gate_reports = checker.check_all(engineering, findings, open_item_dicts)

    # --- Mode: loop ---
    loop_count = 0
    auto_fixes_applied = 0
    change_log: list[str] = []
    if args.mode == "loop":
        fix_input = _load_fix_input(args.fix_input) if args.fix_input else {}
        loop_count, auto_fixes_applied, engineering, gate_reports, change_log, open_items = _run_fix_loop(
            gate_reports, engineering, findings, fix_input,
            max_iterations=5, module=module, open_items=open_items,
            source_count=len(source_entries),
            has_raw_requirements=has_raw,
            has_datasheet=True,
            has_project_constraints=args.constraints is not None,
        )
        # Re-render SRS after modifications
        srs_document = SrsStructureGenerator().build_document(
            engineering, module=module, findings=findings,
            overview=overview_from_features(features, module, safety_level),
        )
        srs_md = MarkdownSrsRenderer().render(srs_document)
        (output_dir / srs_doc(module)).write_text(srs_md, encoding="utf-8")
        deriv_records = deriv_gen.generate(extract_records, engineering, module)
        (output_dir / derivation_doc(module)).write_text(
            deriv_gen.render_markdown(deriv_records, module), encoding="utf-8")
        (output_dir / open_items_doc(module)).write_text(
            render_open_items_markdown(open_items, module), encoding="utf-8")

    # --- Phase 4: Delivery ---
    (output_dir / gate_report_doc(module)).write_text(
        render_gate_check_markdown(gate_reports, module), encoding="utf-8")

    (output_dir / check_list_doc(module)).write_text(
        render_check_list_markdown(
            module=module, gate_reports=gate_reports, open_items=open_items
        ),
        encoding="utf-8",
    )

    (output_dir / review_doc(module)).write_text(
        render_review_record_markdown(
            module=module, gate_reports=gate_reports, open_items=open_items,
            operation_steps_generated=True, check_list_generated=True,
        ), encoding="utf-8")

    (output_dir / operation_steps_doc(module)).write_text(
        render_operation_steps_markdown(
            module=module,
            output_dir=str(output_dir),
            input_file=str(args.input),
            has_raw_requirements=has_raw,
            has_datasheet=True,
            open_items=open_items,
            loop_count=loop_count,
            auto_fixes_applied=auto_fixes_applied,
            requirement_count=len(engineering),
        ), encoding="utf-8")

    post_guide_path = output_dir / post_generation_guide_doc(module)
    post_guide_path.write_text(
        render_post_generation_guidance_markdown(
            module=module,
            srs_file=srs_doc(module),
            has_raw_requirements=has_raw,
            has_datasheet=True,
            has_project_constraints=args.constraints is not None,
            gate_reports=gate_reports,
            open_items=open_items,
        ),
        encoding="utf-8",
    )
    next_step_message = render_post_generation_reply(
        module=module,
        srs_file=srs_doc(module),
        gate_reports=gate_reports,
        open_items=open_items,
    )
    next_step_message_path = output_dir / next_step_message_doc(module)
    next_step_message_path.write_text(next_step_message, encoding="utf-8")

    if change_log:
        (output_dir / f"Change_Log_{module}.md").write_text(
            _render_change_log(change_log, module), encoding="utf-8")

    # --- Mode: review (generate + guided-review) ---
    review_guide_path: Path | None = None
    session_path: Path | None = None
    if args.mode == "review":
        store = SessionStore()
        state = store.load(module)
        round_number = 1
        if state is None:
            state = store.create(module, output_dir=str(output_dir))
        else:
            round_number = state.total_rounds + 1

        review_guide = ReviewGuideBuilder().build(module, engineering, gate_reports, round_number=round_number)
        review_guide_md = render_review_guide_markdown(review_guide)
        review_guide_path = output_dir / f"Review_Guide_{module}.md"
        review_guide_path.write_text(review_guide_md, encoding="utf-8")

        state = store.transition(state, "review")
        state = store.add_round(
            state,
            action="generate",
            input_summary=f"Datasheet: {str(args.input)}, Raw: {bool(args.raw_input)}, Mode: review",
            requirement_changes=[],
            decisions=[f"Gate overall: {review_guide.gate_overall}"],
        )
        state.gate_verdicts[round_number] = review_guide.gate_overall
        state.open_item_count = len(open_items)
        state.blocking_count = sum(
            1 for oi in open_items
            if hasattr(oi, 'item_type')
            and getattr(oi, 'item_type', '') in {"needs_source", "asil_pending", "source_conflict"}
            and getattr(oi, 'status', 'Open') == "Open"
        )
        state.srs_file = srs_doc(module)
        state.review_record_file = review_doc(module)
        store.save(state)
        session_path = store._session_path(module)

        # Write session summary JSON for the skill to consume
        session_summary = {
            "module": module,
            "session_id": state.session_id,
            "current_phase": "review",
            "round_number": round_number,
            "total_requirements": review_guide.total_requirements,
            "ready_count": review_guide.ready_count,
            "open_issue_count": review_guide.open_issue_count,
            "gate_overall": review_guide.gate_overall,
            "blocking_count": state.blocking_count,
            "open_item_count": state.open_item_count,
            "output_dir": str(output_dir),
            "review_guide_file": str(review_guide_path),
            "session_file": str(session_path),
            "next_actions": [
                "查看评审引导: " + str(review_guide_path),
                "通过评审后归档: python -m fc_requirement_workbench.cli ... --mode review 并确认所有需求",
                "补充缺失信息: 提供项目输入后重新运行 --mode review",
            ],
        }
        (output_dir / f"Session_{module}.json").write_text(
            json.dumps(session_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "module": module,
        "output_dir": str(output_dir),
        "files": sorted(f.name for f in output_dir.iterdir() if f.is_file()),
        "requirement_count": len(engineering),
        "gate_status": {r.gate: r.status for r in gate_reports},
        "open_items": len(open_items),
        "loop_count": loop_count,
        "post_generation_guide": str(post_guide_path),
        "next_step_message_file": str(next_step_message_path),
        "next_actions": [
            "补原始需求",
            "补来源资料",
            "修改 SRS 表达",
            "转 Open Item",
            "保持 Draft",
            "Conditional 通过",
            "Baselined",
        ],
        "assistant_reply": next_step_message,
    }
    if review_guide_path:
        summary["review_guide"] = str(review_guide_path)
    if session_path:
        summary["session_file"] = str(session_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.json_only:
        print("")
        print(next_step_message)
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEXT_INPUT_SUFFIXES = {".md", ".txt", ".csv", ".tsv", ".xlsx"}
_DATASHEET_KEYWORDS = ("datasheet", "手册", "芯片", "manual")
_RAW_REQUIREMENT_KEYWORDS = (
    "原始开发需求", "原始需求", "rawreq", "raw_requirement", "raw-requirement",
    "original_requirement", "original-requirement",
)
_REQUIREMENT_DOC_KEYWORDS = ("需求文档", "项目需求", "需求规范", "requirement", "srs")


def _resolve_requirement_inputs(
    *,
    input_path: Path,
    raw_input: Path | None,
    requirement_doc: Path | None,
) -> dict[str, Path]:
    if input_path.is_dir():
        input_root = input_path
        datasheet = _pick_input_file(input_root, "datasheet")
        raw_req = raw_input or _pick_input_file(input_root, "raw_requirement")
        req_doc = requirement_doc or _pick_input_file(input_root, "requirement_doc")
    else:
        input_root = input_path.parent
        category = _classify_input_file(input_path)
        datasheet = input_path if category == "datasheet" else None
        raw_req = raw_input or (input_path if category == "raw_requirement" else None)
        req_doc = requirement_doc or (input_path if category == "requirement_doc" else None)

    primary_input = datasheet or raw_req or req_doc
    if primary_input is None:
        raise ValueError(
            "需求生成输入不完整，至少需要提供以下三者之一：芯片资料、原始开发需求、需求文档。"
        )

    return {
        "input_root": input_root,
        "datasheet": primary_input,
        "raw_input": raw_req,
        "requirement_doc": req_doc,
    }


def _pick_input_file(input_root: Path, category: str) -> Path | None:
    candidates = [
        path for path in sorted(input_root.iterdir())
        if path.is_file() and path.suffix.lower() in _TEXT_INPUT_SUFFIXES
    ]
    for path in candidates:
        if _classify_input_file(path) == category:
            return path
    return None


def _classify_input_file(path: Path) -> str:
    name = path.name.lower()
    if any(keyword in name for keyword in _RAW_REQUIREMENT_KEYWORDS):
        return "raw_requirement"
    if any(keyword in name for keyword in _DATASHEET_KEYWORDS):
        return "datasheet"
    if any(keyword in name for keyword in _REQUIREMENT_DOC_KEYWORDS):
        return "requirement_doc"
    return "datasheet"

def _collect_datasheet_chapters(parsed: Any) -> list[str]:
    """Extract top-level heading texts from a parsed document."""
    chapters: list[str] = []
    for chunk in getattr(parsed, 'chunks', []):
        if getattr(chunk, 'heading_path', []) and chunk.heading_path:
            heading = chunk.heading_path[0]
            if heading not in chapters:
                chapters.append(heading)
    return chapters


def _load_fix_input(path: Path) -> dict[str, Any]:
    """Load a YAML or JSON fix-input file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            return yaml.safe_load(text) or {}
        except ImportError:
            pass
    return json.loads(text)


def _run_fix_loop(
    gate_reports: list[Any],
    engineering: list[Any],
    findings: list[Any],
    fix_input: dict[str, Any],
    max_iterations: int = 5,
    module: str = "FC",
    open_items: list[Any] | None = None,
    source_count: int = 0,
    has_raw_requirements: bool = False,
    has_datasheet: bool = False,
    has_project_constraints: bool = False,
) -> tuple[int, int, list[Any], list[Any], list[str], list[Any]]:
    """Run the fix-iterate loop until gates are clean or max_iterations reached.

    Returns (loop_count, auto_fixes_applied, engineering, gate_reports,
             change_log, open_items).
    """
    loop_count = 0
    auto_fixes_applied = 0
    change_log: list[str] = []
    open_items = open_items or []

    engine = FixLoopEngine()
    modifications = fix_input.get("modifications", [])
    closures = fix_input.get("open_item_closures", [])

    if not modifications and not closures:
        return loop_count, auto_fixes_applied, engineering, gate_reports, change_log, open_items

    while loop_count < max_iterations:
        loop_count += 1

        # 1. Apply field modifications
        if modifications:
            engineering, patch_log = engine.apply_modifications(engineering, modifications)
            change_log.extend(patch_log)
            auto_fixes_applied += len([e for e in patch_log if e.startswith("PATCH")])

        # 2. Close open items
        if closures and open_items:
            open_items, closure_log = engine.apply_open_item_closures(open_items, closures)
            change_log.extend(closure_log)

        # 3. Collect affected requirement IDs for incremental re-check
        affected_ids: set[str] = set()
        for mod in modifications:
            target = mod.get("target", "")
            if target:
                affected_ids.add(target)

        # 4. Incremental re-check
        if affected_ids:
            gate_reports = engine.incremental_recheck(
                gate_reports, engineering, findings, affected_ids, module, open_items,
                source_count=source_count,
                has_raw_requirements=has_raw_requirements,
                has_datasheet=has_datasheet,
                has_project_constraints=has_project_constraints,
            )
        elif closures:
            open_item_dicts = [oi.__dict__ if hasattr(oi, "__dict__") else oi for oi in open_items]
            gate_reports = GateChecker(
                module=module,
                source_count=source_count,
                has_raw_requirements=has_raw_requirements,
                has_datasheet=has_datasheet,
                has_project_constraints=has_project_constraints,
            ).check_all(engineering, findings, open_item_dicts)

        # 5. Check termination
        has_blocking = any(r.is_blocking for r in gate_reports)
        if not has_blocking:
            change_log.append("FIX-LOOP: all blocking issues resolved")
            break

        # Only the first iteration consumes the explicit fix_input
        modifications = []
        closures = []

    if loop_count >= max_iterations and any(r.is_blocking for r in gate_reports):
        change_log.append(f"FIX-LOOP: max iterations ({max_iterations}) reached, {sum(1 for r in gate_reports if r.is_blocking)} gates still blocking")

    return loop_count, auto_fixes_applied, engineering, gate_reports, change_log, open_items


def _write_intermediates(
    *, module: str, output_dir: Path,
    features: list[Any], candidates: list[Any], pruning: Any, planning: Any,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        f"{module} 特征提取中间文件.md": FeatureExtractionMarkdownRenderer().render(features, module),
        f"{module} 需求候选映射中间文件.md": RequirementCandidateMarkdownRenderer().render(candidates, module),
        f"{module} 候选需求压缩中间文件.md": CandidatePruningMarkdownRenderer().render(pruning, module),
        f"{module} 需求规划中间文件.md": RequirementPlanningMarkdownRenderer().render(planning),
    }
    for filename, content in artifacts.items():
        (output_dir / filename).write_text(content, encoding="utf-8")


def _render_change_log(log: list[str], module: str) -> str:
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 修改记录 — {module}",
        "",
        f"**生成时间**: {now}",
        "",
    ]
    for entry in log:
        prefix = entry.split(":")[0] if ":" in entry else ""
        if prefix in ("PATCH", "CLOSE", "SKIP", "FIX-LOOP"):
            lines.append(f"- {entry}")
        else:
            lines.append(f"- {entry}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
