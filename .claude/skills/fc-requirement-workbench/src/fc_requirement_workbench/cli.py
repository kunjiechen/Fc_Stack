"""CLI entry point — single planned SRS path + traceability outputs."""

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
from .rules import RequirementRuleEngine
from .srs import (
    ensure_default_engineering_requirements,
    SrsStructureGenerator,
)
from .traceability import TraceabilityPipeline, load_trace_mapping


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SRS requirements from datasheet markdown via planned SRS path."
    )
    parser.add_argument("input", type=Path, help="Markdown datasheet file")
    parser.add_argument("--module", default="FC", help="Module name used in requirement IDs")
    parser.add_argument(
        "--constraints",
        type=Path,
        help="Optional project constraint Markdown file for rule validation",
    )
    parser.add_argument(
        "--tests", type=Path, help="Optional verification/test trace mapping file"
    )
    parser.add_argument(
        "--raw-input",
        type=Path,
        help="Optional user raw requirement input file (dialog/txt for now).",
    )
    parser.add_argument(
        "--raw-input-type",
        choices=("auto", "dialog", "txt", "excel"),
        default="auto",
        help="Source type for --raw-input (default: auto).",
    )
    parser.add_argument(
        "--changed",
        default="",
        help="Comma-separated SRS requirement IDs for change impact analysis",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        help="Optional project source root used as implemented evidence for bundle export.",
    )
    parser.add_argument(
        "--emit",
        choices=(
            "srs-markdown",
            "srs-html",
            "srs-docx",
            "features-markdown",
            "candidates-markdown",
            "pruning-markdown",
            "planning-markdown",
            "rawreq-markdown",
            "rawreq-json",
            "traceability-markdown",
            "traceability",
            "coverage",
            "raw-coverage",
            "verification",
            "aspice",
            "impact",
            "requirement-bundle",
            "requirement-bundle-json",
            "architecture-seed",
            "test-seed",
            "bundle-validation",
        ),
        default="srs-markdown",
        help="Output type (default: srs-markdown)",
    )
    parser.add_argument("--output", type=Path, help="Output file path")
    parser.add_argument(
        "--with-intermediates",
        action="store_true",
        help="Write intermediate Markdown artifacts. Disabled by default for faster SRS generation.",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        default=Path("artifacts/intermediate"),
        help="Directory for --with-intermediates outputs (default: artifacts/intermediate)",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".cache/fc_requirement_workbench"),
        help="Directory for parser/extraction/planning cache files.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable local cache reuse for parser/extraction/planning stages.",
    )
    args = parser.parse_args()
    cache_dir = args.cache_dir
    use_cache = not args.no_cache
    current_dependency_fingerprint = dependency_fingerprint(__file__)

    # ---- Planned SRS pipeline (single path) ----
    parsed = cached_stage(
        cache_dir,
        "parsed",
        cache_key(args.input, args.module, "parsed", current_dependency_fingerprint),
        lambda: MarkdownStructureParser().parse_file(args.input),
        enabled=use_cache,
    )
    features = cached_stage(
        cache_dir,
        "features",
        cache_key(args.input, args.module, "features", current_dependency_fingerprint),
        lambda: FeatureExtractor(module=args.module).extract(parsed),
        enabled=use_cache,
    )
    if args.emit == "features-markdown":
        return emit_text(
            FeatureExtractionMarkdownRenderer().render(features, args.module),
            args.output,
        )

    candidates = cached_stage(
        cache_dir,
        "candidates",
        cache_key(args.input, args.module, "candidates", current_dependency_fingerprint),
        lambda: RequirementCandidateMapper(module=args.module).map(features),
        enabled=use_cache,
    )
    if args.emit == "candidates-markdown":
        return emit_text(
            RequirementCandidateMarkdownRenderer().render(candidates, args.module),
            args.output,
        )

    pruning = cached_stage(
        cache_dir,
        "pruning",
        cache_key(args.input, args.module, "pruning", current_dependency_fingerprint),
        lambda: RequirementCandidatePruner().prune(candidates),
        enabled=use_cache,
    )
    if args.emit == "pruning-markdown":
        return emit_text(
            CandidatePruningMarkdownRenderer().render(pruning, args.module),
            args.output,
        )

    planning = cached_stage(
        cache_dir,
        "planning",
        cache_key(args.input, args.module, "planning", current_dependency_fingerprint),
        lambda: RequirementPlanner(module=args.module).plan(pruning),
        enabled=use_cache,
    )
    if args.emit == "planning-markdown":
        return emit_text(
            RequirementPlanningMarkdownRenderer().render(planning),
            args.output,
        )

    if args.with_intermediates:
        _write_intermediates(
            module=args.module,
            output_dir=args.intermediate_dir,
            features=features,
            candidates=candidates,
            pruning=pruning,
            planning=planning,
        )

    constraints = load_constraints(args.constraints)
    raw_document = None
    raw_semantic_requirements = []
    if args.raw_input:
        raw_input = RawInputLoader().load(
            args.raw_input,
            source_type=args.raw_input_type,
        )
        raw_document = RawRequirementExtractor().extract(raw_input, module=args.module)
        raw_semantic_requirements = RawRequirementSemanticConverter().convert(raw_document)
        if args.emit == "rawreq-markdown":
            return emit_text(
                RawRequirementMarkdownRenderer().render(raw_document),
                args.output,
            )
        if args.emit == "rawreq-json":
            payload = json.dumps(raw_document.to_dict(), ensure_ascii=False, indent=2)
            return emit_text(payload + "\n", args.output)

    planned_requirements = merge_requirements(planning.requirements, raw_semantic_requirements)
    findings = RequirementRuleEngine().validate(planned_requirements, constraints)

    builder_module = (raw_document.module_name if raw_document and raw_document.module_name else args.module)
    safety_level = raw_document.safety_level if raw_document else "QM"
    engineering = RequirementBuilder(module=builder_module).build(
        planned_requirements, findings
    )
    engineering = enrich_engineering_requirements(
        engineering,
        module=builder_module,
        raw_document=raw_document,
    )
    engineering = ensure_default_engineering_requirements(
        engineering,
        builder_module,
    )
    srs_document = SrsStructureGenerator().build_document(
        engineering,
        module=builder_module,
        findings=findings,
        overview=overview_from_features(features, builder_module, safety_level),
    )

    # ---- Traceability & bundle (always built; bundle is source of truth) ----
    traceability = TraceabilityPipeline().build(
        engineering, tests=load_trace_mapping(args.tests)
    )
    raw_coverage_detail = (
        RawRequirementCoverageAnalyzer().build_detail(raw_document, engineering)
        if raw_document is not None
        else None
    )
    requirement_bundle = RequirementBundleBuilder().build(
        module=builder_module,
        input_document=str(args.input),
        engineering_requirements=engineering,
        findings=findings,
        traceability=traceability,
        raw_document=raw_document,
        raw_coverage_detail=raw_coverage_detail,
        source_root=args.source_root,
    )

    return dispatch_final_emit(
        emit=args.emit,
        output=args.output,
        srs_document=srs_document,
        requirement_bundle=requirement_bundle,
        traceability=traceability,
        raw_document=raw_document,
        raw_coverage_detail=raw_coverage_detail,
        planned_requirements=planned_requirements,
        module=args.module,
        changed=args.changed,
    )
def _write_intermediates(
    *,
    module: str,
    output_dir: Path,
    features: list[Any],
    candidates: list[Any],
    pruning: Any,
    planning: Any,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        f"{module} 特征提取中间文件.md": FeatureExtractionMarkdownRenderer().render(
            features, module
        ),
        f"{module} 需求候选映射中间文件.md": RequirementCandidateMarkdownRenderer().render(
            candidates, module
        ),
        f"{module} 候选需求压缩中间文件.md": CandidatePruningMarkdownRenderer().render(
            pruning, module
        ),
        f"{module} 需求规划中间文件.md": RequirementPlanningMarkdownRenderer().render(
            planning
        ),
    }
    for filename, content in artifacts.items():
        (output_dir / filename).write_text(content, encoding="utf-8")
if __name__ == "__main__":
    raise SystemExit(main())
