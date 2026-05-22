from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIREMENT_HEADING = re.compile(r"^####\s+SRS-[A-Z0-9_-]+", re.MULTILINE)
FIELD_TABLE_HEADER = re.compile(r"^\|\s*字段\s*\|\s*内容\s*\|", re.MULTILINE)


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

    return issues


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
