"""Structured review guide builder for guided SRS review workflow.

Produces a phase-by-phase review prompt that the skill uses to guide the user
through: gate check review → requirement-by-requirement review → fix collection
→ re-run → final approval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .builder import EngineeringRequirement
from .gate_check import GateReport
from .status import compute_requirement_status, render_status_label


# ---------------------------------------------------------------------------
# Review section — groups requirements for phased review
# ---------------------------------------------------------------------------

@dataclass
class ReviewSection:
    category: str          # "功能需求", "接口需求", ...
    category_key: str      # "functional", "interface", ...
    heading: str           # "5.1 模式与功能需求", ...
    items: list[dict[str, Any]] = field(default_factory=list)
    open_count: int = 0
    ready_count: int = 0

    @property
    def total(self) -> int:
        return len(self.items)


# ---------------------------------------------------------------------------
# Overall review guide
# ---------------------------------------------------------------------------

@dataclass
class ReviewGuide:
    module: str
    round_number: int = 1
    generated_at: str = ""

    # Summary counts
    total_requirements: int = 0
    ready_count: int = 0
    open_issue_count: int = 0

    # Gate status
    gate_summary: dict[str, Any] = field(default_factory=dict)

    # Review sections (one per requirement category)
    sections: list[ReviewSection] = field(default_factory=list)

    # Items needing attention
    blocking_items: list[str] = field(default_factory=list)
    conditional_items: list[str] = field(default_factory=list)

    # Overall
    gate_overall: str = "pending"  # Pass / Conditional / Fail


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

_CATEGORY_MAP: dict[str, tuple[str, str, str]] = {
    "functional":    ("功能需求",   "functional",    "5.1 功能需求"),
    "interface":     ("接口需求",   "interface",     "5.2 接口需求"),
    "configuration": ("配置需求",   "configuration", "5.3 配置需求"),
    "diagnostic":    ("诊断需求",   "diagnostic",    "5.4 诊断需求"),
    "timing":        ("时序需求",   "timing",        "6.1 时序需求"),
    "safety":        ("安全需求",   "safety",        "6.2 安全需求"),
    "coding":        ("编码需求",   "coding",        "6.3 编码需求"),
    "resource":      ("资源需求",   "resource",      "6.4 资源需求"),
}


class ReviewGuideBuilder:
    """Build a structured review guide from engineering requirements and gate
    reports, designed for the skill to present to the user phase by phase."""

    def build(
        self,
        module: str,
        engineering: list[EngineeringRequirement],
        gate_reports: list[GateReport],
        round_number: int = 1,
    ) -> ReviewGuide:
        guide = ReviewGuide(
            module=module,
            round_number=round_number,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total_requirements=len(engineering),
        )

        # ---- Group requirements by type ----
        by_type: dict[str, list[EngineeringRequirement]] = {}
        for req in engineering:
            by_type.setdefault(req.requirement_type, []).append(req)

        for req_type, (cat_name, cat_key, heading) in _CATEGORY_MAP.items():
            reqs = by_type.get(req_type, [])
            if not reqs:
                continue
            section = ReviewSection(category=cat_name, category_key=cat_key, heading=heading)
            for req in reqs:
                status = _classify_status(req)
                section.items.append({
                    "id": req.requirement_id,
                    "title": req.title,
                    "description": req.description[:300],
                    "status": status,
                    "source": req.source,
                    "verification": req.verification,
                    "has_exception": bool(req.exception and req.exception.strip()),
                    "has_constraint": bool(req.constraint and req.constraint.strip()),
                    "needs_input": "需确认" in req.constraint
                                   or "待确认" in req.constraint
                                   or "待补充" in req.constraint
                                   or "需项目输入" in req.constraint,
                })
                if status == "Open Issue":
                    section.open_count += 1
                elif status == "Ready":
                    section.ready_count += 1
            guide.sections.append(section)

        # ---- Gate summary ----
        guide.gate_summary = _build_gate_summary(gate_reports)

        # ---- Overall gate verdict ----
        fails = sum(1 for r in gate_reports for i in r.items if i.result == "Fail")
        conds = sum(1 for r in gate_reports for i in r.items if i.result == "Conditional")
        if fails:
            guide.gate_overall = "Fail"
        elif conds:
            guide.gate_overall = "Conditional"
        else:
            guide.gate_overall = "Pass"

        # ---- Blocking & conditional items ----
        for r in gate_reports:
            for item in r.items:
                if item.result == "Fail":
                    guide.blocking_items.append(
                        f"[{r.gate}] {item.check_id}: {item.description} — {item.detail[:120]}"
                    )
                elif item.result == "Conditional":
                    guide.conditional_items.append(
                        f"[{r.gate}] {item.check_id}: {item.description} — {item.detail[:120]}"
                    )

        # ---- Counts ----
        guide.ready_count = sum(1 for req in engineering if _classify_status(req) == "Ready")
        guide.open_issue_count = sum(1 for req in engineering if _classify_status(req) == "Open Issue")

        return guide


def _classify_status(req: EngineeringRequirement) -> str:
    """Classify a requirement's review status using the shared status helper."""
    return render_status_label(compute_requirement_status(req))


def _build_gate_summary(reports: list[GateReport]) -> dict[str, Any]:
    gates = []
    for r in reports:
        gates.append({
            "gate": r.gate,
            "name": r.gate_name,
            "status": r.status,
            "fails": [
                {"check_id": i.check_id, "description": i.description, "detail": i.detail}
                for i in r.items if i.result == "Fail"
            ],
            "conditionals": [
                {"check_id": i.check_id, "description": i.description, "detail": i.detail}
                for i in r.items if i.result == "Conditional"
            ],
        })
    return {
        "total": len(reports),
        "passed": sum(1 for r in reports if r.status == "Pass"),
        "conditional": sum(1 for r in reports if r.status == "Conditional"),
        "failed": sum(1 for r in reports if r.status == "Fail"),
        "gates": gates,
    }


# ---------------------------------------------------------------------------
# Markdown renderer — produces the review "script" shown to the user
# ---------------------------------------------------------------------------

def render_review_guide_markdown(guide: ReviewGuide) -> str:
    """Render the review guide as a Markdown document the skill presents to the
    user for guided review."""

    lines = [
        f"# SRS 评审引导 — {guide.module}",
        "",
        f"**轮次**: Round {guide.round_number}  |  **生成时间**: {guide.generated_at}",
        "",
        "---",
        "",
        "## 评审总览",
        "",
        f"| 指标 | 数值 |",
        f"| --- | --- |",
        f"| 需求总数 | {guide.total_requirements} |",
        f"| Ready | {guide.ready_count} |",
        f"| Open Issue | {guide.open_issue_count} |",
        f"| Gate 结论 | **{guide.gate_overall}** |",
        "",
    ]

    # ---- Gate summary ----
    gs = guide.gate_summary
    lines.extend([
        "## Gate 自检结果",
        "",
        "| Gate | 名称 | 结论 | Fail | Conditional |",
        "| --- | --- | --- | --- | --- |",
    ])
    for g in gs.get("gates", []):
        lines.append(
            f"| {g['gate']} | {g['name']} | **{g['status']}** | "
            f"{len(g['fails'])} | {len(g['conditionals'])} |"
        )
    lines.append("")

    # ---- Blocking items ----
    if guide.blocking_items:
        lines.append("### 阻断项（必须处理）")
        for item in guide.blocking_items:
            lines.append(f"- [ ] {item}")
        lines.append("")

    # ---- Conditional items ----
    if guide.conditional_items:
        lines.append("### 条件项（需确认或补充）")
        for item in guide.conditional_items:
            lines.append(f"- [ ] {item}")
        lines.append("")

    # ---- Requirement review sections ----
    lines.append("---")
    lines.append("")
    lines.append("## 需求逐类评审")
    lines.append("")

    for section in guide.sections:
        lines.append(f"### {section.heading}（{section.total} 条）")
        lines.append("")
        lines.append(f"| 状态 | 数量 |")
        lines.append(f"| --- | --- |")
        lines.append(f"| Ready | {section.ready_count} |")
        lines.append(f"| Open Issue | {section.open_count} |")
        lines.append("")

        lines.append("| 需求ID | 需求名称 | 状态 | 缺项 |")
        lines.append("| --- | --- | --- | --- |")
        for item in section.items:
            needs = ""
            if item["needs_input"]:
                needs = "需补料"
            if not item["has_exception"] and item["status"] != "Ready":
                needs = (needs + " 缺异常处理").strip()
            lines.append(
                f"| {item['id']} | {item['title']} | **{item['status']}** | {needs} |"
            )
        lines.append("")

    # ---- Footer / next actions ----
    lines.extend([
        "---",
        "",
        "## 可执行动作",
        "",
        "在每轮评审中你可以:",
        "",
        "| 动作 | 说明 |",
        "| --- | --- |",
        "| **通过** | 标记当前阶段/需求为已评审，进入下一步 |",
        "| **修改** | 提供修改内容（改标题/描述/补充约束/指定接口名等） |",
        "| **补料** | 提供缺失的项目输入（默认方向表/I2C地址/API命名等） |",
        "| **跳过** | 标记为已知遗留，进入最终评审记录 |",
        "| **批准发布** | 所有阶段完成，生成最终评审记录并归档 |",
        "",
        f"**当前轮次**: Round {guide.round_number}",
        "",
        "## 下一步：评审与发布引导",
        "",
        "- 推荐评审方式 1：直接修改需求文档风险表中的`状态`和`备注`。",
        "- 推荐评审方式 2：在当前窗口回复，例如`R1、R3 已评审；R5 待修改，备注：接口名统一为 xxx`。",
        "- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。",
        "- 如果某项需要修改，可回复：`R5 待修改，备注：xxx`。",
        "- 修改完成后仍保持当前版本的`Draft`，直到所有真实风险项均为`已评审`后发布为`Released`。",
        "- 草稿评审发布不升级版本；只有正式需求文件基线发布时才升级到下一版本。",
        "",
    ])

    return "\n".join(lines)
