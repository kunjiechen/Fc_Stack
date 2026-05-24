#!/usr/bin/env python3
"""Extract configuration objects from FC Cfg.c files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


DECL_RE = re.compile(
    r"(?P<prefix>(?:[A-Z0-9_]+\s+|static\s+|const\s+|GP_[A-Z0-9_]+_\s+)*)"
    r"(?P<type>Gp_[A-Za-z0-9_]+)\s+"
    r"(?P<symbol>Gp_[A-Za-z0-9_]+)"
    r"(?P<dims>(?:\[[^\]]+\])*)\s*=\s*\\?\s*\{",
    re.MULTILINE,
)
FIELD_RE = re.compile(r"\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=")
REF_RE = re.compile(r"&(?P<name>Gp_[A-Za-z0-9_]+)")
DIM_RE = re.compile(r"\[([^\]]+)\]")
INCLUDE_RE = re.compile(r'#include\s+"([^"]+)"')


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def infer_role(symbol: str, fields: list[str], references: list[str], dimensions: list[str]) -> str:
    if "cfgCont" in symbol:
        return "top_level_cfg_container"
    if "cfgChipCore" in symbol:
        return "per_core_chip_config_array"
    if "cfgChip" in symbol:
        return "per_chip_chip_config_array"
    if "PnReg" in symbol:
        return "register_frame_config"
    if "SpiCfg" in symbol:
        return "bus_mapping_config"
    if any("Spi" in field for field in fields):
        return "bus_mapping_config"
    if any(field.startswith(("DO_", "DI_", "EnChn", "PwmChn")) for field in fields):
        return "io_mapping_config"
    if any("Reg" in field for field in fields) or references:
        return "register_or_composite_config"
    if dimensions:
        return "array_config_container"
    return "cfg_object"


def infer_container_level(symbol: str, dimensions: list[str]) -> str:
    if "cfgCont" in symbol:
        return "top_level"
    if "Core" in symbol:
        return "per_core"
    if dimensions:
        return "per_chip"
    return "local"


def infer_semantic_tags(fields: list[str], references: list[str], dimensions: list[str], symbol: str) -> list[str]:
    tags: list[str] = []
    if any("Spi" in field for field in fields):
        tags.append("bus_mapping")
    if any(field.startswith(("DO_", "DI_", "EnChn", "PwmChn", "STEP_ID")) for field in fields):
        tags.append("io_mapping")
    if any("Reg" in field for field in fields) or "PnReg" in symbol:
        tags.append("register_init")
    if any("Fault" in field or "Thd" in field for field in fields):
        tags.append("fault_threshold")
    if references:
        tags.append("composite_container")
    if any("CORE" in dim.upper() for dim in dimensions):
        tags.append("per_core_layout")
    if any("CHIP" in dim.upper() or "MAX_CHIP" in dim.upper() for dim in dimensions):
        tags.append("per_chip_layout")
    return dedupe(tags)


def summarize_object(role: str, fields: list[str], references: list[str], dimensions: list[str]) -> str:
    if role == "top_level_cfg_container":
        if references:
            return f"顶层配置容器，聚合 {', '.join(references[:4])} 等子配置对象。"
        return "顶层配置容器，承载模块正式导出的配置入口。"
    if role == "per_core_chip_config_array":
        return "按 core 组织芯片配置数组，用于多核实例或核内资源分区。"
    if role == "per_chip_chip_config_array":
        return "按芯片实例组织的配置数组。"
    if role == "bus_mapping_config":
        return f"总线/通道映射配置，重点字段包括 {', '.join(fields[:4])}。"
    if role == "register_frame_config":
        return f"寄存器或帧初始化配置，重点字段包括 {', '.join(fields[:4])}。"
    if role == "io_mapping_config":
        return f"控制/故障引脚映射配置，重点字段包括 {', '.join(fields[:4])}。"
    if dimensions:
        return f"数组型配置对象，维度为 {', '.join(dimensions)}。"
    if fields:
        return f"配置对象字段包括 {', '.join(fields[:4])}。"
    return "配置对象。"


def parse_cfg_file(cfg_path: Path, module: str) -> dict[str, Any]:
    text = cfg_path.read_text(encoding="utf-8")
    includes = dedupe(INCLUDE_RE.findall(text))
    objects: list[dict[str, Any]] = []
    for match in DECL_RE.finditer(text):
        symbol = match.group("symbol")
        if not symbol.startswith(f"{module}_"):
            continue
        open_brace = text.find("{", match.end() - 1)
        if open_brace == -1:
            continue
        close_brace = find_matching_brace(text, open_brace)
        if close_brace == -1:
            continue
        block = text[open_brace : close_brace + 1]
        fields = dedupe(FIELD_RE.findall(block))
        references = dedupe(REF_RE.findall(block))
        dimensions = DIM_RE.findall(match.group("dims") or "")
        obj: dict[str, Any] = {
            "module": module,
            "cfg_path": str(cfg_path),
            "symbol": symbol,
            "type": normalize_space(match.group("type")),
            "dimensions": dimensions,
            "container_level": infer_container_level(symbol, dimensions),
            "role": infer_role(symbol, fields, references, dimensions),
            "fields": fields,
            "references": references,
        }
        obj["semantic_tags"] = infer_semantic_tags(fields, references, dimensions, symbol)
        obj["summary"] = summarize_object(obj["role"], fields, references, dimensions)
        objects.append(obj)
    return {
        "module": module,
        "cfg_path": str(cfg_path),
        "includes": includes,
        "cfg_objects": objects,
    }


def find_cfg_path(source_root: Path, module: str) -> Path | None:
    conf_root = source_root / "Conf"
    direct = list(conf_root.rglob(f"Conf_{module}/{module}_Cfg.c"))
    if direct:
        return direct[0]
    fallback = list(conf_root.rglob(f"{module}_Cfg.c"))
    if fallback:
        return fallback[0]
    return None


def extract_cfg_objects_for_modules(source_root: Path, modules: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for module in modules:
        cfg_path = find_cfg_path(source_root, module)
        if cfg_path is None:
            continue
        results.append(parse_cfg_file(cfg_path, module))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract FC Cfg.c objects into YAML or JSON.")
    parser.add_argument("--source-root", required=True, help="AURIX2G source root")
    parser.add_argument("--module", action="append", required=True, help="Module name, may be passed multiple times")
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml", help="Output format")
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()

    source_root = Path(args.source_root)
    modules = args.module
    data = {"modules": extract_cfg_objects_for_modules(source_root, modules)}

    if args.format == "json":
        rendered = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        rendered = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)

    if args.output:
        Path(args.output).write_text(rendered + ("\n" if not rendered.endswith("\n") else ""), encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
