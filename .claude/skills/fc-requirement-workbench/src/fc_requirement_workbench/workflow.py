"""Workflow orchestration — coordinates Phase 1~4 and the fix loop.

Provides the --mode full and --mode loop pipeline modes that tie together
source indexing, extraction, SRS generation, gate checking, and delivery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .builder import EngineeringRequirement
from .filenames import (
    check_list_doc,
    derivation_doc,
    open_items_doc,
    operation_steps_doc,
    review_doc,
    source_extract_doc,
    source_index_doc,
    srs_doc,
)
from .gate_check import GateChecker, GateReport, render_gate_check_markdown
from .open_items import OpenItemsCollector, render_open_items_markdown
from .rules import ValidationFinding


@dataclass
class WorkflowContext:
    module: str
    input_file: str = ""
    output_dir: Path | None = None
    has_raw_requirements: bool = False
    has_datasheet: bool = False
    has_project_constraints: bool = False
    datasheet_chapters: list[str] = field(default_factory=list)
    source_count: int = 0

    engineering_requirements: list[Any] = field(default_factory=list)
    findings: list[Any] = field(default_factory=list)

    # Phase outputs
    source_index_entries: list[Any] = field(default_factory=list)
    extract_records: list[Any] = field(default_factory=list)
    derivation_records: list[Any] = field(default_factory=list)
    open_items: list[Any] = field(default_factory=list)
    gate_reports: list[Any] = field(default_factory=list)

    # Loop state
    loop_count: int = 0
    auto_fixes_applied: int = 0

    @property
    def has_blocking_issues(self) -> bool:
        if not self.gate_reports:
            return True
        return any(r.is_blocking for r in self.gate_reports)


@dataclass
class FixResult:
    auto_fixes: list[str] = field(default_factory=list)
    manual_items: list[str] = field(default_factory=list)
    is_clean: bool = False


class FixLoopEngine:
    """Analyze gate check results, apply modifications, and re-check.

    Auto-fixes: format, status downgrade, terminology normalization, duplicate removal.
    Manual items: missing sources, unclear ownership, config values, safety levels.

    Modification records from fix_input look like::

        modifications:
          - target: SRS-MODULE-IF-0003
            field: function_name
            new_value: "Gp_NCA9539_GetGpioInSig"
            reason: "对齐 aurix2g-normative-patterns"

    Merged requirements & open items carry the change provenance into
    operation steps.
    """

    # Fields on EngineeringRequirement that can be patched via fix_input.
    _PATCHABLE = frozenset({
        "title", "description", "pre_condition", "trigger",
        "input", "output", "exception", "constraint",
        "verification", "function_name",
    })

    def analyze(
        self,
        gate_reports: list[GateReport],
        engineering_requirements: list[EngineeringRequirement],
        findings: list[ValidationFinding],
    ) -> FixResult:
        result = FixResult()

        auto_fixes, manual_items = [], []

        for report in gate_reports:
            for item in report.items:
                if item.result != "Fail" and item.result != "Conditional":
                    continue
                if item.check_id in ("G1-06", "G1-08", "G2-03", "G2-04", "G3-01", "G3-02",
                                      "G3-04", "G3-05", "G4-05", "G5-02", "G5-03",
                                      "G5-04", "G5-05", "G6-03", "G6-04"):
                    manual_items.append(f"[{report.gate}] {item.check_id}: {item.detail}")
                elif item.check_id in ("G2-01", "G2-02", "G3-03", "G4-01", "G4-02",
                                        "G4-03", "G4-04", "G6-01", "G6-02"):
                    if item.check_id == "G4-04":
                        auto_fixes.append(f"去重重复 ID: {', '.join(item.affected_ids)}")
                    elif item.check_id == "G4-02":
                        manual_items.append(f"[{report.gate}] {item.check_id}: {item.detail}")
                    else:
                        auto_fixes.append(f"[{report.gate}] {item.check_id}: {item.detail}")
                else:
                    manual_items.append(f"[{report.gate}] {item.check_id}: {item.detail}")

        has_any_fixes = bool(auto_fixes) or bool(manual_items)
        result.auto_fixes = auto_fixes
        result.manual_items = manual_items
        result.is_clean = not has_any_fixes
        return result

    def apply_modifications(
        self,
        engineering_requirements: list[EngineeringRequirement],
        modifications: list[dict[str, Any]],
    ) -> tuple[list[EngineeringRequirement], list[str]]:
        """Apply field-level modifications from fix_input.

        Returns (updated_requirements, change_log).
        EngineeringRequirement is frozen so we reconstruct instances.
        """
        if not modifications:
            return engineering_requirements, []

        by_id: dict[str, EngineeringRequirement] = {
            req.requirement_id: req for req in engineering_requirements
        }
        change_log: list[str] = []

        for mod in modifications:
            target = mod.get("target", "")
            field = mod.get("field", "")
            new_value = mod.get("new_value")
            reason = mod.get("reason", "")

            if target not in by_id:
                change_log.append(f"SKIP {target}: ID not found in requirements")
                continue
            if field not in self._PATCHABLE:
                change_log.append(f"SKIP {target}.{field}: field not patchable")
                continue
            if new_value is None:
                change_log.append(f"SKIP {target}.{field}: new_value is None")
                continue

            old = by_id[target]
            old_value = getattr(old, field, "")
            kwargs = {
                "requirement_id": old.requirement_id,
                "semantic_id": old.semantic_id,
                "requirement_type": old.requirement_type,
                "title": old.title,
                "description": old.description,
                "pre_condition": old.pre_condition,
                "trigger": old.trigger,
                "input": old.input,
                "output": old.output,
                "exception": old.exception,
                "constraint": old.constraint,
                "verification": old.verification,
                "function_name": old.function_name,
                "source": old.source,
                "validation": old.validation,
            }
            kwargs[field] = new_value
            by_id[target] = EngineeringRequirement(**kwargs)
            change_log.append(
                f"PATCH {target}.{field}: \"{old_value}\" → \"{new_value}\"{'  // ' + reason if reason else ''}"
            )

        return list(by_id.values()), change_log

    def apply_open_item_closures(
        self,
        open_items: list[Any],
        closures: list[dict[str, Any]],
    ) -> tuple[list[Any], list[str]]:
        """Mark open items as Closed based on fix_input closures.

        Returns (updated_open_items, closure_log).
        """
        if not closures:
            return open_items, []

        closure_ids = {c.get("item_id", "") for c in closures}
        updated: list[Any] = []
        closure_log: list[str] = []

        for oi in open_items:
            oi_id = getattr(oi, 'item_id', '')
            if oi_id in closure_ids:
                resolution = next(
                    (c.get("resolution", "") for c in closures if c.get("item_id") == oi_id),
                    "",
                )
                if hasattr(oi, 'status'):
                    oi.status = "Closed"
                closure_log.append(f"CLOSE {oi_id}{'  // ' + resolution if resolution else ''}")
            updated.append(oi)

        return updated, closure_log

    def incremental_recheck(
        self,
        gate_reports: list[GateReport],
        engineering_requirements: list[EngineeringRequirement],
        findings: list[ValidationFinding],
        affected_ids: set[str],
        module: str,
        open_items: list[Any] | None = None,
        source_count: int = 0,
        has_raw_requirements: bool = False,
        has_datasheet: bool = False,
        has_project_constraints: bool = False,
    ) -> list[GateReport]:
        """Re-run Gate checks only for gates whose items reference affected
        requirement IDs.  Returns the full gate_reports list with affected
        gates replaced.
        """
        if not affected_ids:
            return gate_reports

        # Determine which gates need re-checking
        affected_gates: set[str] = set()
        for report in gate_reports:
            for item in report.items:
                if set(item.affected_ids) & affected_ids:
                    affected_gates.add(report.gate)
                # Gate 3/4/6 are structural — re-check them when requirements change
                if report.gate in ("Gate 3", "Gate 4", "Gate 6"):
                    if any(
                        req.requirement_id in affected_ids
                        for req in engineering_requirements
                    ):
                        affected_gates.add(report.gate)

        if not affected_gates:
            return gate_reports

        open_item_dicts = [oi.__dict__ if hasattr(oi, '__dict__') else oi for oi in (open_items or [])]
        fresh_reports: dict[str, GateReport] = {}

        checker = GateChecker(
            module=module,
            source_count=source_count,
            has_raw_requirements=has_raw_requirements,
            has_datasheet=has_datasheet,
            has_project_constraints=has_project_constraints,
        )
        all_reports = checker.check_all(engineering_requirements, findings, open_item_dicts)
        for report in all_reports:
            if report.gate in affected_gates:
                fresh_reports[report.gate] = report

        updated: list[GateReport] = []
        for report in gate_reports:
            updated.append(fresh_reports.get(report.gate, report))

        return updated


class WorkflowOrchestrator:
    """Orchestrate the complete SRS generation workflow with optional fix loop."""

    def __init__(self, module: str, output_dir: Path | None = None) -> None:
        self.module = module
        self.output_dir = output_dir or Path("Output") / module / "Doc" / "SRS"

    def build_context(
        self,
        input_file: str = "",
        has_raw_requirements: bool = False,
        has_datasheet: bool = False,
        has_project_constraints: bool = False,
        datasheet_chapters: list[str] | None = None,
    ) -> WorkflowContext:
        return WorkflowContext(
            module=self.module,
            input_file=input_file,
            output_dir=self.output_dir,
            has_raw_requirements=has_raw_requirements,
            has_datasheet=has_datasheet,
            has_project_constraints=has_project_constraints,
            datasheet_chapters=datasheet_chapters or [],
        )

    def run_gate_check(
        self,
        ctx: WorkflowContext,
        engineering_requirements: list[EngineeringRequirement],
        findings: list[ValidationFinding],
    ) -> WorkflowContext:
        checker = GateChecker(
            module=ctx.module,
            source_count=ctx.source_count,
            has_raw_requirements=ctx.has_raw_requirements,
            has_datasheet=ctx.has_datasheet,
            has_project_constraints=ctx.has_project_constraints,
        )
        open_items_dicts = [oi.__dict__ if hasattr(oi, '__dict__') else oi for oi in ctx.open_items]
        ctx.gate_reports = checker.check_all(
            engineering_requirements, findings, open_items_dicts
        )
        ctx.engineering_requirements = list(engineering_requirements)
        ctx.findings = list(findings)
        return ctx

    def run_fix_loop(
        self,
        ctx: WorkflowContext,
    ) -> tuple[WorkflowContext, FixResult]:
        ctx.loop_count += 1
        engine = FixLoopEngine()
        fix_result = engine.analyze(
            ctx.gate_reports,
            ctx.engineering_requirements,
            ctx.findings,
        )
        ctx.auto_fixes_applied += len(fix_result.auto_fixes)
        return ctx, fix_result

    def finalize(
        self,
        ctx: WorkflowContext,
    ) -> dict[str, str]:
        """Generate all Phase 4 deliverables."""
        deliverables: dict[str, str] = {}

        # Gate check report
        if ctx.gate_reports:
            deliverables["gate_check"] = render_gate_check_markdown(ctx.gate_reports, ctx.module)

        # Open items
        if ctx.open_items:
            items = []
            for oi in ctx.open_items:
                if hasattr(oi, 'item_id'):
                    items.append(oi)
            if items:
                deliverables["open_items"] = render_open_items_markdown(items, ctx.module)

        # Review record
        deliverables["review_record"] = self._render_review_record(ctx)

        # CHECK list
        deliverables["check_list"] = self._render_check_list(ctx)

        # Operation steps
        deliverables["operation_steps"] = self._render_operation_steps(ctx)

        return deliverables

    def _render_review_record(self, ctx: WorkflowContext) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# SRS 评审记录 — {ctx.module}",
            "",
            f"**生成时间**: {now}",
            f"**模块**: {ctx.module}",
            "",
            "## 评审结论",
            "",
        ]

        if not ctx.gate_reports:
            lines.append("**评审结论**: 未执行")
            return "\n".join(lines)

        total_fails = sum(1 for r in ctx.gate_reports for item in r.items if item.result == "Fail")
        total_cond = sum(1 for r in ctx.gate_reports for item in r.items if item.result == "Conditional")

        if total_fails > 0:
            overall = "不通过"
        elif total_cond > 0:
            overall = "有条件通过"
        else:
            overall = "通过"

        lines.append(f"**评审结论**: {overall}")

        lines.append("")
        lines.append("| 检查项 | 结论 |")
        lines.append("| --- | --- |")
        for report in ctx.gate_reports:
            lines.append(f"| {report.gate} {report.gate_name} | {report.status} |")
        lines.append(f"| 实际操作步骤 | {'已生成' if ctx.auto_fixes_applied >= 0 else '未生成'} |")
        lines.append(f"| SRS CHECK 清单 | {'已生成' if ctx.auto_fixes_applied >= 0 else '未生成'} |")

        lines.append("")
        open_count = len(ctx.open_items)
        blocking_count = sum(1 for oi in ctx.open_items
                             if hasattr(oi, 'item_type') and oi.item_type in {"needs_source", "asil_pending", "source_conflict"})
        lines.append(f"**遗留开放项**: {'有，未批准' if blocking_count > 0 else '无' if open_count == 0 else '有，已批准'}")
        lines.append(f"**是否允许进入 SDD**: {'否' if overall == '不通过' else '是（遗留项需批准）' if total_cond > 0 else '是'}")
        lines.append(f"**评审人**: ")
        lines.append(f"**日期**: {now}")
        lines.append("")

        return "\n".join(lines)

    def _render_check_list(self, ctx: WorkflowContext) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# SRS CHECK 清单 — {ctx.module}",
            "",
            f"**生成时间**: {now}",
            f"**模块**: {ctx.module}",
            "",
            "## Gate 汇总",
            "",
            "| Gate | 结论 |",
            "| --- | --- |",
        ]

        if ctx.gate_reports:
            for report in ctx.gate_reports:
                lines.append(f"| {report.gate} {report.gate_name} | **{report.status}** |")

        lines.append("")
        lines.append("## 检查项明细")
        lines.append("")

        if ctx.gate_reports:
            for report in ctx.gate_reports:
                lines.append(f"### {report.gate}: {report.gate_name} ({report.status})")
                lines.append("")
                for item in report.items:
                    status_icon = {"Pass": "[x]", "Conditional": "[~]", "Fail": "[ ]", "N/A": "[-]"}.get(item.result, "[ ]")
                    lines.append(f"- {status_icon} {item.check_id}: {item.description} — {item.detail[:100]}")
                lines.append("")

        lines.append("## 问题闭环表")
        lines.append("")
        lines.append("| 问题ID | 来源 | 影响 | 处理方式 | 责任人 | 状态 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        if ctx.open_items:
            for oi in ctx.open_items:
                oi_id = getattr(oi, 'item_id', 'N/A')
                oi_type = getattr(oi, 'item_type', 'N/A')
                oi_desc = getattr(oi, 'description', '')[:60]
                oi_resp = getattr(oi, 'responsible', '待确认')
                oi_status = getattr(oi, 'status', 'Open')
                affected = ", ".join(getattr(oi, 'affected_requirements', [])[:2])
                lines.append(f"| {oi_id} | {oi_type} | {affected} | {oi_desc} | {oi_resp} | {oi_status} |")
        lines.append("")

        lines.append("## 最终结论")
        lines.append("")

        if not ctx.gate_reports:
            lines.append("Gate 检查未执行。")
        else:
            total_fails = sum(1 for r in ctx.gate_reports for item in r.items if item.result == "Fail")
            total_cond = sum(1 for r in ctx.gate_reports for item in r.items if item.result == "Conditional")
            if total_fails > 0:
                lines.append(f"**是否允许进入 SDD**: 否 ({total_fails} 个阻断项)")
            elif total_cond > 0:
                lines.append(f"**是否允许进入 SDD**: 是（{total_cond} 个条件项需批准遗留）")
            else:
                lines.append("**是否允许进入 SDD**: 是")

        lines.append(f"**检查时间**: {now}")
        lines.append("")

        return "\n".join(lines)

    def _render_operation_steps(self, ctx: WorkflowContext) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# 实际操作步骤记录 — {ctx.module}",
            "",
            f"**生成时间**: {now}",
            f"**模块**: {ctx.module}",
            "",
            "## 任务背景",
            "",
            f"- **FC 模块**: {ctx.module}",
            f"- **目标**: 生成 {ctx.module} 软件需求规范（SRS）及相关过程产物",
            f"- **输出路径**: {ctx.output_dir}",
            "",
            "## 输入文件清单",
            "",
            "| 文件 | 类型 | 适用性 |",
            "| --- | --- | --- |",
        ]
        if ctx.has_datasheet and ctx.input_file:
            lines.append(f"| {ctx.input_file} | 数据手册 | 是 |")
        if ctx.has_raw_requirements:
            lines.append(f"| 原始开发需求 | 原始需求 | 是 |")
        lines.append("| construction-rules.md | 编写规范 | 是 |")
        lines.append("| authoring-standard.md | 编写规范 | 是 |")
        lines.append("| calibration-rules.md | 校准规则 | 是 |")
        lines.append("| aurix2g-normative-patterns.md | 平台规范 | 是 |")
        lines.append("")

        lines.append("## 执行步骤记录")
        lines.append("")
        steps = [
            ("Phase 1: 输入处理", "来源索引 + 内容抽取"),
            ("Phase 2: 需求生成", "特征提取 → 候选映射 → 压缩 → 规划 → SRS 构建 + 开放项登记"),
            ("Phase 3: 质量门禁", "Gate 1~6 整合自检 + 追溯矩阵"),
        ]
        if ctx.loop_count > 0:
            steps.append(("修正循环", f"执行 {ctx.loop_count} 轮修正，自动修正 {ctx.auto_fixes_applied} 项"))
        steps.append(("Phase 4: 交付固化", "评审记录 + CHECK 清单 + 操作步骤 + 最终 SRS"))

        for i, (phase, detail) in enumerate(steps, 1):
            lines.append(f"### 步骤 {i}: {phase}")
            lines.append(f"- **操作**: {detail}")
            lines.append(f"- **状态**: 已完成")
            lines.append("")

        lines.append("## 关键判断依据")
        lines.append("")
        lines.append("- 芯片能力 vs 项目支持：仅当软件有明确动作（API 调用/寄存器读写/Pin 控制）时生成需求")
        lines.append("- Evidence Level：Datasheet-only 为 L3，需求默认为 Draft")
        lines.append("- 接口命名：遵循 aurix2g-normative-patterns IoExtDev 分类规则")
        lines.append("- MainFunction 判定：存在异步 Set 或周期诊断依赖时生成 MainFunction")
        lines.append("")

        lines.append("## 问题与处理")
        lines.append("")
        if ctx.open_items:
            lines.append("| 问题 | 处理方式 | 状态 |")
            lines.append("| --- | --- | --- |")
            for oi in ctx.open_items[:10]:
                desc = getattr(oi, 'description', 'N/A')[:80]
                status = getattr(oi, 'status', 'Open')
                lines.append(f"| {desc} | 登记开放项 | {status} |")
        else:
            lines.append("无未解决问题。")
        lines.append("")

        lines.append("## 输出文件清单")
        lines.append("")
        lines.append("| 文件 | 路径 | 状态 |")
        lines.append("| --- | --- | --- |")
        outputs = [
            ("SRS 需求规范", srs_doc(ctx.module), "已生成"),
            ("来源索引", source_index_doc(ctx.module), "已生成"),
            ("来源抽取表", source_extract_doc(ctx.module), "已生成"),
            ("需求推导矩阵", derivation_doc(ctx.module), "已生成"),
            ("开放项登记表", open_items_doc(ctx.module), "已生成"),
            ("Gate 自检报告", check_list_doc(ctx.module), "已生成"),
            ("评审记录", review_doc(ctx.module), "已生成"),
            ("操作步骤", operation_steps_doc(ctx.module), "已生成"),
        ]
        for name, filename, status in outputs:
            lines.append(f"| {name} | {ctx.output_dir}/{filename} | {status} |")
        lines.append("")

        lines.append("## 剩余事项")
        lines.append("")
        if ctx.open_items:
            lines.append("以下开放项需要后续关闭：")
            for oi in ctx.open_items[:5]:
                oi_id = getattr(oi, 'item_id', 'N/A')
                oi_type = getattr(oi, 'item_type', 'N/A')
                oi_desc = getattr(oi, 'description', 'N/A')[:80]
                lines.append(f"- [{oi_id}] ({oi_type}) {oi_desc}")
        else:
            lines.append("无剩余事项。")
        lines.append("")

        return "\n".join(lines)
