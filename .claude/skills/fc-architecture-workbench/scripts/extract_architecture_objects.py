from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{2,4})\s+(.+)$", re.MULTILINE)
META_RE = re.compile(r"^(架构版本|架构状态|输出模式|Created):\s*\**([^\n*]+)\**$", re.MULTILINE)
BULLET_META_RE = re.compile(r"^- \*\*(架构版本|架构状态|输出模式|生成时间|FC名称)\*\*:\s*(.+)$", re.MULTILINE)
CHANGE_RE = re.compile(r"^- \*\*变更点总结(?:【简洁版】)?\*\*:\s*(.+)$", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|(.+)\|$", re.MULTILINE)


def _clean(text: str) -> str:
    cleaned = text.replace("`", "").replace("**", "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ,;")


def _split_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+.+$", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _extract_table(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in TABLE_ROW_RE.findall(section):
        cells = [cell.strip() for cell in raw.split("|")]
        if len(cells) >= 2:
            rows.append(cells)
    return rows


def _data_rows(section: str) -> list[list[str]]:
    rows = _extract_table(section)
    result: list[list[str]] = []
    for row in rows:
        line = "".join(row).replace("-", "").strip()
        if not line:
            continue
        if row[0] in {"Requirement ID", "Interface Prototype", "Macro or Parameter", "Runtime State Area", "Memory Section", "File", "索引"}:
            continue
        result.append(row)
    return result


def _extract_interfaces(section: str, prefix: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    blocks = re.split(rf"^###\s+{re.escape(prefix)}\.\d+\s+`", section, flags=re.MULTILINE)
    matches = list(re.finditer(rf"^###\s+{re.escape(prefix)}\.(\d+)\s+`([^`]+)`", section, re.MULTILINE))
    if not matches:
        return items
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section)
        block = section[start:end]
        rows = _data_rows(block)
        if not rows:
            continue
        row = rows[0]
        if prefix == "3":
            if len(row) < 6:
                continue
            items.append(
                {
                    "name": _clean(match.group(2)),
                    "prototype": _clean(row[0]),
                    "description": _clean(row[1]),
                    "sync_mode": _clean(row[2]),
                    "reentrancy": _clean(row[3]),
                    "return_value": _clean(row[4]),
                    "constraints": [_clean(part) for part in row[5].split(";") if _clean(part)],
                    "evidence": [],
                    "status": "Formal",
                }
            )
        else:
            if len(row) < 9:
                continue
            items.append(
                {
                    "name": _clean(match.group(2)),
                    "prototype": _clean(row[0]),
                    "description": _clean(row[1]),
                    "sync_mode": _clean(row[2]),
                    "reentrancy": _clean(row[3]),
                    "return_value": _clean(row[4]),
                    "constraints": [_clean(part) for part in row[5].split(";") if _clean(part)],
                    "implemented_by": _clean(row[6]),
                    "evidence": [_clean(part) for part in row[7].split(";") if _clean(part)],
                    "status": _clean(row[8]),
                }
            )
    return items


def _extract_coverage(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _data_rows(section):
        if len(row) < 5:
            continue
        items.append(
            {
                "requirement_id": _clean(row[0]),
                "summary": _clean(row[1]),
                "coverage_object": _clean(row[2]),
                "coverage_status": _clean(row[3]),
                "notes": _clean(row[4]),
            }
        )
    return items


def _extract_config_macros(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _data_rows(section):
        if len(row) < 7:
            continue
        macro_name = _clean(row[0]).upper()
        items.append(
            {
                "name": macro_name,
                "purpose": _clean(row[1]),
                "macro_type": _clean(row[2]) if _clean(row[2]) != "Macro" else "Feature Enable",
                "default_value": _clean(row[3]),
                "usage_location": _clean(row[5]),
                "evidence": [_clean(part) for part in row[4].split(";") if _clean(part)],
                "status": _clean(row[6]),
            }
        )
    return items


def _normalize_macro_types(items: list[dict[str, Any]]) -> None:
    for item in items:
        purpose = item.get("purpose", "").lower()
        name = item.get("name", "").upper()
        if "DEV_ERROR_DETECT" in name or "det" in purpose:
            item["macro_type"] = "Development Error Detect"
        elif "VERSION" in name:
            item["macro_type"] = "Vendor Version Release"
        elif "MODE" in name or "selection" in purpose:
            item["macro_type"] = "Behavior Selection"
        elif "ENABLE" in name:
            item["macro_type"] = "Feature Enable"
        else:
            item["macro_type"] = "Feature Enable"


def _extract_runtime_states(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _data_rows(section):
        if len(row) < 6:
            continue
        items.append(
            {
                "name": _clean(row[0]),
                "owner": _clean(row[1]),
                "read_write_side": _clean(row[2]),
                "lifecycle": _clean(row[3]),
                "memory_section": _clean(row[4]),
                "concurrency_strategy": _clean(row[5]),
                "status": "Formal",
            }
        )
    return items


def _extract_memmap(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _data_rows(section):
        if len(row) < 6:
            continue
        used_files = [_clean(part) for part in row[4].split(",") if _clean(part)]
        items.append(
            {
                "name": _clean(row[0]),
                "target_content": _clean(row[1]),
                "start_macro": _clean(row[2]),
                "stop_macro": _clean(row[3]),
                "used_files": used_files,
                "notes": _clean(row[5]),
                "status": "Formal" if _clean(row[0]) != "CALIB" else "Conditional",
            }
        )
    return items


def _extract_file_items(section: str) -> list[dict[str, Any]]:
    file_section = _split_subsection(section, "### 9.1 文件列表", "### 9.2 文件关系")
    items: list[dict[str, Any]] = []
    for row in _data_rows(file_section):
        if len(row) < 4:
            continue
        items.append(
            {
                "name": _clean(row[0]),
                "required_level": _clean(row[1]),
                "responsibility": _clean(row[2]),
                "key_content": _clean(row[3]),
                "status": "Formal",
            }
        )
    return items


def _split_subsection(section: str, start_heading: str, end_heading: str | None = None) -> str:
    start = section.find(start_heading)
    if start < 0:
        return section
    start += len(start_heading)
    if end_heading:
        end = section.find(end_heading, start)
        if end >= 0:
            return section[start:end].strip()
    return section[start:].strip()


def _extract_risks(section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _data_rows(section):
        if len(row) < 7:
            continue
        items.append(
            {
                "index": _clean(row[0]),
                "title": _clean(row[1]),
                "risk": _clean(row[2]),
                "impact": _clean(row[3]),
                "recommended_action": _clean(row[4]),
                "remark": _clean(row[5]),
                "status": _clean(row[6]),
            }
        )
    return items


def extract_architecture_objects(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    payload: dict[str, Any] = {
        "module": "",
        "architecture_version": "",
        "architecture_status": "",
        "output_mode": "",
        "layer": "",
        "change_summary": [],
        "requirement_coverage": [],
        "external_apis": [],
        "dependency_apis": [],
        "config_macros": [],
        "calibration_items": [],
        "runtime_states": [],
        "memmap_sections": [],
        "file_items": [],
        "risk_items": [],
    }

    project_match = re.search(r"项目编号/Project number:\s*(.+)", text)
    if project_match:
        payload["module"] = _clean(project_match.group(1))

    meta = {key: value for key, value in META_RE.findall(text)}
    payload["architecture_version"] = _clean(meta.get("架构版本", ""))
    payload["architecture_status"] = _clean(meta.get("架构状态", ""))
    payload["output_mode"] = _clean(meta.get("输出模式", ""))
    payload["generated_time"] = _clean(meta.get("Created", ""))

    intro = _split_section(text, "1 FC总结介绍")
    for key, value in BULLET_META_RE.findall(intro):
        if key == "当前软件架构所处层级":
            payload["layer"] = _clean(value)
    layer_match = re.search(r"- \*\*当前软件架构所处层级\*\*:\s*`?([^`\n]+)`?", intro)
    if layer_match:
        payload["layer"] = _clean(layer_match.group(1))
    change_match = CHANGE_RE.search(intro)
    if change_match:
        payload["change_summary"] = [_clean(change_match.group(1))]

    payload["requirement_coverage"] = _extract_coverage(_split_section(text, "2 需求覆盖表"))
    payload["external_apis"] = _extract_interfaces(_split_section(text, "3 外部接口设计"), "3")
    payload["dependency_apis"] = _extract_interfaces(_split_section(text, "8 依赖接口设计"), "8")
    payload["config_macros"] = _extract_config_macros(_split_section(text, "4 配置宏参设计"))
    _normalize_macro_types(payload["config_macros"])
    payload["runtime_states"] = _extract_runtime_states(_split_section(text, "5 全局变量与运行态策略"))
    payload["memmap_sections"] = _extract_memmap(_split_section(text, "6 内存分配宏定义"))
    payload["file_items"] = _extract_file_items(_split_section(text, "9 文件列表与文件关系"))
    payload["risk_items"] = _extract_risks(_split_section(text, "10 架构风险与待确认"))

    evidence_map: dict[str, list[str]] = {}
    for item in payload["requirement_coverage"]:
        coverage = item.get("coverage_object", "")
        for api in payload["external_apis"]:
            if api["name"] in coverage:
                evidence_map.setdefault(api["name"], []).append(item["requirement_id"])
        for api in payload["dependency_apis"]:
            if api["name"] in coverage:
                evidence_map.setdefault(api["name"], []).append(item["requirement_id"])
        for macro in payload["config_macros"]:
            if macro["name"] in coverage:
                macro["evidence"].append(item["requirement_id"])

    for api in payload["external_apis"]:
        api["evidence"] = sorted(set(api.get("evidence", []) + evidence_map.get(api["name"], [])))
    for api in payload["dependency_apis"]:
        api["evidence"] = sorted(set(api.get("evidence", []) + evidence_map.get(api["name"], [])))
    for macro in payload["config_macros"]:
        macro["evidence"] = sorted(set(macro.get("evidence", [])))

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract FC architecture markdown into semantic objects JSON.")
    parser.add_argument("input", type=Path, help="Architecture markdown file")
    parser.add_argument("--output", type=Path, help="Output JSON path")
    args = parser.parse_args()

    payload = extract_architecture_objects(args.input)
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
