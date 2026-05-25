#!/usr/bin/env python3
"""Replay golden regression cases for fc-requirement-workbench."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


EMITS = (
    "requirement-bundle",
    "architecture-seed",
    "test-seed",
    "bundle-validation",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fc-requirement-workbench regression pack.")
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Run only the specified regression case id. Can be provided multiple times.",
    )
    parser.add_argument(
        "--refresh-golden",
        action="store_true",
        help="Overwrite golden artifacts with the newly generated outputs after a successful run.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[4]
    skill_root = Path(__file__).resolve().parents[1]
    cases_dir = skill_root / "regression" / "cases"
    case_paths = sorted(cases_dir.glob("*.json"))
    if args.case_ids:
        wanted = set(args.case_ids)
        case_paths = [path for path in case_paths if path.stem in wanted]

    if not case_paths:
        print("No regression cases selected.", file=sys.stderr)
        return 1

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="fc_req_regression_") as temp_dir_name:
        temp_root = Path(temp_dir_name)
        for case_path in case_paths:
            case = json.loads(case_path.read_text(encoding="utf-8"))
            case_id = case["case_id"]
            case_dir = temp_root / case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            try:
                generated = _run_case(case, repo_root=repo_root, skill_root=skill_root, output_dir=case_dir)
                _check_case(
                    case,
                    repo_root=repo_root,
                    generated=generated,
                    compare_to_golden=not args.refresh_golden,
                )
                if args.refresh_golden:
                    _refresh_golden(case, repo_root=repo_root, generated=generated)
                print(f"[PASS] {case_id}")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{case_id}: {exc}")
                print(f"[FAIL] {case_id}: {exc}", file=sys.stderr)

    if failures:
        print("\nRegression pack failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(f"\nRegression pack passed for {len(case_paths)} case(s).")
    return 0


def _run_case(case: dict[str, Any], *, repo_root: Path, skill_root: Path, output_dir: Path) -> dict[str, Path]:
    generated: dict[str, Path] = {}
    golden = case["golden"]
    for emit in EMITS:
        output_name = Path(golden[emit]).name
        output_path = output_dir / output_name
        command = [
            sys.executable,
            "-m",
            "fc_requirement_workbench.cli",
            str(case["input_document"]),
            "--module",
            str(case["module"]),
            "--raw-input",
            str(case["raw_input"]),
            "--source-root",
            str(case["source_root"]),
            "--emit",
            emit,
            "--output",
            str(output_path),
            "--no-cache",
        ]
        env = os.environ.copy()
        pythonpath = env.get("PYTHONPATH", "")
        skill_src = str(skill_root / "src")
        env["PYTHONPATH"] = skill_src if not pythonpath else f"{skill_src}{os.pathsep}{pythonpath}"
        completed = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"emit `{emit}` failed with code {completed.returncode}: {completed.stderr.strip() or completed.stdout.strip()}"
            )
        generated[emit] = output_path
    return generated


def _check_case(
    case: dict[str, Any],
    *,
    repo_root: Path,
    generated: dict[str, Path],
    compare_to_golden: bool,
) -> None:
    golden = case["golden"]
    expectations = case["expectations"]
    if compare_to_golden:
        for emit, generated_path in generated.items():
            golden_path = repo_root / golden[emit]
            expected = golden_path.read_text(encoding="utf-8")
            actual = generated_path.read_text(encoding="utf-8")
            if actual != expected:
                raise AssertionError(f"`{emit}` output differs from golden `{golden_path}`")

    validation = json.loads(generated["bundle-validation"].read_text(encoding="utf-8"))
    summary = validation.get("summary", {})
    expected_summary = expectations["validation_summary"]
    for key, value in expected_summary.items():
        actual = summary.get(key)
        if actual != value:
            raise AssertionError(f"validation summary `{key}` expected {value}, got {actual}")

    architecture_text = generated["architecture-seed"].read_text(encoding="utf-8")
    for function_name in expectations["architecture_interfaces"]:
        if function_name not in architecture_text:
            raise AssertionError(f"missing architecture interface `{function_name}` in generated architecture seed")

    requirement_text = generated["requirement-bundle"].read_text(encoding="utf-8")
    for title in expectations["requirement_titles"]:
        if title not in requirement_text:
            raise AssertionError(f"missing requirement title `{title}` in generated bundle")


def _refresh_golden(case: dict[str, Any], *, repo_root: Path, generated: dict[str, Path]) -> None:
    golden = case["golden"]
    for emit, generated_path in generated.items():
        golden_path = repo_root / golden[emit]
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(generated_path, golden_path)


if __name__ == "__main__":
    raise SystemExit(main())
