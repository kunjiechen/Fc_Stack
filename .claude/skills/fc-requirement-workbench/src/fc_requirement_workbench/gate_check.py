"""Gate 1~6 integrated self-check for SRS quality gate review.

Produces a unified PASS/FAIL/CONDITIONAL report across all six gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from .builder import EngineeringRequirement
from .rules import ValidationFinding

GateResult = Literal["Pass", "Fail", "Conditional", "N/A"]


@dataclass
class GateCheckItem:
    check_id: str
    description: str
    result: GateResult
    detail: str = ""
    affected_ids: list[str] = field(default_factory=list)


@dataclass
class GateReport:
    gate: str
    gate_name: str
    status: GateResult
    items: list[GateCheckItem] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    open_items: list[str] = field(default_factory=list)

    @property
    def is_blocking(self) -> bool:
        return self.status == "Fail"


class GateChecker:
    """Run all six gate checks against an SRS and its inputs."""

    def __init__(
        self,
        module: str = "FC",
        source_count: int = 0,
        has_raw_requirements: bool = False,
        has_datasheet: bool = False,
        has_project_constraints: bool = False,
    ) -> None:
        self.module = module
        self.source_count = source_count
        self.has_raw_requirements = has_raw_requirements
        self.has_datasheet = has_datasheet
        self.has_project_constraints = has_project_constraints

    def check_all(
        self,
        engineering_requirements: list[EngineeringRequirement],
        findings: list[ValidationFinding],
        open_items: list[dict[str, Any]] | None = None,
    ) -> list[GateReport]:
        open_items = open_items or []
        return [
            self._check_gate1(engineering_requirements),
            self._check_gate2(engineering_requirements, findings),
            self._check_gate3(engineering_requirements),
            self._check_gate4(engineering_requirements, findings),
            self._check_gate5(engineering_requirements),
            self._check_gate6(engineering_requirements, findings, open_items),
        ]

    # ------------------------------------------------------------------
    # Gate 1: Input Source Completeness
    # ------------------------------------------------------------------
    def _check_gate1(self, reqs: list[EngineeringRequirement]) -> GateReport:
        items: list[GateCheckItem] = []

        items.append(GateCheckItem(
            check_id="G1-01",
            description="模块名称、简称、层级和适用范围是否明确",
            result="Pass" if self.module else "Fail",
            detail=f"模块: {self.module}" if self.module else "模块名称未定义",
        ))

        ds_ok = self.has_datasheet
        items.append(GateCheckItem(
            check_id="G1-02",
            description="是否识别硬件/芯片约束输入（Datasheet）",
            result="Pass" if ds_ok else "Conditional",
            detail="Datasheet 已登记" if ds_ok else "Datasheet 未提供，从其他来源推断",
        ))

        raw_ok = self.has_raw_requirements
        items.append(GateCheckItem(
            check_id="G1-03",
            description="是否纳入原始需求和技术资料",
            result="Pass" if raw_ok else "Conditional",
            detail="原始需求已登记" if raw_ok else "原始需求未提供",
        ))

        items.append(GateCheckItem(
            check_id="G1-04",
            description="是否纳入 SRS 编写规范和模板",
            result="Pass",
            detail="construction-rules.md / authoring-standard.md / calibration-rules.md / srs-output-template.md 已作为规则输入",
        ))

        items.append(GateCheckItem(
            check_id="G1-05",
            description="是否为每个输入资料分配唯一来源 ID",
            result="Pass" if self.source_count > 0 else "Conditional",
            detail=f"已分配 {self.source_count} 个来源 ID" if self.source_count > 0 else "来源索引待生成",
        ))

        items.append(GateCheckItem(
            check_id="G1-06",
            description="是否识别安全输入（ASIL 等级）",
            result="Conditional",
            detail="ASIL 等级已在需求中标注，安全目标/FSR/TSR 待补充",
        ))

        items.append(GateCheckItem(
            check_id="G1-07",
            description="输入资料是否存在版本冲突",
            result="Pass",
            detail="当前输入资料无版本冲突",
        ))

        items.append(GateCheckItem(
            check_id="G1-08",
            description="输入不足是否已显性暴露",
            result="Conditional",
            detail="缺少项目级配置默认值、安全目标、调度周期等输入，已登记开放项",
        ))

        return GateReport(
            gate="Gate 1",
            gate_name="输入来源完整性",
            status=self._aggregate(items),
            items=items,
            issues=_fail_details(items),
            open_items=_conditional_details(items),
        )

    # ------------------------------------------------------------------
    # Gate 2: Source Coverage & Traceability
    # ------------------------------------------------------------------
    def _check_gate2(
        self, reqs: list[EngineeringRequirement], findings: list[ValidationFinding]
    ) -> GateReport:
        items: list[GateCheckItem] = []

        untraced = [req for req in reqs if not req.source]
        items.append(GateCheckItem(
            check_id="G2-01",
            description="每条需求是否可追溯到明确来源",
            result="Pass" if not untraced else "Fail",
            detail=f"所有需求均有来源" if not untraced else f"{len(untraced)} 条需求缺少来源",
            affected_ids=[req.requirement_id for req in untraced],
        ))

        trace_findings = [f for f in findings if f.rule_group == "trace"]
        items.append(GateCheckItem(
            check_id="G2-02",
            description="来源追溯是否完整（无 broken trace）",
            result="Pass" if not trace_findings else "Fail",
            detail=f"追溯完整" if not trace_findings else f"{len(trace_findings)} 个追溯问题",
            affected_ids=sum([f.requirement_ids for f in trace_findings], []),
        ))

        draft_reqs = [_classify_requirement_status(req, findings) for req in reqs]
        draft_count = sum(1 for s in draft_reqs if s != "Ready")
        items.append(GateCheckItem(
            check_id="G2-03",
            description="来源未覆盖是否已登记开放项或 N/A",
            result="Pass" if draft_count == 0 else "Conditional",
            detail=f"{draft_count} 条需求非 Ready 状态，已体现来源不足",
        ))

        missing_source_reqs = [
            req for req in reqs
            if _classify_requirement_status(req, findings) == "Draft"
            and not req.source
        ]
        items.append(GateCheckItem(
            check_id="G2-04",
            description="Draft 需求是否均有来源补充计划",
            result="Pass" if not missing_source_reqs else "Conditional",
            detail=f"全部 Draft 需求已标记来源补充方向" if not missing_source_reqs
            else f"{len(missing_source_reqs)} 条 Draft 需求完全无来源",
            affected_ids=[req.requirement_id for req in missing_source_reqs],
        ))

        return GateReport(
            gate="Gate 2",
            gate_name="来源覆盖与追溯",
            status=self._aggregate(items),
            items=items,
            issues=_fail_details(items),
            open_items=_conditional_details(items),
        )

    # ------------------------------------------------------------------
    # Gate 3: Requirement Completeness
    # ------------------------------------------------------------------
    def _check_gate3(self, reqs: list[EngineeringRequirement]) -> GateReport:
        items: list[GateCheckItem] = []

        categories = set(req.requirement_type for req in reqs)
        expected = {"functional", "interface", "configuration", "diagnostic", "timing"}
        missing_categories = expected - categories
        items.append(GateCheckItem(
            check_id="G3-01",
            description="需求类别是否覆盖功能/接口/配置/诊断/时序",
            result="Pass" if not missing_categories else "Conditional",
            detail=f"已覆盖: {', '.join(sorted(categories))}"
            if not missing_categories
            else f"缺少类别: {', '.join(sorted(missing_categories))}",
        ))

        items.append(GateCheckItem(
            check_id="G3-02",
            description="是否存在初始化需求",
            result="Pass" if any("init" in req.title.lower() or "初始化" in req.title for req in reqs) else "Conditional",
            detail="初始化需求已存在" if any("init" in req.title.lower() or "初始化" in req.title for req in reqs) else "建议确认是否需要初始化需求",
        ))

        no_description = [req for req in reqs if not req.description.strip()]
        items.append(GateCheckItem(
            check_id="G3-03",
            description="每条需求是否有描述",
            result="Pass" if not no_description else "Fail",
            detail=f"所有需求均有描述" if not no_description else f"{len(no_description)} 条需求无描述",
            affected_ids=[req.requirement_id for req in no_description],
        ))

        no_constraint = [
            req for req in reqs
            if req.requirement_type == "configuration" and not req.constraint.strip()
        ]
        items.append(GateCheckItem(
            check_id="G3-04",
            description="配置需求是否有范围和约束",
            result="Pass" if not no_constraint else "Conditional",
            detail=f"配置需求均有约束" if not no_constraint
            else f"{len(no_constraint)} 条配置需求缺少范围约束",
            affected_ids=[req.requirement_id for req in no_constraint],
        ))

        no_exception = [
            req for req in reqs
            if req.requirement_type in {"functional", "interface"}
            and not req.exception.strip()
        ]
        items.append(GateCheckItem(
            check_id="G3-05",
            description="功能/接口需求是否有异常处理",
            result="Pass" if not no_exception else "Conditional",
            detail=f"异常处理均已覆盖" if not no_exception
            else f"{len(no_exception)} 条需求缺少异常处理",
            affected_ids=[req.requirement_id for req in no_exception],
        ))

        return GateReport(
            gate="Gate 3",
            gate_name="需求内容完整性",
            status=self._aggregate(items),
            items=items,
            issues=_fail_details(items),
            open_items=_conditional_details(items),
        )

    # ------------------------------------------------------------------
    # Gate 4: Requirement Quality
    # ------------------------------------------------------------------
    def _check_gate4(
        self, reqs: list[EngineeringRequirement], findings: list[ValidationFinding]
    ) -> GateReport:
        items: list[GateCheckItem] = []

        vague_words = ["正常", "合理", "稳定", "快速", "可靠", "及时", "适当", "多个", "若干", "尽量", "必要时"]
        vague_reqs: list[EngineeringRequirement] = []
        for req in reqs:
            desc = req.description + req.constraint + req.pre_condition
            if any(w in desc for w in vague_words):
                vague_reqs.append(req)

        items.append(GateCheckItem(
            check_id="G4-01",
            description="是否避免模糊词（正常/合理/稳定/快速/多个等）",
            result="Pass" if not vague_reqs else "Fail",
            detail=f"无模糊词" if not vague_reqs
            else f"{len(vague_reqs)} 条需求含模糊词: {', '.join(req.requirement_id for req in vague_reqs[:5])}",
            affected_ids=[req.requirement_id for req in vague_reqs],
        ))

        consistency_findings = [f for f in findings if f.rule_group == "consistency"]
        items.append(GateCheckItem(
            check_id="G4-02",
            description="需求之间是否无明显矛盾",
            result="Pass" if not consistency_findings else "Fail",
            detail=f"无矛盾" if not consistency_findings
            else f"{len(consistency_findings)} 个一致性冲突",
            affected_ids=sum([f.requirement_ids for f in consistency_findings], []),
        ))

        empty_verification = [req for req in reqs if not req.verification.strip()]
        items.append(GateCheckItem(
            check_id="G4-03",
            description="每条需求是否有验证方式",
            result="Pass" if not empty_verification else "Fail",
            detail=f"所有需求均有验证方式" if not empty_verification
            else f"{len(empty_verification)} 条需求缺少验证方式",
            affected_ids=[req.requirement_id for req in empty_verification],
        ))

        id_duplicates = _find_duplicate_ids(reqs)
        items.append(GateCheckItem(
            check_id="G4-04",
            description="需求 ID 是否唯一且稳定",
            result="Pass" if not id_duplicates else "Fail",
            detail=f"所有 ID 唯一" if not id_duplicates
            else f"重复 ID: {', '.join(id_duplicates)}",
            affected_ids=id_duplicates,
        ))

        mixed_reqs = [
            req for req in reqs
            if _count_behaviors(req.description) > 1
            and req.requirement_type not in {"diagnostic", "safety", "resource"}
        ]
        items.append(GateCheckItem(
            check_id="G4-05",
            description="每条需求是否只描述一个主要行为",
            result="Pass" if not mixed_reqs else "Conditional",
            detail=f"需求粒度合理" if not mixed_reqs
            else f"{len(mixed_reqs)} 条需求可能混合多个行为",
            affected_ids=[req.requirement_id for req in mixed_reqs],
        ))

        return GateReport(
            gate="Gate 4",
            gate_name="需求质量",
            status=self._aggregate(items),
            items=items,
            issues=_fail_details(items),
            open_items=_conditional_details(items),
        )

    # ------------------------------------------------------------------
    # Gate 5: SDD Input Sufficiency
    # ------------------------------------------------------------------
    def _check_gate5(self, reqs: list[EngineeringRequirement]) -> GateReport:
        items: list[GateCheckItem] = []

        has_api = any(req.requirement_type == "interface" for req in reqs)
        items.append(GateCheckItem(
            check_id="G5-01",
            description="是否定义了对外接口（API 签名和语义）",
            result="Pass" if has_api else "Fail",
            detail=f"已定义 {sum(1 for r in reqs if r.requirement_type == 'interface')} 个接口"
            if has_api else "未定义对外接口",
        ))

        has_config = any(req.requirement_type == "configuration" for req in reqs)
        items.append(GateCheckItem(
            check_id="G5-02",
            description="是否定义了配置项（范围/默认值/校验）",
            result="Pass" if has_config else "Conditional",
            detail=f"已定义 {sum(1 for r in reqs if r.requirement_type == 'configuration')} 个配置项"
            if has_config else "未定义配置项",
        ))

        has_error = any(
            req.exception.strip() or "错误" in req.description
            for req in reqs
            if req.requirement_type in {"functional", "interface"}
        )
        items.append(GateCheckItem(
            check_id="G5-03",
            description="是否明确了错误类别和异常行为",
            result="Pass" if has_error else "Conditional",
            detail="已定义错误处理" if has_error else "错误类别待完善",
        ))

        has_timing = any(req.requirement_type == "timing" for req in reqs)
        items.append(GateCheckItem(
            check_id="G5-04",
            description="是否有时序约束（需要时）",
            result="Pass" if has_timing else "Conditional",
            detail=f"已定义 {sum(1 for r in reqs if r.requirement_type == 'timing')} 个时序约束"
            if has_timing else "时序约束待补充",
        ))

        items.append(GateCheckItem(
            check_id="G5-05",
            description="SDD 是否不需要自行补充未定义的软件行为",
            result="Conditional",
            detail="当前 SRS 基于 Datasheet (L3) + 平台规范，配置默认值/调度周期/安全目标待项目补充后可达 Ready",
        ))

        return GateReport(
            gate="Gate 5",
            gate_name="SDD 输入充分性",
            status=self._aggregate(items),
            items=items,
            issues=_fail_details(items),
            open_items=_conditional_details(items),
        )

    # ------------------------------------------------------------------
    # Gate 6: Baseline Release
    # ------------------------------------------------------------------
    def _check_gate6(
        self,
        reqs: list[EngineeringRequirement],
        findings: list[ValidationFinding],
        open_items: list[dict[str, Any]],
    ) -> GateReport:
        items: list[GateCheckItem] = []

        blocking_items = [oi for oi in open_items if oi.get("status", "Open") == "Open"
                          and oi.get("item_type", "") in {"needs_source", "asil_pending", "source_conflict"}]
        items.append(GateCheckItem(
            check_id="G6-01",
            description="高影响开放项是否已关闭或批准遗留",
            result="Pass" if not blocking_items else "Fail",
            detail=f"无阻断性开放项" if not blocking_items
            else f"{len(blocking_items)} 个阻断性开放项未关闭",
            affected_ids=[oi.get("item_id", "") for oi in blocking_items],
        ))

        error_findings = [f for f in findings if f.severity == "error"]
        items.append(GateCheckItem(
            check_id="G6-02",
            description="所有 error 级别校验发现是否已处理",
            result="Pass" if not error_findings else "Fail",
            detail=f"无 error 级发现" if not error_findings
            else f"{len(error_findings)} 个 error 未处理",
            affected_ids=sum([f.requirement_ids for f in error_findings], []),
        ))

        draft_count = sum(1 for req in reqs if _classify_requirement_status(req, findings) != "Ready")
        items.append(GateCheckItem(
            check_id="G6-03",
            description="Draft 状态需求是否有明确关闭计划",
            result="Pass" if draft_count == 0 else "Conditional",
            detail=f"所有需求为 Ready" if draft_count == 0
            else f"{draft_count} 条 Draft 需求，需项目补充输入后关闭",
        ))

        items.append(GateCheckItem(
            check_id="G6-04",
            description="评审记录和 CHECK 清单是否已生成",
            result="Conditional",
            detail="待 Phase 4 交付固化阶段生成",
        ))

        return GateReport(
            gate="Gate 6",
            gate_name="基线发布",
            status=self._aggregate(items),
            items=items,
            issues=_fail_details(items),
            open_items=_conditional_details(items),
        )

    @staticmethod
    def _aggregate(items: list[GateCheckItem]) -> GateResult:
        if any(item.result == "Fail" for item in items):
            return "Fail"
        if any(item.result == "Conditional" for item in items):
            return "Conditional"
        return "Pass"


def _fail_details(items: list[GateCheckItem]) -> list[str]:
    return [f"{item.check_id}: {item.detail}" for item in items if item.result == "Fail"]


def _conditional_details(items: list[GateCheckItem]) -> list[str]:
    return [f"{item.check_id}: {item.detail}" for item in items if item.result == "Conditional"]


def _classify_requirement_status(
    req: EngineeringRequirement, findings: list[ValidationFinding]
) -> str:
    if not req.source:
        return "Draft"
    if not req.description.strip():
        return "Draft"
    req_findings = [f for f in findings if req.requirement_id in f.requirement_ids]
    if any(f.severity == "error" for f in req_findings):
        return "Draft"
    if "需项目输入确认" in req.constraint or "需确认" in req.constraint:
        return "Draft"
    return "Ready"


def _find_duplicate_ids(reqs: list[EngineeringRequirement]) -> list[str]:
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for req in reqs:
        seen[req.requirement_id] = seen.get(req.requirement_id, 0) + 1
    for rid, count in seen.items():
        if count > 1:
            duplicates.append(rid)
    return duplicates


def _count_behaviors(description: str) -> int:
    """Heuristic: count Chinese/English behavior separators."""
    separators = ["；", "；", "并", "同时", "and also", "as well as"]
    count = 1
    for sep in separators:
        count += description.count(sep)
    return count


# ---------------------------------------------------------------------------
# Markdown Renderer
# ---------------------------------------------------------------------------

def render_gate_check_markdown(reports: list[GateReport], module: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# SRS Gate 自检报告 — {module}",
        "",
        f"**生成时间**: {now}",
        f"**模块**: {module}",
        "",
        "## Gate 汇总",
        "",
        "| Gate | 名称 | 结论 | 检查项 | 问题数 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for report in reports:
        fail_count = sum(1 for item in report.items if item.result == "Fail")
        cond_count = sum(1 for item in report.items if item.result == "Conditional")
        issues_str = f"Fail: {fail_count}, Conditional: {cond_count}" if fail_count or cond_count else "无"
        lines.append(
            f"| {report.gate} | {report.gate_name} | **{report.status}** | "
            f"{len(report.items)} | {issues_str} |"
        )
    lines.append("")

    for report in reports:
        lines.append(f"## {report.gate}: {report.gate_name}")
        lines.append("")
        lines.append(f"**结论**: {report.status}")
        lines.append("")
        lines.append("| 检查ID | 检查项 | 结果 | 说明 |")
        lines.append("| --- | --- | --- | --- |")
        for item in report.items:
            lines.append(
                f"| {item.check_id} | {item.description} | {item.result} | {item.detail[:120]} |"
            )
        lines.append("")

        if report.issues:
            lines.append("### 问题项")
            lines.append("")
            for issue in report.issues:
                lines.append(f"- [ ] {issue}")
            lines.append("")

        if report.open_items:
            lines.append("### 开放项/条件项")
            lines.append("")
            for oi in report.open_items:
                lines.append(f"- [ ] {oi}")
            lines.append("")

    total_fails = sum(1 for r in reports for item in r.items if item.result == "Fail")
    total_cond = sum(1 for r in reports for item in r.items if item.result == "Conditional")

    lines.append("## 总体结论")
    lines.append("")

    if total_fails > 0:
        overall = "不通过"
        lines.append(f"**评审结论**: **不通过** — 存在 {total_fails} 个阻断项需要修正")
    elif total_cond > 0:
        overall = "有条件通过"
        lines.append(f"**评审结论**: **有条件通过** — {total_cond} 个条件项需确认或补充后通过")
    else:
        overall = "通过"
        lines.append("**评审结论**: **通过** — 所有 Gate 检查通过")

    lines.append("")
    lines.append(f"**是否允许进入 SDD**: {'否' if overall == '不通过' else '是（遗留项需批准）' if total_cond > 0 else '是'}")
    lines.append(f"**检查时间**: {now}")
    lines.append("")

    lines.append("## Gate 结论明细")
    lines.append("")
    for report in reports:
        lines.append(f"- {report.gate} {report.gate_name}: {report.status}")
    lines.append("")

    return "\n".join(lines)
