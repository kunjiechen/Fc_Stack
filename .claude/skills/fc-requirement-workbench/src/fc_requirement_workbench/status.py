"""Shared requirement status helpers for bundle and SRS rendering."""

from __future__ import annotations

from .builder import EngineeringRequirement
from .rules import ValidationFinding


def compute_requirement_status(
    requirement: EngineeringRequirement,
    findings: list[ValidationFinding] | None = None,
) -> str:
    findings = findings or []
    if any(finding.severity == "error" for finding in findings):
        return "open_issue"
    if _looks_like_open_issue(requirement):
        return "open_issue"
    if _looks_like_draft(requirement, findings):
        return "draft"
    return "ready"


def render_status_label(status: str) -> str:
    mapping = {
        "ready": "Ready",
        "draft": "Draft",
        "open_issue": "Open Issue",
    }
    return mapping.get(status, "Draft")


def _looks_like_open_issue(requirement: EngineeringRequirement) -> bool:
    status_text = " ".join(
        [
            requirement.description,
            requirement.constraint,
            requirement.pre_condition,
            requirement.trigger,
            requirement.input,
            requirement.output,
            requirement.exception,
            requirement.verification,
            _source_summary(requirement),
        ]
    ).lower()
    return any(
        token in status_text
        for token in (
            "needs review",
            "project input required",
            "open issue",
            "缺失输入",
            "需确认",
            "需项目输入确认",
        )
    )


def _looks_like_draft(
    requirement: EngineeringRequirement,
    findings: list[ValidationFinding],
) -> bool:
    if _is_candidate_requirement(requirement):
        return True
    status_text = " ".join(
        [
            requirement.description,
            requirement.constraint,
            requirement.pre_condition,
            requirement.trigger,
            requirement.input,
            requirement.output,
            requirement.exception,
            requirement.verification,
            _source_summary(requirement),
        ]
    ).lower()
    if any(
        token in status_text
        for token in ("draft candidate", "required inputs:", "draft template default")
    ):
        return True
    if findings or requirement.validation:
        return True
    if not requirement.source or not requirement.description:
        return True
    if _should_hold_as_draft(requirement):
        return True
    return False


def _is_candidate_requirement(requirement: EngineeringRequirement) -> bool:
    return any(
        source.get("document") in {"RequirementCandidate", "RequirementPlan"}
        or str(source.get("chunk_id", "")).startswith("CAND-")
        for source in requirement.source
    )


def _should_hold_as_draft(requirement: EngineeringRequirement) -> bool:
    if requirement.requirement_id.endswith("9001"):
        return False
    title = requirement.title.strip()
    generic_titles = {
        "初始化",
        "模式控制",
        "配置管理",
        "状态读取",
        "初始化配置",
        "模式控制配置",
        "配置管理配置",
    }
    if title not in generic_titles:
        return False
    if requirement.requirement_type not in {"functional", "configuration"}:
        return False
    if requirement.requirement_type == "configuration":
        return True
    if requirement.trigger or requirement.input or requirement.output or requirement.exception:
        return False
    return True


def _source_summary(requirement: EngineeringRequirement) -> str:
    parts: list[str] = []
    for source in requirement.source:
        parts.append(str(source.get("document", "")))
        parts.append(str(source.get("chunk_id", "")))
        parts.append(str(source.get("evidence", "")))
    return " ".join(part for part in parts if part)
