#!/usr/bin/env python3
"""Check SRS markdown consistency against the requirement bundle.

Verifies that the SRS markdown is a faithful rendering of the requirement bundle
and has not drifted independently.  Checks:

- Every bundle requirement appears in the SRS markdown
- Every SRS requirement block references a known bundle requirement
- Title and status consistency between bundle and markdown
- Requirement block count matches

Usage:
  python3.11 scripts/check_requirement_markdown.py \\
      --bundle artifacts/gp_nca95yy_requirement_bundle.yaml \\
      --srs artifacts/srs_Gp_NCA95yy.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SRS_REQUIREMENT_HEADING = re.compile(
    r"^####\s+(SRS-[A-Z0-9_-]+)\s+(.+)$", re.MULTILINE
)
STATUS_BADGE = re.compile(r"`(Draft|Ready|Open Issue)`")
RENDERER_SYNTHESIZED_ID = re.compile(
    r"^SRS-[A-Z0-9_-]+-(SAFE-0001|CODE-0001|RES-0001|DIAG-0001|IF-9001)$"
)


# Regex to extract requirement blocks from the bundle YAML.
# Each requirement item starts with a "  -" line and its fields are at 4-space indent.
_REQ_ID_RE = re.compile(r"^    requirement_id:\s*\"?([^\"\n]+?)\"?$", re.MULTILINE)
_REQ_TITLE_RE = re.compile(r"^    title:\s*\"?([^\"\n]+?)\"?$", re.MULTILINE)
_REQ_STATUS_RE = re.compile(r"^    status:\s*\"?([^\"\n]+?)\"?$", re.MULTILINE)


def load_bundle(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        return _parse_bundle_yaml(text)
    return json.loads(text)


def _parse_bundle_yaml(text: str) -> dict[str, Any]:
    """Extract requirement objects from bundle YAML using regex.

    Relies on the stable YAML structure produced by bundle.py:
    fields are at consistent 4-space indent under ``requirements:``.
    """
    # Extract all requirement_id, title, status values under the requirements section.
    # Use finditer within the section between "requirements:" and the next top-level key.
    req_section_match = re.search(r"^requirements:\n", text, re.MULTILINE)
    if not req_section_match:
        return {"requirements": []}

    section_start = req_section_match.end()
    next_section = re.search(r"^(?!#|\s)\w+:", text[section_start:], re.MULTILINE)
    section_end = section_start + next_section.start() if next_section else len(text)
    section = text[section_start:section_end]

    ids = [m.group(1).strip().strip('"').strip("'") for m in _REQ_ID_RE.finditer(section)]
    titles = [m.group(1).strip().strip('"').strip("'") for m in _REQ_TITLE_RE.finditer(section)]
    statuses = [m.group(1).strip().strip('"').strip("'") for m in _REQ_STATUS_RE.finditer(section)]

    # Pad shorter lists to match requirement count
    count = len(ids)
    titles += [""] * (count - len(titles))
    statuses += [""] * (count - len(statuses))

    requirements: list[dict[str, Any]] = []
    for i in range(count):
        requirements.append({
            "requirement_id": ids[i],
            "title": titles[i],
            "status": statuses[i],
        })

    return {"requirements": requirements}


def check(bundle: dict[str, Any], srs_path: Path) -> list[str]:
    issues: list[str] = []
    srs_text = srs_path.read_text(encoding="utf-8")

    bundle_reqs: dict[str, dict[str, str]] = {}
    for req in bundle.get("requirements", []):
        req_id = req.get("requirement_id", "")
        if req_id:
            bundle_reqs[req_id] = {
                "title": req.get("title", ""),
                "status": req.get("status", ""),
                "shall": req.get("shall", ""),
            }

    srs_reqs: dict[str, dict[str, str]] = {}
    for match in SRS_REQUIREMENT_HEADING.finditer(srs_text):
        req_id = match.group(1)
        title = match.group(2).strip()
        block_start = match.start()
        next_heading = re.search(r"^####\s+SRS-", srs_text[block_start + 1:], re.MULTILINE)
        block_end = (block_start + 1 + next_heading.start()) if next_heading else len(srs_text)
        block = srs_text[block_start:block_end]

        status = "draft"
        status_match = STATUS_BADGE.search(block)
        if status_match:
            status = status_match.group(1).lower().replace(" ", "_")

        srs_reqs[req_id] = {"title": title, "status": status}

    bundle_ids = set(bundle_reqs)
    srs_ids = set(srs_reqs)
    synthesized_srs_ids = {
        req_id for req_id in srs_ids
        if RENDERER_SYNTHESIZED_ID.match(req_id) and req_id not in bundle_ids
    }
    comparable_srs_ids = srs_ids - synthesized_srs_ids

    # 1. Bundle requirements missing from SRS
    missing_from_srs = bundle_ids - srs_ids
    for req_id in sorted(missing_from_srs):
        issues.append(
            f"{srs_path}: bundle requirement `{req_id}` not found in SRS markdown"
        )

    # 2. SRS requirements not in bundle (stale/extra content)
    extra_in_srs = comparable_srs_ids - bundle_ids
    for req_id in sorted(extra_in_srs):
        issues.append(
            f"{srs_path}: SRS requirement `{req_id}` is not present in the requirement bundle"
        )

    # 3. Title mismatch
    for req_id in sorted(bundle_ids & comparable_srs_ids):
        bundle_title = bundle_reqs[req_id]["title"]
        srs_title = srs_reqs[req_id]["title"]
        if bundle_title and srs_title:
            if not _titles_match(bundle_title, srs_title):
                issues.append(
                    f"{srs_path}: `{req_id}` title mismatch — bundle: `{bundle_title}`, SRS: `{srs_title}`"
                )

    # 4. Status inconsistency
    for req_id in sorted(bundle_ids & comparable_srs_ids):
        bundle_status = bundle_reqs[req_id]["status"]
        srs_status = srs_reqs[req_id]["status"]
        if bundle_status == "ready" and srs_status == "draft":
            issues.append(
                f"{srs_path}: `{req_id}` is `ready` in bundle but `Draft` in SRS"
            )

    # 5. Count mismatch (summary-level)
    if len(bundle_ids) != len(comparable_srs_ids):
        issues.append(
            f"{srs_path}: requirement count mismatch — bundle has {len(bundle_ids)}, SRS has {len(comparable_srs_ids)} comparable requirements"
        )

    return issues


def _titles_match(bundle_title: str, srs_title: str) -> bool:
    """Check if titles match with tolerance for formatting differences."""
    a = bundle_title.strip().rstrip("。.")
    b = srs_title.strip().rstrip("。.")
    if a == b:
        return True
    # Common suffix differences
    if a.endswith("接口") and b == a:
        return True
    if b.endswith("接口") and a == b:
        return True
    # Configuration titles often have "配置" suffix in one but not the other
    if a.endswith("配置") and b == a[:-2]:
        return True
    if b.endswith("配置") and a == b[:-2]:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check SRS markdown consistency against requirement bundle."
    )
    parser.add_argument("--bundle", type=Path, required=True, help="Requirement bundle YAML/JSON")
    parser.add_argument("--srs", type=Path, required=True, help="SRS markdown file")
    args = parser.parse_args()

    if not args.bundle.exists():
        print(f"Bundle file not found: {args.bundle}", file=sys.stderr)
        return 1
    if not args.srs.exists():
        print(f"SRS file not found: {args.srs}", file=sys.stderr)
        return 1

    bundle = load_bundle(args.bundle)
    issues = check(bundle, args.srs)

    if issues:
        for issue in issues:
            print(issue)
        print(f"\n{len(issues)} drift issue(s) found.", file=sys.stderr)
        return 1

    bundle_count = len(bundle.get("requirements", []))
    print(f"SRS markdown matches requirement bundle ({bundle_count} requirements).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
