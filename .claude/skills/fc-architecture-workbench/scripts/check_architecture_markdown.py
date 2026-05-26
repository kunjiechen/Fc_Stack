from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VERSION_LINE = re.compile(r"架构版本:\s*\*\*V\d+\*\*")
STATUS_LINE = re.compile(r"架构状态:\s*\*\*(Draft|Released)\*\*", re.IGNORECASE)
OUTPUT_MODE_LINE = re.compile(r"输出模式:\s*\*\*(Quick Draft|Formal Draft|Released)\*\*", re.IGNORECASE)
CREATED_LINE = re.compile(r"Created:\s*.+")
RISK_ROW = re.compile(r"^\|\s*(R\d+|R-OTHER)\s*\|", re.MULTILINE)
RISK_STATUS = re.compile(r"\|\s*(待评审|已评审|待修改)\s*\|")


def check_architecture_markdown(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []

    if not VERSION_LINE.search(text):
        issues.append(f"{path}: missing architecture version metadata like `架构版本: **V1**`")
    if not STATUS_LINE.search(text):
        issues.append(f"{path}: missing architecture status metadata like `架构状态: **Draft**`")
    if not OUTPUT_MODE_LINE.search(text):
        issues.append(f"{path}: missing output mode metadata like `输出模式: **Formal Draft**`")
    if not CREATED_LINE.search(text):
        issues.append(f"{path}: missing Created timestamp")

    risk_rows = RISK_ROW.findall(text)
    output_mode_match = OUTPUT_MODE_LINE.search(text)
    output_mode = output_mode_match.group(1).lower() if output_mode_match else ""
    if not risk_rows:
        issues.append(f"{path}: missing indexed risk rows such as R1/R2/R-OTHER")
    else:
        statuses = RISK_STATUS.findall(text)
        if not statuses:
            issues.append(f"{path}: risk table exists but does not use supported statuses `待评审/已评审/待修改`")
        real_rows = [row for row in risk_rows if row != "R-OTHER"]
        if output_mode == "quick draft" and len(real_rows) > 5:
            issues.append(f"{path}: Quick Draft should keep only 3..5 real risk rows before R-OTHER")

    lowered = text.lower()
    is_released = "架构状态: **released**" in lowered or "status: **released**" in lowered
    is_quick_draft = output_mode == "quick draft"
    if is_released and any(status in text for status in ("待评审", "待修改")):
        issues.append(f"{path}: architecture is marked Released but still contains pending risk statuses")
    if is_released and is_quick_draft:
        issues.append(f"{path}: Quick Draft output cannot be marked Released")

    if "callout" in lowered:
        if "Callout.h" not in text or "Callout.c" not in text:
            issues.append(f"{path}: callout usage detected but file list does not include both Callout.h and Callout.c")

    if "i2c" in lowered or "spi" in lowered or "register" in lowered:
        if "Reg.h" not in text:
            issues.append(f"{path}: register-based external communication detected but Reg.h carrier is missing")

    diag_interface_signals = (
        "getfault",
        "getdiag",
        "getfaultstatus",
        "fault interface",
        "diagnostic interface",
        "fault status interface",
        "diagnostic status interface",
        "故障接口",
        "诊断接口",
        "故障状态",
        "诊断状态",
    )
    if any(token in lowered for token in diag_interface_signals):
        if not any(token in lowered for token in ("getfault", "getdiag", "getfaultstatus", "getdevfaultsig", "faultsig", "故障读取", "诊断读取")):
            issues.append(f"{path}: diagnostic/fault behavior detected but no readable fault/diagnostic status interface is present")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check generated FC architecture markdown format.")
    parser.add_argument("paths", nargs="+", help="Architecture markdown file(s) to validate")
    args = parser.parse_args()

    issues: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*.md")):
                issues.extend(check_architecture_markdown(child))
        else:
            issues.extend(check_architecture_markdown(path))

    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("Architecture format check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
