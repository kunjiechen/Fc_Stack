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
import sys
from pathlib import Path
from typing import Any

from .bundle import RequirementBundleBuilder
from .builder import RequirementBuilder
from .cache_support import cache_key, cached_stage, dependency_fingerprint
from .candidate_mapping import RequirementCandidateMapper, RequirementCandidateMarkdownRenderer
from .candidate_pruner import CandidatePruningMarkdownRenderer, RequirementCandidatePruner
from .chip_view_extractor import generate_chip_views
from .emit_support import dispatch_final_emit, emit_text
from .feature_extraction import FeatureExtractionMarkdownRenderer, FeatureExtractor
from .normative_rules import DriverTypeProfile, NormativeRules
from .filenames import (
    check_list_doc,
    review_doc,
    srs_doc,
    trace_matrix_doc,
)
from .gate_check import GateChecker
from .open_items import OpenItemsCollector
from .operation_checklist import (
    render_check_list_markdown,
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
from .session_state import SessionStore
from .source_index import (
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
    parser.add_argument("--module", default="FC", help="FC driver name used in requirement IDs")
    parser.add_argument(
        "--safety-level", default="",
        choices=("", "QM", "ASIL-A", "ASIL-B", "ASIL-C", "ASIL-D"),
        help="Functional safety level (QM, ASIL-A/B/C/D). Required before pipeline execution.",
    )
    parser.add_argument(
        "--core-mode", default="",
        choices=("", "single", "multi"),
        help="Core control mode: single or multi. Required before pipeline execution.",
    )
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
        "--chip-view-dir", type=Path,
        help="Chip-view output directory (default: <input-root>/Output/<MODULE>/Doc/ChipViews).",
    )
    parser.add_argument(
        "--skip-chip-view", action="store_true",
        help="Skip chip-view generation even when datasheet input is present.",
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

    # ---- Pre-flight: validate required project context ----
    _validate_prerequisites(args.module, args.safety_level, args.core_mode)

    resolved = _resolve_requirement_inputs(
        input_path=args.input,
        raw_input=args.raw_input,
        requirement_doc=args.constraints,
    )
    args.input = resolved["datasheet"]
    args.raw_input = resolved["raw_input"]
    args.constraints = resolved["requirement_doc"]
    input_root = resolved["input_root"]
    has_datasheet = resolved["has_datasheet"]

    cache_dir = args.cache_dir
    use_cache = not args.no_cache
    current_dependency_fingerprint = dependency_fingerprint(__file__)

    # ---- Planned SRS pipeline ----
    parsed = cached_stage(cache_dir, "parsed",
        cache_key(args.input, args.module, "parsed", current_dependency_fingerprint),
        lambda: MarkdownStructureParser().parse_file(args.input), enabled=use_cache)

    # ---- Load normative rules (mandatory) ----
    refs_dir = _resolve_references_dir()
    normative_rules = NormativeRules.from_references(refs_dir)

    # Detect driver type from datasheet content (early, before feature extraction)
    driver_profile = _detect_driver_profile(parsed, normative_rules)

    # Refine has_datasheet with content-based verification (both directions)
    if not has_datasheet:
        has_datasheet = _verify_datasheet_content(parsed)
    elif not _verify_datasheet_content(parsed):
        # Filename suggested datasheet but content doesn't match
        has_datasheet = False

    # Detect whether the datasheet contains fault/flag/diagnostic sections.
    # Used by G3-06 to verify that hardware fault diagnostic requirements
    # are generated when the datasheet clearly describes them.
    _fault_kw = ("flag", "fault", "failure", "diagnostic", "protection",
                 "interrupt", "error", "undervoltage", "overtemperature",
                 "thermal", "short-circuit", "标志", "故障", "诊断", "保护",
                 "中断", "错误")
    datasheet_has_fault_sections = any(
        any(kw in " ".join(c.heading_path).lower() for kw in _fault_kw)
        for c in parsed.chunks
    ) if has_datasheet else False

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
        lambda: RequirementPlanner(module=args.module, profile=driver_profile).plan(pruning), enabled=use_cache)

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
    safety_level = args.safety_level or (raw_document.safety_level if raw_document else "QM")
    engineering = RequirementBuilder(module=builder_module, profile=driver_profile, rules=normative_rules).build(planned_requirements, findings)

    # ---- Post-build validation: construction-rules + authoring-standard ----
    findings = _validate_engineering_requirements(engineering, normative_rules, findings)

    engineering = enrich_engineering_requirements(engineering, module=builder_module, raw_document=raw_document)
    engineering, default_findings = ensure_default_engineering_requirements(
        engineering, builder_module, safety_level,
        mainfunction_required=driver_profile.mainfunction_required,
    )
    findings.extend(default_findings)

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
            has_datasheet=has_datasheet,
            has_project_constraints=args.constraints is not None,
            datasheet_has_fault_sections=datasheet_has_fault_sections,
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
            has_datasheet=has_datasheet,
            feature_groups=[fg.to_dict() if hasattr(fg, "to_dict") else fg for fg in features],
        )

    # ---- Default: full-workflow deliverables ----
    output_dir = args.output_dir or input_root / "Output" / builder_module / "Doc" / "SRS"
    output_dir.mkdir(parents=True, exist_ok=True)
    module = builder_module
    has_raw = raw_document is not None

    # --- Phase 0: Chip-view generation (deterministic, before SRS) ---
    chip_view_dir = args.chip_view_dir or input_root / "Output" / module / "Doc" / "ChipViews"
    chip_view_status: dict[str, Any] = {"generated": False, "arch_exists": False, "design_exists": False}
    if not has_datasheet:
        chip_view_status["skipped"] = "no datasheet input"
    elif args.skip_chip_view:
        chip_view_status["skipped"] = "--skip-chip-view flag"
    else:
        arch_path = chip_view_dir / f"{module}_芯片架构输入.md"
        design_path = chip_view_dir / f"{module}_芯片详细设计输入.md"
        chip_view_status["arch_exists"] = arch_path.exists()
        chip_view_status["design_exists"] = design_path.exists()
        chip_view_status["arch_path"] = str(arch_path)
        chip_view_status["design_path"] = str(design_path)
        if not arch_path.exists() or not design_path.exists():
            try:
                gen_arch, gen_design = generate_chip_views(
                    parsed, module, chip_view_dir, doc=str(args.input),
                )
                chip_view_status["generated"] = True
                chip_view_status["arch_generated"] = str(gen_arch)
                chip_view_status["design_generated"] = str(gen_design)
                chip_view_status["missing_before"] = {
                    "arch": not arch_path.exists(),
                    "design": not design_path.exists(),
                }
            except Exception as exc:
                chip_view_status["error"] = str(exc)
        else:
            chip_view_status["skipped"] = "both files already exist"

    # --- Phase 1: Source entries (for gate check) ---
    datasheet_chapters = _collect_datasheet_chapters(parsed)
    source_gen = SourceIndexGenerator(module=module)
    source_entries = source_gen.generate(
        input_file=str(args.input),
        datasheet_chapters=datasheet_chapters,
        has_raw_requirements=has_raw,
        has_project_constraints=args.constraints is not None,
    )

    # --- Phase 2: SRS ---
    srs_md = MarkdownSrsRenderer().render(srs_document)
    (output_dir / srs_doc(module)).write_text(srs_md, encoding="utf-8")

    collector = OpenItemsCollector()
    open_items = collector.collect(engineering, findings, module)

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
        has_datasheet=has_datasheet,
        has_project_constraints=args.constraints is not None,
        datasheet_has_fault_sections=datasheet_has_fault_sections,
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
            has_datasheet=has_datasheet,
            has_project_constraints=args.constraints is not None,
            datasheet_has_fault_sections=datasheet_has_fault_sections,
        )
        # Re-render SRS after modifications
        srs_document = SrsStructureGenerator().build_document(
            engineering, module=module, findings=findings,
            overview=overview_from_features(features, module, safety_level),
        )
        srs_md = MarkdownSrsRenderer().render(srs_document)
        (output_dir / srs_doc(module)).write_text(srs_md, encoding="utf-8")

    # --- Phase 4: Delivery ---
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

    next_step_message = render_post_generation_reply(
        module=module,
        srs_file=srs_doc(module),
        gate_reports=gate_reports,
        open_items=open_items,
    )

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
        "chip_view": chip_view_status,
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

def _validate_prerequisites(module: str, safety_level: str, core_mode: str) -> None:
    """Validate that the three required project context items are provided.

    Raises SystemExit with a clear message if any are missing.
    """
    missing: list[str] = []
    if module == "FC":
        missing.append("FC 驱动名称 (--module)")
    if not safety_level:
        missing.append("功能安全等级 (--safety-level)，可选: QM / ASIL-A / ASIL-B / ASIL-C / ASIL-D")
    if not core_mode:
        missing.append("单核/多核控制模式 (--core-mode)，可选: single / multi")

    if missing:
        msg = (
            "\n"
            "============================================================\n"
            "  前置校验失败：缺少必需的工程上下文信息\n"
            "============================================================\n"
            "\n"
            "  以下信息必须明确给定，否则不允许继续向下执行：\n\n"
        )
        for i, item in enumerate(missing, 1):
            msg += f"    {i}. {item}\n"
        msg += (
            "\n"
            "  请补充以上信息后重新运行。示例：\n"
            "\n"
            '    python -m fc_requirement_workbench.cli <输入> \\\n'
            '      --module Gp_NCA9539 \\\n'
            '      --safety-level ASIL-B \\\n'
            '      --core-mode single\n'
            "\n"
            "============================================================\n"
        )
        print(msg, file=sys.stderr)
        raise SystemExit(1)


_TEXT_INPUT_SUFFIXES = {".md", ".txt", ".csv", ".tsv", ".xlsx"}
_DATASHEET_KEYWORDS = ("datasheet", "手册", "芯片", "manual", "数据手册", "数据表", "规格书",
                       "registers", "register map", "pin description", "电气特性",
                       "绝对最大额定", "时序", "timing", "package information")
_RAW_REQUIREMENT_KEYWORDS = (
    "原始开发需求", "原始需求", "rawreq", "raw_requirement", "raw-requirement",
    "original_requirement", "original-requirement", "raw_input", "rawinput",
)
_REQUIREMENT_DOC_KEYWORDS = ("需求文档", "项目需求", "需求规范", "requirement", "srs",
                              "软件需求", "系统需求", "sysreq", "swreq")
# Patterns in content that strongly indicate a datasheet
_DATASHEET_CONTENT_PATTERNS = (
    "绝对最大额定", "absolute maximum rating", "electrical characteristic",
    "pin configur", "引脚配置", "register map", "寄存器映射",
    "dynamic characteristic", "时序特性", "package information",
    "recommended operating", "thermal characteristic",
)


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

    _has_ds = _classify_input_file(primary_input) == "datasheet"

    return {
        "input_root": input_root,
        "datasheet": primary_input,
        "raw_input": raw_req,
        "requirement_doc": req_doc,
        "has_datasheet": _has_ds,
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
    # Default: treat unknown files as potential datasheets
    return "datasheet"


def _verify_datasheet_content(parsed: Any) -> bool:
    """Post-parse verification: check if document content looks like a datasheet."""
    full_text = ""
    for chunk in getattr(parsed, 'chunks', []):
        full_text += " ".join(getattr(chunk, 'heading_path', [])) + " "
        full_text += getattr(chunk, 'text', '') + " "
    full_lower = full_text.lower()
    matches = sum(1 for p in _DATASHEET_CONTENT_PATTERNS if p in full_lower)
    return matches >= 2


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
    datasheet_has_fault_sections: bool = False,
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
                datasheet_has_fault_sections=datasheet_has_fault_sections,
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





# ---------------------------------------------------------------------------
# Normative rules support
# ---------------------------------------------------------------------------


def _resolve_references_dir() -> Path:
    """Locate the references/ directory relative to this source file."""
    this_file = Path(__file__).resolve()
    # src/fc_requirement_workbench/cli.py → references/
    refs_dir = this_file.parent.parent.parent / "references"
    if not refs_dir.is_dir():
        raise FileNotFoundError(
            f"Normative references directory not found: {refs_dir}\n"
            f"The pipeline requires reference documents to operate correctly."
        )
    return refs_dir


def _validate_engineering_requirements(
    engineering: list[Any],
    rules: NormativeRules,
    existing_findings: list[Any],
) -> list[Any]:
    """Post-build validation: check required fields + vague words per normative rules."""
    findings = list(existing_findings)
    from .rules import ValidationFinding

    for req in engineering:
        req_dict = req.to_dict() if hasattr(req, "to_dict") else req
        req_type = req_dict.get("requirement_type", "")

        # 1. Field completeness check (construction-rules)
        missing = rules.validate_required_fields(req_type, req_dict)
        if missing:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    rule="construction-rules:required-fields",
                    rule_group="construction-rules",
                    status="failed",
                    requirement_ids=[req_dict.get("requirement_id", "")],
                    message=f"缺少必填字段: {', '.join(missing)}",
                    recommendation="补充缺失字段或将状态设为 Draft",
                )
            )

        # 2. Vague word + forbidden placeholder check (authoring-standard)
        # Check ALL user-visible requirement fields — not just description.
        text_to_check = " ".join([
            req_dict.get("description", ""),
            req_dict.get("constraint", ""),
            req_dict.get("exception", ""),
            req_dict.get("verification", ""),
            req_dict.get("pre_condition", ""),
            req_dict.get("trigger", ""),
            req_dict.get("input", ""),
            req_dict.get("output", ""),
            req_dict.get("title", ""),
        ])
        vague = rules.find_vague_words(text_to_check)
        if vague:
            findings.append(
                ValidationFinding(
                    severity="info",
                    rule="authoring-standard:vague-words",
                    rule_group="authoring-standard",
                    status="failed",
                    requirement_ids=[req_dict.get("requirement_id", "")],
                    message=f"包含禁用的占位或模糊词: {', '.join(vague)}",
                    recommendation="替换为可度量的条件、边界或验收规则。若暂时无法确定具体值，标记为 Open Issue 状态而非填写占位符。",
                )
            )

    return findings


def _detect_driver_profile(parsed: Any, rules: NormativeRules) -> DriverTypeProfile:
    """Detect the normative driver profile from parsed datasheet content."""
    chip_description: list[str] = []
    for chunk in parsed.chunks:
        text = getattr(chunk, "text", "")
        # Collect from identity-relevant sections: title, description, features
        heading = " ".join(getattr(chunk, "heading_path", []))
        if any(kw in heading.lower() for kw in (
            "特性", "features", "说明", "description", "概述", "overview", "应用",
        )):
            chip_description.append(text[:500])
        # Also check the first few chunks for chip title
        if len(chip_description) < 3 and len(text) > 50:
            chip_description.append(text[:300])
        if len(chip_description) >= 5:
            break

    combined = " ".join(chip_description)
    return rules.resolve_profile(combined)


if __name__ == "__main__":
    raise SystemExit(main())
