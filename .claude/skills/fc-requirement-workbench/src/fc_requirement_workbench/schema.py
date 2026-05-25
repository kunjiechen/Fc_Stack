"""Phase-1 semantic data structures.

These objects intentionally stay close to the requested intermediate schema.
They are not SRS objects and do not contain builder, ASPICE, or complex trace
fields.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


RequirementType = Literal[
    "functional",
    "interface",
    "configuration",
    "timing",
    "state",
]


@dataclass(frozen=True)
class SourceRef:
    document: str
    chunk_id: str
    heading_path: list[str] = field(default_factory=list)
    content_type: str = "paragraph"
    line_start: int | None = None
    line_end: int | None = None
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FunctionalRequirementObject:
    id: str
    type: Literal["functional"]
    name: str
    description: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    source: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class InterfaceRequirementObject:
    id: str
    type: Literal["interface"]
    interface_name: str
    direction: str
    dependency: str
    evidence: str
    function_name: str = ""
    source: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class ConfigurationRequirementObject:
    id: str
    type: Literal["configuration"]
    config_name: str
    range: str
    default: str
    dependency: str
    source: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class TimingRequirementObject:
    id: str
    type: Literal["timing"]
    constraint: str
    minimum: str
    maximum: str
    source: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class StateRequirementObject:
    id: str
    type: Literal["state"]
    state_name: str
    transition: list[str] = field(default_factory=list)
    dependency: list[str] = field(default_factory=list)
    source: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


RequirementObject = (
    FunctionalRequirementObject
    | InterfaceRequirementObject
    | ConfigurationRequirementObject
    | TimingRequirementObject
    | StateRequirementObject
)


def _to_dict(value: Any) -> dict[str, Any]:
    data = asdict(value)
    if "source" in data:
        data["source"] = [src if isinstance(src, dict) else asdict(src) for src in value.source]
    return data


def requirement_from_dict(data: dict[str, Any]) -> RequirementObject:
    sources = [
        SourceRef(
            document=source.get("document", ""),
            chunk_id=source.get("chunk_id", ""),
            heading_path=source.get("heading_path", []),
            content_type=source.get("content_type", "paragraph"),
            line_start=source.get("line_start"),
            line_end=source.get("line_end"),
            evidence=source.get("evidence", ""),
        )
        for source in data.get("source", [])
    ]
    requirement_type = data.get("type")
    if requirement_type == "functional":
        return FunctionalRequirementObject(
            id=data["id"],
            type="functional",
            name=data.get("name", ""),
            description=data.get("description", ""),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            constraints=data.get("constraints", []),
            source=sources,
        )
    if requirement_type == "interface":
        return InterfaceRequirementObject(
            id=data["id"],
            type="interface",
            interface_name=data.get("interface_name", ""),
            direction=data.get("direction", ""),
            dependency=data.get("dependency", ""),
            evidence=data.get("evidence", ""),
            function_name=data.get("function_name", ""),
            source=sources,
        )
    if requirement_type == "configuration":
        return ConfigurationRequirementObject(
            id=data["id"],
            type="configuration",
            config_name=data.get("config_name", ""),
            range=data.get("range", ""),
            default=data.get("default", ""),
            dependency=data.get("dependency", ""),
            source=sources,
        )
    if requirement_type == "timing":
        return TimingRequirementObject(
            id=data["id"],
            type="timing",
            constraint=data.get("constraint", ""),
            minimum=data.get("minimum", ""),
            maximum=data.get("maximum", ""),
            source=sources,
        )
    if requirement_type == "state":
        return StateRequirementObject(
            id=data["id"],
            type="state",
            state_name=data.get("state_name", ""),
            transition=data.get("transition", []),
            dependency=data.get("dependency", []),
            source=sources,
        )
    raise ValueError(f"Unsupported requirement type: {requirement_type}")


def requirements_from_payload(payload: dict[str, Any] | list[dict[str, Any]]) -> list[RequirementObject]:
    items = payload.get("requirements", []) if isinstance(payload, dict) else payload
    return [requirement_from_dict(item) for item in items]


# ---------------------------------------------------------------------------
# RAWREQ data models — 原始开发需求文档的语义对象
# ---------------------------------------------------------------------------

RawReqCategory = Literal["FUNC", "INTF", "CFG", "NFR"]
RawReqSource = Literal["user", "datasheet", "enriched"]


@dataclass
class RawRequirementEntry:
    """单条原始需求条目，覆盖 FUNC/INTF/CFG/NFR 四类"""
    id: str
    category: RawReqCategory
    title: str
    description: str
    source: RawReqSource = "datasheet"
    source_detail: str = ""
    priority: str = "Medium"
    status: str = "Draft"
    confidence: str = "Inferred"
    inputs: str | None = None
    outputs: str | None = None
    return_value: str | None = None
    exceptions: str | None = None
    config_timing: str | None = None
    default_value: str | None = None
    valid_range: str | None = None
    error_handling: str | None = None
    nfr_category: str | None = None
    constraint_value: str | None = None
    verification_suggestion: str | None = None
    notes: str | None = None
    disposition: str = "formal_requirement"
    gate_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RawRequirementDocument:
    """完整的原始开发需求文档"""
    doc_id: str
    module_name: str
    module_abbr: str
    layer: str = "IoExtDrv"
    source: str = ""
    project: str = "FcStack"
    safety_level: str = "QM"
    status: str = "Draft"
    date: str = ""
    functional_reqs: list[RawRequirementEntry] = field(default_factory=list)
    interface_reqs: list[RawRequirementEntry] = field(default_factory=list)
    config_reqs: list[RawRequirementEntry] = field(default_factory=list)
    nfr_reqs: list[RawRequirementEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "module_name": self.module_name,
            "module_abbr": self.module_abbr,
            "layer": self.layer,
            "source": self.source,
            "project": self.project,
            "safety_level": self.safety_level,
            "status": self.status,
            "date": self.date,
            "functional_reqs": [r.to_dict() for r in self.functional_reqs],
            "interface_reqs": [r.to_dict() for r in self.interface_reqs],
            "config_reqs": [r.to_dict() for r in self.config_reqs],
            "nfr_reqs": [r.to_dict() for r in self.nfr_reqs],
        }


@dataclass
class CoverageReport:
    """覆盖检查报告"""
    total_user_reqs: int = 0
    covered: int = 0
    uncovered: list[str] = field(default_factory=list)
    coverage_rate: float = 0.0
    is_satisfied: bool = False
    gaps_detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RawInputEntry:
    """归一化后的输入条目"""
    raw_text: str
    likely_category: str | None = None
    structured_fields: dict[str, str] = field(default_factory=dict)
    source_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UnifiedRawInput:
    """多源归一化输入"""
    source_type: str
    source_name: str
    module_hints: dict[str, str] = field(default_factory=dict)
    entries: list[RawInputEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_name": self.source_name,
            "module_hints": self.module_hints,
            "entries": [e.to_dict() for e in self.entries],
        }
