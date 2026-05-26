"""Open Items Registry — cross-layer aggregation of unresolved items.

Collects open items from validation findings, engineering requirements,
and missing project inputs into a unified registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .builder import EngineeringRequirement
from .rules import ValidationFinding


@dataclass
class OpenItem:
    item_id: str
    item_type: str
    description: str
    affected_requirements: list[str] = field(default_factory=list)
    responsible: str = "待确认"
    close_condition: str = ""
    status: str = "Open"


OPEN_ITEM_TYPE_LABELS: dict[str, str] = {
    "needs_source": "需求无来源",
    "uncovered_source": "来源未覆盖",
    "ownership_unclear": "所有权不清",
    "asil_pending": "安全等级待确认",
    "config_pending": "配置值缺失",
    "source_conflict": "来源冲突",
    "boundary_unclear": "行为边界不清",
    "field_missing": "必需字段缺失",
    "verification_missing": "验证方式缺失",
    "vague_language": "模糊表述",
    "consistency_issue": "一致性问题",
    "dependency_incomplete": "依赖不完整",
    "naming_violation": "命名违规",
}


class OpenItemsCollector:
    """Aggregate open items from all pipeline layers."""

    def collect(
        self,
        engineering_requirements: list[EngineeringRequirement],
        findings: list[ValidationFinding],
        module: str = "FC",
    ) -> list[OpenItem]:
        items: list[OpenItem] = []
        counter = 1

        # 1. From validation findings
        for finding in findings:
            if finding.status != "failed":
                continue
            item_type = _finding_to_open_item_type(finding)
            items.append(OpenItem(
                item_id=f"OI-{module}-{counter:04d}",
                item_type=item_type,
                description=finding.message,
                affected_requirements=list(finding.requirement_ids),
                responsible=_suggest_responsible(item_type),
                close_condition=_suggest_close_condition(item_type, finding),
                status="Open",
            ))
            counter += 1

        # 2. From engineering requirements with unresolved fields
        for req in engineering_requirements:
            sub_items = _extract_requirement_open_items(req, module)
            for si in sub_items:
                si.item_id = f"OI-{module}-{counter:04d}"
                counter += 1
                items.append(si)

        # 3. From requirements without sources
        for req in engineering_requirements:
            if not req.source:
                items.append(OpenItem(
                    item_id=f"OI-{module}-{counter:04d}",
                    item_type="needs_source",
                    description=f"需求 {req.requirement_id} ({req.title}) 缺少来源",
                    affected_requirements=[req.requirement_id],
                    responsible="需求工程师",
                    close_condition=f"补充 Datasheet 或项目需求来源后关闭",
                    status="Open",
                ))
                counter += 1

        return items


def _finding_to_open_item_type(finding: ValidationFinding) -> str:
    group_map = {
        "completeness": "field_missing",
        "consistency": "consistency_issue",
        "constraint": "source_conflict",
        "ownership": "ownership_unclear",
        "dependency": "dependency_incomplete",
        "configuration": "config_pending",
        "naming": "naming_violation",
        "trace": "needs_source",
    }
    return group_map.get(finding.rule_group, "field_missing")


def _suggest_responsible(item_type: str) -> str:
    mapping = {
        "needs_source": "需求工程师",
        "uncovered_source": "需求工程师",
        "ownership_unclear": "系统工程师/架构师",
        "asil_pending": "功能安全工程师",
        "config_pending": "项目配置负责人",
        "source_conflict": "需求工程师/系统工程师",
        "boundary_unclear": "需求工程师/架构师",
        "field_missing": "需求工程师",
        "verification_missing": "测试工程师",
        "vague_language": "需求工程师",
        "consistency_issue": "需求工程师",
        "dependency_incomplete": "架构师",
        "naming_violation": "需求工程师",
    }
    return mapping.get(item_type, "需求工程师")


def _suggest_close_condition(item_type: str, finding: ValidationFinding) -> str:
    default = "需求经评审确认后关闭"
    specific: dict[str, str] = {
        "needs_source": "补充可追溯的来源证据",
        "ownership_unclear": "明确引脚/接口所有权归属",
        "config_pending": "提供项目级配置默认值和范围",
        "asil_pending": "安全分析确认 ASIL 等级",
        "source_conflict": "确认有效版本并消除冲突",
        "naming_violation": "按 aurix2g-normative-patterns 修正命名",
    }
    return specific.get(item_type, default)


def _extract_requirement_open_items(
    req: EngineeringRequirement, module: str
) -> list[OpenItem]:
    items: list[OpenItem] = []

    if not req.description.strip():
        items.append(OpenItem(
            item_id="",  # filled by caller
            item_type="field_missing",
            description=f"需求 {req.requirement_id} 缺少描述",
            affected_requirements=[req.requirement_id],
            responsible="需求工程师",
            close_condition="补充需求描述后关闭",
        ))

    if not req.verification.strip():
        items.append(OpenItem(
            item_id="",
            item_type="verification_missing",
            description=f"需求 {req.requirement_id} ({req.title}) 缺少验证方式",
            affected_requirements=[req.requirement_id],
            responsible="测试工程师",
            close_condition="补充验证方式后关闭",
        ))

    if "需项目输入确认" in req.constraint:
        items.append(OpenItem(
            item_id="",
            item_type="config_pending",
            description=f"需求 {req.requirement_id} ({req.title}) 配置值需项目输入确认",
            affected_requirements=[req.requirement_id],
            responsible="项目配置负责人",
            close_condition="提供项目级配置值后关闭",
        ))

    vague_words = ["正常", "合理", "稳定", "快速", "可靠", "及时", "适当", "多个", "若干", "尽量", "必要时"]
    found_vague = [w for w in vague_words if w in req.description]
    if found_vague:
        items.append(OpenItem(
            item_id="",
            item_type="vague_language",
            description=f"需求 {req.requirement_id} ({req.title}) 含模糊词: {', '.join(found_vague)}",
            affected_requirements=[req.requirement_id],
            responsible="需求工程师",
            close_condition="替换为可验证的量化表述后关闭",
        ))

    return items


# ---------------------------------------------------------------------------
# Markdown Renderer
# ---------------------------------------------------------------------------

def render_open_items_markdown(items: list[OpenItem], module: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 开放项登记表 — {module}",
        "",
        f"**生成时间**: {now}",
        f"**模块**: {module}",
        f"**开放项总数**: {len(items)}",
        "",
        "## 开放项明细",
        "",
        "| 开放项ID | 类型 | 问题描述 | 影响需求 | 责任方 | 关闭条件 | 状态 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for item in items:
        label = OPEN_ITEM_TYPE_LABELS.get(item.item_type, item.item_type)
        affected = ", ".join(item.affected_requirements[:3])
        if len(item.affected_requirements) > 3:
            affected += f" 等 {len(item.affected_requirements)} 条"
        lines.append(
            f"| {item.item_id} | {label} | {item.description[:80]} | "
            f"{affected} | {item.responsible} | {item.close_condition[:60]} | "
            f"{item.status} |"
        )

    lines.append("")

    # Summary by type
    type_counts: dict[str, int] = {}
    for item in items:
        label = OPEN_ITEM_TYPE_LABELS.get(item.item_type, item.item_type)
        type_counts[label] = type_counts.get(label, 0) + 1

    lines.append("## 类型分布")
    lines.append("")
    lines.append("| 类型 | 数量 |")
    lines.append("| --- | --- |")
    for label, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {label} | {count} |")
    lines.append("")

    blocking_types = {"需求无来源", "安全等级待确认", "来源冲突"}
    blocking_count = sum(c for t, c in type_counts.items() if t in blocking_types)

    lines.append("## 汇总")
    lines.append("")
    if blocking_count > 0:
        lines.append(f"**存在 {blocking_count} 个阻断性开放项**，需要在 SRS 基线前关闭或经评审批准遗留。")
    else:
        lines.append("无阻断性开放项。")
    lines.append(f"**非阻断性开放项**: {len(items) - blocking_count} 个，可进入 SDD 后逐步关闭。")
    lines.append("")

    return "\n".join(lines)
