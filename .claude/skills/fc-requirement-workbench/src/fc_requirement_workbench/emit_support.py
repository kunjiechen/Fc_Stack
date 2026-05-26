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
from .raw_requirements import RawRequirementCoverageAnalyzer, render_coverage_markdown
from .schema import CoverageReport
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
) -> int:
    if emit == "srs-markdown":
        return emit_text(MarkdownSrsRenderer().render(srs_document), output)
    if emit == "srs-html":
        return emit_text(HtmlSrsRenderer().render(srs_document), output)
    if emit == "srs-docx":
        out = output or Path("artifacts/doc/srs.docx")
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
