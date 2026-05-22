"""Requirement planning layer for author-quality SRS generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .candidate_pruner import CandidatePruningResult, RequiredInputItem
from .profiles import (
    build_plan_item_specs as build_profile_plan_item_specs,
    build_requirement_objects as build_profile_requirement_objects,
)
from .schema import (
    ConfigurationRequirementObject,
    FunctionalRequirementObject,
    InterfaceRequirementObject,
    RequirementObject,
    SourceRef,
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
        self.module = _module_token(module)

    def plan(self, pruning: CandidatePruningResult | None) -> RequirementPlanningResult:
        required_inputs = pruning.required_inputs if pruning else []
        candidates = pruning.retained_candidates if pruning else []
        by_family = _candidate_index(candidates)

        items = _profile_plan_items(self.module, by_family) or _generic_plan_items(by_family)
        requirements = _profile_requirements(self.module) or _generic_requirements(self.module, items)
        return RequirementPlanningResult(
            module=self.module,
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
            domain=family,
            include_in_srs="是",
            planned_requirements=["按能力域规划需求"],
            merge_strategy="合并同族候选，保留可验证的软件行为。",
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
        result.append(
            FunctionalRequirementObject(
                id=f"REQ-{module}-FUNC-{index:04d}",
                type="functional",
                name=item.domain,
                description=f"软件应实现 {item.domain} 相关行为，并定义输入、输出、边界条件和异常处理。",
                constraints=["需确认：项目使用范围、接口粒度、错误返回语义和验证方法"],
                source=[source],
            )
        )
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


def _profile_plan_items(
    module: str,
    by_family: dict[str, list[str]],
) -> list[RequirementPlanItem] | None:
    specs = build_profile_plan_item_specs(module, by_family)
    if specs is None:
        return None
    return [RequirementPlanItem(**spec) for spec in specs]


def _profile_requirements(module: str) -> list[RequirementObject] | None:
    return build_profile_requirement_objects(module, _source(f"PLAN-{module}"))


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
