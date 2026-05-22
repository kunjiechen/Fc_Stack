"""Requirement planning layer for author-quality SRS generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .candidate_pruner import CandidatePruningResult, RequiredInputItem
from .schema import (
    ConfigurationRequirementObject,
    FunctionalRequirementObject,
    InterfaceRequirementObject,
    RequirementObject,
    SourceRef,
    StateRequirementObject,
    TimingRequirementObject,
)


@dataclass(frozen=True)
class RequirementPlanItem:
    domain: str
    include_in_srs: str
    planned_requirements: list[str] = field(default_factory=list)
    merge_strategy: str = ""
    authoring_strategy: str = ""
    verification_strategy: str = ""
    missing_inputs: list[str] = field(default_factory=list)
    source_candidates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequirementPlanningResult:
    module: str
    plan_items: list[RequirementPlanItem]
    requirements: list[RequirementObject]
    required_inputs: list[RequiredInputItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "plan_items": [item.to_dict() for item in self.plan_items],
            "requirements": [requirement.to_dict() for requirement in self.requirements],
            "required_inputs": [item.to_dict() for item in self.required_inputs],
        }


class RequirementPlanner:
    """Plan a compact set of SRS requirements from pruned candidates."""

    def __init__(self, module: str = "FC") -> None:
        self.display_module = module
        self.module = _module_token(module)

    def plan(self, pruning: CandidatePruningResult | None) -> RequirementPlanningResult:
        required_inputs = pruning.required_inputs if pruning else []
        candidates = pruning.retained_candidates if pruning else []
        by_family = _candidate_index(candidates)

        items = _generic_plan_items(by_family)
        requirements = _generic_requirements(self.module, items)

        return RequirementPlanningResult(
            module=self.display_module,
            plan_items=items,
            requirements=requirements,
            required_inputs=required_inputs,
        )


class RequirementPlanningMarkdownRenderer:
    def render(self, result: RequirementPlanningResult) -> str:
        lines = [
            f"# Requirement Planning - {result.module}",
            "",
            "## Strategy",
            "",
            "- 本阶段从需求制定者角度规划 SRS，不直接照搬候选需求。",
            "- 先定义驱动能力域，再决定每个能力域进入 SRS 的条目数量、合并策略和验证策略。",
            "- SRS 正文不得出现候选、证据等级、映射过程等中间态内容。",
            "- 当项目输入不足时，规划项保留缺失输入，SRS 条目状态保持 Open Issue。",
            "",
            "## Planning Matrix",
            "",
            "| 能力域 | 是否进入 SRS | 规划需求 | 合并策略 | 编写策略 | 验证策略 | 缺失输入 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for item in result.plan_items:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        item.domain,
                        item.include_in_srs,
                        "; ".join(item.planned_requirements),
                        item.merge_strategy,
                        item.authoring_strategy,
                        item.verification_strategy,
                        "; ".join(item.missing_inputs),
                    )
                )
                + " |"
            )

        lines.extend(["", "## Planned SRS Requirement Objects", ""])
        lines.extend(["| ID | Type | Name | Description |", "| --- | --- | --- | --- |"])
        for requirement in result.requirements:
            data = requirement.to_dict()
            name = data.get("name") or data.get("interface_name") or data.get("config_name") or data.get("state_name") or data.get("constraint", "")
            description = data.get("description") or data.get("dependency") or data.get("constraint", "")
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        data.get("id", ""),
                        data.get("type", ""),
                        name,
                        description,
                    )
                )
                + " |"
            )

        lines.extend(["", "## Required Inputs for Ready SRS", ""])
        lines.extend(["| 缺失项 | 影响候选 | 影响类别 | 建议提供方 | 示例 |", "| --- | --- | --- | --- | --- |"])
        for item in result.required_inputs:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        item.missing_input,
                        "; ".join(item.affected_candidates),
                        "; ".join(item.affected_types),
                        item.owner_hint,
                        item.example,
                    )
                )
                + " |"
            )
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def _generic_plan_items(by_family: dict[str, list[str]]) -> list[RequirementPlanItem]:
    return [
        RequirementPlanItem(
            domain=_DOMAIN_CN.get(family, family),
            include_in_srs="是",
            planned_requirements=_DOMAIN_PLANNED.get(family, ["按能力域规划需求"]),
            merge_strategy=_DOMAIN_MERGE_STRATEGY.get(family, "合并同族候选，保留可验证的软件行为。"),
            authoring_strategy="按条件、行为、边界、异常和验证方法编写。",
            verification_strategy="按输入输出和异常路径设计评审/测试验证。",
            source_candidates=candidates,
        )
        for family, candidates in sorted(by_family.items())
    ]


def _generic_requirements(module: str, items: list[RequirementPlanItem]) -> list[RequirementObject]:
    source = _source("PLAN-GENERIC")
    result: list[RequirementObject] = []
    for index, item in enumerate(items, start=1):
        req_type = _DOMAIN_TYPE.get(item.domain, "functional")
        result.append(_build_typed_requirement(module, index, item, req_type, source))
    return result


def _candidate_index(candidates: list[Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for candidate in candidates:
        family = _family(candidate)
        result.setdefault(family, []).append(candidate.candidate_id)
    return result


def _family(candidate: Any) -> str:
    text = f"{candidate.source_feature} {candidate.source_subfunction}".lower()
    if "polarity" in text or "inversion" in text:
        return "gpio_polarity"
    if "direction" in text or "configuration" in text:
        return "gpio_direction"
    if "output" in text and ("write" in text or "port" in text or "pin" in text):
        return "gpio_output_write"
    if "input" in text and ("read" in text or "port" in text or "pin" in text):
        return "gpio_input_read"
    if "i2c" in text or "register" in text:
        return "register_access"
    if "interrupt" in text or "diagnostic" in text:
        return "interrupt_diagnostic"
    if "reset" in text or "power-on" in text:
        return "reset_default"
    if "timing" in text or "timeout" in text or "wait" in text:
        return "timing_guard"
    if "invalid" in text or "reserved" in text or "unsupported" in text:
        return "invalid_rejection"
    return "other"


def _source(chunk_id: str) -> SourceRef:
    return SourceRef(
        document="RequirementPlan",
        chunk_id=chunk_id,
        heading_path=["Requirement Planning"],
        content_type="planning",
        evidence="Planned from feature and candidate intermediate artifacts.",
    )


def _module_token(value: str) -> str:
    token = "".join(ch for ch in value.upper() if ch.isalnum())
    return token or "FC"


# ---------------------------------------------------------------------------
# Domain mapping: family key → Chinese name, planned requirements, merge strategy, requirement type
# ---------------------------------------------------------------------------

_DOMAIN_CN: dict[str, str] = {
    "gpio_direction": "GPIO 方向配置",
    "gpio_input_read": "GPIO 输入读取",
    "gpio_output_write": "GPIO 输出写入",
    "gpio_polarity": "GPIO 极性反转",
    "register_access": "I2C 寄存器访问",
    "interrupt_diagnostic": "中断与诊断",
    "reset_default": "复位与默认状态",
    "timing_guard": "时序约束",
    "invalid_rejection": "边界与异常处理",
    "other": "其他功能",
}

_DOMAIN_PLANNED: dict[str, list[str]] = {
    "gpio_direction": ["1 条方向配置需求", "1 条方向读取接口需求"],
    "gpio_input_read": ["1 条输入读取接口需求"],
    "gpio_output_write": ["1 条输出写入接口需求"],
    "gpio_polarity": ["1 条极性配置需求"],
    "register_access": ["1 条 I2C 读写接口需求"],
    "interrupt_diagnostic": ["1 条诊断读取接口需求", "1 条中断处理需求"],
    "reset_default": ["1 条复位行为需求", "1 条默认状态需求"],
    "timing_guard": ["1 条时序约束需求"],
    "invalid_rejection": ["1 条异常拒绝需求"],
    "other": ["按能力域规划需求"],
}

_DOMAIN_MERGE_STRATEGY: dict[str, str] = {
    "gpio_direction": "合并方向配置与方向读取为统一配置接口，保留可验证的软件行为。",
    "gpio_input_read": "合并同族输入读取候选，统一 uint16 Id 寻址语义。",
    "gpio_output_write": "合并同族输出写入候选，确保读改写原子性。",
    "gpio_polarity": "合并极性反转配置候选为一个配置项。",
    "register_access": "合并 I2C 读写候选，定义统一寄存器访问模式。",
    "interrupt_diagnostic": "合并中断与诊断候选，区分芯片级故障与信号级诊断。",
    "reset_default": "合并复位与默认状态候选。",
    "timing_guard": "合并时序候选为统一时序约束。",
    "invalid_rejection": "合并异常拒绝候选，统一错误返回语义。",
}

_DOMAIN_TYPE: dict[str, str] = {
    "gpio_direction": "configuration",
    "gpio_input_read": "interface",
    "gpio_output_write": "interface",
    "gpio_polarity": "configuration",
    "register_access": "interface",
    "interrupt_diagnostic": "diagnostic",
    "reset_default": "state",
    "timing_guard": "timing",
    "invalid_rejection": "functional",
    "other": "functional",
}


def _build_typed_requirement(
    module: str,
    index: int,
    item: RequirementPlanItem,
    req_type: str,
    source: SourceRef,
) -> RequirementObject:
    """Build a typed requirement object based on the domain type."""
    req_id = f"REQ-{module}-{req_type.upper()}-{index:04d}"

    if req_type == "interface":
        iface_name = item.domain.replace("GPIO ", "").replace("I2C ", "")
        return InterfaceRequirementObject(
            id=req_id,
            type="interface",
            interface_name=iface_name,
            direction="output" if "输出" in item.domain or "写入" in item.domain or "访问" in item.domain else "input",
            dependency=f"软件应提供 {item.domain} 接口，定义输入参数、输出结果、返回值和错误处理。",
            evidence="从候选需求合并生成，待项目确认接口粒度和寻址方式。",
            source=[source],
        )

    if req_type == "configuration":
        return ConfigurationRequirementObject(
            id=req_id,
            type="configuration",
            config_name=item.domain,
            range="待确认",
            default="待确认",
            dependency=f"软件应支持 {item.domain} 的可配置能力，并定义默认值、取值范围和非法值处理规则。",
            source=[source],
        )

    if req_type == "timing":
        return TimingRequirementObject(
            id=req_id,
            type="timing",
            constraint=item.domain,
            minimum="待确认",
            maximum="待确认",
            source=[source],
        )

    if req_type == "state":
        return StateRequirementObject(
            id=req_id,
            type="state",
            state_name=item.domain,
            transition=[],
            dependency=[f"软件应定义 {item.domain} 的状态行为、触发条件和恢复策略。"],
            source=[source],
        )

    if req_type == "diagnostic":
        return FunctionalRequirementObject(
            id=req_id,
            type="diagnostic",
            name=item.domain,
            description=f"软件应支持 {item.domain} 相关的诊断、故障观测或错误处理行为，并定义故障读取接口和恢复策略。",
            constraints=["需确认：诊断覆盖目标、故障读取接口粒度和上报路径"],
            source=[source],
        )

    # functional (default)
    return FunctionalRequirementObject(
        id=req_id,
        type="functional",
        name=item.domain,
        description=f"软件应实现 {item.domain} 相关行为，并定义输入、输出、边界条件和异常处理。",
        constraints=["需确认：项目使用范围、接口粒度、错误返回语义和验证方法"],
        source=[source],
    )


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
