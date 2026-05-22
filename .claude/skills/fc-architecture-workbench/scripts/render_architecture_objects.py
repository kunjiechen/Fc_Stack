from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _code(value: str) -> str:
    return f"`{value}`" if value else ""


def _join(items: list[str]) -> str:
    return "; ".join(item for item in items if item)


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    for sep in (". ", "。", "; ", "；"):
        if sep in text:
            return text.split(sep)[0].strip().rstrip(".")
    return text.strip()


def _summary_intro(module: str, payload: dict[str, Any]) -> tuple[str, str, str]:
    external_count = len(payload.get("external_apis", []))
    dependency_count = len(payload.get("dependency_apis", []))
    config_count = len(payload.get("config_macros", []))
    fc_intro = (
        f"{module} 是当前项目的 FC 模块架构对象集合，对外提供 {external_count} 个正式外部接口，"
        f"并通过 {dependency_count} 个依赖接口完成平台和外设适配。"
    )
    app = (
        f"适用于需要配置宏、运行态缓存、MemMap 分段和故障可读接口协同设计的嵌入式外设驱动场景。"
    )
    idea = (
        f"架构以外部接口、依赖接口、配置宏、运行态和文件载体分层组织，当前共收敛 {config_count} 个配置宏对象。"
    )
    return fc_intro, app, idea


def _status_label(status: str) -> str:
    return "草稿" if status == "Draft" else "发布"


def _created_time(payload: dict[str, Any]) -> str:
    return payload.get("generated_time") or datetime.now().strftime("%Y-%m-%d %H:%M")


def _doc_header(module: str, version: str, status: str, output_mode: str, created: str) -> list[str]:
    return [
        f"# 《{module} 软件架构设计》",
        "",
        f"**{module}_软件架构设计**",
        "",
        f"**{module} Software Architecture Design**",
        "",
        f"项目编号/Project number: {module}",
        "保密性/Security: 内部",
        "",
        "**Document Properties**",
        f"Status: **{_status_label(status)}**",
        f"架构版本: **{version}**",
        f"架构状态: **{status}**",
        f"输出模式: **{output_mode}**",
        "Author: FC Architecture Workbench",
        f"Created: {created}",
        "",
        "---",
        "",
    ]


def _render_coverage_table(items: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            f"| {_code(item.get('requirement_id', ''))} | {item.get('summary', '')} | "
            f"{_code(item.get('coverage_object', ''))} | {item.get('coverage_status', '')} | {item.get('notes', '')} |"
        )
    return lines


def _render_external_api_sections(items: list[dict[str, Any]], section_prefix: str) -> list[str]:
    lines: list[str] = []
    for idx, api in enumerate(items, start=1):
        lines.extend(
            [
                f"### {section_prefix}.{idx} `{api.get('name', '')}`",
                "",
                "| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |",
                "| --- | --- | --- | --- | --- | --- |",
                f"| `{api.get('prototype', '')}` | {api.get('description', '')} | {api.get('sync_mode', '')} | "
                f"{api.get('reentrancy', '')} | {api.get('return_value', '')} | {_join(api.get('constraints', []))} |",
                "",
            ]
        )
    return lines


def _render_dependency_sections(items: list[dict[str, Any]], section_prefix: str) -> list[str]:
    lines: list[str] = []
    for idx, api in enumerate(items, start=1):
        lines.extend(
            [
                f"### {section_prefix}.{idx} `{api.get('name', '')}`",
                "",
                "| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                f"| `{api.get('prototype', '')}` | {api.get('description', '')} | {api.get('sync_mode', '')} | "
                f"{api.get('reentrancy', '')} | {api.get('return_value', '')} | {_join(api.get('constraints', []))} | "
                f"{api.get('implemented_by', '')} | {_join(api.get('evidence', []))} | {api.get('status', '')} |",
                "",
            ]
        )
    return lines


def _render_file_items(items: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| File | Required/Optional | Responsibility | Key Content |",
        "| --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('required_level', '')} | {item.get('responsibility', '')} | {item.get('key_content', '')} |"
        )
    return lines


def _render_risk_table(items: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            f"| {item.get('index', '')} | {item.get('title', '')} | {item.get('risk', '')} | "
            f"{item.get('impact', '')} | {item.get('recommended_action', '')} | {item.get('remark', '')} | {item.get('status', '')} |"
        )
    return lines


def render_summary_markdown(payload: dict[str, Any]) -> str:
    module = payload["module"]
    version = payload["architecture_version"]
    status = payload["architecture_status"]
    output_mode = payload["output_mode"]
    layer = payload.get("layer", "")
    created = _created_time(payload)
    change_summary = payload.get("change_summary", [])
    fc_intro, app_scene, design_idea = _summary_intro(module, payload)

    lines = _doc_header(module, version, status, output_mode, created)
    lines.extend(
        [
            "## 1 FC总结介绍",
            "",
            f"- **架构版本**: {version}",
            f"- **架构状态**: {status}",
            f"- **输出模式**: {output_mode}",
            f"- **生成时间**: {created}",
            f"- **变更点总结**: {_join(change_summary) or '初版生成。'}",
            f"- **FC名称**: {_code(module)}",
            f"- **FC功能介绍**: {fc_intro}",
            f"- **应用场景**: {app_scene}",
            f"- **架构设计思路**: {design_idea}",
            "- **AUTOSAR架构层级**: BSW / FC",
            f"- **当前软件架构所处层级**: {_code(layer)}" if layer else "- **当前软件架构所处层级**: `N/A`",
            "",
            "---",
            "",
            "## 2 需求覆盖表",
            "",
        ]
    )
    lines.extend(_render_coverage_table(payload.get("requirement_coverage", [])))

    lines.extend(["", "---", "", "## 3 外部接口设计", ""])
    lines.extend(_render_external_api_sections(payload.get("external_apis", []), "3"))

    lines.extend(
        [
            "---",
            "",
            "## 4 配置宏参设计",
            "",
            "| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in payload.get("config_macros", []):
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('purpose', '')} | Macro | `{item.get('default_value', '')}` | "
            f"{_join(item.get('evidence', []))} | `{item.get('usage_location', '')}` | {item.get('status', '')} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 5 全局变量与运行态策略",
            "",
            "状态：`Empty`",
            "",
            "| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in payload.get("runtime_states", []):
        lines.append(
            f"| {item.get('name', '')} | {item.get('owner', '')} | {item.get('read_write_side', '')} | "
            f"{item.get('lifecycle', '')} | `{item.get('memory_section', '')}` | {item.get('concurrency_strategy', '')} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 6 内存分配宏定义",
            "",
            "| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in payload.get("memmap_sections", []):
        used_files = ", ".join(_code(name) for name in item.get("used_files", []))
        lines.append(
            f"| {item.get('name', '')} | {item.get('target_content', '')} | `{item.get('start_macro', '')}` | "
            f"`{item.get('stop_macro', '')}` | {used_files} | {item.get('notes', '')} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 7 全局标定参数设计",
            "",
            "| Parameter Name | Type | Initial Value | Description | Status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    calibration_items = payload.get("calibration_items", [])
    if calibration_items:
        for item in calibration_items:
            lines.append(
                f"| `{item.get('name', '')}` | `{item.get('type', '')}` | `{item.get('initial_value', '')}` | "
                f"{item.get('description', '')} | `{item.get('status', '')}` |"
            )
    else:
        lines.append("| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。 | `Empty` |")

    lines.extend(["", "---", "", "## 8 依赖接口设计", ""])
    lines.extend(_render_dependency_sections(payload.get("dependency_apis", []), "8"))

    lines.extend(
        [
            "---",
            "",
            "## 9 文件列表与文件关系",
            "",
            "### 9.1 文件列表",
            "",
        ]
    )
    lines.extend(_render_file_items(payload.get("file_items", [])))

    lines.extend(
        [
            "",
            "---",
            "",
            "## 10 架构风险与待确认",
            "",
        ]
    )
    lines.extend(_render_risk_table(payload.get("risk_items", [])))

    lines.extend(
        [
            "",
            "---",
            "",
            "## 附录：架构元信息",
            "",
            f"- **架构版本**: {version}",
            f"- **架构状态**: {status}",
            f"- **输出模式**: {output_mode}",
            f"- **生成时间**: {created}",
            f"- **生成/修订说明**: {_join(change_summary) or '初版生成。'}",
            "- **版本策略**: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。",
            "- **发布条件**: 所有真实风险项均为 `已评审`。",
            "",
        ]
    )

    if status == "Draft":
        lines.extend(
            [
                "---",
                "",
                "## 下一步：评审与发布引导",
                "",
                f"当前架构状态为 **{version} {status}**。请通过以下方式完成评审：",
                "",
                "- **推荐评审方式 1**：直接修改第 10 章风险表中的 `状态` 和 `备注` 列。",
                "- **推荐评审方式 2**：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：按 xxx 方案调整`。",
                "- 如果所有风险项均认可，可回复：**`全部已评审，R-OTHER 无其他建议，直接发布`**。",
                "- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_full_markdown(payload: dict[str, Any]) -> str:
    module = payload["module"]
    version = payload["architecture_version"]
    status = payload["architecture_status"]
    output_mode = payload["output_mode"]
    layer = payload.get("layer", "")
    created = _created_time(payload)
    change_summary = payload.get("change_summary", [])
    requirement_coverage = payload.get("requirement_coverage", [])
    external_apis = payload.get("external_apis", [])
    dependency_apis = payload.get("dependency_apis", [])
    config_macros = payload.get("config_macros", [])
    runtime_states = payload.get("runtime_states", [])
    memmap_sections = payload.get("memmap_sections", [])
    file_items = payload.get("file_items", [])
    risk_items = payload.get("risk_items", [])

    lines = _doc_header(module, version, status, output_mode, created)
    lines.extend(
        [
            "## 文档元信息",
            "",
            f"- 架构版本: `{version}`",
            f"- 架构状态: `{status}`",
            f"- 输出模式: `{output_mode}`",
            f"- 生成时间: {created}",
            f"- 生成/修订说明: {_join(change_summary) or '初版生成。'}",
            f"- 变更点总结【简洁版】: {_join(change_summary) or '初版生成。'}",
            "",
            "## 0. 抽取与判定总览",
            "",
            "### 0.1 需求抽取与分类表",
            "",
            "| 需求条目 | 抽取点 | 是否外部接口 | 分类 | 暂定落点 | 判定依据 | 备注/待确认 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in requirement_coverage:
        coverage_object = item.get("coverage_object", "")
        is_external = "是" if any(api.get("name", "") in coverage_object for api in external_apis) else "否"
        category = "外部接口" if is_external == "是" else "配置/运行态/依赖"
        lines.append(
            f"| {_code(item.get('requirement_id', ''))} | {item.get('summary', '')} | {is_external} | {category} | "
            f"{_code(coverage_object)} | {item.get('coverage_status', '')} | {item.get('notes', '')} |"
        )

    lines.extend(
        [
            "",
            "### 0.2 外部接口候选清单",
            "",
            "| 候选接口 | 所属模块 | 来源需求 | 接口类型 | 输入参数 | 输出参数 | 置信度 | 是否保留 | 是否人工确认 | 保留原因/不保留原因 | 备注 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for api in external_apis:
        lines.append(
            f"| `{api.get('name', '')}` | `{module}` | {_join(api.get('evidence', []))} | 外部调用 | prototype defined | return value defined | 高 | 是 | 否 | formal external API | |"
        )

    lines.extend(
        [
            "",
            "### 0.3 配置宏参清单",
            "",
            "| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in config_macros:
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('purpose', '')} | {item.get('macro_type', '')} | `{item.get('default_value', '')}` | "
            f"{_join(item.get('evidence', []))} | `{item.get('usage_location', '')}` | {item.get('status', '')} |"
        )

    lines.extend(
        [
            "",
            "## 1. FC概述",
            f"- FC名称: `{module}`",
            f"- 核心职责: 对外提供 {len(external_apis)} 个正式外部接口，并通过 {len(dependency_apis)} 个依赖接口完成平台适配。",
            f"- 功能摘要: {_first_sentence(_summary_intro(module, payload)[0])}。",
            "- 运行模型: Init + MainFunction + synchronous/asynchronous semantic APIs.",
            f"- 目标场景: {_summary_intro(module, payload)[1]}",
            "",
            "## 2. 设计输入",
            "### 2.1 输入文档",
            f"- FC需求: `{module}.arch.json` / 需求覆盖对象集合",
            "",
            "### 2.2 场景约束",
            f"- 当前软件层级: `{layer or 'N/A'}`",
            "- 多核: 是",
            "- 多实例: 是",
            "- 其他约束: 依赖 I2C 外设寄存器通信和故障可读接口。",
            "",
            "## 3. 假设与缺失信息",
            "- 假设1: I2C 底层驱动和 DIO/OS 依赖由项目适配层提供。",
            "- 假设2: 多核调用遵循每核独立配置和运行态隔离。",
            "- 缺失信息1: 中断检测方式最终由项目确认。",
            "- 缺失信息2: RESET 引脚控制归属最终由项目确认。",
            "",
            "## 4. 需求到架构映射",
            "",
        ]
    )
    lines.extend(_render_coverage_table(requirement_coverage))
    lines.extend(
        [
            "",
            "### 4.1 接口覆盖率表",
            "",
            "| 需求ID | 功能描述 | 对应接口/配置/运行态 | 覆盖状态 | 备注 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in requirement_coverage:
        lines.append(
            f"| {_code(item.get('requirement_id', ''))} | {item.get('summary', '')} | {_code(item.get('coverage_object', ''))} | {item.get('coverage_status', '')} | {item.get('notes', '')} |"
        )
    lines.extend(
        [
            "",
            "### 4.2 反向追踪表",
            "",
            "| 接口名 | 来源需求ID | 来源类型 | 置信度 | 备注 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for api in external_apis:
        lines.append(
            f"| `{api.get('name', '')}` | {_join(api.get('evidence', []))} | 需求/规则 | 高 | formal external API |"
        )

    lines.extend(["", "## 5. 文件列表定义", "", "### 5.1 文件列表", ""])
    lines.extend(_render_file_items(file_items))
    lines.extend(
        [
            "",
            "### 5.2 五大类头文件承载关系",
            "",
            "| 类别 | 主承载头文件 | 次承载头文件 | 承载说明 |",
            "| --- | --- | --- | --- |",
            f"| 对外接口 | `{module}.h` | `{module}_Types.h` | 对外 API 原型和公开类型引用。 |",
            f"| 配置宏参 | `{module}_Cfg.h` | `{module}_CfgData.h` | 编译期开关和基础配置宏。 |",
            f"| 寄存器定义 | `{module}_Reg.h` | `{module}_Cfg.h` | 承载寄存器地址、位定义和协议常量。 |",
            f"| 标定参数 | `{module}_CfgData.h` | `{module}_Types.h` | 当前无正式标定项，保留载体关系。 |",
            f"| 内存分配宏 | `{module}_MemMap.h` | section-managed files | 所有段边界的统一 MemMap 载体。 |",
            "",
            "## 6. 外部接口定义",
            "",
        ]
    )
    lines.extend(_render_external_api_sections(external_apis, "6"))
    lines.extend(["## 7. 外部依赖与Callout定义", ""])
    lines.extend(_render_dependency_sections(dependency_apis, "7.2"))
    lines.extend(
        [
            "## 8. 全局参数定义",
            "",
            "| 参数名 | 作用域 | 角色 | 分类 | 类型 | 存储/内存段 | 备注 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    if runtime_states:
        for item in runtime_states:
            lines.append(
                f"| `{item.get('name', '')}` | Internal | runtime state | 状态/缓存 | `N/A` | `{item.get('memory_section', '')}` | {item.get('owner', '')} |"
            )
    lines.extend(
        [
            "",
            "## 9. 配置宏参定义",
            "",
            "### 9.1 基础配置",
            "",
            "| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in config_macros:
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('purpose', '')} | {item.get('macro_type', '')} | `{item.get('default_value', '')}` | {_join(item.get('evidence', []))} | `{item.get('usage_location', '')}` | {item.get('status', '')} |"
        )
    lines.extend(["", "## 10. 内存分配宏定义", ""])
    lines.extend(
        [
            "| 内存段 | 目标内容 | 进入宏 | 退出宏 | 使用文件 | 备注 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in memmap_sections:
        lines.append(
            f"| {item.get('name', '')} | {item.get('target_content', '')} | `{item.get('start_macro', '')}` | `{item.get('stop_macro', '')}` | {_join(item.get('used_files', []))} | {item.get('notes', '')} |"
        )
    lines.extend(
        [
            "",
            "## 11. 全局标定参数定义",
            "",
            "| 参数名 | 类型 | 初始值 | 描述 | 状态 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if payload.get("calibration_items", []):
        for item in payload["calibration_items"]:
            lines.append(
                f"| `{item.get('name', '')}` | `{item.get('type', '')}` | `{item.get('initial_value', '')}` | {item.get('description', '')} | {item.get('status', '')} |"
            )
    else:
        lines.append("| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。 | Empty |")
    lines.extend(
        [
            "",
            "## 12. 命名与符合性检查",
            "",
            "### 12.1 命名规则应用",
            f"- 文件/模块命名规则: 保留 `{module}` 命名空间。",
            f"- C标识符命名空间规则: 外部接口和依赖接口均保持 `{module}_...` 前缀。",
            "- 全局参数命名规则: 配置宏使用全大写宏命名。",
            "",
            "### 12.2 符合性观察",
            "- 观察1: 外部接口与依赖接口已分离。",
            "- 观察2: 配置宏、运行态和 MemMap 对象均有独立承载。",
            "",
            "## 13. 风险与待确认问题",
            "",
        ]
    )
    lines.extend(_render_risk_table(risk_items))
    lines.extend(
        [
            "",
            "### 13.1 接口遗漏风险清单",
            "",
            "| 风险项 | 风险等级 | 说明 | 建议动作 |",
            "| --- | --- | --- | --- |",
            "| Fault/diag readable API | 中 | 已提供 `GetFaultStatus`，需持续保持与需求一致。 | 变更诊断行为时同步更新外部接口。 |",
            "",
            "### 13.2 待确认接口清单",
            "",
            "| 接口名 | 来源需求 | 置信度 | 待确认原因 | 建议处理 |",
            "| --- | --- | --- | --- | --- |",
            f"| `{module}_Reset` | SRS-Gp_NCA95xx-INTF-0007 | 中 | RESET 控制归属待确认 | 确认是否保留 CalloutWriteDio |",
            "",
            "## 附录：架构元信息",
            "",
            f"- 架构版本: `{version}`",
            f"- 架构状态: `{status}`",
            f"- 输出模式: `{output_mode}`",
            f"- 生成时间: {created}",
            f"- 生成/修订说明: {_join(change_summary) or '初版生成。'}",
            "- 版本策略: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。",
            "- 发布条件: 所有真实风险项均为 `已评审`。",
            "",
        ]
    )
    if status == "Draft":
        lines.extend(
            [
                "## 下一步：评审与发布引导",
                "",
                "- 推荐评审方式 1：直接修改风险表中的 `状态` 和 `备注`。",
                "- 推荐评审方式 2：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：按 xxx 方案调整`。",
                "- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render FC architecture object JSON into summary/full markdown.")
    parser.add_argument("input", type=Path, help="Architecture objects JSON file")
    parser.add_argument("--output", type=Path, help="Output markdown file path")
    parser.add_argument(
        "--mode",
        choices=("summary", "full", "both"),
        default="summary",
        help="Render summary, full, or both outputs (default: summary).",
    )
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if args.mode == "summary":
        content = render_summary_markdown(payload)
        if args.output:
            args.output.write_text(content, encoding="utf-8")
        else:
            print(content, end="")
    elif args.mode == "full":
        content = render_full_markdown(payload)
        if args.output:
            args.output.write_text(content, encoding="utf-8")
        else:
            print(content, end="")
    else:
        summary_content = render_summary_markdown(payload)
        full_content = render_full_markdown(payload)
        if args.output:
            summary_path = args.output.with_name(args.output.stem + "_summary" + args.output.suffix)
            full_path = args.output.with_name(args.output.stem + "_full" + args.output.suffix)
            summary_path.write_text(summary_content, encoding="utf-8")
            full_path.write_text(full_content, encoding="utf-8")
        else:
            print("# Summary Output", end="\n\n")
            print(summary_content, end="\n")
            print("# Full Output", end="\n\n")
            print(full_content, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
