from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIREMENT_HEADING = re.compile(r"^####\s+SRS-[A-Z0-9_-]+", re.MULTILINE)
FIELD_TABLE_HEADER = re.compile(r"^\|\s*字段\s*\|\s*内容\s*\|", re.MULTILINE)
OVERVIEW_SECTION = re.compile(r"^##\s+4\s+概述\s*$", re.MULTILINE)
FUNCTION_SECTION = re.compile(r"^##\s+5\s+功能需求\s*$", re.MULTILINE)


def _requirement_blocks(text: str) -> list[str]:
    matches = list(REQUIREMENT_HEADING.finditer(text))
    if not matches:
        return []

    blocks: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[start:end])
    return blocks


def check_srs_markdown(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []

    for block in _requirement_blocks(text):
        heading = block.splitlines()[0].strip()
        if FIELD_TABLE_HEADER.search(block):
            issues.append(f"{path}: {heading} contains deprecated field table layout")
        if "- **" not in block:
            issues.append(f"{path}: {heading} is missing bullet-style constraint fields")

    overview_len = _section_length(text, OVERVIEW_SECTION, FUNCTION_SECTION)
    function_len = _section_length(text, FUNCTION_SECTION, re.compile(r"^##\s+6\s+非功能需求\s*$", re.MULTILINE))
    if overview_len and function_len and overview_len > function_len * 0.5:
        issues.append(
            f"{path}: overview section is too heavy ({overview_len} chars vs {function_len} chars in functional requirements)"
        )
    overview_bullets = _section_bullet_count(text, OVERVIEW_SECTION, FUNCTION_SECTION)
    if overview_bullets > 16:
        issues.append(f"{path}: overview section has too many bullets ({overview_bullets}), risks head-heavy output")

    return issues


def _section_length(text: str, start_pattern: re.Pattern[str], end_pattern: re.Pattern[str]) -> int:
    bounds = _section_bounds(text, start_pattern, end_pattern)
    if not bounds:
        return 0
    start, end = bounds
    return len(text[start:end].strip())


def _section_bullet_count(text: str, start_pattern: re.Pattern[str], end_pattern: re.Pattern[str]) -> int:
    bounds = _section_bounds(text, start_pattern, end_pattern)
    if not bounds:
        return 0
    start, end = bounds
    return len(re.findall(r"^\s*(?:- |\d+\.\s)", text[start:end], re.MULTILINE))


def _section_bounds(
    text: str,
    start_pattern: re.Pattern[str],
    end_pattern: re.Pattern[str],
) -> tuple[int, int] | None:
    start_match = start_pattern.search(text)
    if not start_match:
        return None
    end_match = end_pattern.search(text, start_match.end())
    end = end_match.start() if end_match else len(text)
    return (start_match.end(), end)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check generated SRS markdown format.")
    parser.add_argument("paths", nargs="+", help="Markdown file(s) to validate")
    args = parser.parse_args()

    issues: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*.md")):
                issues.extend(check_srs_markdown(child))
        else:
            issues.extend(check_srs_markdown(path))

    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("SRS format check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
