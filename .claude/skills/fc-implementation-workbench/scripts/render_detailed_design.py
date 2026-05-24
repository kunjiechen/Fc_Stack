#!/usr/bin/env python3
"""Render FC detailed design markdown from a structured bundle."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Bundle root must be a mapping object.")
    return data


def render_list(items: list[str], empty_text: str = "无") -> str:
    if not items:
        return f"- {empty_text}"
    return "\n".join(f"- {item}" for item in items)


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        lines.append("| " + " | ".join(padded[: len(headers)]) + " |")
    return "\n".join(lines)


def short_name(full_name: str, module: str) -> str:
    prefix = f"{module}_"
    if full_name.startswith(prefix):
        return full_name[len(prefix) :]
    return full_name


def infer_layer(bundle: dict) -> str:
    grounding_modules = bundle.get("grounding_modules", [])
    if "IoMcu" in grounding_modules:
        return "IoExtDev / IoMcu adapted FC"
    return "FC"


def infer_runtime_model(patterns: list[str]) -> str:
    if "interrupt_polling_mainfunction" in patterns:
        return "周期轮询 + 事件采样"
    if "chip_mainfunction_pattern" in patterns:
        return "初始化 + 周期任务混合"
    return "事件驱动"


def infer_core_mode(bundle: dict) -> str:
    for assumption in bundle.get("assumptions", []):
        if "单核独立部署" in assumption or "不共享 I2C 总线" in assumption:
            return "单核"
        if "多核" in assumption or "per-core" in assumption:
            return "多核"
    if "per_core_runtime_container" in bundle.get("grounding_patterns", []):
        return "多核"
    return "单核"


def format_trace_ids(trace_ids: list[str]) -> str:
    if not trace_ids:
        return "待补需求追踪"
    return ", ".join(f"`{trace}`" for trace in trace_ids)


def pending_items(bundle: dict) -> list[dict]:
    return [req for req in bundle.get("requirements", []) if req.get("status") == "pending_confirm"]


def implementation_scheme(bundle: dict) -> list[str]:
    patterns = bundle.get("grounding_patterns", [])
    scheme = [
        "通过 `Init` 完成芯片初始化、配置加载和运行态建立。",
    ]
    if any(item["name"].endswith("_MainFunction") for item in bundle["architecture"]["external_interfaces"]):
        scheme.append("通过 `MainFunction` 周期轮询中断/状态输入，并驱动故障确认与运行态更新。")
    scheme.append("通过 external interface 暴露业务能力，通过 dependency callout 隔离底层资源访问。")
    if "runtime_capability_reserved_in_config" in patterns:
        scheme.append("方向/极性等运行时能力当前通过配置保留，不作为本版本正式外部接口开放。")
    return scheme


def dependency_platform_label(dep_name: str) -> str:
    if "I2c" in dep_name or "I2C" in dep_name:
        return "I2C驱动模块"
    if "Dio" in dep_name or "DIO" in dep_name:
        return "DIO驱动模块"
    if "CoreId" in dep_name:
        return "Core管理模块"
    return "平台适配模块"


def mermaid_id(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum()) or "N"


def render_function_block_diagram(bundle: dict) -> list[str]:
    module = bundle["module"]
    dd_external = bundle["detailed_design"]["external_interfaces"]
    internal_names = {item["name"] for item in bundle["detailed_design"]["internal_interfaces"]}
    dependency_names = {item["name"] for item in bundle["detailed_design"]["dependency_interfaces"]}

    lines = [
        "```mermaid",
        "flowchart LR",
        "    U[上层业务模块]",
        f"    subgraph FC[{module} 当前模块]",
        "      direction LR",
    ]

    platform_nodes: dict[str, str] = {}
    emitted_platforms: set[str] = set()
    ext_nodes: dict[str, str] = {}
    int_nodes: dict[str, str] = {}
    dep_nodes: dict[str, str] = {}
    emitted_fc_nodes: set[str] = set()
    emitted_links: set[tuple[str, str]] = set()

    for item in dd_external:
        ext_short = short_name(item["name"], module)
        ext_id = ext_nodes.setdefault(item["name"], f"E{mermaid_id(ext_short)}")
        if ext_id not in emitted_fc_nodes:
            lines.append(f"      {ext_id}[外部接口\\n{ext_short}]")
            emitted_fc_nodes.add(ext_id)
        if ("U", ext_id) not in emitted_links:
            lines.append(f"    U --> {ext_id}")
            emitted_links.add(("U", ext_id))

        internal_links = [link for link in item.get("relationship_links", []) if link in internal_names][:2]
        dependency_links = [link for link in item.get("relationship_links", []) if link in dependency_names][:2]

        if internal_links:
            for link in internal_links:
                int_short = short_name(link, module)
                int_id = int_nodes.setdefault(link, f"I{mermaid_id(int_short)}")
                if int_id not in emitted_fc_nodes:
                    lines.append(f"      {int_id}[内部接口\\n{int_short}]")
                    emitted_fc_nodes.add(int_id)
                if (ext_id, int_id) not in emitted_links:
                    lines.append(f"      {ext_id} --> {int_id}")
                    emitted_links.add((ext_id, int_id))

                local_deps = dependency_links[:2]
                for dep in local_deps:
                    dep_short = short_name(dep, module)
                    dep_id = dep_nodes.setdefault(dep, f"D{mermaid_id(dep_short)}")
                    if dep_id not in emitted_fc_nodes:
                        lines.append(f"      {dep_id}[依赖接口\\n{dep_short}]")
                        emitted_fc_nodes.add(dep_id)
                    if (int_id, dep_id) not in emitted_links:
                        lines.append(f"      {int_id} --> {dep_id}")
                        emitted_links.add((int_id, dep_id))
                    platform_label = dependency_platform_label(dep_short)
                    platform_id = platform_nodes.setdefault(platform_label, f"P{len(platform_nodes) + 1}")
                    if platform_id not in emitted_platforms:
                        lines.append(f"    {platform_id}[{platform_label}]")
                        emitted_platforms.add(platform_id)
                    if (dep_id, platform_id) not in emitted_links:
                        lines.append(f"    {dep_id} --> {platform_id}")
                        emitted_links.add((dep_id, platform_id))
        else:
            for dep in dependency_links:
                dep_short = short_name(dep, module)
                dep_id = dep_nodes.setdefault(dep, f"D{mermaid_id(dep_short)}")
                if dep_id not in emitted_fc_nodes:
                    lines.append(f"      {dep_id}[依赖接口\\n{dep_short}]")
                    emitted_fc_nodes.add(dep_id)
                if (ext_id, dep_id) not in emitted_links:
                    lines.append(f"      {ext_id} --> {dep_id}")
                    emitted_links.add((ext_id, dep_id))
                platform_label = dependency_platform_label(dep_short)
                platform_id = platform_nodes.setdefault(platform_label, f"P{len(platform_nodes) + 1}")
                if platform_id not in emitted_platforms:
                    lines.append(f"    {platform_id}[{platform_label}]")
                    emitted_platforms.add(platform_id)
                if (dep_id, platform_id) not in emitted_links:
                    lines.append(f"    {dep_id} --> {platform_id}")
                    emitted_links.add((dep_id, platform_id))

    lines.extend([
        "    end",
        "```",
    ])
    return lines


def function_design_sections(bundle: dict) -> str:
    module = bundle["module"]
    patterns = bundle.get("grounding_patterns", [])
    core_mode = infer_core_mode(bundle)
    dep_names = [short_name(item["name"], module) for item in bundle["architecture"]["dependency_interfaces"]]
    lines = [
        "## 4. 功能设计",
        "",
        "### 4.1 功能设计说明",
        "",
        render_list(implementation_scheme(bundle)),
        "",
        "### 4.2 功能框图",
        "",
        *render_function_block_diagram(bundle),
        "",
        "### 4.3 分层设计思想",
        "",
    ]
    bullets = [
        "external interface 只承载业务入口和对外契约，不直接承担底层访问细节。",
        "internal interface 承载访问检查、寄存器访问、故障更新、状态同步等实现动作。",
        "dependency interface / callout 只负责资源适配边界，不在业务层分散展开平台细节。",
    ]
    if core_mode == "多核":
        bullets.append("运行态和配置对象按 core 所有权组织，避免跨核共享状态无序扩散。")
    if "chip_mainfunction_pattern" in patterns:
        bullets.append("MainFunction 采用周期轮询模型，将输入采样、故障处理和状态更新集中在统一节拍内完成。")
    if dep_names:
        bullets.append(f"当前主要依赖接口包括 {', '.join(f'`{name}`' for name in dep_names)}。")
    lines.append(render_list(bullets))
    return "\n".join(lines)


def file_dependency_headers(bundle: dict) -> list[list[str]]:
    module = bundle["module"]
    return [
        [f"`{module}.c`", "Required", "实现 external API 与内部接口主体。", "public API, internal logic, runtime", f"`{module}.h`, `{module}_Cfg.h`, `{module}_Callout.h`, `{module}_MemMap.h`"],
        [f"`{module}.h`", "Required", "对外发布 external API。", "formal interfaces", "`Std_Types.h`, `Compiler.h`"],
        [f"`{module}_Cfg.h`", "Required", "声明配置宏参和参数边界。", "formal / reserved config", "`Std_Types.h`"],
        [f"`{module}_Cfg.c`", "Required", "定义配置参数与映射表。", "cfg params / bindings", f"`{module}_Cfg.h`, `{module}_MemMap.h`"],
        [f"`{module}_Callout.h/.c`", "Required", "承载 dependency interface 适配边界。", "callout contract / adaptation", f"`{module}.h`, `IoMcu` / platform headers"],
        [f"`{module}_MemMap.h`", "Required", "承载 MemMap section 映射。", "section boundaries", "project MemMap base headers"],
    ]


def render_external_interface_sections(bundle: dict) -> str:
    module = bundle["module"]
    arch_external = {item["name"]: item for item in bundle["architecture"]["external_interfaces"]}
    dd_external = {item["name"]: item for item in bundle["detailed_design"]["external_interfaces"]}
    dependency_map = {item["name"]: item for item in bundle["detailed_design"]["dependency_interfaces"]}
    internal_map = {item["name"]: item for item in bundle["detailed_design"]["internal_interfaces"]}
    sections: list[str] = ["## 7. 外部接口设计", ""]
    for idx, name in enumerate(arch_external, start=1):
        item = dd_external.get(name, {"name": name, "relationship_links": []})
        arch = arch_external[name]
        links = item.get("relationship_links", [])
        internal_links = [link for link in links if link in internal_map]
        dependency_links = [link for link in links if link in dependency_map]
        unresolved_links = [link for link in links if link not in internal_map and link not in dependency_map]
        sections.append(f"### 7.{idx} `{name}`")
        sections.append(
            render_table(
                ["Interface Prototype", "功能说明", "同步属性", "重入性", "返回值", "基本约束", "关联接口", "需求追踪"],
                [[
                    arch.get("prototype", name),
                    f"{short_name(name, module)} 为 architecture 已冻结 external interface，本节展开其实现动作、依赖调用和内部接口协作关系。",
                    arch.get("sync", "Synchronous"),
                    arch.get("reentrancy", "TBD"),
                    "遵循 architecture 定义。",
                    "必须保持与 formal architecture interface、关联内部接口和依赖接口一致。",
                    ", ".join(f"`{link}`" if link in internal_map else f"`{short_name(link, module)}`" for link in internal_links + dependency_links) or "—",
                    format_trace_ids(arch.get("trace_ids", [])),
                ]],
            )
        )
        sub_rows = [["1", "入口约束检查", "接口输入与运行条件", "访问合法性结论", "DET / 初始化 / 指针 / 范围检查", "`Prv_CheckAccess` 或等效实现"]]
        step_no = 2
        for link in internal_links:
            sub_rows.append([str(step_no), short_name(link, module), "接口上下文", "内部动作结果", "按内部接口职责执行", f"`{short_name(link, module)}`"])
            step_no += 1
        for link in dependency_links:
            sub_rows.append([str(step_no), short_name(link, module), "内部接口或接口上下文", "依赖访问结果", "formal dependency callout", f"`{short_name(link, module)}`"])
            step_no += 1
        sections.extend([
            "",
            f"#### 7.{idx}.1 子功能拆分",
            render_table(["步骤", "子功能", "输入", "输出", "关键检查/约束", "依赖对象"], sub_rows),
            "",
            f"#### 7.{idx}.2 执行步骤",
            "",
        ])
        step_lines = ["1. 进入接口并完成边界检查，确保调用场景满足 formal 约束。"]
        for link in internal_links:
            step_lines.append(f"{len(step_lines)+1}. 调用 `{short_name(link, module)}` 执行该接口的主要内部职责。")
        for link in dependency_links:
            step_lines.append(f"{len(step_lines)+1}. 通过 `{short_name(link, module)}` 完成对底层资源的访问。")
        step_lines.append(f"{len(step_lines)+1}. 汇总结果并按 `{name}` 的返回策略结束接口。")
        sections.extend(step_lines)
        sections.extend([
            "",
            f"#### 7.{idx}.3 参与内部接口",
        ])
        rows = [[f"`{link}`", internal_map[link].get("evidence", ["由 bundle 关系推导。"])[0], "由 relationship_links 推导"] for link in internal_links]
        if not rows:
            rows = [["`None`", "当前无显式内部接口关系。", "—"]]
        sections.append(render_table(["内部接口", "作用", "调用时机"], rows))
        if short_name(name, module) in {"Init", "MainFunction"} or len(internal_links) + len(dependency_links) >= 3:
            sections.extend([
                "",
                f"#### 7.{idx}.4 流程图",
                "```mermaid",
                "flowchart TD",
                "    A[接口入口] --> B[执行前检查]",
            ])
            if internal_links:
                sections.append(f"    B --> C[调用 {short_name(internal_links[0], module)}]")
                tail = "C"
                if len(internal_links) > 1:
                    sections.append(f"    C --> D[调用 {short_name(internal_links[-1], module)}]")
                    tail = "D"
            else:
                tail = "B"
            sections.extend([
                f"    {tail} --> E[访问依赖接口或汇总结果]",
                "    E --> F[返回]",
                "```",
            ])
        if unresolved_links:
            sections.extend([
                "",
                f"#### 7.{idx}.5 待修正文档关系",
                render_list([f"`{short_name(link, module)}` 目前未在内部接口/依赖接口定义中落地，需补定义或删关系。" for link in unresolved_links]),
            ])
        sections.append("")
    return "\n".join(sections).strip()


def render_internal_section(bundle: dict) -> str:
    module = bundle["module"]
    ext_map = {item["name"]: short_name(item["name"], module) for item in bundle["detailed_design"]["external_interfaces"]}
    dep_map = {item["name"]: short_name(item["name"], module) for item in bundle["detailed_design"]["dependency_interfaces"]}
    lines = ["## 8. 内部接口设计", ""]
    rows: list[list[str]] = []
    for item in bundle["detailed_design"]["internal_interfaces"]:
        rel = item.get("relationship_links", [])
        callers = [f"`{ext_map[ref]}`" for ref in rel if ref in ext_map]
        deps = [f"`{dep_map[ref]}`" for ref in rel if ref in dep_map]
        rows.append([
            f"`{item['name']}`",
            "`static`",
            item.get("evidence", ["承载内部实现职责。"])[0],
            ", ".join(callers) if callers else "—",
            ", ".join(deps) if deps else "—",
        ])
    if not rows:
        rows = [["`None`", "—", "当前无内部接口。", "—", "—"]]
    lines.append(render_table(["内部接口名", "作用域", "职责", "调用方", "依赖方"], rows))
    for idx, item in enumerate(bundle["detailed_design"]["internal_interfaces"], start=1):
        rel = item.get("relationship_links", [])
        callers = [f"`{ext_map[ref]}`" for ref in rel if ref in ext_map]
        deps = [f"`{dep_map[ref]}`" for ref in rel if ref in dep_map]
        lines.extend([
            "",
            f"### 8.{idx} `{item['name']}`",
            render_table(
                ["Interface Name", "类别", "作用域", "功能说明", "调用方", "依赖方"],
                [[
                    item["name"],
                    "内部控制 / 校验 / 访问辅助",
                    "`static`",
                    item.get("evidence", ["承载内部实现职责。"])[0],
                    ", ".join(callers) if callers else "—",
                    ", ".join(deps) if deps else "—",
                ]],
            ),
            "",
            f"#### 8.{idx}.1 设计说明",
            "",
            f"- `{item['name']}` 用于承载可复用的实现动作，避免将底层访问和状态处理散落在 external interface 主流程中。",
            f"- 该内部接口当前由 {', '.join(callers) if callers else '相关外部接口'} 触发，并与 {', '.join(deps) if deps else '必要依赖接口'} 协作。",
        ])
    return "\n".join(lines)


def render_dependency_section(bundle: dict) -> str:
    module = bundle["module"]
    arch_dep = {item["name"]: item for item in bundle["architecture"]["dependency_interfaces"]}
    dd_dep = {item["name"]: item for item in bundle["detailed_design"]["dependency_interfaces"]}
    internal_names = {internal["name"] for internal in bundle["detailed_design"]["internal_interfaces"]}
    external_names = {external["name"] for external in bundle["detailed_design"]["external_interfaces"]}
    sections: list[str] = ["## 9. 依赖接口与Callout设计", ""]
    for idx, name in enumerate(arch_dep, start=1):
        item = dd_dep.get(name, {"name": name, "relationship_links": []})
        arch = arch_dep[name]
        unresolved_links = [link for link in item.get("relationship_links", []) if link not in internal_names and link not in external_names]
        sections.append(f"### 9.{idx} `{name}`")
        sections.append(
            render_table(
                ["Interface Prototype", "功能说明", "实现边界", "同步属性", "重入性", "基本约束", "关联接口", "覆盖状态", "需求追踪"],
                [[
                    arch.get("prototype", name),
                    f"{short_name(name, module)} 为 detailed design 依赖接口 / callout 边界。",
                    "项目适配层 / 平台层",
                    arch.get("sync", "Synchronous"),
                    arch.get("reentrancy", "TBD"),
                    "必须与 architecture formal dependency contract 保持一致。",
                    ", ".join(
                        f"`{link}`" if link in internal_names else f"`{short_name(link, module)}`"
                        for link in item.get("relationship_links", [])
                        if link not in unresolved_links
                    ) or "—",
                    "已在 DD 主体中定义" if name in dd_dep else "architecture 已冻结，但当前 DD 尚未补全",
                    format_trace_ids(arch.get("trace_ids", [])),
                ]],
            )
        )
        sections.append("")
        sections.append(render_list([
            "实现方应位于项目适配层或平台层，不能在业务接口内部直接替代。",
            "调用失败时应通过返回值、故障更新或待确认策略反馈给 FC 主体。",
        ]))
        if unresolved_links:
            sections.extend([
                "",
                render_list([f"`{short_name(link, module)}` 当前只在关系中被引用，尚未定义为内部接口或 external interface。" for link in unresolved_links]),
            ])
        sections.append("")
    return "\n".join(sections).strip()


def render_state_machine(bundle: dict) -> str:
    if any("状态机" in risk for risk in bundle.get("risks", [])):
        return "\n".join([
            "## 11. 状态机设计",
            "",
            "- 当前模块存在复杂状态机需求，后续应补软件状态机、芯片状态机及其关系图。",
        ])
    return "\n".join([
        "## 11. 状态机设计",
        "",
        "- 当前模块以接口调用、运行态缓存和故障位更新为主，不单独构造复杂状态机。",
        "- 若后续版本引入模式切换、恢复阶段或芯片状态联动，再强化状态机章节。",
    ])


def explicit_runtime_variables(bundle: dict) -> list[list[str]]:
    module = bundle["module"]
    core_mode = infer_core_mode(bundle)
    rows = [
        [f"`{module}_Runtime`", "运行态容器", "保存模块运行态、初始化状态和最近一次采样结果。", "`Init` / `MainFunction`", "public APIs / internal interfaces", "FC 生命周期", core_mode],
        [f"`{module}_FaultState`", "故障状态", "保存 I2C / 输入采样 / 初始化相关故障位。", "`Init` / `MainFunction` / fault helpers", "诊断接口 / 查询接口", "FC 生命周期", core_mode],
    ]
    if any(item["name"].endswith("_MainFunction") for item in bundle["architecture"]["external_interfaces"]):
        rows.append([f"`{module}_IntSampleCache`", "采样缓存", "缓存 MainFunction 周期内的输入状态变化与去抖结果。", "`MainFunction`", "内部接口 / 查询接口", "FC 生命周期", core_mode])
    return rows


def config_point_rows(bundle: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for req in bundle.get("requirements", []):
        if req.get("category") != "config":
            continue
        rows.append([
            req["statement"],
            "来自需求侧的配置点，后续应在 `Cfg.c` / 配置结构中落实。",
            format_trace_ids([req["id"]]),
        ])
    return rows


def cfg_object_rows(bundle: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in bundle.get("cfg_objects", []):
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", ""))
        if not symbol:
            continue
        module = str(item.get("module", ""))
        role = str(item.get("role", "cfg_object"))
        fields = item.get("fields", [])
        references = item.get("references", [])
        dimensions = item.get("dimensions", [])
        if not isinstance(fields, list):
            fields = []
        if not isinstance(references, list):
            references = []
        if not isinstance(dimensions, list):
            dimensions = []

        config_points: list[str] = []
        if fields:
            config_points.extend(fields[:6])
        if references and len(config_points) < 6:
            config_points.extend(references[: 6 - len(config_points)])
        if dimensions:
            config_points.append(f"维度: {', '.join(dimensions[:2])}")
        summary = str(item.get("summary", "")) or "参考 grounding 模块中的真实 Cfg.c 配置对象。"
        rows.append([
            module,
            f"`{symbol}`",
            role,
            ", ".join(f"`{point}`" if not point.startswith("维度:") else point for point in config_points) or "—",
            summary,
        ])
    return rows


def cfg_group_label(item: dict) -> str:
    role = str(item.get("role", ""))
    tags = item.get("semantic_tags", [])
    if not isinstance(tags, list):
        tags = []
    tag_set = {str(tag) for tag in tags}
    if role == "top_level_cfg_container":
        return "顶层配置容器"
    if role in {"per_core_chip_config_array", "per_chip_chip_config_array"}:
        return "芯片实例配置"
    if "register_init" in tag_set or role == "register_frame_config":
        return "寄存器初值配置"
    if "bus_mapping" in tag_set or role == "bus_mapping_config":
        return "总线映射配置"
    if "io_mapping" in tag_set or role == "io_mapping_config":
        return "IO映射配置"
    return "其他配置对象"


def grouped_cfg_sections(bundle: dict) -> list[str]:
    objects = bundle.get("cfg_objects", [])
    if not isinstance(objects, list) or not objects:
        return []

    group_order = [
        "顶层配置容器",
        "芯片实例配置",
        "寄存器初值配置",
        "总线映射配置",
        "IO映射配置",
        "其他配置对象",
    ]
    grouped: dict[str, list[dict]] = {name: [] for name in group_order}
    for item in objects:
        if not isinstance(item, dict):
            continue
        grouped.setdefault(cfg_group_label(item), []).append(item)

    lines: list[str] = []
    section_no = 1
    for group_name in group_order:
        group_items = grouped.get(group_name, [])
        if not group_items:
            continue
        lines.extend([
            f"#### 15.2.{section_no} {group_name}",
            "",
        ])
        config_points: list[str] = []
        dimensions: list[str] = []
        role_hints: list[str] = []
        for item in group_items:
            fields = item.get("fields", [])
            refs = item.get("references", [])
            dims = item.get("dimensions", [])
            if isinstance(fields, list):
                for field in fields:
                    if isinstance(field, str) and field not in config_points:
                        config_points.append(field)
            if isinstance(refs, list):
                for ref in refs:
                    if isinstance(ref, str) and ref not in role_hints:
                        role_hints.append(ref)
            if isinstance(dims, list):
                for dim in dims:
                    if isinstance(dim, str) and dim not in dimensions:
                        dimensions.append(dim)

        organization = "按模块统一组织"
        if any("CORE" in dim.upper() for dim in dimensions):
            organization = "按 core 分组组织"
        elif any("CHIP" in dim.upper() or "MAX_CHIP" in dim.upper() for dim in dimensions):
            organization = "按芯片实例组织"

        if group_name == "顶层配置容器":
            description = "当前模块应提供顶层配置容器，用于统一聚合各类子配置并作为正式配置入口。"
            if role_hints:
                description = "当前模块应提供顶层配置容器，用于聚合寄存器初始化、总线映射和实例配置等子配置。"
            points_text = "顶层配置入口, 子配置聚合关系"
        elif group_name == "芯片实例配置":
            description = "当前模块应为每个芯片实例或每个 core 下的芯片实例提供独立配置。"
            points_text = ", ".join(f"`{point}`" for point in config_points[:8]) if config_points else "芯片实例参数"
        elif group_name == "寄存器初值配置":
            description = "当前模块应定义芯片上电初始化或默认工作模式所需的寄存器初值。"
            points_text = ", ".join(f"`{point}`" for point in config_points[:8]) if config_points else "寄存器默认值"
        elif group_name == "总线映射配置":
            description = "当前模块应定义底层总线访问通道、序列或地址映射关系。"
            points_text = ", ".join(f"`{point}`" for point in config_points[:8]) if config_points else "总线/通道映射"
        elif group_name == "IO映射配置":
            description = "当前模块应定义控制引脚、故障引脚或 PWM 等 IO 资源映射。"
            points_text = ", ".join(f"`{point}`" for point in config_points[:8]) if config_points else "控制/故障 IO 映射"
        else:
            description = "当前模块应补充其他与业务实现相关的辅助配置对象。"
            points_text = ", ".join(f"`{point}`" for point in config_points[:8]) if config_points else "辅助配置项"

        rows = [[group_name, points_text, organization, description]]
        lines.append(render_table(["配置类别", "建议配置内容", "组织方式", "说明"], rows))
        lines.append("")
        section_no += 1
    return lines


def render_config_section(bundle: dict) -> str:
    macro_rows = []
    param_rows = config_point_rows(bundle)
    for item in bundle["architecture"].get("config_items", []):
        row = [
            f"`{item['name']}`",
            item.get("decision", "配置控制项或能力保留项。"),
            item.get("status", "formal"),
            format_trace_ids(item.get("trace_ids", [])),
        ]
        macro_rows.append(row)
    if not macro_rows:
        macro_rows = [["`Empty`", "当前无确认配置宏参。", "Empty", "—"]]
    if not param_rows:
        param_rows = [["当前未提取到具体 `Cfg.c` 配置点", "当前只能稳定识别到配置需求，还未落到具体配置变量名。", "—"]]
    lines = [
        "## 15. 配置宏参设计",
        "",
        "### 15.1 配置宏参",
        "",
        render_table(["宏参/开关", "作用", "状态", "需求追踪"], macro_rows),
        "",
        "### 15.2 配置参数",
        "",
    ]
    grouped_sections = grouped_cfg_sections(bundle)
    if grouped_sections:
        lines.extend(grouped_sections)
    else:
        lines.append(render_table(["配置点", "说明", "需求追踪"], param_rows))
    return "\n".join(lines)


def render_arch_dd_coverage(bundle: dict) -> str:
    rows = []
    dd_external = {item["name"] for item in bundle["detailed_design"]["external_interfaces"]}
    dd_dependency = {item["name"] for item in bundle["detailed_design"]["dependency_interfaces"]}
    dd_internal = {item["name"] for item in bundle["detailed_design"]["internal_interfaces"]}
    for item in bundle["architecture"]["external_interfaces"]:
        rows.append([item["name"], "External Interface", "7. 外部接口设计", item["name"] if item["name"] in dd_external else "—", "Covered" if item["name"] in dd_external else "Missing", format_trace_ids(item.get("trace_ids", []))])
    for item in bundle["architecture"]["dependency_interfaces"]:
        rows.append([item["name"], "Dependency Interface", "9. 依赖接口与Callout设计", item["name"] if item["name"] in dd_dependency else "—", "Covered" if item["name"] in dd_dependency else "Partial", format_trace_ids(item.get("trace_ids", []))])
    for item in bundle["detailed_design"]["internal_interfaces"]:
        rows.append([item["name"], "Internal Interface", "8. 内部接口设计", item["name"] if item["name"] in dd_internal else "—", "Covered", "由 DD 内部展开"])
    return "\n".join([
        "## 18. 架构与详细设计覆盖表",
        "",
        render_table(["架构对象", "分类", "DD落位章节", "DD对象名", "覆盖状态", "备注"], rows),
    ])


def render_markdown(bundle: dict) -> str:
    module = bundle["module"]
    core_mode = infer_core_mode(bundle)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    function_intro = "负责对外部芯片能力进行初始化、输入输出访问、故障诊断和周期状态维护。"
    lines = [
        f"# {module} 详细设计（Rendered Draft）",
        "",
        "## 文档元信息",
        "",
        "- 详细设计版本: `V1`",
        "- 详细设计状态: `Draft`",
        f"- 生成时间: `{now}`",
        "- 生成/修订说明: 基于结构化设计对象自动生成第一版正文初稿。",
        "",
        "## 1. FC概述",
        "",
        f"- FC名称: `{module}`",
        f"- 功能介绍: {function_intro}",
        f"- 所属层级: `{infer_layer(bundle)}`",
        f"- 实现方案: 采用 `{infer_runtime_model(bundle.get('grounding_patterns', []))}` 方式组织初始化、周期任务、内部接口和底层 callout 协作。",
        "",
        "## 2. 设计输入",
        "",
        f"- 需求输入: `SRS_{module}` 及其接口/功能需求条目。",
        f"- 架构输入: `Architecture_{module}` 已冻结的 external interface、dependency interface 和配置边界。",
        "- 平台约束: 芯片访问依赖 I2C / DIO / CoreId 等平台能力，具体由项目适配层提供。",
        "- 项目约束: 当前版本遵循已冻结接口集合，不在详细设计阶段擅自扩展未确认能力。",
        "",
        function_design_sections(bundle),
        "",
        "## 5. 文件列表设计",
        "",
        render_table(["文件名", "必需/可选", "职责", "关键内容", "依赖头文件"], file_dependency_headers(bundle)),
        "",
        "## 6. 单核/多核框架设计",
        "",
        "### 6.1 框架结论",
        "",
        render_list([
            f"当前按 `{core_mode}` 方案展开详细设计。",
            "接口层负责对外契约，内部接口层负责实现动作归并，依赖接口层负责平台资源适配。",
            "周期任务和运行时变量的组织方式必须服从 architecture freeze 和已确认项目约束。",
        ]),
        "",
        "### 6.2 任务与执行框架",
        "",
        render_table(["任务/入口", "执行主体", "触发方式", "作用", "说明"], [["`Init`", module, "上电初始化", "建立配置与运行态", "初始化阶段入口"], ["`MainFunction`" if any(item["name"].endswith("_MainFunction") for item in bundle["architecture"]["external_interfaces"]) else "`None`", module, "周期调度", "输入采样、故障确认、运行态刷新", "若项目未启用周期任务则不实现"]]),
        "",
        "### 6.3 共享对象与一致性",
        "",
        render_table(["对象", "写方", "读方", "用途", "一致性要求"], [[f"`{module}_Runtime`", "`Init` / `MainFunction`", "public APIs / internal interfaces", "保持运行态与缓存一致", "禁止绕过统一更新路径直接改写"]]),
        "",
        render_external_interface_sections(bundle),
        "",
        render_internal_section(bundle),
        "",
        render_dependency_section(bundle),
        "",
        render_state_machine(bundle),
        "",
        "## 12. DET设计",
        "",
        render_table(
            ["检查点", "触发条件", "记录方式", "返回策略", "适用API"],
            [
                ["初始化检查", "模块未初始化即被调用", "`Det_ReportError` 或项目等效路径", "立即返回", "查询/设置类 public API"],
                ["参数/指针检查", "空指针、非法 Id、越界参数", "`Det_ReportError` 或项目等效路径", "返回 `E_NOT_OK`", "需要输入参数的 public API"],
            ],
        ),
        "",
        "## 13. 故障处理设计",
        "",
        render_table(
            ["故障类型", "检测条件", "确认规则", "响应动作", "恢复条件", "对外体现"],
            [
                ["通信故障", "I2C 读写失败或返回异常", "按连续失败/成功规则确认或恢复", "置位故障状态、限制后续访问或维持缓存值", "连续成功达到恢复阈值", "通过故障查询接口或状态位暴露"],
                ["输入采样故障", "INT / 输入状态异常或不一致", "按去抖与周期采样规则确认", "更新故障状态并保留上次有效值", "输入状态恢复稳定", "通过状态查询接口暴露"],
            ],
        ),
        "",
        "## 14. 运行时变量设计",
        "",
        render_table(["变量名", "类别", "目的", "写方", "读方", "生命周期", "所属Core"], explicit_runtime_variables(bundle)),
        "",
        render_config_section(bundle),
        "",
        "## 16. MemMap设计",
        "",
        render_table(
            ["Memory Section", "Target Content", "Start Macro", "Stop Macro", "Used Files", "Notes"],
            [
                ["CODE", "external APIs / internal interfaces", f"`{module.upper()}_CODE_START`", f"`{module.upper()}_CODE_STOP`", f"`{module}.c`, `{module}_Callout.c`", "按代码与适配边界组织"],
                ["RUNTIME", "runtime objects / fault state / caches", f"`{module.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx_START`", f"`{module.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx_STOP`", f"`{module}.c`", "是否按 core 分区取决于已确认部署方式"],
                ["CONST", "cfg params / mappings", f"`{module.upper()}_CONST_FAR_DATA_ALIGN4_GLOBAL_START`", f"`{module.upper()}_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP`", f"`{module}_Cfg.c`", "配置参数和映射表统一归入常量区"],
            ],
        ),
        "",
        "## 17. 代码编写限制要求",
        "",
        render_list([
            "不得在详细设计阶段新增 architecture 未冻结的 external interface 或 dependency interface。",
            "不得绕过统一的访问检查路径直接访问底层资源。",
            "reserved 配置能力不得在本版本实现为正式 public API。",
            "relationship_links 暴露的未定义对象必须先修正定义或关系后再进入编码。",
        ]),
        "",
        render_arch_dd_coverage(bundle),
        "",
    ]
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render FC detailed design markdown from a bundle.")
    parser.add_argument("--bundle", required=True, help="Path to generation bundle YAML")
    parser.add_argument("--output", required=True, help="Path to write rendered markdown")
    args = parser.parse_args()

    bundle = load_yaml(Path(args.bundle))
    output = Path(args.output)
    output.write_text(render_markdown(bundle), encoding="utf-8")
    print(f"OK: rendered detailed design to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
