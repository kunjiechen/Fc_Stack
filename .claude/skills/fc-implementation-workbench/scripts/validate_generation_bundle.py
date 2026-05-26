#!/usr/bin/env python3
"""Validate a structured FC generation bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from script_dependency_support import require_modules

require_modules({"PyYAML": "yaml", "jsonschema": "jsonschema"}, context="validate_generation_bundle.py")

import yaml
from jsonschema import Draft202012Validator


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Bundle root must be a mapping object.")
    return data


def grounding_module_names(index_path: Path) -> set[str]:
    data = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    modules = data.get("modules", []) if isinstance(data, dict) else []
    return {item.get("name", "") for item in modules if isinstance(item, dict) and item.get("name")}


def validate_with_schema(instance: dict, schema: dict, label: str) -> list[str]:
    errors: list[str] = []
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{label} schema violation at {path}: {error.message}")
    return errors


def names_by_status(items: list[dict], accepted: set[str]) -> set[str]:
    names = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("status") in accepted and item.get("name"):
            names.add(str(item["name"]))
    return names


def trace_ids_for(items: list[dict], name: str) -> list[str]:
    for item in items:
        if isinstance(item, dict) and item.get("name") == name:
            trace_ids = item.get("trace_ids", [])
            if isinstance(trace_ids, list):
                return [str(entry) for entry in trace_ids]
    return []


def validate_bundle(bundle: dict, root: Path) -> list[str]:
    errors: list[str] = []

    schemas_dir = root / "references" / "schemas"
    grounding_index = root / "references" / "grounding" / "index.yaml"

    req_schema = load_json(schemas_dir / "requirements.schema.json")
    arch_schema = load_json(schemas_dir / "architecture.schema.json")
    dd_schema = load_json(schemas_dir / "detailed_design.schema.json")
    known_grounding = grounding_module_names(grounding_index)

    if "module" not in bundle:
        return ["bundle missing top-level module"]

    module = bundle["module"]

    requirements_obj = {"module": module, "requirements": bundle.get("requirements", [])}
    errors.extend(validate_with_schema(requirements_obj, req_schema, "requirements"))
    for item in requirements_obj.get("requirements", []):
        if not isinstance(item, dict):
            continue
        if item.get("status") == "pending_confirm":
            if not item.get("decision"):
                errors.append(f"pending_confirm requirement missing decision: {item.get('id', '<unknown>')}")
            if not item.get("decision_reason"):
                errors.append(f"pending_confirm requirement missing decision_reason: {item.get('id', '<unknown>')}")

    architecture = bundle.get("architecture", {})
    detailed_design = bundle.get("detailed_design", {})
    if not isinstance(architecture, dict):
        errors.append("architecture must be an object")
        architecture = {}
    if not isinstance(detailed_design, dict):
        errors.append("detailed_design must be an object")
        detailed_design = {}

    errors.extend(validate_with_schema(architecture, arch_schema, "architecture"))
    dd_for_schema = {
        "module": detailed_design.get("module"),
        "grounding_modules": bundle.get("grounding_modules", []),
        "grounding_patterns": bundle.get("grounding_patterns", []),
        "grounding_rejections": bundle.get("grounding_rejections", []),
        "external_interfaces": detailed_design.get("external_interfaces", []),
        "internal_interfaces": detailed_design.get("internal_interfaces", []),
        "dependency_interfaces": detailed_design.get("dependency_interfaces", []),
        "assumptions": bundle.get("assumptions", []),
        "risks": bundle.get("risks", []),
        "conf_evidence": bundle.get("conf_evidence", []),
    }
    errors.extend(validate_with_schema(dd_for_schema, dd_schema, "detailed_design"))

    top_grounding = bundle.get("grounding_modules", [])
    if not isinstance(top_grounding, list):
        errors.append("grounding_modules must be a list")
        top_grounding = []

    unknown_grounding = sorted(set(str(item) for item in top_grounding) - known_grounding)
    if unknown_grounding:
        errors.append(f"unknown grounding modules: {', '.join(unknown_grounding)}")

    cfg_objects = bundle.get("cfg_objects", [])
    if cfg_objects and not isinstance(cfg_objects, list):
        errors.append("cfg_objects must be a list when present")
        cfg_objects = []
    for index, item in enumerate(cfg_objects):
        if not isinstance(item, dict):
            errors.append(f"cfg_objects[{index}] must be an object")
            continue
        module_name = str(item.get("module", ""))
        symbol = str(item.get("symbol", ""))
        cfg_path = str(item.get("cfg_path", ""))
        if not module_name:
            errors.append(f"cfg_objects[{index}] missing module")
        elif module_name not in top_grounding:
            errors.append(f"cfg_objects[{index}] module not selected in grounding_modules: {module_name}")
        if not symbol:
            errors.append(f"cfg_objects[{index}] missing symbol")
        if not cfg_path:
            errors.append(f"cfg_objects[{index}] missing cfg_path")

    if architecture.get("module") != module:
        errors.append("architecture.module does not match bundle.module")
    if detailed_design.get("module") != module:
        errors.append("detailed_design.module does not match bundle.module")

    arch_grounding = architecture.get("grounding_modules", [])
    if arch_grounding and arch_grounding != top_grounding:
        errors.append("architecture.grounding_modules does not match top-level grounding_modules")

    formal_external = names_by_status(architecture.get("external_interfaces", []), {"formal"})
    formal_dependency = names_by_status(architecture.get("dependency_interfaces", []), {"formal"})
    dd_external = {item.get("name") for item in detailed_design.get("external_interfaces", []) if isinstance(item, dict)}
    dd_dependency = {item.get("name") for item in detailed_design.get("dependency_interfaces", []) if isinstance(item, dict)}

    missing_external = sorted(name for name in formal_external if name not in dd_external)
    missing_dependency = sorted(name for name in formal_dependency if name not in dd_dependency)
    if missing_external:
        errors.append(f"DD missing formal external interfaces: {', '.join(missing_external)}")
    if missing_dependency:
        errors.append(f"DD missing formal dependency interfaces: {', '.join(missing_dependency)}")

    for name in sorted(formal_external):
        trace_ids = trace_ids_for(architecture.get("external_interfaces", []), name)
        if not trace_ids:
            errors.append(f"architecture formal external interface missing trace_ids: {name}")
        dd_trace_ids = trace_ids_for(detailed_design.get("external_interfaces", []), name)
        if name in dd_external and not dd_trace_ids:
            errors.append(f"DD external interface missing trace_ids: {name}")

    for name in sorted(formal_dependency):
        trace_ids = trace_ids_for(architecture.get("dependency_interfaces", []), name)
        if not trace_ids:
            errors.append(f"architecture formal dependency interface missing trace_ids: {name}")
        dd_trace_ids = trace_ids_for(detailed_design.get("dependency_interfaces", []), name)
        if name in dd_dependency and not dd_trace_ids:
            errors.append(f"DD dependency interface missing trace_ids: {name}")

    all_names = set()
    allowed_external_refs = {"Det_ReportError"}
    for key in ("external_interfaces", "internal_interfaces", "dependency_interfaces"):
        for item in detailed_design.get(key, []):
            if isinstance(item, dict) and item.get("name"):
                all_names.add(str(item["name"]))

    for key in ("external_interfaces", "internal_interfaces", "dependency_interfaces"):
        for item in detailed_design.get(key, []):
            if not isinstance(item, dict):
                continue
            name = item.get("name", "<unknown>")
            for ref in item.get("relationship_links", []) or []:
                if ref in allowed_external_refs:
                    continue
                if ref not in all_names:
                    errors.append(f"{key}.{name} has undefined relationship link: {ref}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an FC generation bundle against local schemas and grounding rules.")
    parser.add_argument("--bundle", required=True, help="Path to YAML generation bundle")
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    skill_root = bundle_path.parent.parent if False else Path(__file__).resolve().parent.parent
    bundle = load_yaml(bundle_path)
    errors = validate_bundle(bundle, skill_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: bundle validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
