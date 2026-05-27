"""Output helpers for CLI emit dispatch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bundle import (
    render_architecture_seed_yaml,
    render_bundle_json,
    render_bundle_yaml,
    render_test_seed_yaml,
)
from .bundle_validation import build_validation_report
from .gate_check import GateChecker, render_gate_check_markdown
from .open_items import OpenItemsCollector, render_open_items_markdown
from .operation_checklist import (
    render_check_list_markdown,
    render_operation_steps_markdown,
    render_review_record_markdown,
)
from .raw_requirements import RawRequirementCoverageAnalyzer, render_coverage_markdown
from .schema import CoverageReport
from .source_index import (
    DerivationMatrixGenerator,
    ExtractRecordGenerator,
    SourceIndexGenerator,
)
from .srs import DocxSrsRenderer, HtmlSrsRenderer, MarkdownSrsRenderer
from .traceability import ChangeImpactAnalyzer, TraceabilityMarkdownRenderer
def emit_text(content: str, output: Path | None) -> int:
    if output is None:
        print(content, end="")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(json.dumps({"output": str(output)}, ensure_ascii=False, indent=2))
    return 0


def dispatch_final_emit(
    *,
    emit: str,
    output: Path | None,
    srs_document: Any,
    requirement_bundle: Any,
    traceability: Any,
    raw_document: Any | None,
    raw_coverage_detail: list[dict[str, Any]] | None,
    planned_requirements: list[Any],
    module: str,
    changed: str,
    **kwargs: Any,
) -> int:
    engineering_reqs = kwargs.get("engineering_reqs", [])
    findings = kwargs.get("findings", [])

    if emit == "srs-markdown":
        return emit_text(MarkdownSrsRenderer().render(srs_document), output)
    if emit == "srs-html":
        return emit_text(HtmlSrsRenderer().render(srs_document), output)
    if emit == "srs-docx":
        out = output or Path("Output/doc/srs.docx")
        DocxSrsRenderer().render_to_file(srs_document, out)
        print(json.dumps({"output": str(out)}, ensure_ascii=False, indent=2))
        return 0
    if emit == "requirement-bundle":
        return emit_text(render_bundle_yaml(requirement_bundle), output)
    if emit == "requirement-bundle-json":
        return emit_text(render_bundle_json(requirement_bundle), output)
    if emit == "architecture-seed":
        return emit_text(render_architecture_seed_yaml(requirement_bundle), output)
    if emit == "test-seed":
        return emit_text(render_test_seed_yaml(requirement_bundle), output)
    if emit == "bundle-validation":
        payload = build_validation_report(requirement_bundle.to_dict())
        return emit_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", output)
    if emit == "traceability-markdown":
        content = TraceabilityMarkdownRenderer().render(
            traceability,
            module=module,
            raw_document=raw_document,
            raw_coverage=raw_coverage_detail,
        )
        return emit_text(content, output)
    if emit == "raw-coverage":
        report = raw_document and RawRequirementCoverageAnalyzer().analyze(
            raw_document, planned_requirements
        )
        if report is None:
            report = CoverageReport(
                total_user_reqs=0,
                covered=0,
                uncovered=[],
                coverage_rate=1.0,
                is_satisfied=True,
                gaps_detail="",
            )
        return emit_text(render_coverage_markdown(report, module), output)

    # ---- New workflow emits ----
    if emit == "source-index":
        generator = SourceIndexGenerator(module=module)
        entries = generator.generate(
            input_file=kwargs.get("input_file", ""),
            has_raw_requirements=kwargs.get("has_raw_requirements", False),
            has_project_constraints=kwargs.get("has_project_constraints", False),
        )
        return emit_text(generator.render_markdown(entries, module), output)

    if emit == "extract-records":
        feature_groups = kwargs.get("feature_groups", [])
        generator = SourceIndexGenerator(module=module)
        entries = generator.generate(
            input_file=kwargs.get("input_file", ""),
            has_raw_requirements=kwargs.get("has_raw_requirements", False),
        )
        extract_gen = ExtractRecordGenerator()
        records = extract_gen.generate_from_features(feature_groups, entries, module)
        return emit_text(extract_gen.render_markdown(records, module), output)

    if emit == "open-items":
        collector = OpenItemsCollector()
        items = collector.collect(engineering_reqs, findings, module)
        return emit_text(render_open_items_markdown(items, module), output)

    if emit == "gate-check":
        source_count = kwargs.get("source_count", 0)
        checker = GateChecker(
            module=module,
            source_count=source_count,
            has_raw_requirements=kwargs.get("has_raw_requirements", False),
            has_datasheet=kwargs.get("has_datasheet", True),
            has_project_constraints=kwargs.get("has_project_constraints", False),
        )
        open_items_list = kwargs.get("open_items", [])
        reports = checker.check_all(engineering_reqs, findings, open_items_list)
        return emit_text(render_gate_check_markdown(reports, module), output)

    if emit == "review-record":
        gate_reports = kwargs.get("gate_reports", [])
        open_items_list = kwargs.get("open_items", [])
        return emit_text(
            render_review_record_markdown(
                module=module,
                gate_reports=gate_reports,
                open_items=open_items_list,
            ),
            output,
        )

    if emit == "check-list":
        gate_reports = kwargs.get("gate_reports", [])
        open_items_list = kwargs.get("open_items", [])
        return emit_text(
            render_check_list_markdown(
                module=module,
                gate_reports=gate_reports,
                open_items=open_items_list,
            ),
            output,
        )

    if emit == "operation-steps":
        open_items_list = kwargs.get("open_items", [])
        return emit_text(
            render_operation_steps_markdown(
                module=module,
                output_dir=str(output.parent) if output else "",
                input_file=kwargs.get("input_file", ""),
                has_raw_requirements=kwargs.get("has_raw_requirements", False),
                has_datasheet=kwargs.get("has_datasheet", True),
                open_items=open_items_list,
                loop_count=kwargs.get("loop_count", 0),
                auto_fixes_applied=kwargs.get("auto_fixes_applied", 0),
                requirement_count=len(engineering_reqs),
            ),
            output,
        )

    payload: dict[str, Any]
    if emit == "traceability":
        payload = {"trace_links": [item.to_dict() for item in traceability.trace_links]}
    elif emit == "coverage":
        payload = {"coverage": [item.to_dict() for item in traceability.coverage]}
    elif emit == "verification":
        payload = {"verification": [item.to_dict() for item in traceability.verification]}
    elif emit == "aspice":
        payload = traceability.evidence.to_dict()
    elif emit == "impact":
        changed_ids = [item.strip() for item in changed.split(",") if item.strip()]
        payload = {
            "impact": [
                item.to_dict()
                for item in ChangeImpactAnalyzer().analyze(
                    traceability.trace_links, changed_ids
                )
            ]
        }
    else:
        payload = {}

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
