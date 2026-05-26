from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parents[3]
ARTIFACTS_DIR = ROOT_DIR / "artifacts"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_module = _load_module("build_architecture_freeze_bundle", SCRIPT_DIR / "build_architecture_freeze_bundle.py")
freeze_validator = _load_module("validate_architecture_freeze_bundle", SCRIPT_DIR / "validate_architecture_freeze_bundle.py")
object_validator = _load_module("validate_architecture_objects", SCRIPT_DIR / "validate_architecture_objects.py")
source_validator = _load_module("validate_architecture_source_alignment", SCRIPT_DIR / "validate_architecture_source_alignment.py")
render_module = _load_module("render_architecture_objects", SCRIPT_DIR / "render_architecture_objects.py")
markdown_checker = _load_module("check_architecture_markdown", SCRIPT_DIR / "check_architecture_markdown.py")
release_gate_module = _load_module("evaluate_architecture_release_gate", SCRIPT_DIR / "evaluate_architecture_release_gate.py")
workflow_module = _load_module("render_architecture_workflow_artifacts", SCRIPT_DIR / "render_architecture_workflow_artifacts.py")


@dataclass(frozen=True)
class Baseline:
    seed: str
    bundle: str
    summary_md: str
    release_gate_json: str
    release_gate_md: str


BASELINES = (
    Baseline(
        "gp_nca95yy_architecture_seed.yaml",
        "gp_nca95yy_architecture_freeze_bundle.json",
        "gp_nca95yy_architecture_summary.md",
        "gp_nca95yy_architecture_release_gate.json",
        "gp_nca95yy_architecture_release_gate.md",
    ),
    Baseline(
        "gp_iomcudio_architecture_seed.yaml",
        "gp_iomcudio_architecture_freeze_bundle.json",
        "gp_iomcudio_architecture_summary.md",
        "gp_iomcudio_architecture_release_gate.json",
        "gp_iomcudio_architecture_release_gate.md",
    ),
    Baseline(
        "gp_06_adc3ph_architecture_seed.yaml",
        "gp_06_adc3ph_architecture_freeze_bundle.json",
        "gp_06_adc3ph_architecture_summary.md",
        "gp_06_adc3ph_architecture_release_gate.json",
        "gp_06_adc3ph_architecture_release_gate.md",
    ),
    Baseline(
        "gp_wkupsrcp_architecture_seed.yaml",
        "gp_wkupsrcp_architecture_freeze_bundle.json",
        "gp_wkupsrcp_architecture_summary.md",
        "gp_wkupsrcp_architecture_release_gate.json",
        "gp_wkupsrcp_architecture_release_gate.md",
    ),
)


def _render_summary(bundle_path: Path, summary_path: Path) -> None:
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    content = render_module.render_summary_markdown(payload)
    summary_path.write_text(content, encoding="utf-8")


def _render_release_gate(bundle_path: Path, report_json_path: Path, report_md_path: Path) -> None:
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    report = release_gate_module.evaluate_architecture_release_gate(payload)
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_md_path.write_text(release_gate_module.render_release_gate_markdown(report), encoding="utf-8")


def _render_workflow_artifacts(bundle_path: Path) -> None:
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    for file_name, content in workflow_module.render_workflow_artifacts(payload, bundle_path).items():
        (ARTIFACTS_DIR / file_name).write_text(content, encoding="utf-8")


def run_regression() -> list[str]:
    issues: list[str] = []
    for baseline in BASELINES:
        seed_path = ARTIFACTS_DIR / baseline.seed
        bundle_path = ARTIFACTS_DIR / baseline.bundle
        summary_path = ARTIFACTS_DIR / baseline.summary_md
        release_gate_json_path = ARTIFACTS_DIR / baseline.release_gate_json
        release_gate_md_path = ARTIFACTS_DIR / baseline.release_gate_md

        bundle = build_module.build_freeze_bundle(seed_path)
        bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        issues.extend(freeze_validator.validate_architecture_freeze_bundle(bundle_path))
        issues.extend(object_validator.validate_architecture_objects(bundle_path))
        issues.extend(source_validator.validate_architecture_source_alignment(bundle_path))

        _render_summary(bundle_path, summary_path)
        issues.extend(markdown_checker.check_architecture_markdown(summary_path))
        _render_release_gate(bundle_path, release_gate_json_path, release_gate_md_path)
        _render_workflow_artifacts(bundle_path)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Run architecture regression across baseline seeds and rendered markdown.")
    parser.parse_args()

    issues = run_regression()
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("Architecture regression passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
