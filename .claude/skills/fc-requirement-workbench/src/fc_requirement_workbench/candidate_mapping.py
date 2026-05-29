"""Feature-to-requirement candidate mapping intermediate layer."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from .feature_extraction import FeatureRecord, SubfunctionRecord


@dataclass(frozen=True)
class RequirementCandidate:
    candidate_id: str
    source_feature_id: str
    source_feature: str
    source_subfunction: str
    candidate_type: str
    mapping_reason: str
    evidence_level: str
    software_responsibility: str
    software_actions: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    ready_conditions: list[str] = field(default_factory=list)
    status: str = "Needs Review"
    can_promote_to_requirement: str = "Needs Review"
    target_requirement_fields: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementCandidateMapper:
    """Map aggregated feature groups and subfunctions to reviewable candidates."""

    def __init__(self, module: str = "FC") -> None:
        self.module = _module_token(module)

    def map(self, features: list[FeatureRecord]) -> list[RequirementCandidate]:
        groups = [feature for feature in features if feature.type == "feature_group"]
        counters: Counter[str] = Counter()
        candidates: list[RequirementCandidate] = []
        for group in groups:
            if group.subfunctions:
                for subfunction in group.subfunctions:
                    candidates.extend(self._map_subfunction(group, subfunction, counters))
            else:
                candidates.extend(self._map_feature(group, counters))
        return candidates

    def _map_subfunction(
        self,
        feature: FeatureRecord,
        subfunction: SubfunctionRecord,
        counters: Counter[str],
    ) -> list[RequirementCandidate]:
        requirement_types = subfunction.candidate_requirement_types or feature.candidate_requirement_types
        required_inputs = _unique([*feature.missing_inputs, *subfunction.missing_inputs])
        ready_conditions = _ready_conditions(required_inputs)
        actions = feature.software_actions
        return [
            self._candidate(
                counters,
                feature,
                subfunction.name,
                requirement_type,
                _mapping_reason(requirement_type, feature, subfunction),
                actions,
                required_inputs,
                ready_conditions,
                _target_fields(requirement_type, feature, subfunction),
            )
            for requirement_type in requirement_types
        ]

    def _map_feature(
        self,
        feature: FeatureRecord,
        counters: Counter[str],
    ) -> list[RequirementCandidate]:
        return [
            self._candidate(
                counters,
                feature,
                "",
                requirement_type,
                _mapping_reason(requirement_type, feature, None),
                feature.software_actions,
                feature.missing_inputs,
                feature.ready_conditions,
                _target_fields(requirement_type, feature, None),
            )
            for requirement_type in feature.candidate_requirement_types
        ]

    def _candidate(
        self,
        counters: Counter[str],
        feature: FeatureRecord,
        subfunction: str,
        requirement_type: str,
        mapping_reason: str,
        software_actions: list[str],
        required_inputs: list[str],
        ready_conditions: list[str],
        target_fields: dict[str, str],
    ) -> RequirementCandidate:
        type_code = _type_code(requirement_type)
        counters[type_code] += 1
        gate_passed = bool(software_actions)
        can_promote = "Needs Review" if gate_passed else "No"
        status = "Needs Review" if gate_passed else "Blocked"
        return RequirementCandidate(
            candidate_id=f"CAND-{self.module}-{type_code}-{counters[type_code]:04d}",
            source_feature_id=feature.id,
            source_feature=feature.name,
            source_subfunction=subfunction,
            candidate_type=requirement_type,
            mapping_reason=mapping_reason,
            evidence_level=feature.evidence_level,
            software_responsibility=feature.software_responsibility,
            software_actions=software_actions,
            required_inputs=required_inputs,
            ready_conditions=ready_conditions,
            status=status,
            can_promote_to_requirement=can_promote,
            target_requirement_fields=target_fields,
        )


class RequirementCandidateMarkdownRenderer:
    def render(self, candidates: list[RequirementCandidate], module: str = "FC") -> str:
        lines = [
            f"# Requirement Candidate Mapping - {module}",
            "",
            "## Strategy",
            "",
            "- One input feature may map to multiple candidate requirement types.",
            "- Mapping is performed at Feature/Subfunction level to reduce omission and avoid direct Datasheet-to-SRS jumps.",
            "- A candidate is reviewable only when mapping reason, evidence level, software action, required inputs, and Ready conditions are visible.",
            "- Datasheet-only candidates remain `Needs Review` until project evidence confirms scope and software responsibility.",
            "",
            "## Summary",
            "",
            "| Candidate Type | Count |",
            "| --- | ---: |",
        ]
        counts = Counter(candidate.candidate_type for candidate in candidates)
        for candidate_type, count in sorted(counts.items()):
            lines.append(f"| {candidate_type} | {count} |")
        lines.extend(["", "## Candidate Mapping Matrix", ""])
        lines.extend(
            [
                "| Candidate | Feature | Subfunction | Type | Evidence | Software Action Gate | Required Inputs | Status |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for candidate in candidates:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        candidate.candidate_id,
                        candidate.source_feature,
                        candidate.source_subfunction,
                        candidate.candidate_type,
                        candidate.evidence_level,
                        _software_action_gate(candidate),
                        "; ".join(candidate.required_inputs),
                        candidate.status,
                    )
                )
                + " |"
            )
        lines.extend(["", "## Candidate Details", ""])
        for candidate in candidates:
            lines.extend(_candidate_markdown(candidate))
        return "\n".join(lines).rstrip() + "\n"


def _candidate_markdown(candidate: RequirementCandidate) -> list[str]:
    rows = [
        ("Source Feature ID", candidate.source_feature_id),
        ("Source Feature", candidate.source_feature),
        ("Source Subfunction", candidate.source_subfunction),
        ("Candidate Type", candidate.candidate_type),
        ("Mapping Reason", candidate.mapping_reason),
        ("Evidence Level", candidate.evidence_level),
        ("Software Responsibility", candidate.software_responsibility),
        ("Software Actions", ", ".join(candidate.software_actions)),
        ("Required Inputs", "; ".join(candidate.required_inputs)),
        ("Ready Conditions", "; ".join(candidate.ready_conditions)),
        ("Can Promote To Requirement", candidate.can_promote_to_requirement),
        ("Status", candidate.status),
        ("Target Requirement Fields", _fields_summary(candidate.target_requirement_fields)),
    ]
    lines = [f"### {candidate.candidate_id} {candidate.source_subfunction or candidate.source_feature}", ""]
    lines.extend(["| 字段 | 内容 |", "| --- | --- |"])
    for key, value in rows:
        if value:
            lines.append(f"| {key} | {_escape(value)} |")
    lines.append("")
    return lines


def _mapping_reason(
    requirement_type: str,
    feature: FeatureRecord,
    subfunction: SubfunctionRecord | None,
) -> str:
    subject = subfunction.name if subfunction else feature.name
    if "接口" in requirement_type:
        return f"{subject} has software entry, input/output, parameter, or error semantics that may require an interface requirement."
    if "配置" in requirement_type:
        return f"{subject} depends on default value, range, mapping, or runtime policy that may require a configuration requirement."
    if "功能" in requirement_type:
        return f"{subject} describes observable software behavior that may require a functional requirement."
    if "状态" in requirement_type:
        return f"{subject} affects initialization, reset, configured, error, or runtime state."
    if "诊断" in requirement_type:
        return f"{subject} includes error, interrupt, status, rejection, or reporting behavior."
    if "时序" in requirement_type:
        return f"{subject} includes wait, timeout, sampling, stabilization, or timing responsibility."
    if "非功能" in requirement_type or "资源" in requirement_type:
        return f"{subject} constrains resource, performance, timing, or acceptance boundaries."
    return f"{subject} is mapped for review because the feature declares candidate type {requirement_type}."


def _target_fields(
    requirement_type: str,
    feature: FeatureRecord,
    subfunction: SubfunctionRecord | None,
) -> dict[str, str]:
    subject = subfunction.name if subfunction else feature.name
    summary = subfunction.summary if subfunction else feature.functional_summary
    boundary = subfunction.boundary if subfunction else feature.gap
    fields = {
        "Title": subject,
        "Description": summary,
        "Source": feature.id,
        "Status": "Needs Review",
        "Missing Inputs": "; ".join(feature.missing_inputs),
    }
    if "接口" in requirement_type:
        fields.update(
            {
                "Inputs": subfunction.inputs if subfunction else "",
                "Outputs": subfunction.outputs if subfunction else "",
                "Error Behavior": boundary,
            }
        )
    if "配置" in requirement_type:
        fields.update({"Configuration Item": subject, "Default/Range": "Project input required"})
    if "时序" in requirement_type:
        fields.update({"Timing": subfunction.timing if subfunction else "Project timing responsibility required"})
    if "诊断" in requirement_type:
        diag_fields = {"Diagnostic Signal": subject, "Signal Interpretation": boundary}
        # Carry structured fault rows parsed from datasheet fault summary tables
        if subfunction and subfunction.fault_rows:
            diag_fields["FaultRows"] = "\n".join(subfunction.fault_rows)
        fields.update(diag_fields)
    return fields


def _ready_conditions(required_inputs: list[str]) -> list[str]:
    return [
        "Evidence reaches L1/L2 or L3 Datasheet evidence is confirmed by project input",
        "At least one software action is explicit",
        "Mapping reason is non-empty and reviewed",
        "construction-rules.md mandatory fields are complete",
        *[f"Provide: {item}" for item in required_inputs],
    ]


def _software_action_gate(candidate: RequirementCandidate) -> str:
    if candidate.software_actions:
        return "Pass: " + ", ".join(candidate.software_actions)
    return "Blocked: no software action"


def _fields_summary(fields: dict[str, str]) -> str:
    return "; ".join(f"{key}={value}" for key, value in fields.items() if value)


def _type_code(requirement_type: str) -> str:
    if "功能" in requirement_type:
        return "FUNC"
    if "接口" in requirement_type:
        return "IF"
    if "配置" in requirement_type:
        return "CFG"
    if "状态" in requirement_type:
        return "STATE"
    if "诊断" in requirement_type:
        return "DIAG"
    if "时序" in requirement_type:
        return "TIME"
    if "安全" in requirement_type:
        return "SAFE"
    if "资源" in requirement_type or "非功能" in requirement_type:
        return "NF"
    return "REQ"


def _module_token(value: str) -> str:
    token = "".join(ch for ch in value.upper() if ch.isalnum())
    return token or "FC"


def _unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = item.strip()
        if not value or value.lower() in seen:
            continue
        seen.add(value.lower())
        result.append(value)
    return result


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
