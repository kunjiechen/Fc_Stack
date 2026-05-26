from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release_gate_module = _load_module("evaluate_architecture_release_gate", SCRIPT_DIR / "evaluate_architecture_release_gate.py")


def _safe(items: list[Any] | None) -> list[Any]:
    return items if isinstance(items, list) else []


def _join(values: list[str] | None) -> str:
    if not values:
        return ""
    return "; ".join(str(value) for value in values if str(value).strip())


def _coverage_items(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _safe(bundle.get("coverage_result")) if isinstance(item, dict)]


def _risk_items(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _safe(bundle.get("risk_items")) if isinstance(item, dict)]


def _artifact_names(module: str) -> dict[str, str]:
    return {
        "architecture_doc": f"{module}_软件架构设计.md",
        "input_index": f"{module}_架构输入索引.md",
        "trace": f"{module}_需求架构追溯.md",
        "check": f"{module}_SDD检查清单.md",
        "review": f"{module}_架构评审记录.md",
        "operation_steps": f"{module}_SDD操作步骤.md",
        "baseline_summary": f"{module}_SDD基线总结.md",
    }


def _status_label(status: str) -> str:
    if status == "PASS":
        return "通过"
    if status == "FAIL":
        return "不通过"
    return "条件通过"


def _gate_status(passed: bool, conditional: bool = False) -> str:
    if passed:
        return "PASS"
    if conditional:
        return "CONDITIONAL"
    return "FAIL"


def _input_rows(bundle: dict[str, Any]) -> list[dict[str, str]]:
    contract = bundle.get("input_contract", {})
    grounding = bundle.get("grounding_summary", {})
    module = bundle.get("module", "")
    rows: list[dict[str, str]] = []

    requirement_input = str(contract.get("requirement_input", "")).strip()
    rows.append(
        {
            "input_id": f"AIN-{module}-0001",
            "file_name": Path(requirement_input).name if requirement_input else "N/A",
            "input_type": "SRS",
            "section": "Module scope / requirement coverage",
            "version": "待补充" if not requirement_input else "当前版本",
            "applicable": "部分适用" if not requirement_input else "是",
            "purpose": "提供模块职责、接口、配置、安全和追溯入口。",
            "design_class": "ARCH/INTF/CFG/SAFE/TRACE",
        }
    )
    rows.append(
        {
            "input_id": f"AIN-{module}-0002",
            "file_name": Path(str(contract.get("architecture_seed", ""))).name or "N/A",
            "input_type": "Architecture Seed",
            "section": "Seed root",
            "version": "当前版本",
            "applicable": "是",
            "purpose": "提供模块层级、接口草案、配置对象、运行态和风险种子。",
            "design_class": "ARCH/INTF/CFG/DEP/MEM",
        }
    )
    for index, source in enumerate(_safe(contract.get("grounding_sources")), start=3):
        rows.append(
            {
                "input_id": f"AIN-{module}-{index:04d}",
                "file_name": Path(str(source)).name,
                "input_type": "Grounding Rule",
                "section": grounding.get("module_family", "Live baseline"),
                "version": "当前版本",
                "applicable": "是",
                "purpose": "为文件族划分、依赖抽象、MemMap 和模块边界提供落地依据。",
                "design_class": "ARCH/FILE/DEP/MEM",
            }
        )
    for offset, constraint in enumerate(_safe(contract.get("project_constraints")), start=len(rows) + 1):
        rows.append(
            {
                "input_id": f"AIN-{module}-{offset:04d}",
                "file_name": "Project Constraint",
                "input_type": "Project Constraint",
                "section": "Constraint note",
                "version": "当前版本",
                "applicable": "是",
                "purpose": str(constraint),
                "design_class": "ARCH/PROCESS",
            }
        )
    return rows


def render_architecture_input_index(bundle: dict[str, Any]) -> str:
    module = bundle.get("module", "")
    names = _artifact_names(module)
    lines = [
        f"# {module} 架构输入索引",
        "",
        f"- **Module**: `{module}`",
        f"- **Document File**: `{names['input_index']}`",
        f"- **Architecture Version**: {bundle.get('architecture_version', '')}",
        f"- **Architecture Status**: {bundle.get('architecture_status', '')}",
        f"- **Generated Time**: {bundle.get('generated_time', '')}",
        "",
        "| Input ID | File Name | Input Type | Section/Location | Version/Date | Applicable | Purpose | Design Category |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in _input_rows(bundle):
        lines.append(
            f"| `{row['input_id']}` | {row['file_name']} | {row['input_type']} | {row['section']} | "
            f"{row['version']} | {row['applicable']} | {row['purpose']} | {row['design_class']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_trace_srs_sdd(bundle: dict[str, Any]) -> str:
    module = bundle.get("module", "")
    names = _artifact_names(module)
    lines = [
        f"# {module} 需求-架构追溯",
        "",
        f"- **Module**: `{module}`",
        f"- **Document File**: `{names['trace']}`",
        f"- **Architecture Version**: {bundle.get('architecture_version', '')}",
        "",
        "| SRS ID | Coverage Object | Coverage Status | Architecture Target | Design Decision | Gate Level | Close Condition | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in _coverage_items(bundle):
        lines.append(
            f"| `{item.get('requirement_id', '')}` | `{item.get('coverage_object', '')}` | {item.get('coverage_status', '')} | "
            f"{item.get('architecture_target', '')} | {item.get('decision', '')} | {item.get('gate_level', '')} | "
            f"{item.get('close_condition', '')} | {item.get('reason', '')} |"
        )
    if len(lines) == 6:
        lines.append("| `N/A` | `N/A` | no_coverage_input | N/A | N/A | N/A | N/A | 当前 bundle 未携带 SRS coverage_result。 |")
    return "\n".join(lines).rstrip() + "\n"


def _gate_rows(bundle: dict[str, Any], report: dict[str, Any]) -> list[dict[str, str]]:
    coverage_items = _coverage_items(bundle)
    risk_items = _risk_items(bundle)
    freeze_summary = Counter(
        item.get("freeze_status", "unknown")
        for item in _safe(bundle.get("freeze_matrix"))
        if isinstance(item, dict)
    )
    requirement_input = str(bundle.get("input_contract", {}).get("requirement_input", "")).strip()
    has_arch_objects = any(
        _safe(bundle.get(group))
        for group in ("external_apis", "dependency_apis", "config_macros", "runtime_states", "file_items", "memmap_sections")
    )
    has_trace = bool(coverage_items)
    has_open_blockers = bool(report["release_gate"]["blocking_findings"])
    has_open_risks = any(item.get("status") in {"待评审", "待修改"} for item in risk_items)
    has_impl_blockers = bool(report["proof_summary"]["implementation_blocker_pending"]) or bool(
        report["proof_summary"]["implementation_blocker_reserved"]
    ) or bool(report["proof_summary"]["implementation_blocker_risks"])

    return [
        {
            "gate": "Gate1",
            "name": "输入充分性检查",
            "status": _gate_status(bool(requirement_input), conditional=not requirement_input and has_trace),
            "evidence": "requirement_input / coverage_result / input index",
            "issue": "未绑定明确 SRS 输入，当前更像 seed-driven draft。" if not requirement_input else "无",
            "next_action": "补齐 SRS 路径并重新确认输入充分性。" if not requirement_input else "保持当前输入基线。",
        },
        {
            "gate": "Gate2",
            "name": "模块边界与职责检查",
            "status": _gate_status(has_arch_objects),
            "evidence": "external_apis / dependency_apis / file_items / layer",
            "issue": "缺少可支撑边界设计的核心对象。" if not has_arch_objects else "无",
            "next_action": "补齐架构对象种子。" if not has_arch_objects else "进入详细架构设计。",
        },
        {
            "gate": "Gate3",
            "name": "接口配置运行态完整性检查",
            "status": _gate_status(
                bool(_safe(bundle.get("external_apis")))
                and bool(_safe(bundle.get("config_macros")))
                and bool(_safe(bundle.get("memmap_sections"))),
                conditional=has_arch_objects,
            ),
            "evidence": "external_apis / config_macros / runtime_states / memmap_sections",
            "issue": "接口、配置或 MemMap 尚不完整。" if not (_safe(bundle.get("external_apis")) and _safe(bundle.get("config_macros")) and _safe(bundle.get("memmap_sections"))) else "无",
            "next_action": "补齐对象后重生 CHECK_SDD。" if not (_safe(bundle.get("external_apis")) and _safe(bundle.get("config_macros")) and _safe(bundle.get("memmap_sections"))) else "进入追溯和评审。",
        },
        {
            "gate": "Gate4",
            "name": "SRS 到 SDD 追溯检查",
            "status": _gate_status(
                has_trace and not any(item.get("coverage_status") == "not_covered" for item in coverage_items),
                conditional=has_trace,
            ),
            "evidence": "coverage_result / Trace_SRS_SDD",
            "issue": "仍存在 pending/reserved/not_covered 需求。" if has_trace and any(item.get("coverage_status") in {"pending_confirm", "reserved", "not_covered"} for item in coverage_items) else ("缺少 coverage_result。" if not has_trace else "无"),
            "next_action": "关闭追溯缺口或显式登记开放项。" if has_trace else "先建立 SRS coverage_result。",
        },
        {
            "gate": "Gate5",
            "name": "风险与评审闭环检查",
            "status": _gate_status(not has_open_risks, conditional=bool(risk_items)),
            "evidence": "risk_items / release_gate warning-blocking split",
            "issue": "仍有待评审或待修改风险项。" if has_open_risks else ("尚未形成风险表。" if not risk_items else "无"),
            "next_action": "在 Review_SDD 中关闭或接受遗留风险。" if risk_items else "补风险表或评审说明。",
        },
        {
            "gate": "Gate6",
            "name": "实现就绪性检查",
            "status": _gate_status(not has_impl_blockers and not has_open_blockers, conditional=not has_impl_blockers),
            "evidence": "implementation_constraints / release gate proof",
            "issue": "仍存在 implementation-blocker 项。" if has_impl_blockers else ("仍有 release blocker，暂不建议进入 SDS。" if has_open_blockers else "无"),
            "next_action": "优先关闭 implementation-blocker 和 reserved capability。" if has_impl_blockers else ("条件进入 SDS，持续跟踪 blocker。" if has_open_blockers else "可进入 SDS 输入准备。"),
        },
        {
            "gate": "Gate7",
            "name": "架构基线发布检查",
            "status": _gate_status(report["release_gate"]["release_ready"], conditional=not report["release_gate"]["release_ready"]),
            "evidence": "release_gate / rule_evidence / grounding_evidence",
            "issue": _join(report["release_gate"]["blocking_findings"]) or "无",
            "next_action": report["release_gate"]["recommended_next_action"],
        },
    ]


def render_check_sdd(bundle: dict[str, Any], report: dict[str, Any]) -> str:
    module = bundle.get("module", "")
    names = _artifact_names(module)
    lines = [
        f"# {module} SDD检查清单",
        "",
        f"- **Module**: `{module}`",
        f"- **Document File**: `{names['check']}`",
        f"- **Architecture Version**: {bundle.get('architecture_version', '')}",
        f"- **Architecture Status**: {bundle.get('architecture_status', '')}",
        "",
        "| Gate | Check Item | Result | Evidence | Main Issue | Next Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for gate in _gate_rows(bundle, report):
        lines.append(
            f"| {gate['gate']} | {gate['name']} | {_status_label(gate['status'])} | {gate['evidence']} | {gate['issue']} | {gate['next_action']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_review_sdd(bundle: dict[str, Any], report: dict[str, Any]) -> str:
    module = bundle.get("module", "")
    names = _artifact_names(module)
    lines = [
        f"# {module} 架构评审记录",
        "",
        f"- **Module**: `{module}`",
        f"- **Document File**: `{names['review']}`",
        f"- **Architecture Version**: {bundle.get('architecture_version', '')}",
        f"- **Current Decision**: {'建议进入 Baseline' if report['release_gate']['release_ready'] else '建议保持 Draft / Conditional'}",
        "",
        "## 1. 本轮评审重点",
        "",
        "- 检查模块职责和非职责边界是否已被 SRS 或架构约束明确支撑。",
        "- 检查外部接口、依赖接口、配置宏、运行态和 MemMap 是否已经形成稳定对象。",
        "- 检查 pending_confirm / reserved / risk 是否都被正确登记，而不是静默落入 SDD 正式内容。",
        "- 检查当前版本是否已经适合进入 SDS，还是只能条件进入。",
        "",
        "## 2. 需要重点关闭的问题",
        "",
    ]
    blocking = report["release_gate"]["blocking_findings"]
    warnings = report["release_gate"]["warning_findings"]
    if blocking:
        lines.extend(f"- {item}" for item in blocking)
    else:
        lines.append("- 无 release blocker。")
    if warnings:
        lines.extend(f"- Warning: {item}" for item in warnings)
    else:
        lines.append("- 无额外 warning。")

    lines.extend(
        [
            "",
            "## 3. 风险关闭记录",
            "",
            "| Risk ID | Topic | Current Status | Review Comment | Owner | Close Plan |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in _risk_items(bundle):
        lines.append(
            f"| {item.get('index', '')} | {item.get('title', '')} | {item.get('status', '')} | 待填写 | 待填写 | {item.get('recommended_action', '')} |"
        )
    if len(lines) == 20:
        lines.append("| N/A | N/A | N/A | 当前无风险项 | N/A | N/A |")

    lines.extend(
        [
            "",
            "## 4. 评审结论",
            "",
            f"- **Recommended Decision**: {report['release_gate']['recommended_next_action']}",
            "- **Reviewer Decision**: 待填写",
            "- **Residual Risk Acceptance**: 待填写",
            "- **Can Enter SDS**: 待填写",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_operation_steps_sdd(bundle: dict[str, Any], report: dict[str, Any], source_path: Path) -> str:
    module = bundle.get("module", "")
    names = _artifact_names(module)
    coverage_items = _coverage_items(bundle)
    lines = [
        f"# {module} SDD操作步骤",
        "",
        f"- **Module**: `{module}`",
        f"- **Document File**: `{names['operation_steps']}`",
        f"- **Freeze Bundle**: `{source_path}`",
        f"- **Architecture Version**: {bundle.get('architecture_version', '')}",
        "",
        "## 1. 本次执行步骤",
        "",
        f"1. 收集架构输入并建立 `{names['input_index']}`。",
        "2. 基于 architecture seed 构建 freeze bundle，冻结正式对象、保留对象和待确认对象。",
        f"3. 渲染正式架构文档 `{names['architecture_doc']}`，并同步生成 `{names['trace']}`。",
        "4. 运行 release gate 评估，确认 pending_confirm、reserved、risk 和 rule_evidence 完整性。",
        f"5. 输出 `{names['check']}`、`{names['review']}`、`{names['baseline_summary']}`，用于人工评审和阶段归档。",
        "",
        "## 2. 本次关键判断",
        "",
        f"- 覆盖条目数: {len(coverage_items)}",
        f"- 风险条目数: {len(_risk_items(bundle))}",
        f"- Release Ready: {'Yes' if report['release_gate']['release_ready'] else 'No'}",
        f"- 推荐下一步: {report['release_gate']['recommended_next_action']}",
        "",
        "## 3. 本次建议动作",
        "",
    ]
    for item in report["release_gate"]["blocking_findings"]:
        lines.append(f"- 优先处理: {item}")
    if not report["release_gate"]["blocking_findings"]:
        lines.append("- 当前无 release blocker，可准备架构基线归档。")
    return "\n".join(lines).rstrip() + "\n"


def render_sdd_baseline_summary(bundle: dict[str, Any], report: dict[str, Any]) -> str:
    module = bundle.get("module", "")
    names = _artifact_names(module)
    coverage = Counter(item.get("coverage_status", "unknown") for item in _coverage_items(bundle))
    lines = [
        f"# {module} SDD基线总结",
        "",
        f"- **Module**: `{module}`",
        f"- **Document File**: `{names['baseline_summary']}`",
        f"- **Architecture Version**: {bundle.get('architecture_version', '')}",
        f"- **Architecture Status**: {bundle.get('architecture_status', '')}",
        f"- **Release Ready**: {'Yes' if report['release_gate']['release_ready'] else 'No'}",
        "",
        "## 1. 基线概况",
        "",
        f"- covered: {coverage.get('covered', 0)}",
        f"- covered_with_constraint: {coverage.get('covered_with_constraint', 0)}",
        f"- pending_confirm: {coverage.get('pending_confirm', 0)}",
        f"- reserved: {coverage.get('reserved', 0)}",
        f"- not_covered: {coverage.get('not_covered', 0)}",
        "",
        "## 2. 下游 SDS 必须继承的约束",
        "",
    ]
    impl = bundle.get("implementation_constraints", {})
    for item in _safe(impl.get("implementation_prohibitions")):
        lines.append(f"- 禁止: {item}")
    for item in _safe(impl.get("implementation_required_areas")):
        lines.append(f"- 必须保留: {item}")
    if not _safe(impl.get("implementation_prohibitions")) and not _safe(impl.get("implementation_required_areas")):
        lines.append("- 当前 bundle 未提供实现约束摘要。")

    lines.extend(
        [
            "",
            "## 3. 阶段结论",
            "",
            f"- **Recommended Conclusion**: {report['release_gate']['recommended_next_action']}",
            f"- **Residual Risks**: {len(report['proof_summary']['open_risks'])}",
            f"- **Pending Confirm Items**: {len(report['proof_summary']['pending_confirm_requirements'])}",
            f"- **Reserved Capabilities**: {len(report['proof_summary']['reserved_capabilities'])}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_workflow_artifacts(bundle: dict[str, Any], source_path: Path) -> dict[str, str]:
    report = release_gate_module.evaluate_architecture_release_gate(bundle)
    module = bundle.get("module", "FC")
    names = _artifact_names(module)
    return {
        names["input_index"]: render_architecture_input_index(bundle),
        names["trace"]: render_trace_srs_sdd(bundle),
        names["check"]: render_check_sdd(bundle, report),
        names["review"]: render_review_sdd(bundle, report),
        names["operation_steps"]: render_operation_steps_sdd(bundle, report, source_path),
        names["baseline_summary"]: render_sdd_baseline_summary(bundle, report),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render workflow-layer FC architecture artifacts from a freeze bundle.")
    parser.add_argument("input", type=Path, help="Architecture freeze bundle JSON path")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write workflow artifacts into")
    args = parser.parse_args()

    bundle = json.loads(args.input.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for file_name, content in render_workflow_artifacts(bundle, args.input).items():
        (args.output_dir / file_name).write_text(content, encoding="utf-8")
    print(f"Wrote architecture workflow artifacts to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
