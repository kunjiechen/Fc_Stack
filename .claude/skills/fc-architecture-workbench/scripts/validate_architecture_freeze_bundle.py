from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


TOP_LEVEL_REQUIRED = {
    "module",
    "architecture_version",
    "architecture_status",
    "output_mode",
    "freeze_matrix",
    "coverage_result",
    "implementation_constraints",
}

OBJECT_GROUPS = (
    "external_apis",
    "dependency_apis",
    "binding_items",
    "config_macros",
    "strategy_items",
    "calibration_items",
    "runtime_states",
    "memmap_sections",
    "file_items",
    "risk_items",
)

FREEZE_STATUS = {"formal", "conditional", "reserved", "pending_confirm", "rejected"}
FREEZE_ACTION = {
    "freeze_external_api",
    "freeze_dependency_api",
    "freeze_binding_item",
    "freeze_config_macro",
    "freeze_strategy_item",
    "freeze_calibration_item",
    "freeze_runtime_state",
    "freeze_memmap_section",
    "freeze_file_item",
    "reserve",
    "mark_pending_confirm",
    "reject",
    "architecture_only_constraint",
}
SOURCE_TYPE = {"requirement", "constraint", "architecture_seed", "grounding_rule"}
COVERAGE_STATUS = {
    "covered",
    "covered_with_constraint",
    "reserved",
    "pending_confirm",
    "not_applicable_at_architecture",
    "not_covered",
}
ARCH_STATUS = {"Draft", "Released"}
OUTPUT_MODE = {"Quick Draft", "Formal Draft", "Released"}
FORMAL_STATUS = {"Formal", "Conditional", "Pending Confirmation", "Not Recommended"}
RISK_STATUS = {"待评审", "已评审", "待修改"}
RISK_GATE_LEVEL = {"release_blocker", "implementation_blocker", "incremental_followup"}
RISK_IMPACT_SCOPE = {
    "core_behavior",
    "implementation_behavior",
    "architecture_followup",
    "project_compliance",
    "safety_compliance",
    "nonfunctional_budget",
}
RISK_INDEX = re.compile(r"^R\d+$|^R-OTHER$")


def _require_fields(
    issues: list[str],
    path: Path,
    group: str,
    index: int,
    item: dict[str, Any],
    required: tuple[str, ...],
) -> None:
    missing = [field for field in required if item.get(field) in (None, "", [])]
    if missing:
        issues.append(f"{path}: {group}[{index}] missing required fields: {', '.join(missing)}")


def _expect_list(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    field: str,
) -> list[Any]:
    value = payload.get(field, [])
    if not isinstance(value, list):
        issues.append(f"{path}: {field} must be a list")
        return []
    return value


def _validate_semantic_objects(path: Path, payload: dict[str, Any], issues: list[str]) -> None:
    for group in OBJECT_GROUPS:
        items = payload.get(group, [])
        if items is None:
            continue
        if not isinstance(items, list):
            issues.append(f"{path}: {group} must be a list")
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                issues.append(f"{path}: {group}[{index}] must be an object")
                continue
            freeze_status = item.get("freeze_status")
            if freeze_status and freeze_status not in FREEZE_STATUS:
                issues.append(f"{path}: {group}[{index}] has invalid freeze_status")
            if group == "risk_items":
                _require_fields(
                    issues, path, group, index, item,
                    ("index", "title", "risk", "impact", "recommended_action", "status"),
                )
                risk_index = item.get("index", "")
                if risk_index and not RISK_INDEX.fullmatch(risk_index):
                    issues.append(f"{path}: {group}[{index}] index must look like R1 or R-OTHER")
                if item.get("gate_level") and item["gate_level"] not in RISK_GATE_LEVEL:
                    issues.append(f"{path}: {group}[{index}] has invalid gate_level")
                if item.get("impact_scope") and item["impact_scope"] not in RISK_IMPACT_SCOPE:
                    issues.append(f"{path}: {group}[{index}] has invalid impact_scope")
                if item.get("status") and item["status"] not in RISK_STATUS:
                    issues.append(f"{path}: {group}[{index}] has invalid risk status")
            else:
                if item.get("status") and item["status"] not in FORMAL_STATUS:
                    issues.append(f"{path}: {group}[{index}] has invalid semantic status")


def validate_architecture_freeze_bundle(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    if not isinstance(payload, dict):
        return [f"{path}: top-level payload must be a JSON object"]

    missing_top = sorted(field for field in TOP_LEVEL_REQUIRED if payload.get(field) in (None, ""))
    if missing_top:
        issues.append(f"{path}: missing top-level fields: {', '.join(missing_top)}")

    architecture_status = payload.get("architecture_status")
    if architecture_status and architecture_status not in ARCH_STATUS:
        issues.append(f"{path}: architecture_status must be Draft or Released")

    output_mode = payload.get("output_mode")
    if output_mode and output_mode not in OUTPUT_MODE:
        issues.append(f"{path}: output_mode must be Quick Draft, Formal Draft, or Released")
    if output_mode == "Quick Draft" and architecture_status == "Released":
        issues.append(f"{path}: Quick Draft cannot be used with architecture_status Released")

    freeze_matrix = _expect_list(issues, path, payload, "freeze_matrix")
    for index, item in enumerate(freeze_matrix):
        if not isinstance(item, dict):
            issues.append(f"{path}: freeze_matrix[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "freeze_matrix", index, item,
            ("source_id", "source_type", "architecture_target", "target_name", "freeze_action", "freeze_status", "reason"),
        )
        if item.get("source_type") and item["source_type"] not in SOURCE_TYPE:
            issues.append(f"{path}: freeze_matrix[{index}] has invalid source_type")
        if item.get("freeze_action") and item["freeze_action"] not in FREEZE_ACTION:
            issues.append(f"{path}: freeze_matrix[{index}] has invalid freeze_action")
        if item.get("freeze_status") and item["freeze_status"] not in FREEZE_STATUS:
            issues.append(f"{path}: freeze_matrix[{index}] has invalid freeze_status")

    coverage_result = _expect_list(issues, path, payload, "coverage_result")
    for index, item in enumerate(coverage_result):
        if not isinstance(item, dict):
            issues.append(f"{path}: coverage_result[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "coverage_result", index, item,
            ("requirement_id", "coverage_status", "coverage_object", "reason"),
        )
        if item.get("coverage_status") and item["coverage_status"] not in COVERAGE_STATUS:
            issues.append(f"{path}: coverage_result[{index}] has invalid coverage_status")

    rule_evidence = _expect_list(issues, path, payload, "rule_evidence")
    for index, item in enumerate(rule_evidence):
        if not isinstance(item, dict):
            issues.append(f"{path}: rule_evidence[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "rule_evidence", index, item,
            ("object_group", "object_name", "rule_source", "rule_reason"),
        )

    grounding_evidence = _expect_list(issues, path, payload, "grounding_evidence")
    for index, item in enumerate(grounding_evidence):
        if not isinstance(item, dict):
            issues.append(f"{path}: grounding_evidence[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "grounding_evidence", index, item,
            ("object_group", "object_name", "grounding_source", "grounding_reason"),
        )

    implementation_constraints = payload.get("implementation_constraints", {})
    if not isinstance(implementation_constraints, dict):
        issues.append(f"{path}: implementation_constraints must be an object")
    else:
        required_lists = (
            "frozen_external_interfaces",
            "frozen_dependency_interfaces",
            "frozen_binding_items",
            "frozen_config_items",
            "frozen_strategy_items",
            "frozen_calibration_items",
            "reserved_capabilities",
            "pending_confirm_items",
            "implementation_prohibitions",
            "implementation_required_areas",
        )
        for field in required_lists:
            value = implementation_constraints.get(field, [])
            if not isinstance(value, list):
                issues.append(f"{path}: implementation_constraints.{field} must be a list")

    _validate_semantic_objects(path, payload, issues)

    formal_targets = set()
    for item in freeze_matrix:
        if isinstance(item, dict) and item.get("freeze_status") == "formal":
            name = item.get("target_name")
            if name:
                formal_targets.add(name)

    if architecture_status == "Released":
        for index, item in enumerate(freeze_matrix):
            if not isinstance(item, dict):
                continue
            if item.get("freeze_status") in {"reserved", "pending_confirm"}:
                issues.append(
                    f"{path}: freeze_matrix[{index}] uses {item.get('freeze_status')} in Released architecture"
                )

    for group in ("external_apis", "dependency_apis", "binding_items", "config_macros", "runtime_states", "memmap_sections", "file_items"):
        for index, item in enumerate(payload.get(group, [])):
            if not isinstance(item, dict):
                continue
            freeze_status = item.get("freeze_status")
            if freeze_status == "formal" and not item.get("evidence") and group != "file_items":
                issues.append(f"{path}: {group}[{index}] is formal but missing evidence")

    if implementation_constraints and formal_targets:
        frozen_external = set(implementation_constraints.get("frozen_external_interfaces", []))
        for item in payload.get("external_apis", []):
            if not isinstance(item, dict):
                continue
            if item.get("freeze_status") == "formal" and item.get("name") and item["name"] not in frozen_external:
                issues.append(
                    f"{path}: formal external API `{item['name']}` must appear in implementation_constraints.frozen_external_interfaces"
                )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FC architecture freeze bundle JSON.")
    parser.add_argument("paths", nargs="+", help="JSON file(s) to validate")
    args = parser.parse_args()

    issues: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                issues.extend(validate_architecture_freeze_bundle(child))
        else:
            issues.extend(validate_architecture_freeze_bundle(path))

    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("Architecture freeze bundle validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
