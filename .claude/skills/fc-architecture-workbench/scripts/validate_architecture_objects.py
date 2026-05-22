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
}

OBJECT_GROUPS = (
    "external_apis",
    "dependency_apis",
    "config_macros",
    "calibration_items",
    "runtime_states",
    "memmap_sections",
    "file_items",
    "risk_items",
)

FORMAL_STATUS = {
    "Formal",
    "Conditional",
    "Pending Confirmation",
    "Not Recommended",
}

RISK_STATUS = {"待评审", "已评审", "待修改"}
REQUIRED_LEVEL = {"Required", "Conditional", "Optional"}
MACRO_TYPE = {
    "Feature Enable",
    "Development Error Detect",
    "Behavior Selection",
    "Count Size",
    "Timeout Retry Timing",
    "Vendor Version Release",
}
OUTPUT_MODE = {"Quick Draft", "Formal Draft", "Released"}
ARCH_STATUS = {"Draft", "Released"}
MACRO_NAME = re.compile(r"^[A-Z0-9_]+$")
RISK_INDEX = re.compile(r"^R\d+$|^R-OTHER$")


def _require_fields(
    issues: list[str],
    path: Path,
    group: str,
    index: int,
    item: dict[str, Any],
    required: tuple[str, ...],
) -> None:
    missing = [field for field in required if not item.get(field)]
    if missing:
        issues.append(f"{path}: {group}[{index}] missing required fields: {', '.join(missing)}")


def validate_architecture_objects(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    if not isinstance(payload, dict):
        return [f"{path}: top-level payload must be a JSON object"]

    missing_top = sorted(field for field in TOP_LEVEL_REQUIRED if not payload.get(field))
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

    for group in OBJECT_GROUPS:
        items = payload.get(group, [])
        if items is None:
            continue
        if not isinstance(items, list):
            issues.append(f"{path}: {group} must be a list")

    for index, item in enumerate(payload.get("external_apis", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: external_apis[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "external_apis", index, item,
            ("name", "prototype", "description", "sync_mode", "reentrancy", "return_value", "constraints", "evidence", "status"),
        )
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: external_apis[{index}] has invalid status")

    for index, item in enumerate(payload.get("dependency_apis", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: dependency_apis[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "dependency_apis", index, item,
            ("name", "prototype", "description", "implemented_by", "evidence", "status"),
        )
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: dependency_apis[{index}] has invalid status")

    for index, item in enumerate(payload.get("config_macros", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: config_macros[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "config_macros", index, item,
            ("name", "purpose", "macro_type", "default_value", "usage_location", "evidence", "status"),
        )
        name = item.get("name", "")
        if name and not MACRO_NAME.fullmatch(name):
            issues.append(f"{path}: config_macros[{index}] name must be ALL_CAPS macro style")
        if item.get("macro_type") and item["macro_type"] not in MACRO_TYPE:
            issues.append(f"{path}: config_macros[{index}] has invalid macro_type")
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: config_macros[{index}] has invalid status")

    for index, item in enumerate(payload.get("calibration_items", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: calibration_items[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "calibration_items", index, item,
            ("name", "type", "initial_value", "description", "status"),
        )
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: calibration_items[{index}] has invalid status")

    for index, item in enumerate(payload.get("runtime_states", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: runtime_states[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "runtime_states", index, item,
            ("name", "owner", "read_write_side", "lifecycle", "memory_section", "concurrency_strategy"),
        )
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: runtime_states[{index}] has invalid status")

    for index, item in enumerate(payload.get("memmap_sections", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: memmap_sections[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "memmap_sections", index, item,
            ("name", "target_content", "start_macro", "stop_macro", "used_files", "notes"),
        )
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: memmap_sections[{index}] has invalid status")

    for index, item in enumerate(payload.get("file_items", [])):
        if not isinstance(item, dict):
            issues.append(f"{path}: file_items[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "file_items", index, item,
            ("name", "required_level", "responsibility", "key_content"),
        )
        if item.get("required_level") and item["required_level"] not in REQUIRED_LEVEL:
            issues.append(f"{path}: file_items[{index}] has invalid required_level")
        if item.get("status") and item["status"] not in FORMAL_STATUS:
            issues.append(f"{path}: file_items[{index}] has invalid status")

    risk_items = payload.get("risk_items", [])
    real_risk_count = 0
    for index, item in enumerate(risk_items):
        if not isinstance(item, dict):
            issues.append(f"{path}: risk_items[{index}] must be an object")
            continue
        _require_fields(
            issues, path, "risk_items", index, item,
            ("index", "title", "risk", "impact", "recommended_action", "status"),
        )
        risk_index = item.get("index", "")
        if risk_index and not RISK_INDEX.fullmatch(risk_index):
            issues.append(f"{path}: risk_items[{index}] index must look like R1 or R-OTHER")
        if risk_index and risk_index != "R-OTHER":
            real_risk_count += 1
        if item.get("status") and item["status"] not in RISK_STATUS:
            issues.append(f"{path}: risk_items[{index}] has invalid risk status")

    if output_mode == "Quick Draft" and real_risk_count > 5:
        issues.append(f"{path}: Quick Draft should keep only 3..5 real risk_items before R-OTHER")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FC architecture semantic objects JSON.")
    parser.add_argument("paths", nargs="+", help="JSON file(s) to validate")
    args = parser.parse_args()

    issues: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                issues.extend(validate_architecture_objects(child))
        else:
            issues.extend(validate_architecture_objects(path))

    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("Architecture object validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
