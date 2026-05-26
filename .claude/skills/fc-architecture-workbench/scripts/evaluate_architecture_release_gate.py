from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


FORMAL_GROUPS = (
    "external_apis",
    "dependency_apis",
    "binding_items",
    "config_macros",
    "strategy_items",
    "calibration_items",
    "runtime_states",
    "memmap_sections",
    "file_items",
)


def _object_name(item: dict[str, Any], fallback: str) -> str:
    for key in ("name", "index", "title"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _collect_formal_objects(bundle: dict[str, Any]) -> list[tuple[str, str]]:
    objects: list[tuple[str, str]] = []
    for group in FORMAL_GROUPS:
        for index, item in enumerate(bundle.get(group, [])):
            if not isinstance(item, dict):
                continue
            if item.get("freeze_status") == "formal":
                objects.append((group, _object_name(item, f"{group}[{index}]")))
    return objects


def _evidence_index(items: list[dict[str, Any]], source_key: str) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        group = item.get("object_group")
        name = item.get("object_name")
        source = item.get(source_key)
        if isinstance(group, str) and isinstance(name, str) and isinstance(source, str):
            if group.strip() and name.strip() and source.strip():
                result.add((group.strip(), name.strip()))
    return result


def _has_module_grounding(bundle: dict[str, Any]) -> bool:
    module_name = bundle.get("module", "")
    for item in bundle.get("grounding_evidence", []):
        if not isinstance(item, dict):
            continue
        if item.get("object_group") == "module_family" and item.get("object_name") == module_name:
            grounding_source = item.get("grounding_source")
            grounding_reason = item.get("grounding_reason")
            if grounding_source and grounding_reason:
                return True
    return False


def _split_risks_by_gate_level(risk_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    release_blockers: list[dict[str, Any]] = []
    implementation_blockers: list[dict[str, Any]] = []
    incremental_followups: list[dict[str, Any]] = []
    for item in risk_items:
        if not isinstance(item, dict):
            continue
        level = item.get("gate_level")
        if level == "release_blocker":
            release_blockers.append(item)
        elif level == "implementation_blocker":
            implementation_blockers.append(item)
        else:
            incremental_followups.append(item)
    return release_blockers, implementation_blockers, incremental_followups


def _split_reserved_by_gate_level(reserved_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    release_blockers: list[dict[str, Any]] = []
    implementation_blockers: list[dict[str, Any]] = []
    incremental_followups: list[dict[str, Any]] = []
    for item in reserved_items:
        if not isinstance(item, dict):
            continue
        level = item.get("gate_level")
        if level == "release_blocker":
            release_blockers.append(item)
        elif level == "implementation_blocker":
            implementation_blockers.append(item)
        else:
            incremental_followups.append(item)
    return release_blockers, implementation_blockers, incremental_followups


def _split_pending_by_gate_level(pending_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    release_blockers: list[dict[str, Any]] = []
    implementation_blockers: list[dict[str, Any]] = []
    incremental_followups: list[dict[str, Any]] = []
    for item in pending_items:
        if not isinstance(item, dict):
            continue
        level = item.get("gate_level")
        if level == "release_blocker":
            release_blockers.append(item)
        elif level == "implementation_blocker":
            implementation_blockers.append(item)
        else:
            incremental_followups.append(item)
    return release_blockers, implementation_blockers, incremental_followups


def evaluate_architecture_release_gate(bundle: dict[str, Any]) -> dict[str, Any]:
    coverage_counts = Counter(
        item.get("coverage_status", "unknown")
        for item in bundle.get("coverage_result", [])
        if isinstance(item, dict)
    )
    freeze_counts = Counter(
        item.get("freeze_status", "unknown")
        for item in bundle.get("freeze_matrix", [])
        if isinstance(item, dict)
    )
    object_counts = {
        group: len([item for item in bundle.get(group, []) if isinstance(item, dict)])
        for group in FORMAL_GROUPS + ("risk_items",)
    }

    formal_objects = _collect_formal_objects(bundle)
    rule_index = _evidence_index(bundle.get("rule_evidence", []), "rule_source")
    missing_rule_evidence = [
        {"object_group": group, "object_name": name}
        for group, name in formal_objects
        if (group, name) not in rule_index
    ]
    module_grounding_present = _has_module_grounding(bundle)

    pending_confirm_requirements = [
        {
            "requirement_id": item.get("requirement_id", ""),
            "coverage_object": item.get("coverage_object", ""),
            "reason": item.get("reason", ""),
            "gate_level": item.get("gate_level", ""),
            "impact_scope": item.get("impact_scope", ""),
            "close_condition": item.get("close_condition", ""),
        }
        for item in bundle.get("coverage_result", [])
        if isinstance(item, dict) and item.get("coverage_status") == "pending_confirm"
    ]
    release_blocker_pending, implementation_blocker_pending, incremental_followup_pending = _split_pending_by_gate_level(
        pending_confirm_requirements
    )
    reserved_requirements = [
        item.get("requirement_id", "")
        for item in bundle.get("coverage_result", [])
        if isinstance(item, dict) and item.get("coverage_status") == "reserved"
    ]
    open_risks = [
        {
            "index": item.get("index", ""),
            "title": item.get("title", ""),
            "status": item.get("status", ""),
            "gate_level": item.get("gate_level", ""),
            "impact_scope": item.get("impact_scope", ""),
            "close_condition": item.get("close_condition", ""),
            "source_requirement_id": item.get("source_requirement_id", ""),
        }
        for item in bundle.get("risk_items", [])
        if isinstance(item, dict) and item.get("status") in {"待评审", "待修改"}
    ]
    release_blocker_risks, implementation_blocker_risks, incremental_followup_risks = _split_risks_by_gate_level(open_risks)
    reserved_capabilities = [
        {
            "title": item.get("target_name", ""),
            "reason": item.get("reason", ""),
            "gate_level": item.get("gate_level", ""),
            "impact_scope": item.get("impact_scope", ""),
            "close_condition": item.get("close_condition", ""),
            "source_requirement_ids": item.get("source_requirement_ids", []),
        }
        for item in bundle.get("freeze_matrix", [])
        if isinstance(item, dict) and item.get("freeze_status") == "reserved"
    ]
    release_blocker_reserved, implementation_blocker_reserved, incremental_followup_reserved = _split_reserved_by_gate_level(
        reserved_capabilities
    )

    blocking_findings: list[str] = []
    warning_findings: list[str] = []

    if bundle.get("architecture_status") != "Released":
        blocking_findings.append("architecture_status 不是 Released")
    if bundle.get("output_mode") != "Released":
        blocking_findings.append("output_mode 不是 Released")
    if release_blocker_pending:
        blocking_findings.append(f"仍有 {len(release_blocker_pending)} 个 release-blocker pending requirement")
    if implementation_blocker_pending:
        blocking_findings.append(f"仍有 {len(implementation_blocker_pending)} 个 implementation-blocker pending requirement")
    if freeze_counts.get("pending_confirm", 0):
        blocking_findings.append(f"freeze_matrix 中仍有 {freeze_counts['pending_confirm']} 个 pending_confirm 对象")
    if release_blocker_risks:
        blocking_findings.append(f"仍有 {len(release_blocker_risks)} 个 release-blocker 风险项")
    if implementation_blocker_risks:
        blocking_findings.append(f"仍有 {len(implementation_blocker_risks)} 个 implementation-blocker 风险项")
    if release_blocker_reserved:
        blocking_findings.append(f"仍有 {len(release_blocker_reserved)} 个 release-blocker reserved capability")
    if implementation_blocker_reserved:
        blocking_findings.append(f"仍有 {len(implementation_blocker_reserved)} 个 implementation-blocker reserved capability")
    if missing_rule_evidence:
        blocking_findings.append(f"有 {len(missing_rule_evidence)} 个 formal 对象缺少 rule_evidence")
    if not module_grounding_present:
        blocking_findings.append("缺少 module-family grounding_evidence")

    if coverage_counts.get("covered_with_constraint", 0):
        warning_findings.append(
            f"存在 {coverage_counts['covered_with_constraint']} 个 covered_with_constraint requirement"
        )
    if reserved_requirements:
        warning_findings.append(f"存在 {len(reserved_requirements)} 个 reserved requirement")
    if incremental_followup_pending:
        warning_findings.append(f"存在 {len(incremental_followup_pending)} 个 incremental-followup pending requirement")
    if incremental_followup_risks:
        warning_findings.append(f"存在 {len(incremental_followup_risks)} 个 incremental-followup 风险项")
    if incremental_followup_reserved:
        warning_findings.append(f"存在 {len(incremental_followup_reserved)} 个 incremental-followup reserved capability")

    release_ready = not blocking_findings
    next_action = (
        "可进入正式发布或作为 released 架构基线固化。"
        if release_ready
        else "保持 Draft/Formal Draft，优先清理 pending_confirm/reserved/open risk，补齐 formal 对象证据后再申请 Released。"
    )

    return {
        "module": bundle.get("module", ""),
        "architecture_version": bundle.get("architecture_version", ""),
        "architecture_status": bundle.get("architecture_status", ""),
        "output_mode": bundle.get("output_mode", ""),
        "release_gate": {
            "release_ready": release_ready,
            "blocking_findings": blocking_findings,
            "warning_findings": warning_findings,
            "recommended_next_action": next_action,
        },
        "coverage_summary": dict(coverage_counts),
        "freeze_summary": dict(freeze_counts),
        "object_summary": object_counts,
        "proof_summary": {
            "formal_object_count": len(formal_objects),
            "rule_evidence_coverage": len(formal_objects) - len(missing_rule_evidence),
            "module_grounding_present": module_grounding_present,
            "pending_confirm_requirements": pending_confirm_requirements,
            "release_blocker_pending": release_blocker_pending,
            "implementation_blocker_pending": implementation_blocker_pending,
            "incremental_followup_pending": incremental_followup_pending,
            "reserved_requirements": reserved_requirements,
            "open_risks": open_risks,
            "release_blocker_risks": release_blocker_risks,
            "implementation_blocker_risks": implementation_blocker_risks,
            "incremental_followup_risks": incremental_followup_risks,
            "reserved_capabilities": reserved_capabilities,
            "release_blocker_reserved": release_blocker_reserved,
            "implementation_blocker_reserved": implementation_blocker_reserved,
            "incremental_followup_reserved": incremental_followup_reserved,
            "missing_rule_evidence": missing_rule_evidence,
        },
    }


def render_release_gate_markdown(report: dict[str, Any]) -> str:
    gate = report["release_gate"]
    coverage = report["coverage_summary"]
    freeze = report["freeze_summary"]
    objects = report["object_summary"]
    proof = report["proof_summary"]

    lines = [
        f"# {report['module']} Architecture Release Gate",
        "",
        f"- **Architecture Version**: {report['architecture_version']}",
        f"- **Architecture Status**: {report['architecture_status']}",
        f"- **Output Mode**: {report['output_mode']}",
        f"- **Release Ready**: {'Yes' if gate['release_ready'] else 'No'}",
        "",
        "## 1. Gate Decision",
        "",
        f"- **Recommended Action**: {gate['recommended_next_action']}",
        "",
        "## 2. Blocking Findings",
        "",
    ]
    lines.extend(f"- {item}" for item in gate["blocking_findings"]) if gate["blocking_findings"] else lines.append("- None")
    lines.extend(["", "## 3. Warning Findings", ""])
    lines.extend(f"- {item}" for item in gate["warning_findings"]) if gate["warning_findings"] else lines.append("- None")
    lines.extend(
        [
            "",
            "## 4. Coverage Proof",
            "",
            "| Metric | Count |",
            "| --- | ---: |",
            f"| covered | {coverage.get('covered', 0)} |",
            f"| covered_with_constraint | {coverage.get('covered_with_constraint', 0)} |",
            f"| pending_confirm | {coverage.get('pending_confirm', 0)} |",
            f"| reserved | {coverage.get('reserved', 0)} |",
            f"| not_covered | {coverage.get('not_covered', 0)} |",
            "",
            "## 5. Freeze Proof",
            "",
            "| Metric | Count |",
            "| --- | ---: |",
            f"| formal | {freeze.get('formal', 0)} |",
            f"| conditional | {freeze.get('conditional', 0)} |",
            f"| reserved | {freeze.get('reserved', 0)} |",
            f"| pending_confirm | {freeze.get('pending_confirm', 0)} |",
            f"| rejected | {freeze.get('rejected', 0)} |",
            "",
            "## 6. Object Inventory",
            "",
            "| Object Group | Count |",
            "| --- | ---: |",
        ]
    )
    for group, count in objects.items():
        lines.append(f"| {group} | {count} |")
    lines.extend(
        [
            "",
            "## 7. Evidence Completeness",
            "",
            f"- **Formal Objects**: {proof['formal_object_count']}",
            f"- **Rule Evidence Covered**: {proof['rule_evidence_coverage']}",
            f"- **Module Grounding Present**: {'Yes' if proof['module_grounding_present'] else 'No'}",
            "",
        ]
    )
    if proof["pending_confirm_requirements"]:
        lines.extend(["### 7.1 Pending Confirm Requirements", ""])
        lines.extend(
            f"- {item['requirement_id']} {item['coverage_object']} gate={item['gate_level']} scope={item['impact_scope']}"
            for item in proof["pending_confirm_requirements"]
        )
        lines.append("")
    if proof["release_blocker_pending"]:
        lines.extend(["### 7.1A Release Blocker Pending Requirements", ""])
        lines.extend(
            f"- {item['requirement_id']} {item['coverage_object']}: {item['close_condition']}"
            for item in proof["release_blocker_pending"]
        )
        lines.append("")
    if proof["implementation_blocker_pending"]:
        lines.extend(["### 7.1B Implementation Blocker Pending Requirements", ""])
        lines.extend(
            f"- {item['requirement_id']} {item['coverage_object']}: {item['close_condition']}"
            for item in proof["implementation_blocker_pending"]
        )
        lines.append("")
    if proof["incremental_followup_pending"]:
        lines.extend(["### 7.1C Incremental Follow-up Pending Requirements", ""])
        lines.extend(
            f"- {item['requirement_id']} {item['coverage_object']}: {item['close_condition']}"
            for item in proof["incremental_followup_pending"]
        )
        lines.append("")
    if proof["reserved_requirements"]:
        lines.extend(["### 7.2 Reserved Requirements", ""])
        lines.extend(f"- {item}" for item in proof["reserved_requirements"])
        lines.append("")
    if proof["reserved_capabilities"]:
        lines.extend(["### 7.2A Reserved Capabilities", ""])
        lines.extend(
            f"- {item['title']} gate={item['gate_level']} scope={item['impact_scope']}"
            for item in proof["reserved_capabilities"]
        )
        lines.append("")
    if proof["open_risks"]:
        lines.extend(["### 7.3 Open Risks", ""])
        lines.extend(
            f"- {item['index']} {item['title']} [{item['status']}] "
            f"gate={item['gate_level']} scope={item['impact_scope']}"
            for item in proof["open_risks"]
        )
        lines.append("")
    if proof["release_blocker_risks"]:
        lines.extend(["### 7.4 Release Blocker Risks", ""])
        lines.extend(
            f"- {item['index']} {item['title']}: {item['close_condition']}"
            for item in proof["release_blocker_risks"]
        )
        lines.append("")
    if proof["implementation_blocker_risks"]:
        lines.extend(["### 7.5 Implementation Blocker Risks", ""])
        lines.extend(
            f"- {item['index']} {item['title']}: {item['close_condition']}"
            for item in proof["implementation_blocker_risks"]
        )
        lines.append("")
    if proof["incremental_followup_risks"]:
        lines.extend(["### 7.6 Incremental Follow-up Risks", ""])
        lines.extend(
            f"- {item['index']} {item['title']}: {item['close_condition']}"
            for item in proof["incremental_followup_risks"]
        )
        lines.append("")
    if proof["release_blocker_reserved"]:
        lines.extend(["### 7.7 Release Blocker Reserved Capabilities", ""])
        lines.extend(
            f"- {item['title']}: {item['close_condition']}"
            for item in proof["release_blocker_reserved"]
        )
        lines.append("")
    if proof["implementation_blocker_reserved"]:
        lines.extend(["### 7.8 Implementation Blocker Reserved Capabilities", ""])
        lines.extend(
            f"- {item['title']}: {item['close_condition']}"
            for item in proof["implementation_blocker_reserved"]
        )
        lines.append("")
    if proof["incremental_followup_reserved"]:
        lines.extend(["### 7.9 Incremental Follow-up Reserved Capabilities", ""])
        lines.extend(
            f"- {item['title']}: {item['close_condition']}"
            for item in proof["incremental_followup_reserved"]
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate coverage proof and release gate for architecture freeze bundles.")
    parser.add_argument("input", type=Path, help="Architecture freeze bundle JSON path")
    parser.add_argument("--output-json", type=Path, help="Release gate report JSON path")
    parser.add_argument("--output-md", type=Path, help="Release gate report markdown path")
    parser.add_argument("--require-release-ready", action="store_true", help="Return non-zero when the bundle is not release-ready.")
    args = parser.parse_args()

    bundle = json.loads(args.input.read_text(encoding="utf-8"))
    report = evaluate_architecture_release_gate(bundle)

    if args.output_json:
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output_md:
        args.output_md.write_text(render_release_gate_markdown(report), encoding="utf-8")

    if args.require_release_ready and not report["release_gate"]["release_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
