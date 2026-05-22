"""Phase-3 requirement builder.

This module converts Phase-1 semantic objects plus Phase-2 validation findings
into engineering requirement instances. It deliberately stops at SRS document
generation and leaves trace, coverage, and ASPICE evidence to the Phase-4
requirement evidence layer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
import re
from typing import Any, Literal

from .rules import ValidationFinding
from .schema import RequirementObject


EngineeringRequirementType = Literal[
    "functional",
    "interface",
    "configuration",
    "timing",
    "state",
    "safety",
    "coding",
    "resource",
]


TYPE_CODES = {
    "functional": "FUNC",
    "interface": "IF",
    "configuration": "CFG",
    "timing": "TIME",
    "state": "STATE",
    "safety": "SAFE",
    "coding": "CODE",
    "resource": "RES",
}


@dataclass(frozen=True)
class EngineeringRequirement:
    requirement_id: str
    semantic_id: str
    requirement_type: EngineeringRequirementType
    title: str
    description: str
    pre_condition: str = ""
    trigger: str = ""
    input: str = ""
    output: str = ""
    exception: str = ""
    constraint: str = ""
    verification: str = ""
    source: list[dict[str, Any]] = field(default_factory=list)
    validation: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementIdEngine:
    """Generate stable SRS IDs by module and requirement type."""

    def __init__(self, module: str) -> None:
        self.module = _normalize_module(module)
        self._counters: defaultdict[str, int] = defaultdict(int)
        self._assigned: dict[str, str] = {}

    def id_for(self, semantic_id: str, requirement_type: str) -> str:
        if semantic_id in self._assigned:
            return self._assigned[semantic_id]
        type_code = TYPE_CODES.get(requirement_type, requirement_type.upper())
        self._counters[type_code] += 1
        requirement_id = f"SRS-{self.module}-{type_code}-{self._counters[type_code]:04d}"
        self._assigned[semantic_id] = requirement_id
        return requirement_id


class RequirementBuilder:
    """Map semantic requirement objects to engineering requirement instances."""

    def __init__(self, module: str = "FC") -> None:
        self.module = module
        self.id_engine = RequirementIdEngine(module)

    def build(
        self,
        requirements: list[RequirementObject],
        findings: list[ValidationFinding] | None = None,
    ) -> list[EngineeringRequirement]:
        findings_by_req = _findings_by_requirement(findings or [])
        return [
            self._build_one(req.to_dict(), findings_by_req.get(req.to_dict()["id"], []))
            for req in requirements
        ]

    def _build_one(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        req_type = item["type"]
        if req_type == "functional":
            return self._build_functional(item, findings)
        if req_type == "interface":
            return self._build_interface(item, findings)
        if req_type == "configuration":
            return self._build_configuration(item, findings)
        if req_type == "timing":
            return self._build_timing(item, findings)
        if req_type == "state":
            return self._build_state(item, findings)
        raise ValueError(f"Unsupported requirement type: {req_type}")

    def _base(
        self,
        item: dict[str, Any],
        findings: list[ValidationFinding],
        title: str,
        description: str,
        **kwargs: str,
    ) -> EngineeringRequirement:
        req_type = item["type"]
        verification = kwargs.pop("verification", _default_verification(req_type))
        verification = _refine_verification(
            verification,
            trigger=kwargs.get("trigger", ""),
            input_value=kwargs.get("input", ""),
            output_value=kwargs.get("output", ""),
            exception=kwargs.get("exception", ""),
            constraint=kwargs.get("constraint", ""),
        )
        return EngineeringRequirement(
            requirement_id=self.id_engine.id_for(item["id"], req_type),
            semantic_id=item["id"],
            requirement_type=req_type,
            title=title,
            description=description,
            source=item.get("source", []),
            validation=[finding.to_dict() for finding in findings],
            verification=verification,
            **kwargs,
        )

    def _build_functional(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        name = item.get("name") or "Functional Behavior"
        description = item.get("description") or f"The software shall support {name}."
        if not description.lower().startswith("the ") and not description.startswith("软件"):
            description = f"软件应支持{description.rstrip('。.') }。"
        return self._base(
            item,
            findings,
            title=name,
            description=description,
            input=", ".join(item.get("inputs", [])),
            output=", ".join(item.get("outputs", [])),
            constraint=", ".join(item.get("constraints", [])),
            verification=_planned_verification(name, req_type="functional"),
        )

    def _build_interface(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        interface = item.get("interface_name") or "Interface"
        direction = item.get("direction") or "unknown"
        description = _interface_description(interface)
        if direction == "input":
            description = _interface_description(interface)
        elif direction == "output":
            description = _interface_description(interface)
        return self._base(
            item,
            findings,
            title=_append_suffix(interface, "接口"),
            description=description,
            input=interface if direction == "input" else "",
            output=interface if direction == "output" else "",
            constraint=item.get("dependency", ""),
            verification=_planned_verification(interface, req_type="interface"),
        )

    def _build_configuration(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        config = item.get("config_name") or "Configuration"
        description = f"软件应支持 `{config}`，并定义默认值、取值范围和非法值处理规则。"
        return self._base(
            item,
            findings,
            title=_append_suffix(config, "配置"),
            description=description,
            constraint=f"范围：{_project_value(item.get('range', ''))}；默认值：{_project_value(item.get('default', ''))}",
            pre_condition=item.get("dependency", ""),
            verification=_planned_verification(config, req_type="configuration"),
        )

    def _build_timing(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        constraint = item.get("constraint") or "Timing Constraint"
        description = _timing_description(constraint, item.get("minimum", ""), item.get("maximum", ""))
        return self._base(
            item,
            findings,
            title="时序约束",
            description=description,
            constraint=constraint,
            verification=_planned_verification(constraint, req_type="timing"),
        )

    def _build_state(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        state = item.get("state_name") or "State"
        transitions = item.get("transition", [])
        if transitions:
            description = f"软件应支持 `{state}` 状态行为，状态转换为：{', '.join(transitions)}。"
        else:
            description = f"软件应支持 `{state}` 状态行为，并定义触发条件、观测方式和恢复策略。"
        return self._base(
            item,
            findings,
            title=_append_suffix(state, "状态"),
            description=description,
            trigger=", ".join(transitions),
            constraint=", ".join(item.get("dependency", [])),
            verification=_planned_verification(state, req_type="state"),
        )


def _findings_by_requirement(
    findings: list[ValidationFinding],
) -> dict[str, list[ValidationFinding]]:
    result: dict[str, list[ValidationFinding]] = defaultdict(list)
    for finding in findings:
        for req_id in finding.requirement_ids:
            result[req_id].append(finding)
    return result


def _normalize_module(module: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "", module).upper()
    return normalized or "FC"


def _default_verification(req_type: str) -> str:
    return {
        "functional": "通过功能测试和边界测试验证：对有效输入执行目标行为时，应输出预期结果；对非法输入、失败依赖或前置条件不满足场景，应返回定义错误并保持无关状态不被意外修改。",
        "interface": "通过接口测试和集成测试验证：调用接口后应检查返回值、输出参数和外部可观测结果；对非法参数、未初始化和底层访问失败场景，应返回定义错误且不破坏既有状态。",
        "configuration": "通过配置评审、默认值检查和边界测试验证：加载默认配置后应得到期望配置结果；超出有效范围、缺失配置或非法组合时，应拒绝配置并给出定义结果。",
        "timing": "通过时序分析、超时注入和集成测试验证：在定义测量点记录开始和结束时刻，确认满足最小/最大时序约束；超时场景应触发定义错误或恢复动作。",
        "state": "通过状态转换测试验证：在有效触发条件下应进入目标状态并更新可观测状态；非法触发、失败依赖或恢复场景下应保持或回退到定义状态。",
        "safety": "通过安全需求评审和失效场景分析验证：确认安全边界、检测机制和失效响应完整，并且异常场景下的系统反应有可审查证据。",
        "coding": "通过编码规范检查和静态分析验证：确认约束适用于目标文件和接口，违规项能够被工具或评审记录识别并产出结果。",
        "resource": "通过资源统计、评审或集成测试验证：在目标构建和典型运行场景下记录资源占用结果，并确认未超出定义预算或限制。",
    }.get(req_type, "通过评审、分析或测试验证，并给出可观测结果。")


def _timing_description(constraint: str, minimum: str, maximum: str) -> str:
    lowered = constraint.lower()
    if constraint.startswith("软件"):
        return constraint.rstrip("。") + "。"
    if "err_n" in lowered and minimum:
        return f"软件应在采样 ERR_N 前至少等待 {minimum}。"
    if minimum and maximum:
        return f"软件应满足 {minimum} 到 {maximum} 的时序约束。"
    if minimum:
        return f"软件应满足最小 {minimum} 的时序约束。"
    if maximum:
        return f"软件应满足最大 {maximum} 的时序约束。"
    return f"软件应满足以下时序约束：{constraint}。"


def _project_value(value: str) -> str:
    if not value or value == "Project input required":
        return "需项目输入确认"
    return value


def _append_suffix(value: str, suffix: str) -> str:
    return value if value.endswith(suffix) else f"{value}{suffix}"


def _interface_description(interface: str) -> str:
    if "初始化" in interface or "Init" in interface:
        return "软件应提供初始化接口，用于加载项目配置、建立 I2C 访问上下文、配置 GPIO 默认状态，并在配置非法或初始化失败时返回错误。"
    if "MainFunction" in interface or "周期调度" in interface:
        return "软件应提供 MainFunction 接口，用于周期推进异步请求、处理超时、刷新运行时状态和执行诊断轮询，接口不得执行长时间阻塞操作。"
    if "输入读取" in interface:
        return "软件应提供 GPIO 输入读取接口，用于按项目定义的 pin 或 port 粒度返回 GPIO 输入状态，并对非法参数或方向不匹配返回错误。"
    if "输出写入" in interface:
        return "软件应提供 GPIO 输出写入接口，用于按项目定义的 pin 或 port 粒度设置 GPIO 输出电平，并对非法参数、方向不匹配或写入失败返回错误。"
    if "配置" in interface:
        return "软件应提供 GPIO 配置接口，用于设置项目允许的方向和极性配置，并拒绝未授权的运行时配置变更。"
    return f"软件应提供 `{interface}`，并定义输入参数、输出结果、返回值和错误处理。"


def _planned_verification(name: str, req_type: str) -> str:
    if "初始化" in name or "Init" in name:
        return "通过初始化接口测试验证：在加载默认配置时应完成上下文建立和默认状态设置；注入非法配置、I2C 初始化失败和重复初始化场景时，应返回定义错误，且已建立状态不得被部分破坏。"
    if "MainFunction" in name or "周期调度" in name:
        return "通过周期调度和集成测试验证：周期调用 MainFunction 时应推进异步请求、处理超时并刷新运行时状态；当无待处理任务时不得产生额外状态变化；注入超时和诊断轮询场景时应得到定义结果。"
    if "输入" in name and req_type in {"functional", "interface"}:
        return "通过功能测试和边界测试验证：模拟输入寄存器值和极性配置后，接口应返回与目标 pin/port 一致的输入状态；非法参数、方向不匹配或底层访问失败时，应返回定义错误并保持缓存状态一致。"
    if "输出" in name and req_type in {"functional", "interface"}:
        return "通过功能测试和集成测试验证：对目标 pin/port 执行输出写入后，应仅改变目标 bit 的可观测输出结果；读改写过程中其他 bit 不得被破坏；非法方向、非法参数或 I2C 写失败时，应返回定义错误并保持原输出状态。"
    if "极性" in name:
        return "通过配置测试和边界测试验证：加载默认极性后应得到期望读写语义；切换反转极性时应只影响定义范围内的输入解释结果；未授权运行时修改或非法组合时应被拒绝并保留原配置。"
    if "I2C" in name or "寄存器" in name:
        return "通过接口测试和故障注入测试验证：寄存器读写成功时应返回期望结果并更新相关状态；注入 NACK、timeout 或总线错误时，应返回定义错误并保持软件状态与硬件可观测状态一致。"
    if "默认配置" in name or "地址" in name or req_type == "configuration":
        return "通过配置评审和边界测试验证：默认值加载后应形成定义配置结果；有效范围内的配置应被接受并生效；超范围、缺失或冲突配置时，应拒绝生效并给出定义结果。"
    if "状态" in name or "模式" in name:
        return "通过状态转换测试验证：在定义触发条件下应进入目标状态并更新状态观测结果；无效触发、错误恢复和重新初始化场景下，应保持或回退到定义状态。"
    if "中断" in name or "复位" in name:
        return "通过中断、复位和错误恢复场景测试验证：触发中断或复位后应产生定义状态变化或恢复动作；故障恢复完成前不得误报成功；恢复完成后应能重新进入定义运行状态。"
    if req_type == "timing":
        return "通过时序分析、超时注入和集成测试验证：在定义测量点记录等待、超时或采样间隔，确认满足最小/最大时序要求；超时到达时应触发定义错误处理。"
    return _default_verification(req_type)


def _refine_verification(
    verification: str,
    *,
    trigger: str = "",
    input_value: str = "",
    output_value: str = "",
    exception: str = "",
    constraint: str = "",
) -> str:
    clauses: list[str] = []
    if trigger:
        clauses.append(f"触发条件覆盖 `{trigger}`")
    if input_value:
        clauses.append(f"输入覆盖 `{input_value}`")
    if output_value:
        clauses.append(f"观测 `{output_value}`")
    if exception:
        clauses.append(f"异常场景覆盖 `{exception}`")
    elif constraint and any(token in constraint for token in ("非法", "错误", "拒绝", "范围", "超时", "失败")):
        clauses.append(f"边界/异常覆盖 `{constraint}`")

    if not clauses:
        return verification

    refined = verification.rstrip("。.")
    return f"{refined}；至少覆盖：{'；'.join(clauses)}。"
