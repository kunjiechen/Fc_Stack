#!/usr/bin/env python3
"""Run implementation-workbench regression cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from script_dependency_support import require_modules


def load_case(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid regression case: {path}")
    return {str(key): str(value) for key, value in data.items()}


def run_command(args: list[str], cwd: Path) -> None:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode == 0:
        return
    message = result.stderr.strip() or result.stdout.strip() or "unknown error"
    raise RuntimeError(message)


def case_paths(root: Path, case: dict[str, str]) -> dict[str, Path]:
    return {
        "bundle": root / case["bundle"],
        "arch": root / case["architecture_markdown"],
        "golden": root / case["golden_rendered_dd"],
    }


def run_case(case_path: Path, root: Path, refresh_golden: bool) -> None:
    case = load_case(case_path)
    paths = case_paths(root, case)
    script_root = root / ".claude/skills/fc-implementation-workbench/scripts"

    for label, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"{case['case_id']}: missing {label} file: {path}")

    run_command(
        [
            sys.executable,
            str(script_root / "validate_generation_bundle.py"),
            "--bundle",
            str(paths["bundle"]),
        ],
        root,
    )

    with tempfile.TemporaryDirectory(prefix=f"{case['case_id']}_dd_") as temp_dir:
        rendered = Path(temp_dir) / f"{case['case_id']}_rendered_dd.md"
        run_command(
            [
                sys.executable,
                str(script_root / "render_detailed_design.py"),
                "--bundle",
                str(paths["bundle"]),
                "--output",
                str(rendered),
                "--generated-at",
                case.get("generated_at", "2026-01-01 00:00:00"),
            ],
            root,
        )
        run_command(
            [
                sys.executable,
                str(script_root / "validate_fc_docs.py"),
                "--arch",
                str(paths["arch"]),
                "--dd",
                str(rendered),
            ],
            root,
        )

        if refresh_golden:
            shutil.copyfile(rendered, paths["golden"])
        elif rendered.read_text(encoding="utf-8") != paths["golden"].read_text(encoding="utf-8"):
            raise RuntimeError(f"{case['case_id']}: rendered detailed design does not match golden")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run implementation-workbench regression pack.")
    parser.add_argument("--case", help="Run a single regression case by case id")
    parser.add_argument("--refresh-golden", action="store_true", help="Refresh rendered DD golden outputs")
    args = parser.parse_args()

    require_modules({"PyYAML": "yaml", "jsonschema": "jsonschema"}, context="run_regression_pack.py")

    root = Path(__file__).resolve().parents[4]
    case_dir = root / ".claude/skills/fc-implementation-workbench/regression/cases"
    if args.case:
        case_paths_list = [case_dir / f"{args.case}.json"]
    else:
        case_paths_list = sorted(case_dir.glob("*.json"))

    if not case_paths_list:
        print("No regression cases found.")
        return 1

    for case_path in case_paths_list:
        try:
            run_case(case_path, root, args.refresh_golden)
            print(f"[PASS] {case_path.stem}")
        except Exception as exc:
            print(f"[FAIL] {case_path.stem}: {exc}")
            return 1

    print(f"\nImplementation regression pack passed for {len(case_paths_list)} case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
