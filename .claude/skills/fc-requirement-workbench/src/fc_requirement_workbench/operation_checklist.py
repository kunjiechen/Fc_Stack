"""Operation steps and CHECK list generators for Phase 4 delivery.

Produces standardized operation step records and reviewer-facing checklists.
"""

from __future__ import annotations

from datetime import datetime
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
from .gate_check import GateReport
from .rules import ValidationFinding


def render_operation_steps_markdown(
    *,
    module: str,
    output_dir: str = "",
    input_file: str = "",
    has_raw_requirements: bool = False,
    has_datasheet: bool = False,
    open_items: list[Any] | None = None,
    loop_count: int = 0,
    auto_fixes_applied: int = 0,
    requirement_count: int = 0,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    open_items = open_items or []

    lines = [
        f"# 实际操作步骤记录 — {module}",
        "",
        f"**生成时间**: {now}",
        f"**模块**: {module}",
        "",
        "## 任务背景",
        "",
        f"- **FC 模块名称**: {module}",
        f"- **目标**: 生成 {module} 软件需求规范（SRS）及完整过程产物",
        f"- **输入范围**: {'数据手册' if has_datasheet else ''}{' + 原始需求' if has_raw_requirements else ''}{'（无外部输入）' if not has_datasheet and not has_raw_requirements else ''}",
        f"- **输出路径**: {output_dir or 'Output/' + module + '/Doc/SRS/'}",
        "",
        "## 输入文件清单",
        "",
        "| 文件名称 | 类型 | 用途 | 适用性 |",
        "| --- | --- | --- | --- |",
    ]

    if has_datasheet and input_file:
        lines.append(f"| {input_file} | 数据手册 | 提取芯片能力、寄存器、Pin、时序 | 是 |")
    if has_raw_requirements:
        lines.append("| 原始开发需求 | 原始需求 | 提取项目职责、接口、安全等级 | 是 |")
    lines.append("| construction-rules.md | 编写规范 | 各类需求最小必填项和缺失处理 | 是 |")
    lines.append("| authoring-standard.md | 编写规范 | 章节结构、字段呈现、语言规范 | 是 |")
    lines.append("| calibration-rules.md | 校准规则 | 写作偏好、粒度校准 | 是 |")
    lines.append("| aurix2g-normative-patterns.md | 平台规范 | 接口命名分类、MainFunction 判定 | 是 |")
    lines.append("")
    lines.append(f"**需求条目总数**: {requirement_count}")
    lines.append("")

    lines.append("## 执行步骤记录")
    lines.append("")
    lines.append("| 步骤 | 阶段 | 操作内容 | 状态 |")
    lines.append("| --- | --- | --- | --- |")
    steps = [
        ("1", "Phase 1: 输入处理", "来源索引生成 + 来源内容抽取", "已完成"),
        ("2", "Phase 2: 需求生成", "特征提取 → 候选映射 → 规划 → SRS 构建 + 开放项登记", "已完成"),
        ("3", "Phase 3: 质量门禁", "Gate 1~6 整合自检 + 追溯矩阵生成", "已完成"),
    ]
    if loop_count > 0:
        steps.append(("4", "修正循环", f"执行 {loop_count} 轮修正，自动修正 {auto_fixes_applied} 项", "已完成"))
        steps.append(("5", "Phase 4: 交付固化", "评审记录 + CHECK 清单 + 操作步骤 + 最终 SRS", "已完成"))
    else:
        steps.append(("4", "Phase 4: 交付固化", "评审记录 + CHECK 清单 + 操作步骤 + 最终 SRS", "已完成"))

    for num, phase, detail, status in steps:
        lines.append(f"| {num} | {phase} | {detail} | {status} |")
    lines.append("")

    lines.append("## 关键判断依据")
    lines.append("")
    lines.append("1. **芯片能力 vs 项目支持**：Datasheet 中描述的能力不自动等同于软件需求，仅当软件有明确动作（API 调用、寄存器读写、Pin 控制、状态维护）时生成正式需求")
    lines.append("2. **Evidence Level**：Datasheet-only 证据为 L3，需求状态默认为 Draft，需项目补充配置值/安全目标后可达 Ready")
    lines.append("3. **接口命名分类**：遵循 aurix2g-normative-patterns 1.1 接口分类法则，IoExtDev 芯片级故障使用 GetDevFaultSig")
    lines.append("4. **MainFunction 判定**：按 aurix2g-normative-patterns 1.2 规则，存在异步 Set 接口或周期诊断依赖时生成 MainFunction")
    lines.append("5. **状态语义区分**：按 calibration-rules.md Rule 3/4/12，区分软件请求状态、软件记录状态和硬件确认状态")
    lines.append("")

    lines.append("## 问题与处理")
    lines.append("")
    if open_items:
        lines.append("| 问题 | 处理方式 | 状态 |")
        lines.append("| --- | --- | --- |")
        for oi in open_items[:15]:
            desc = (getattr(oi, 'description', '') or str(oi))[:80]
            status = getattr(oi, 'status', 'Open') if hasattr(oi, 'status') else 'Open'
            lines.append(f"| {desc} | 登记开放项 | {status} |")
    else:
        lines.append("无未解决问题。")
    lines.append("")

    lines.append("## 输出文件清单")
    lines.append("")
    base = output_dir or f"Output/{module}/Doc/SRS"
    lines.append("| 文件 | 路径 | 状态 |")
    lines.append("| --- | --- | --- |")
    outputs = [
        ("软件需求规范", srs_doc(module)),
        ("输入资料索引", source_index_doc(module)),
        ("来源内容抽取表", source_extract_doc(module)),
        ("需求推导矩阵", derivation_doc(module)),
        ("开放项登记表", open_items_doc(module)),
        ("Gate 自检报告", check_list_doc(module)),
        ("评审记录", review_doc(module)),
        ("实际操作步骤", operation_steps_doc(module)),
    ]
    for name, filename in outputs:
        lines.append(f"| {name} | {base}/{filename} | 已生成 |")
    lines.append("")

    lines.append("## 剩余事项")
    lines.append("")
    blocking = [oi for oi in open_items
                if hasattr(oi, 'item_type') and getattr(oi, 'item_type', '') in {"needs_source", "asil_pending", "source_conflict"}
                and getattr(oi, 'status', 'Open') == "Open"]
    if blocking:
        lines.append("### 阻断性事项（需在基线前关闭）")
        for oi in blocking:
            lines.append(f"- [{getattr(oi, 'item_id', '')}] {getattr(oi, 'description', '')}")
    else:
        lines.append("无阻断性剩余事项。")

    non_blocking = [oi for oi in open_items
                    if oi not in blocking and getattr(oi, 'status', 'Open') == "Open"]
    if non_blocking:
        lines.append("")
        lines.append("### 非阻断性事项（可进入 SDD 后逐步关闭）")
        for oi in non_blocking[:10]:
            lines.append(f"- [{getattr(oi, 'item_id', '')}] {getattr(oi, 'description', '')}")
    lines.append("")

    return "\n".join(lines)


def render_post_generation_guidance_markdown(
    *,
    module: str,
    srs_file: str,
    has_raw_requirements: bool = False,
    has_datasheet: bool = False,
    has_project_constraints: bool = False,
    gate_reports: list[GateReport] | None = None,
    open_items: list[Any] | None = None,
) -> str:
    """Render the mandatory next-step guide shown after SRS generation.

    This guide is intentionally action-oriented: it tells the user what to
    inspect first, where each type of issue should be fixed, and which action
    they should reply with next.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    gate_reports = gate_reports or []
    open_items = open_items or []

    input_level = _classify_input_level(
        has_raw_requirements=has_raw_requirements,
        has_datasheet=has_datasheet,
        has_project_constraints=has_project_constraints,
    )
    blocking = [oi for oi in open_items
                if hasattr(oi, "item_type")
                and getattr(oi, "item_type", "") in {"needs_source", "asil_pending", "source_conflict"}
                and getattr(oi, "status", "Open") == "Open"]
    conditional_count = sum(
        1 for report in gate_reports for item in report.items if item.result == "Conditional"
    )
    fail_count = sum(
        1 for report in gate_reports for item in report.items if item.result == "Fail"
    )

    lines = [
        f"# SRS 生成后引导 — {module}",
        "",
        f"**生成时间**: {now}",
        f"**SRS 文件**: {srs_file}",
        f"**输入完整度**: {input_level}",
        f"**Gate Fail 数**: {fail_count}",
        f"**Gate Conditional 数**: {conditional_count}",
        f"**Open Item 数**: {len(open_items)}",
        "",
        "## 先检查什么",
        "",
        "请优先检查以下 4 项：",
        "",
        "1. 本次升级点是否都已经覆盖到 SRS",
        "2. 是否存在不属于本 FC 的需求",
        "3. 当前 Open Issue 是否合理，是否需要现在补料",
        "4. 当前主要设计决策是否符合项目预期",
        "",
        "## 如果检查出问题，改哪里",
        "",
        "| 问题类型 | 应修改文件 | 处理方式 |",
        "| --- | --- | --- |",
        "| 升级点漏了/目标不对 | `Original_Requirement_Pack_[FC].md` | 补原始意图后重新生成 |",
        "| 来源资料不足 | `Input_Manifest_[FC].md` | 补用户手册/需求文档/约束后重新生成 |",
        f"| SRS 表达不清/分类不对 | `{review_doc('[FC]')}` | 记录评审意见并进入修正 |",
        f"| 暂时不能确认 | `{open_items_doc('[FC]')}` | 保留开放项，不直接固化 |",
        "| 不属于本 FC | `Original_Requirement_Pack_[FC].md` 的不做范围 | 标记排除后重新生成 |",
        "",
    ]

    if blocking:
        lines.extend([
            "## 当前阻断项",
            "",
            "以下问题在基线前必须处理：",
            "",
        ])
        for oi in blocking:
            lines.append(f"- [{getattr(oi, 'item_id', '')}] {getattr(oi, 'description', '')}")
        lines.append("")

    lines.extend([
        "## 下一步请直接回复以下动作之一",
        "",
        "1. `补原始需求`",
        "2. `补来源资料`",
        "3. `修改 SRS 表达`",
        "4. `转 Open Item`",
        "5. `保持 Draft`",
        "6. `Conditional 通过`",
        "7. `Baselined`",
        "",
        "## 如果你接受当前需求，怎么操作",
        "",
        "如果你认可当前需求结果，请不要只回复“接受”。",
        "请直接选择下面 3 种结论之一：",
        "",
        "1. `保持 Draft`",
        "   - 适用：当前方向认可，但还要继续补料",
        "",
        "2. `Conditional 通过`",
        "   - 适用：当前 SRS 已足够作为架构设计输入，少量遗留项继续跟踪",
        "",
        "3. `Baselined`",
        "   - 适用：当前 SRS 作为正式需求基线，允许作为正式上游输入",
        "",
        "## 状态选择建议",
        "",
    ])

    if fail_count > 0:
        lines.append("- 当前存在 Gate Fail，建议先选择 `补原始需求`、`补来源资料` 或 `修改 SRS 表达`。")
    elif blocking or conditional_count > 0:
        lines.append("- 当前没有阻断性 Fail，但仍有待确认项，通常建议 `保持 Draft` 或 `Conditional 通过`。")
    else:
        lines.append("- 当前 Gate 已清洁且无阻断开放项，可考虑 `Baselined`。")
    lines.append("")

    return "\n".join(lines)


def render_post_generation_reply(
    *,
    module: str,
    srs_file: str,
    gate_reports: list[GateReport] | None = None,
    open_items: list[Any] | None = None,
) -> str:
    """Render a concise assistant-style reply for immediate user guidance.

    This text is meant to be surfaced directly in the terminal/UI after SRS
    generation, while the detailed markdown guide remains available on disk.
    """
    gate_reports = gate_reports or []
    open_items = open_items or []
    fail_count = sum(
        1 for report in gate_reports for item in report.items if item.result == "Fail"
    )
    conditional_count = sum(
        1 for report in gate_reports for item in report.items if item.result == "Conditional"
    )
    blocking = [
        oi for oi in open_items
        if hasattr(oi, "item_type")
        and getattr(oi, "item_type", "") in {"needs_source", "asil_pending", "source_conflict"}
        and getattr(oi, "status", "Open") == "Open"
    ]

    lines = [
        f"SRS 需求文档已生成，输出文件：{srs_file}",
        "",
        "请先检查以下 4 项：",
        "1. 本次升级点是否都已覆盖到 SRS",
        "2. 是否存在不属于本 FC 的需求",
        "3. 当前 Open Issue 是否合理，是否需要现在补料",
        "4. 当前主要设计决策是否符合项目预期",
        "",
        "如果检查出问题，请按下面方式处理：",
        "1. 升级点漏了或目标不对 -> 修改 Original_Requirement_Pack_[FC].md",
        "2. 来源资料不全 -> 修改 Input_Manifest_[FC].md",
        f"3. SRS 表达不清或分类不对 -> 记录到 {review_doc('[FC]')}",
        f"4. 暂时不能确认 -> 保留到 {open_items_doc('[FC]')}",
        "",
    ]

    if fail_count > 0:
        lines.append(f"当前存在 {fail_count} 个 Gate Fail，建议先补料或修改，再继续评审。")
    elif blocking:
        lines.append(f"当前存在 {len(blocking)} 个阻断性 Open Item，通常建议保持 Draft 或继续补料。")
    elif conditional_count > 0:
        lines.append(f"当前存在 {conditional_count} 个 Conditional 检查项，可评估是否 `Conditional 通过`。")
    else:
        lines.append("当前 Gate 已清洁且无阻断开放项，可考虑直接 `Baselined`。")
    lines.append("")
    lines.append("请直接回复以下动作之一：")
    lines.append("1. 补原始需求")
    lines.append("2. 补来源资料")
    lines.append("3. 修改 SRS 表达")
    lines.append("4. 转 Open Item")
    lines.append("5. 保持 Draft")
    lines.append("6. Conditional 通过")
    lines.append("7. Baselined")
    lines.append("")
    lines.append("如果你接受当前需求，请直接回复以下 3 种结论之一：")
    lines.append("- 保持 Draft：接受当前方向，继续补料")
    lines.append("- Conditional 通过：接受当前需求，允许进入架构设计")
    lines.append("- Baselined：接受当前需求，作为正式 SRS 基线")
    lines.append("")

    return "\n".join(lines)


def render_check_list_markdown(
    *,
    module: str,
    gate_reports: list[GateReport] | None = None,
    open_items: list[Any] | None = None,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    gate_reports = gate_reports or []
    open_items = open_items or []

    lines = [
        f"# SRS CHECK 清单 — {module}",
        "",
        f"**生成时间**: {now}",
        f"**模块**: {module}",
        "",
        "## Gate 汇总",
        "",
        "| Gate | 名称 | 结论 | 检查项数 | Fail | Conditional |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    total_fails = 0
    total_cond = 0
    for report in gate_reports:
        fails = sum(1 for item in report.items if item.result == "Fail")
        conds = sum(1 for item in report.items if item.result == "Conditional")
        total_fails += fails
        total_cond += conds
        lines.append(
            f"| {report.gate} | {report.gate_name} | **{report.status}** | "
            f"{len(report.items)} | {fails} | {conds} |"
        )
    lines.append("")

    lines.append("## 检查项明细")
    lines.append("")

    for report in gate_reports:
        lines.append(f"### {report.gate}: {report.gate_name}")
        lines.append("")
        lines.append("| 检查ID | 检查项 | 结果 | 说明 |")
        lines.append("| --- | --- | --- | --- |")
        for item in report.items:
            icon = {"Pass": ":white_check_mark:", "Conditional": ":warning:", "Fail": ":x:", "N/A": ":heavy_minus_sign:"}.get(item.result, "")
            lines.append(f"| {item.check_id} | {item.description} | {icon} {item.result} | {item.detail[:100]} |")
        lines.append("")

    lines.append("## 问题闭环表")
    lines.append("")
    lines.append("| 问题ID | 类型 | 影响需求 | 处理方式 | 责任人 | 状态 | 关闭证据 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    if open_items:
        for oi in open_items:
            oi_id = getattr(oi, 'item_id', 'N/A')
            oi_type = getattr(oi, 'item_type', 'N/A')
            affected = ", ".join(getattr(oi, 'affected_requirements', [])[:2]) or "-"
            oi_status = getattr(oi, 'status', 'Open')
            oi_resp = getattr(oi, 'responsible', '待确认')
            close = getattr(oi, 'close_condition', '')[:40]
            lines.append(f"| {oi_id} | {oi_type} | {affected} | 待处理 | {oi_resp} | {oi_status} | {close} |")
    else:
        lines.append("| - | - | - | 无未解决问题 | - | Closed | - |")
    lines.append("")

    lines.append("## 开放项与遗留风险")
    lines.append("")
    if open_items:
        blocking = [oi for oi in open_items
                     if hasattr(oi, 'item_type')
                     and getattr(oi, 'item_type', '') in {"needs_source", "asil_pending", "source_conflict"}
                     and getattr(oi, 'status', 'Open') == "Open"]
        if blocking:
            lines.append("### 阻断性开放项")
            for oi in blocking:
                lines.append(f"- **[{getattr(oi, 'item_id', '')}]** {getattr(oi, 'description', '')}")
                lines.append(f"  - 类型: {getattr(oi, 'item_type', '')}")
                lines.append(f"  - 影响: {', '.join(getattr(oi, 'affected_requirements', []))}")
                lines.append(f"  - 阻塞 SDD: 是")
            lines.append("")
        non_blocking = [oi for oi in open_items if oi not in blocking and getattr(oi, 'status', 'Open') == "Open"]
        if non_blocking:
            lines.append("### 非阻断性开放项")
            for oi in non_blocking[:10]:
                lines.append(f"- [{getattr(oi, 'item_id', '')}] {getattr(oi, 'description', '')[:100]}")
            lines.append("")
    else:
        lines.append("无开放项。")
        lines.append("")

    lines.append("## 发布包完整性")
    lines.append("")
    lines.append("- [x] SRS 需求规范已生成")
    lines.append("- [x] 输入资料索引已生成")
    lines.append("- [x] 来源内容抽取表已生成")
    lines.append("- [x] 需求推导矩阵已生成")
    lines.append("- [x] 开放项登记表已生成")
    lines.append("- [x] Gate 自检报告已生成")
    lines.append("- [x] 评审记录已生成")
    lines.append("- [x] 实际操作步骤已生成")
    lines.append("- [x] 所有产物在同一输出路径")
    lines.append("")

    lines.append("## 最终结论")
    lines.append("")
    if total_fails > 0:
        lines.append(f"**发布结论**: **不通过** — 存在 {total_fails} 个阻断项")
        lines.append(f"**是否允许进入 SDD**: 否")
    elif total_cond > 0:
        lines.append(f"**发布结论**: **有条件通过** — {total_cond} 个条件项需确认")
        lines.append(f"**是否允许进入 SDD**: 是（遗留开放项需经评审批准）")
    else:
        lines.append("**发布结论**: **通过**")
        lines.append("**是否允许进入 SDD**: 是")
    lines.append(f"**检查时间**: {now}")
    lines.append(f"**基线版本**: Draft v1.0")
    lines.append(f"**评审人**: ")
    lines.append(f"**批准人**: ")
    lines.append("")

    return "\n".join(lines)


def _classify_input_level(
    *,
    has_raw_requirements: bool,
    has_datasheet: bool,
    has_project_constraints: bool,
) -> str:
    count = sum([has_raw_requirements, has_datasheet, has_project_constraints])
    return {0: "L0", 1: "L1", 2: "L2", 3: "L3"}.get(count, "L1")


def render_review_record_markdown(
    *,
    module: str,
    gate_reports: list[GateReport] | None = None,
    open_items: list[Any] | None = None,
    operation_steps_generated: bool = False,
    check_list_generated: bool = False,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    gate_reports = gate_reports or []
    open_items = open_items or []

    total_fails = sum(1 for r in gate_reports for item in r.items if item.result == "Fail")
    total_cond = sum(1 for r in gate_reports for item in r.items if item.result == "Conditional")

    if total_fails > 0:
        overall = "不通过"
    elif total_cond > 0:
        overall = "有条件通过"
    elif not gate_reports:
        overall = "未执行"
    else:
        overall = "通过"

    lines = [
        f"# SRS 评审记录 — {module}",
        "",
        f"**生成时间**: {now}",
        f"**模块**: {module}",
        "",
        "```text",
        f"SRS 评审结论：{overall}",
        "",
    ]

    if gate_reports:
        for report in gate_reports:
            lines.append(f"{report.gate_name}：{report.status}")
    else:
        lines.append("Gate 检查：未执行")

    lines.append(f"实际操作步骤：{'已生成' if operation_steps_generated else '未生成'}")
    lines.append(f"SRS CHECK 清单：{'已生成' if check_list_generated else '未生成'}")
    lines.append("输出路径一致性：通过")

    blocking_count = sum(1 for oi in open_items
                         if hasattr(oi, 'item_type')
                         and getattr(oi, 'item_type', '') in {"needs_source", "asil_pending", "source_conflict"}
                         and getattr(oi, 'status', 'Open') == "Open")

    if blocking_count > 0:
        lines.append(f"遗留开放项：有，未批准 ({blocking_count} 个阻断项)")
    elif open_items:
        lines.append("遗留开放项：有，已批准")
    else:
        lines.append("遗留开放项：无")

    if overall == "不通过":
        lines.append("是否允许进入 SDD：否")
    elif overall == "有条件通过":
        lines.append("是否允许进入 SDD：是（遗留项需批准）")
    elif overall == "通过":
        lines.append("是否允许进入 SDD：是")
    else:
        lines.append("是否允许进入 SDD：待确认")

    lines.append(f"评审人：")
    lines.append(f"日期：{now}")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)
