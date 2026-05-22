"""Candidate pruning and compression intermediate layer."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any

from .candidate_mapping import RequirementCandidate


@dataclass(frozen=True)
class CandidatePruningDecision:
    candidate_id: str
    decision: str
    cluster: str
    retained_by: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequiredInputItem:
    missing_input: str
    affected_candidates: list[str] = field(default_factory=list)
    affected_types: list[str] = field(default_factory=list)
    owner_hint: str = ""
    example: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidatePruningResult:
    retained_candidates: list[RequirementCandidate]
    decisions: list[CandidatePruningDecision]
    required_inputs: list[RequiredInputItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "retained_candidates": [candidate.to_dict() for candidate in self.retained_candidates],
            "decisions": [decision.to_dict() for decision in self.decisions],
            "required_inputs": [item.to_dict() for item in self.required_inputs],
        }


class RequirementCandidatePruner:
    """Compress candidates while preserving traceable pruning decisions."""

    def prune(self, candidates: list[RequirementCandidate]) -> CandidatePruningResult:
        clusters: dict[str, list[RequirementCandidate]] = defaultdict(list)
        for candidate in candidates:
            clusters[_cluster_key(candidate)].append(candidate)

        retained: list[RequirementCandidate] = []
        decisions: list[CandidatePruningDecision] = []
        retained_ids: set[str] = set()
        for cluster, items in clusters.items():
            keepers = _select_keepers(items)
            keeper_ids = {candidate.candidate_id for candidate in keepers}
            for candidate in keepers:
                if candidate.candidate_id not in retained_ids:
                    retained.append(candidate)
                    retained_ids.add(candidate.candidate_id)
            primary = next(iter(keeper_ids), "")
            for candidate in items:
                if candidate.candidate_id in keeper_ids:
                    decisions.append(
                        CandidatePruningDecision(
                            candidate_id=candidate.candidate_id,
                            decision="Keep",
                            cluster=cluster,
                            reason=_keep_reason(candidate, items),
                        )
                    )
                else:
                    decisions.append(
                        CandidatePruningDecision(
                            candidate_id=candidate.candidate_id,
                            decision="Merge",
                            cluster=cluster,
                            retained_by=primary,
                            reason=_merge_reason(candidate, primary),
                        )
                    )

        return CandidatePruningResult(
            retained_candidates=sorted(retained, key=lambda candidate: candidate.candidate_id),
            decisions=sorted(decisions, key=lambda decision: decision.candidate_id),
            required_inputs=_required_inputs(retained),
        )


class CandidatePruningMarkdownRenderer:
    def render(self, result: CandidatePruningResult, module: str = "FC") -> str:
        counts = Counter(decision.decision for decision in result.decisions)
        lines = [
            f"# Candidate Pruning - {module}",
            "",
            "## Strategy",
            "",
            "- 候选压缩不丢弃来源证据，只对进入 SRS 草稿的候选做保留、合并或延后决策。",
            "- 功能需求优先保留抽象层次合适的父候选，避免同一行为在父/子功能中重复生成。",
            "- 接口需求优先保留可落地的具体接口候选，聚合接口候选作为合并依据。",
            "- 诊断、安全、资源、编码等暂未完全结构化的候选不硬塞进功能需求，由默认模板或 unsupported 清单承接。",
            "",
            "## Summary",
            "",
            "| Item | Count |",
            "| --- | ---: |",
            f"| Input Candidates | {len(result.decisions)} |",
            f"| Retained Candidates | {len(result.retained_candidates)} |",
        ]
        for decision, count in sorted(counts.items()):
            lines.append(f"| {decision} | {count} |")

        lines.extend(["", "## Pruning Decision Matrix", ""])
        lines.extend(
            [
                "| Candidate | Decision | Cluster | Retained By | Reason |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for decision in result.decisions:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        decision.candidate_id,
                        decision.decision,
                        decision.cluster,
                        decision.retained_by,
                        decision.reason,
                    )
                )
                + " |"
            )

        lines.extend(["", "## Retained Candidate Matrix", ""])
        lines.extend(
            [
                "| Candidate | Type | Feature | Subfunction | Required Inputs | Status |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for candidate in result.retained_candidates:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        candidate.candidate_id,
                        candidate.candidate_type,
                        candidate.source_feature,
                        candidate.source_subfunction,
                        "; ".join(candidate.required_inputs),
                        candidate.status,
                    )
                )
                + " |"
            )

        lines.extend(["", "## Required Inputs for Ready SRS", ""])
        lines.extend(
            [
                "| 缺失项 | 影响候选 | 影响类别 | 建议提供方 | 示例 |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
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


def _cluster_key(candidate: RequirementCandidate) -> str:
    return f"{candidate.candidate_type}:{_behavior_family(candidate)}"


def _behavior_family(candidate: RequirementCandidate) -> str:
    subject_text = " ".join([candidate.source_feature, candidate.source_subfunction]).lower()
    family = _family_from_text(subject_text)
    if family:
        return family
    fallback_text = " ".join(
        [
            candidate.mapping_reason,
            " ".join(candidate.target_requirement_fields.values()),
        ]
    ).lower()
    return _family_from_text(fallback_text) or _normalize(candidate.source_subfunction or candidate.source_feature)


def _family_from_text(text: str) -> str:
    if "invalid" in text or "reserved" in text or "unsupported" in text or "rejection" in text:
        return "invalid_rejection"
    if "interrupt" in text or "diagnostic" in text:
        return "interrupt_diagnostic"
    if "reset" in text or "power-on" in text:
        return "reset_default"
    if "timing" in text or "timeout" in text or "wait" in text:
        return "timing_guard"
    if "polarity" in text or "inversion" in text:
        return "gpio_polarity"
    if "direction" in text or "configuration register" in text:
        return "gpio_direction"
    if "register" in text and ("read" in text or "write" in text or "address" in text):
        return "register_access"
    if "output" in text and ("write" in text or "level" in text or "port" in text or "pin" in text):
        return "gpio_output_write"
    if "input" in text and ("read" in text or "port" in text or "pin" in text):
        return "gpio_input_read"
    return ""


def _select_keepers(items: list[RequirementCandidate]) -> list[RequirementCandidate]:
    if len(items) <= 1:
        return items
    candidate_type = items[0].candidate_type
    if "接口" in candidate_type:
        aggregate = [
            item
            for item in items
            if item.source_feature == "16-bit GPIO Port Capability"
            or item.source_subfunction.lower().startswith("gpio ")
        ]
        return [_best_candidate(aggregate or items)]
    if "功能" in candidate_type:
        parent = [
            item
            for item in items
            if item.source_feature == "16-bit GPIO Port Capability"
            or item.source_subfunction.lower().startswith("gpio ")
        ]
        return [_best_candidate(parent or items)]
    if "配置" in candidate_type:
        parent = [
            item
            for item in items
            if item.source_feature in {"16-bit GPIO Port Capability", "Register Map", "Reset and Default State"}
        ]
        return [_best_candidate(parent or items)]
    return [_best_candidate(items)]


def _best_candidate(items: list[RequirementCandidate]) -> RequirementCandidate:
    return sorted(items, key=lambda candidate: (_priority(candidate), candidate.candidate_id))[0]


def _priority(candidate: RequirementCandidate) -> tuple[int, int]:
    evidence_rank = {"L1": 0, "L2": 1, "L3": 2, "L4": 3, "L5": 4}
    evidence = candidate.evidence_level.split(" ", 1)[0]
    missing = len(candidate.required_inputs)
    return (evidence_rank.get(evidence, 9), missing)


def _keep_reason(candidate: RequirementCandidate, items: list[RequirementCandidate]) -> str:
    if len(items) == 1:
        return "无同族重复候选，保留进入后续提升。"
    if "接口" in candidate.candidate_type:
        return "接口候选更接近可落地 API 或 I/O 行为，保留具体接口粒度。"
    if "功能" in candidate.candidate_type:
        return "功能候选作为父行为覆盖同族子功能，避免功能需求重复。"
    if "配置" in candidate.candidate_type:
        return "配置候选作为项目策略入口，保留用于补充默认值、范围和非法值处理。"
    return "同族候选中证据和缺口条件较优，保留。"


def _merge_reason(candidate: RequirementCandidate, retained_by: str) -> str:
    return f"与同族候选存在行为重叠，合并到 {retained_by}，其证据和缺失输入仍保留在裁剪中间产物。"


def _required_inputs(candidates: list[RequirementCandidate]) -> list[RequiredInputItem]:
    grouped: dict[str, list[RequirementCandidate]] = defaultdict(list)
    for candidate in candidates:
        for item in candidate.required_inputs:
            grouped[item].append(candidate)
    result: list[RequiredInputItem] = []
    for missing_input, affected in sorted(grouped.items()):
        result.append(
            RequiredInputItem(
                missing_input=missing_input,
                affected_candidates=[candidate.candidate_id for candidate in affected],
                affected_types=sorted({candidate.candidate_type for candidate in affected}),
                owner_hint=_owner_hint(missing_input),
                example=_example(missing_input),
            )
        )
    return result


def _owner_hint(item: str) -> str:
    text = item.lower()
    if "api" in text or "接口" in item or "返回" in item:
        return "软件架构/接口设计"
    if "pin" in text or "port" in text or "reset" in text or "int" in text:
        return "硬件/软件架构"
    if "默认" in item or "配置" in item or "范围" in item:
        return "项目配置/软件架构"
    if "错误" in item or "nack" in text or "超时" in item:
        return "软件架构/测试"
    return "项目需求"


def _example(item: str) -> str:
    text = item.lower()
    if "api" in text:
        return "Nca9539_ReadPin / Nca9539_WritePort"
    if "pin" in text or "port" in text:
        return "P00-P07 输入，P10-P17 输出"
    if "默认" in item:
        return "默认方向=input，默认输出=low，默认极性=normal"
    if "reset" in text:
        return "RESET 由硬件上拉，软件仅做复位后重新初始化"
    if "错误" in item or "nack" in text or "超时" in item:
        return "I2C NACK/timeout 返回 E_NOT_OK 并记录诊断事件"
    return "按项目约束填写"


def _normalize(value: str) -> str:
    return "_".join(value.lower().split()) or "unknown"


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
