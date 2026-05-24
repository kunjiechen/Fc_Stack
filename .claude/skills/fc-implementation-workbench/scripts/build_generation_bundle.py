#!/usr/bin/env python3
"""Build a structured FC generation bundle from local markdown artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

from extract_cfg_objects import extract_cfg_objects_for_modules


HEADING_H3_RE = re.compile(r"^###(?:\s+\d+(?:\.\d+)*)?\s+`?([A-Za-z0-9_]+)`?\s*$", re.MULTILINE)
HEADING_H4_REQ_RE = re.compile(r"^####\s+(SRS-[A-Z0-9-]+)\s+(.+?)\s*$", re.MULTILINE)
BACKTICK_NAME_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")
SRS_API_RE = re.compile(r"`(Gp_[A-Za-z0-9_]+)\(([^`]*)\)`")
REQ_ID_RE = re.compile(r"SRS-[A-Z0-9-]+")
GENERIC_BACKTICK_RE = re.compile(r"`([^`]+)`")


def section_slice(text: str, start_heading: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return ""
    remainder = text[start:]
    next_h2 = remainder.find("\n## ", 1)
    if next_h2 == -1:
        return remainder
    return remainder[:next_h2]


def split_h3_blocks(section_text: str) -> list[tuple[str, str]]:
    matches = list(HEADING_H3_RE.finditer(section_text))
    blocks: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        name = match.group(1)
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section_text)
        blocks.append((name, section_text[start:end]))
    return blocks


def split_h4_requirement_blocks(section_text: str) -> list[tuple[str, str, str]]:
    matches = list(HEADING_H4_REQ_RE.finditer(section_text))
    blocks: list[tuple[str, str, str]] = []
    for idx, match in enumerate(matches):
        req_id = match.group(1)
        title = match.group(2).strip()
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section_text)
        blocks.append((req_id, title, section_text[start:end]))
    return blocks


def normalize_space(text: str) -> str:
    return " ".join(text.replace("\u3000", " ").split())


def split_evidence_cell(cell: str) -> list[str]:
    if not cell or cell == "—":
        return []
    parts = re.split(r"[；;]\s*|\s*,\s*|\s+/\s+", cell)
    values = [normalize_space(part) for part in parts if normalize_space(part)]
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "":
        return '""'
    return json.dumps(text, ensure_ascii=False)


def dump_yaml(value: object, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(dump_yaml(item, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return f"{pad}[]"
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{pad}- {next(iter(item))}: {yaml_scalar(next(iter(item.values())))}")
                remainder = dict(list(item.items())[1:])
                if remainder:
                    lines.append(dump_yaml(remainder, indent + 2))
            elif isinstance(item, list):
                lines.append(f"{pad}-")
                lines.append(dump_yaml(item, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{pad}{yaml_scalar(value)}"


def find_first_table(block_text: str) -> list[dict[str, str]]:
    lines = block_text.splitlines()
    for idx, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        table_lines = []
        for subline in lines[idx:]:
            if subline.strip().startswith("|"):
                table_lines.append(subline.strip())
            elif table_lines:
                break
        if len(table_lines) < 2:
            continue
        return parse_table_lines(table_lines)
    return []


def parse_table_lines(lines: list[str]) -> list[dict[str, str]]:
    if len(lines) < 2:
        return []
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for raw in lines[2:]:
        cells = [cell.strip() for cell in raw.strip("|").split("|")]
        if len(cells) < len(header):
            cells.extend([""] * (len(header) - len(cells)))
        row = {header[i]: cells[i] for i in range(len(header))}
        rows.append(row)
    return rows


def extract_internal_function_rows(dd_text: str) -> list[dict[str, str]]:
    section = section_slice(dd_text, "## 8. 内部函数设计")
    table = find_first_table(section)
    return table


def extract_internal_relation_map(dd_text: str, module: str) -> dict[str, list[str]]:
    section = section_slice(dd_text, "### 8.2 与外部接口的关联")
    table = find_first_table(section)
    relation_map: dict[str, list[str]] = {}
    for row in table:
        internal_name = unwrap_backticks(row.get("内部函数", ""))
        if not internal_name:
            continue
        links: list[str] = []
        for cell_name in ("关联外部接口", "关联依赖接口"):
            raw = row.get(cell_name, "")
            for ref in extract_cell_links(raw, module):
                if ref not in links:
                    links.append(ref)
        relation_map[normalize_link(internal_name, module)] = links
    return relation_map


def unwrap_backticks(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("`") and stripped.endswith("`"):
        stripped = stripped[1:-1]
    return stripped.split("(", 1)[0].strip()


def normalize_link(name: str, module: str) -> str:
    value = unwrap_backticks(name)
    if not value or value == "—":
        return ""
    if value in {"Det_ReportError"}:
        return value
    if value.startswith(f"{module}_"):
        return value
    if value.startswith("Gp_"):
        return value
    if value.startswith("Prv_"):
        return f"{module}_{value}"
    if value.startswith("Callout"):
        return f"{module}_{value}"
    if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", value):
        return f"{module}_{value}"
    return value


def extract_cell_links(cell: str, module: str) -> list[str]:
    if not cell or cell == "—":
        return []
    refs = [normalize_link(ref, module) for ref in BACKTICK_NAME_RE.findall(cell)]
    if refs:
        return dedupe(refs)
    raw_parts = re.split(r"[，,；;]\s*", cell)
    normalized = [normalize_link(part.strip(), module) for part in raw_parts if part.strip()]
    return dedupe([item for item in normalized if item])


def dedupe(values: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return seen


def extract_requirement_metadata(block: str) -> tuple[str | None, str | None]:
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("`接口需求`"):
            tokens = GENERIC_BACKTICK_RE.findall(stripped)
            status = tokens[3] if len(tokens) >= 4 else None
            source = None
            for token in tokens:
                if token.startswith("来源:"):
                    source = token.replace("来源:", "", 1).strip()
                    break
            return status, source
    return None, None


def extract_requirement_statement(block: str) -> str:
    lines = block.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith("`接口需求`"):
            for candidate in lines[idx + 1:]:
                stripped = candidate.strip()
                if not stripped or stripped.startswith("**") or stripped.startswith("---"):
                    continue
                return normalize_space(stripped)
    return ""


def category_from_cn(name: str) -> str:
    key = name.strip()
    mapping = {
        "接口需求": "interface",
        "功能需求": "functional",
        "配置需求": "config",
        "诊断需求": "diag",
        "时序需求": "timing",
        "安全需求": "safety",
        "安全等级需求": "safety",
        "编码需求": "resource",
        "编码规范需求": "resource",
        "资源需求": "resource",
        "资源消耗需求": "resource",
    }
    return mapping.get(key, "functional")


def status_from_text(text: str) -> str:
    mapping = {
        "Draft": "draft",
        "Ready": "ready",
        "Confirmed": "confirmed",
        "Pending": "pending_confirm",
        "Pending Confirm": "pending_confirm",
        "Derived": "derived",
        "Formal": "formal",
        "Reserved": "reserved",
        "Conditional": "conditional",
    }
    return mapping.get(text.strip(), "draft")


def parse_srs_requirements(srs_text: str, srs_path: str) -> list[dict[str, object]]:
    appendix = section_slice(srs_text, "## 附录A 需求清单")
    appendix_rows = find_first_table(appendix)

    details: dict[str, dict[str, object]] = {}
    interface_section = section_slice(srs_text, "### 5.2 接口需求")
    for req_id, title, block in split_h4_requirement_blocks(interface_section):
        status_text, source_text = extract_requirement_metadata(block)
        statement = extract_requirement_statement(block)
        evidence = [api for api, _params in SRS_API_RE.findall(block)]
        details[req_id] = {
            "statement": statement or title,
            "status": status_from_text(status_text or "Draft"),
            "source": source_text or srs_path,
            "evidence": evidence,
        }

    requirements: list[dict[str, object]] = []
    for row in appendix_rows:
        req_id = row.get("需求ID", "")
        detail = details.get(req_id, {})
        category = category_from_cn(row.get("类别", row.get("分类", "功能需求")))
        statement = str(detail.get("statement") or row.get("需求名称", "")).strip()
        requirement: dict[str, object] = {
            "id": req_id,
            "category": category,
            "statement": statement,
            "source": str(detail.get("source") or srs_path),
            "status": str(detail.get("status") or status_from_text(row.get("状态", "Draft"))),
        }
        evidence = dedupe([srs_path] + list(detail.get("evidence", [])))
        if evidence:
            requirement["evidence"] = evidence
        requirements.append(requirement)
    return requirements


def build_requirement_lookup(requirements: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(item["id"]): item for item in requirements if isinstance(item, dict) and item.get("id")}


def extract_interface_requirement_map(requirements: list[dict[str, object]]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for item in requirements:
        if item.get("category") != "interface":
            continue
        req_id = str(item.get("id", ""))
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list):
            continue
        for entry in evidence:
            value = str(entry)
            if value.startswith("Gp_"):
                mapping.setdefault(value, [])
                if req_id not in mapping[value]:
                    mapping[value].append(req_id)
    return mapping


def infer_trace_ids_from_evidence(evidence: list[str]) -> list[str]:
    trace_ids: list[str] = []
    for entry in evidence:
        for req_id in REQ_ID_RE.findall(entry):
            if req_id not in trace_ids:
                trace_ids.append(req_id)
    return trace_ids


def annotate_requirement_decisions(
    requirements: list[dict[str, object]],
    arch_external: list[dict[str, object]],
    config_items: list[dict[str, object]],
) -> None:
    requirement_lookup = build_requirement_lookup(requirements)
    arch_external_names = {str(item.get("name", "")) for item in arch_external}

    reserved_items: list[dict[str, object]] = []
    for item in config_items:
        if str(item.get("status", "")) == "reserved":
            reserved_items.append(item)

    for item in reserved_items:
        evidence = [str(entry) for entry in item.get("evidence", [])] if isinstance(item.get("evidence"), list) else []
        trace_ids = infer_trace_ids_from_evidence(evidence)
        config_name = str(item.get("name", ""))
        for req_id in trace_ids:
            requirement = requirement_lookup.get(req_id)
            if not requirement:
                continue
            requirement["status"] = "pending_confirm"
            if "DIRECTION" in config_name:
                requirement["decision"] = "V1 keeps direction handling inside init configuration only"
            elif "POLARITY" in config_name:
                requirement["decision"] = "V1 keeps polarity handling inside init configuration only"
            else:
                requirement["decision"] = f"V1 keeps {config_name} as reserved configuration only"
            requirement["decision_reason"] = "architecture freeze keeps this capability behind reserved configuration until project confirmation"
            requirement["impacts"] = dedupe(
                list(requirement.get("impacts", []))
                + [
                    "architecture.config_items",
                    "architecture.external_interfaces",
                    "detailed_design.config",
                ]
            )

    interface_req_map = extract_interface_requirement_map(requirements)
    for api_name, req_ids in interface_req_map.items():
        if api_name in arch_external_names:
            continue
        for req_id in req_ids:
            requirement = requirement_lookup.get(req_id)
            if not requirement:
                continue
            if requirement.get("decision"):
                continue
            requirement["status"] = "pending_confirm"
            requirement["decision"] = f"{api_name} is not frozen into V1 architecture"
            requirement["decision_reason"] = "interface remains outside the architecture freeze and needs explicit project confirmation before promotion"
            requirement["impacts"] = dedupe(
                list(requirement.get("impacts", []))
                + [
                    "architecture.external_interfaces",
                    "detailed_design.external_interfaces",
                ]
            )


def parse_interface_section(section_text: str, module: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for name, block in split_h3_blocks(section_text):
        table = find_first_table(block)
        row = table[0] if table else {}
        item: dict[str, object] = {
            "name": name,
            "prototype": unwrap_backticks(row.get("Interface Prototype", "")) or f"{name}(/* TODO */)",
            "sync": row.get("Sync/Async", ""),
            "reentrancy": row.get("Reentrancy", ""),
            "status": status_from_text(row.get("Status", "") or "Formal"),
        }
        evidence = split_evidence_cell(row.get("Evidence", ""))
        if evidence:
            item["evidence"] = evidence
        trace_ids = REQ_ID_RE.findall(row.get("Evidence", ""))
        if trace_ids:
            item["trace_ids"] = dedupe(trace_ids)
        if "关联接口" in row:
            links = extract_cell_links(row.get("关联接口", ""), module)
            if links:
                item["relationship_links"] = links
        items.append(item)
    return items


def extract_dd_external_links(block: str, module: str) -> list[str]:
    links: list[str] = []

    internal_section = section_slice(block, "####")
    # Extract names from "参与内部函数" table first.
    match = re.search(r"####\s+\d+(?:\.\d+)?\.?3\s+参与内部函数", block)
    if match:
        table = find_first_table(block[match.start():])
        for row in table:
            name = normalize_link(row.get("内部函数", ""), module)
            if name and name not in links:
                links.append(name)

    for ref in BACKTICK_NAME_RE.findall(block):
        normalized = normalize_link(ref, module)
        if normalized.startswith(f"{module}_Prv_") or normalized.startswith(f"{module}_Callout"):
            if normalized not in links:
                links.append(normalized)
    return links


def parse_dd_external_section(section_text: str, module: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for name, block in split_h3_blocks(section_text):
        table = find_first_table(block)
        row = table[0] if table else {}
        item: dict[str, object] = {
            "name": name,
            "relationship_links": extract_dd_external_links(block, module),
        }
        prototype = unwrap_backticks(row.get("Interface Prototype", ""))
        if prototype:
            item["prototype"] = prototype
        if row.get("Sync/Async"):
            item["sync"] = row.get("Sync/Async", "")
        if row.get("Reentrancy"):
            item["reentrancy"] = row.get("Reentrancy", "")
        items.append(item)
    return items


def parse_dd_dependency_section(section_text: str, module: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for name, block in split_h3_blocks(section_text):
        table = find_first_table(block)
        row = table[0] if table else {}
        item: dict[str, object] = {
            "name": name,
            "relationship_links": extract_cell_links(row.get("关联接口", ""), module),
        }
        prototype = unwrap_backticks(row.get("Interface Prototype", ""))
        if prototype:
            item["prototype"] = prototype
        evidence = split_evidence_cell(row.get("Evidence", ""))
        if evidence:
            item["evidence"] = evidence
        items.append(item)
    return items


def parse_dd_internal_section(dd_text: str, module: str) -> list[dict[str, object]]:
    rows = extract_internal_function_rows(dd_text)
    relation_map = extract_internal_relation_map(dd_text, module)
    items: list[dict[str, object]] = []
    for row in rows:
        name = normalize_link(row.get("函数名", ""), module)
        if not name:
            continue
        item: dict[str, object] = {
            "name": name,
            "relationship_links": relation_map.get(name, []),
        }
        duty = row.get("职责", "")
        if duty:
            item["evidence"] = [normalize_space(duty)]
        items.append(item)
    return items


def parse_arch_config_items(arch_text: str) -> list[dict[str, object]]:
    section = section_slice(arch_text, "## 4. 配置宏参设计")
    rows = find_first_table(section)
    items: list[dict[str, object]] = []
    for row in rows:
        name = unwrap_backticks(
            row.get("Macro Name", "")
            or row.get("Macro or Parameter", "")
            or row.get("Parameter Name", "")
            or row.get("配置项", "")
        )
        if not name:
            continue
        status = status_from_text(row.get("Status", "Formal") or "Formal")
        item: dict[str, object] = {"name": name, "status": status}
        evidence: list[str] = []
        for key in ("Declared In", "File", "Evidence"):
            evidence.extend(split_evidence_cell(row.get(key, "")))
        if evidence:
            item["evidence"] = dedupe(evidence)
        items.append(item)
    return items


def assign_arch_trace_ids(
    external_items: list[dict[str, object]],
    dependency_items: list[dict[str, object]],
    config_items: list[dict[str, object]],
    interface_req_map: dict[str, list[str]],
) -> None:
    for item in external_items:
        trace_ids = dedupe(interface_req_map.get(str(item.get("name", "")), []) + list(item.get("trace_ids", [])))
        if trace_ids:
            item["trace_ids"] = trace_ids

    for item in dependency_items:
        evidence = [str(entry) for entry in item.get("evidence", [])] if isinstance(item.get("evidence"), list) else []
        trace_ids = dedupe(list(item.get("trace_ids", [])) + infer_trace_ids_from_evidence(evidence))
        if trace_ids:
            item["trace_ids"] = trace_ids

    for item in config_items:
        evidence = [str(entry) for entry in item.get("evidence", [])] if isinstance(item.get("evidence"), list) else []
        trace_ids = infer_trace_ids_from_evidence(evidence)
        if trace_ids:
            item["trace_ids"] = trace_ids


def trace_map(items: list[dict[str, object]]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for item in items:
        name = str(item.get("name", ""))
        if not name:
            continue
        trace_ids = [str(entry) for entry in item.get("trace_ids", [])] if isinstance(item.get("trace_ids"), list) else []
        mapping[name] = dedupe(trace_ids)
    return mapping


def assign_dd_trace_ids(
    dd_external: list[dict[str, object]],
    dd_internal: list[dict[str, object]],
    dd_dependency: list[dict[str, object]],
    arch_external: list[dict[str, object]],
    arch_dependency: list[dict[str, object]],
) -> None:
    arch_external_map = trace_map(arch_external)
    arch_dependency_map = trace_map(arch_dependency)

    for item in dd_external:
        item["trace_ids"] = dedupe(arch_external_map.get(str(item.get("name", "")), []))

    for item in dd_dependency:
        name = str(item.get("name", ""))
        trace_ids = dedupe(arch_dependency_map.get(name, []))
        if trace_ids:
            item["trace_ids"] = trace_ids


def infer_grounding_patterns(
    grounding_modules: list[str],
    arch_external: list[dict[str, object]],
    arch_dependency: list[dict[str, object]],
    config_items: list[dict[str, object]],
    dd_internal: list[dict[str, object]],
    conf_evidence: list[str],
) -> tuple[list[str], list[str]]:
    patterns: list[str] = []
    rejections: list[str] = []

    external_names = {str(item.get("name", "")) for item in arch_external}
    dependency_names = {str(item.get("name", "")) for item in arch_dependency}
    internal_names = {str(item.get("name", "")) for item in dd_internal}
    config_names = {str(item.get("name", "")) for item in config_items}

    if any(name.endswith("CalloutGetCoreId") for name in dependency_names):
        patterns.append("per_core_runtime_container")

    if dependency_names and any(module in grounding_modules for module in ("IoMcu", "Gp_TLE92104", "Gp_DRV8889")):
        patterns.append("dependency_interface_shape")

    if "Gp_DRV8889" in grounding_modules and "Gp_NCA95yy_MainFunction" in external_names:
        patterns.append("chip_mainfunction_pattern")

    if conf_evidence and config_names:
        patterns.append("conf_cfg_mapping")

    reserved_runtime_switch = {
        "GP_NCA95YY_CFG_RUNTIME_DIRECTION_CHANGE",
        "GP_NCA95YY_CFG_RUNTIME_POLARITY_CHANGE",
    }
    if reserved_runtime_switch & config_names:
        patterns.append("runtime_capability_reserved_in_config")

    conditional_api_tokens = ("SetGpDirection", "SetGpPolarity")
    if reserved_runtime_switch & config_names and not any(
        any(token in name for token in conditional_api_tokens) for name in external_names
    ):
        rejections.append("conditional_external_interfaces")

    if "Gp_TPT1145" not in grounding_modules and any(name.endswith("CalloutGetCoreId") for name in dependency_names):
        rejections.append("single_array_runtime")

    if "Gp_NCA95yy_Prv_HandleInt" in internal_names and "Gp_NCA95yy_MainFunction" in external_names:
        patterns.append("interrupt_polling_mainfunction")

    return dedupe(patterns), dedupe(rejections)

    dd_external_map = trace_map(dd_external)
    dd_dependency_map = trace_map(dd_dependency)

    for item in dd_internal:
        related = item.get("relationship_links", [])
        trace_ids: list[str] = []
        if isinstance(related, list):
            for ref in related:
                trace_ids.extend(dd_external_map.get(str(ref), []))
                trace_ids.extend(dd_dependency_map.get(str(ref), []))
        trace_ids = dedupe(trace_ids)
        if trace_ids:
            item["trace_ids"] = trace_ids


def parse_dd_assumptions(dd_text: str) -> list[str]:
    section = section_slice(dd_text, "## 3. 假设与待确认项")
    rows = find_first_table(section)
    values: list[str] = []
    for row in rows:
        parts = [normalize_space(value) for value in row.values() if normalize_space(value) and value != "—"]
        if parts:
            values.append(" | ".join(parts))
    return values


def parse_dd_risks(dd_text: str) -> list[str]:
    section = section_slice(dd_text, "## 19. 风险与待确认项")
    rows = find_first_table(section)
    values: list[str] = []
    for row in rows:
        risk_name = normalize_space(row.get("问题项", "") or row.get("Risk", "") or row.get("索引", ""))
        issue = normalize_space(row.get("问题/风险", "") or row.get("Description", ""))
        if risk_name and issue:
            values.append(f"{risk_name}: {issue}")
        elif issue:
            values.append(issue)
    return values


def collect_conf_evidence(grounding_modules: list[str]) -> list[str]:
    mapping = {
        "Gp_TPT1145": ["Gp_TPT1145_CfgData.h", "Gp_TPT1145_Callout.h"],
        "Gp_TLE92104": ["Gp_TLE92104_Cfg.h", "Gp_TLE92104_Callout.h"],
        "Gp_DRV8889": ["Gp_DRV8889_Cfg.h", "Gp_DRV8889_Callout.h"],
    }
    evidence: list[str] = []
    for module in grounding_modules:
        evidence.extend(mapping.get(module, []))
    return dedupe(evidence)


def flatten_cfg_objects(cfg_sources: list[dict[str, object]]) -> list[dict[str, object]]:
    flattened: list[dict[str, object]] = []
    for source in cfg_sources:
        module = str(source.get("module", ""))
        cfg_path = str(source.get("cfg_path", ""))
        includes = source.get("includes", [])
        if not isinstance(includes, list):
            includes = []
        for item in source.get("cfg_objects", []) if isinstance(source.get("cfg_objects"), list) else []:
            if not isinstance(item, dict):
                continue
            entry = dict(item)
            entry["module"] = module
            entry["cfg_path"] = cfg_path
            entry["includes"] = includes
            flattened.append(entry)
    return flattened


def build_bundle(
    module: str,
    srs_path: Path,
    arch_path: Path,
    dd_path: Path,
    grounding_modules: list[str],
    source_root: Path | None = None,
) -> dict[str, object]:
    srs_text = srs_path.read_text(encoding="utf-8")
    arch_text = arch_path.read_text(encoding="utf-8")
    dd_text = dd_path.read_text(encoding="utf-8")

    requirements = parse_srs_requirements(srs_text, str(srs_path))
    interface_req_map = extract_interface_requirement_map(requirements)
    arch_external = parse_interface_section(section_slice(arch_text, "## 3. 外部接口设计"), module)
    arch_dependency = parse_interface_section(section_slice(arch_text, "## 8. 依赖接口设计"), module)
    config_items = parse_arch_config_items(arch_text)
    assign_arch_trace_ids(arch_external, arch_dependency, config_items, interface_req_map)
    annotate_requirement_decisions(requirements, arch_external, config_items)

    dd_external = parse_dd_external_section(section_slice(dd_text, "## 7. 外部接口设计"), module)
    dd_internal = parse_dd_internal_section(dd_text, module)
    dd_dependency = parse_dd_dependency_section(section_slice(dd_text, "## 9. 依赖接口与Callout设计"), module)
    assign_dd_trace_ids(dd_external, dd_internal, dd_dependency, arch_external, arch_dependency)

    conf_evidence = collect_conf_evidence(grounding_modules)
    cfg_sources = extract_cfg_objects_for_modules(source_root, grounding_modules) if source_root else []
    cfg_objects = flatten_cfg_objects(cfg_sources)
    grounding_patterns, grounding_rejections = infer_grounding_patterns(
        grounding_modules,
        arch_external,
        arch_dependency,
        config_items,
        dd_internal,
        conf_evidence,
    )

    bundle: dict[str, object] = {
        "module": module,
        "grounding_modules": grounding_modules,
        "grounding_patterns": grounding_patterns,
        "grounding_rejections": grounding_rejections,
        "requirements": requirements,
        "architecture": {
            "module": module,
            "grounding_modules": grounding_modules,
            "external_interfaces": arch_external,
            "dependency_interfaces": arch_dependency,
            "config_items": config_items,
        },
        "detailed_design": {
            "module": module,
            "external_interfaces": dd_external,
            "internal_interfaces": dd_internal,
            "dependency_interfaces": dd_dependency,
        },
        "conf_evidence": conf_evidence,
        "cfg_objects": cfg_objects,
        "assumptions": parse_dd_assumptions(dd_text),
        "risks": parse_dd_risks(dd_text),
    }
    return bundle


def infer_module_name(path: Path) -> str:
    match = re.search(r"(Gp_[A-Za-z0-9_]+)", path.stem)
    if match:
        return match.group(1)
    raise ValueError("Unable to infer module name; pass --module explicitly.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a structured FC generation bundle from markdown artifacts.")
    parser.add_argument("--srs", required=True, help="Path to SRS markdown")
    parser.add_argument("--arch", required=True, help="Path to architecture markdown")
    parser.add_argument("--dd", required=True, help="Path to detailed design markdown")
    parser.add_argument("--module", help="Target module short name, for example Gp_NCA95yy")
    parser.add_argument(
        "--grounding-module",
        action="append",
        default=[],
        dest="grounding_modules",
        help="Grounding module to include in the generated bundle; may be supplied multiple times.",
    )
    parser.add_argument("--source-root", help="Optional AURIX2G source root for real Cfg.c object extraction")
    parser.add_argument("--output", required=True, help="Path to write the YAML bundle")
    args = parser.parse_args()

    srs_path = Path(args.srs)
    arch_path = Path(args.arch)
    dd_path = Path(args.dd)
    module = args.module or infer_module_name(dd_path)
    grounding_modules = dedupe(args.grounding_modules)
    source_root = Path(args.source_root) if args.source_root else None

    bundle = build_bundle(module, srs_path, arch_path, dd_path, grounding_modules, source_root)
    output_path = Path(args.output)
    output_path.write_text(dump_yaml(bundle) + "\n", encoding="utf-8")
    print(f"OK: wrote bundle to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
