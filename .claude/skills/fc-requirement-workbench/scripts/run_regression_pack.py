#!/usr/bin/env python3
"""Replay golden regression cases for fc-requirement-workbench.

Usage:
  python3.11 scripts/run_regression_pack.py              # run all cases
  python3.11 scripts/run_regression_pack.py --case gp_nca95yy  # single case
  python3.11 scripts/run_regression_pack.py --ci          # CI mode (expectations only)
  python3.11 scripts/run_regression_pack.py --refresh-golden  # update baselines

Environment variables:
  FC_SOURCE_ROOT   override source_root for all cases
"""

from __future__ import annotations

import argparse
import difflib
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
SRS_EMIT = "srs-markdown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fc-requirement-workbench regression pack.")
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Run only the specified regression case id. Can be provided multiple times.",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: skip byte-exact golden comparison; only check expectations and validation summaries.",
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
        missing = wanted - {path.stem for path in case_paths}
        if missing:
            print(f"Unknown case(s): {', '.join(sorted(missing))}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(path.stem for path in sorted(cases_dir.glob('*.json'))))}", file=sys.stderr)
            return 1

    if not case_paths:
        print("No regression cases selected.", file=sys.stderr)
        return 1

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="fc_req_regression_") as temp_dir_name:
        temp_root = Path(temp_dir_name)
        for case_path in case_paths:
            case = _load_case(case_path, repo_root=repo_root)
            case_id = case["case_id"]
            case_dir = temp_root / case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            try:
                generated = _run_case(case, repo_root=repo_root, skill_root=skill_root, output_dir=case_dir)
                _check_case(
                    case,
                    repo_root=repo_root,
                    generated=generated,
                    compare_to_golden=not args.refresh_golden and not args.ci,
                )
                if args.refresh_golden:
                    _refresh_golden(case, repo_root=repo_root, generated=generated)
                print(f"[PASS] {case_id}")
            except Exception as exc:
                failures.append(f"{case_id}: {exc}")
                print(f"[FAIL] {case_id}: {exc}", file=sys.stderr)

    if failures:
        print(f"\nRegression pack failed ({len(failures)}/{len(case_paths)} cases):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(f"\nRegression pack passed for {len(case_paths)} case(s).")
    return 0


def _load_case(case_path: Path, *, repo_root: Path) -> dict[str, Any]:
    case = json.loads(case_path.read_text(encoding="utf-8"))

    source_root = os.environ.get("FC_SOURCE_ROOT", "")
    if not source_root:
        source_root = case.get("source_root", "") or case.get("source_root_abs", "")
        if source_root:
            source_root = str(repo_root / source_root) if not source_root.startswith("/") else source_root
    case["_resolved_source_root"] = source_root or ""

    # Resolve golden paths to absolute for file operations, but keep original
    # input paths relative so generated output matches golden files byte-for-byte.
    for field in ("input_document", "raw_input"):
        value = case.get(field, "")
        if value and not value.startswith("/"):
            case[f"_{field}_abs"] = str(repo_root / value)
        else:
            case[f"_{field}_abs"] = value

    for emit, golden_path in case.get("golden", {}).items():
        if not golden_path.startswith("/"):
            case["golden"][emit] = str(repo_root / golden_path)

    return case


def _run_case(case: dict[str, Any], *, repo_root: Path, skill_root: Path, output_dir: Path) -> dict[str, Path]:
    generated: dict[str, Path] = {}
    golden = case["golden"]
    for emit in (*EMITS, SRS_EMIT):
        if emit == SRS_EMIT:
            output_name = f"{case['case_id']}_srs.md"
        else:
            output_name = Path(golden[emit]).name
        output_path = output_dir / output_name
        # Use original (relative) paths for CLI so generated output matches golden
        input_doc = case.get("input_document")  # keep as-is from JSON
        raw_input = case.get("raw_input")        # keep as-is from JSON
        command = [
            sys.executable,
            "-m",
            "fc_requirement_workbench.cli",
            input_doc,
            "--module",
            str(case["module"]),
            "--raw-input",
            raw_input,
            "--emit",
            emit,
            "--output",
            str(output_path),
            "--no-cache",
        ]
        source_root = case.get("_resolved_source_root", "")
        if source_root:
            command.extend(["--source-root", source_root])

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
                f"emit `{emit}` failed with code {completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
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
    source_root = case.get("_resolved_source_root", "")

    if compare_to_golden:
        for emit, generated_path in generated.items():
            if emit not in golden:
                continue
            golden_path = Path(golden[emit])
            expected = golden_path.read_text(encoding="utf-8")
            actual = generated_path.read_text(encoding="utf-8")
            if source_root:
                expected = expected.replace(source_root, "${SOURCE_ROOT}")
                actual = actual.replace(source_root, "${SOURCE_ROOT}")
            if actual != expected:
                diff = "\n".join(
                    difflib.unified_diff(
                        expected.splitlines(),
                        actual.splitlines(),
                        fromfile=f"golden/{golden_path.name}",
                        tofile=f"generated/{generated_path.name}",
                        lineterm="",
                    )
                )
                raise AssertionError(
                    f"`{emit}` output differs from golden `{golden_path}`\n{diff}"
                )

    validation = json.loads(generated["bundle-validation"].read_text(encoding="utf-8"))
    summary = validation.get("summary", {})
    expected_summary = expectations["validation_summary"]
    for key, value in expected_summary.items():
        actual = summary.get(key)
        if actual != value:
            raise AssertionError(
                f"validation summary `{key}` expected {value}, got {actual}"
            )

    architecture_text = generated["architecture-seed"].read_text(encoding="utf-8")
    for function_name in expectations["architecture_interfaces"]:
        if function_name not in architecture_text:
            raise AssertionError(
                f"missing architecture interface `{function_name}` in generated architecture seed"
            )

    requirement_text = generated["requirement-bundle"].read_text(encoding="utf-8")
    for title in expectations["requirement_titles"]:
        if title not in requirement_text:
            raise AssertionError(
                f"missing requirement title `{title}` in generated bundle"
            )

    _check_srs_consistency(
        repo_root=repo_root,
        bundle_path=generated["requirement-bundle"],
        srs_path=generated[SRS_EMIT],
    )


def _refresh_golden(case: dict[str, Any], *, repo_root: Path, generated: dict[str, Path]) -> None:
    golden = case["golden"]
    for emit, generated_path in generated.items():
        if emit not in golden:
            continue
        golden_path = Path(golden[emit])
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(generated_path, golden_path)


def _check_srs_consistency(*, repo_root: Path, bundle_path: Path, srs_path: Path) -> None:
    script = repo_root / ".claude/skills/fc-requirement-workbench/scripts/check_requirement_markdown.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--bundle",
            str(bundle_path),
            "--srs",
            str(srs_path),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "generated SRS markdown drifted from requirement bundle: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
