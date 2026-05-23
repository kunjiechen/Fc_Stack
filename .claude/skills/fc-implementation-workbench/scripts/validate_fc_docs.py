#!/usr/bin/env python3
"""Validate SRS, architecture, and detailed-design markdown consistency."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^###(?:\s+\d+(?:\.\d+)*)?\s+`?([A-Za-z0-9_]+)`?\s*$", re.MULTILINE)
TABLE_HEADER_RE = re.compile(r"^\|(.+)\|\s*$", re.MULTILINE)
IDENT_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")
SRS_API_RE = re.compile(r"`(Gp_[A-Za-z0-9_]+)\(([^`]*)\)`")


def section_slice(text: str, start_heading: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return ""
    remainder = text[start:]
    next_h2 = remainder.find("\n## ", 1)
    if next_h2 == -1:
        return remainder
    return remainder[:next_h2]


def extract_interface_names(section_text: str) -> list[str]:
    return HEADING_RE.findall(section_text)


def extract_backticked_names(section_text: str) -> list[str]:
    names: list[str] = []
    for name in IDENT_RE.findall(section_text):
        if name not in names:
            names.append(name)
    return names


def split_h3_blocks(section_text: str) -> list[tuple[str, str]]:
    matches = list(HEADING_RE.finditer(section_text))
    blocks: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        name = match.group(1)
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section_text)
        blocks.append((name, section_text[start:end]))
    return blocks


def first_table_header(block_text: str) -> str:
    for match in TABLE_HEADER_RE.finditer(block_text):
        line = match.group(0)
        if "---" not in line:
            return line
    return ""


def validate_relationship_tables(text: str, defined_names: set[str]) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    current_header: list[str] | None = None
    relation_index: int | None = None

    common_prefix = os.path.commonprefix(sorted(defined_names)) if defined_names else ""
    alias_prefix = common_prefix[: common_prefix.rfind("_") + 1] if "_" in common_prefix else ""
    alias_names = {name[len(alias_prefix):] for name in defined_names if alias_prefix and name.startswith(alias_prefix)}
    for name in defined_names:
        if name.startswith("Gp_"):
            parts = name.split("_", 2)
            if len(parts) == 3:
                alias_names.add(parts[2])

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            current_header = None
            relation_index = None
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if set(cells) == {"---"} or all(cell.startswith("---") for cell in cells):
            continue

        if "关联接口" in cells:
            current_header = cells
            relation_index = cells.index("关联接口")
            continue

        if current_header is None or relation_index is None:
            continue

        if relation_index >= len(cells):
            continue

        relation_cell = cells[relation_index]
        for ref in IDENT_RE.findall(relation_cell):
            if ref in defined_names:
                continue
            if ref in alias_names:
                continue
            if ref in {"Det_ReportError"}:
                continue
            errors.append(f"Undefined 关联接口 reference: {ref}")

    return errors


def extract_srs_api_names(srs_text: str) -> list[str]:
    section = section_slice(srs_text, "### 5.2 接口需求")
    names: list[str] = []
    for name, _params in SRS_API_RE.findall(section):
        if name not in names:
            names.append(name)
    return names


def validate(arch_path: Path, dd_path: Path, srs_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    arch_text = arch_path.read_text(encoding="utf-8")
    dd_text = dd_path.read_text(encoding="utf-8")
    srs_text = srs_path.read_text(encoding="utf-8") if srs_path else None

    arch_external = section_slice(arch_text, "## 3. 外部接口设计")
    arch_dependency = section_slice(arch_text, "## 8. 依赖接口设计")
    dd_external = section_slice(dd_text, "## 7. 外部接口设计")
    dd_dependency = section_slice(dd_text, "## 9. 依赖接口与Callout设计")

    arch_external_names = extract_interface_names(arch_external)
    arch_dependency_names = extract_interface_names(arch_dependency)
    dd_external_names = extract_interface_names(dd_external)
    dd_internal = section_slice(dd_text, "## 8. 内部函数设计")
    dd_internal_names = extract_backticked_names(dd_internal)
    dd_dependency_names = extract_interface_names(dd_dependency)
    defined_names = set(dd_external_names) | set(dd_internal_names) | set(dd_dependency_names)

    missing_external = sorted(set(arch_external_names) - set(dd_external_names))
    extra_external = sorted(set(dd_external_names) - set(arch_external_names))
    missing_dependency = sorted(set(arch_dependency_names) - set(dd_dependency_names))
    extra_dependency = sorted(set(dd_dependency_names) - set(arch_dependency_names))

    if missing_external:
        errors.append(f"Missing external interfaces in DD: {', '.join(missing_external)}")
    if extra_external:
        errors.append(f"Unexpected external interfaces in DD: {', '.join(extra_external)}")
    if missing_dependency:
        errors.append(f"Missing dependency interfaces in DD: {', '.join(missing_dependency)}")
    if extra_dependency:
        errors.append(f"Unexpected dependency interfaces in DD: {', '.join(extra_dependency)}")

    if srs_text is not None:
        srs_api_names = extract_srs_api_names(srs_text)
        missing_arch_vs_srs = sorted(set(srs_api_names) - set(arch_external_names))
        extra_arch_vs_srs = sorted(set(arch_external_names) - set(srs_api_names))
        missing_dd_vs_srs = sorted(set(srs_api_names) - set(dd_external_names))
        extra_dd_vs_srs = sorted(set(dd_external_names) - set(srs_api_names))
        if missing_arch_vs_srs:
            errors.append(f"Missing SRS interface APIs in Architecture: {', '.join(missing_arch_vs_srs)}")
        if extra_arch_vs_srs:
            errors.append(f"Architecture external APIs not declared in SRS interface section: {', '.join(extra_arch_vs_srs)}")
        if missing_dd_vs_srs:
            errors.append(f"Missing SRS interface APIs in DD: {', '.join(missing_dd_vs_srs)}")
        if extra_dd_vs_srs:
            errors.append(f"DD external APIs not declared in SRS interface section: {', '.join(extra_dd_vs_srs)}")

    conditional_tokens = ("conditional", "条件编译", "条件接口")
    for label, section_text in (
        ("Architecture external", arch_external),
        ("Architecture dependency", arch_dependency),
        ("DD external", dd_external),
        ("DD dependency", dd_dependency),
    ):
        lowered = section_text.lower()
        if any(token in section_text for token in ("条件编译", "条件接口")) or "conditional" in lowered:
            errors.append(f"{label} interface section contains explicit conditional-interface wording")

    for name, block in split_h3_blocks(dd_external):
        header = first_table_header(block)
        if not header:
            errors.append(f"External interface block has no table header: {name}")
        elif "关联接口" not in header:
            errors.append(f"External interface block missing 关联接口 field: {name}")

    for name, block in split_h3_blocks(dd_dependency):
        header = first_table_header(block)
        if not header:
            errors.append(f"Dependency interface block has no table header: {name}")
        elif "关联接口" not in header:
            errors.append(f"Dependency interface block missing 关联接口 field: {name}")

    errors.extend(validate_relationship_tables(dd_text, defined_names))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FC SRS, architecture, and detailed-design markdown artifacts.")
    parser.add_argument("--arch", required=True, help="Path to architecture markdown")
    parser.add_argument("--dd", required=True, help="Path to detailed design markdown")
    parser.add_argument("--srs", help="Path to SRS markdown")
    args = parser.parse_args()

    errors = validate(Path(args.arch), Path(args.dd), Path(args.srs) if args.srs else None)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
