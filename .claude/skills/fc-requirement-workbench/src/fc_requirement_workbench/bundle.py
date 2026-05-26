"""Requirement bundle export helpers.

This module adds a structured export layer on top of the existing requirement
pipeline so that SRS markdown is no longer the only consumable output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json
import re
from typing import Any

from .builder import EngineeringRequirement
from .raw_requirements import RawRequirementDocument
from .rules import ValidationFinding
from .status import compute_requirement_status
from .traceability import TraceabilityPackage


@dataclass(frozen=True)
class SourceInventoryEntry:
    source_type: str
    source_name: str
    role: str
    confidence: str = "medium"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModuleIdentity:
    module_name: str
    module_abbr: str
    layer: str
    project: str
    safety_level: str
    input_document: str
    source_root: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GroundingSummary:
    grounding_mode: str
    reference_modules: list[str] = field(default_factory=list)
    adopted_patterns: list[str] = field(default_factory=list)
    rejected_patterns: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GenerationNotes:
    source_root_used: bool
    raw_requirement_input_used: bool
    coverage_gap_count: int
    raw_gate_counts: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequirementBundle:
    module_identity: ModuleIdentity
    source_inventory: list[SourceInventoryEntry]
    grounding_summary: GroundingSummary
    requirements: list["BundleRequirement"]
    raw_gate_summary: "RawGateSummary"
    coverage_matrix: list["CoverageMatrixItem"]
    open_issues: list["OpenIssueItem"]
    architecture_seed: "ArchitectureSeed"
    test_seed: "TestSeed"
    generation_notes: GenerationNotes

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_identity": self.module_identity.to_dict(),
            "source_inventory": [item.to_dict() for item in self.source_inventory],
            "grounding_summary": self.grounding_summary.to_dict(),
            "requirements": [item.to_dict() for item in self.requirements],
            "raw_gate_summary": self.raw_gate_summary.to_dict(),
            "coverage_matrix": [item.to_dict() for item in self.coverage_matrix],
            "open_issues": [item.to_dict() for item in self.open_issues],
            "architecture_seed": self.architecture_seed.to_dict(),
            "test_seed": self.test_seed.to_dict(),
            "generation_notes": self.generation_notes.to_dict(),
        }


@dataclass(frozen=True)
class RequirementTraceInfo:
    source_ids: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    verification_levels: list[str] = field(default_factory=list)
    coverage_status: str = "uncovered"
    linked_raw_items: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BundleRequirement:
    requirement_id: str
    semantic_id: str
    type: str
    bundle_type: str
    title: str
    shall: str
    pre_condition: str = ""
    trigger: str = ""
    input: str = ""
    output: str = ""
    exception: str = ""
    constraint: str = ""
    verification: str = ""
    function_name: str = ""
    source: list[dict[str, Any]] = field(default_factory=list)
    status: str = "draft"
    decision: str = "needs_confirmation"
    decision_reason: str = ""
    trace: RequirementTraceInfo = field(default_factory=RequirementTraceInfo)
    validation: list[dict[str, Any]] = field(default_factory=list)
    global_validation_context: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["trace"] = self.trace.to_dict()
        return payload


@dataclass(frozen=True)
class GateItem:
    raw_id: str
    category: str
    title: str
    description: str
    gate_reason: str
    source_detail: str
    linked_formal_requirements: list[str] = field(default_factory=list)
    promotion_candidate: bool = False
    promotion_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoverageMatrixItem:
    raw_id: str
    category: str
    title: str
    source: str
    status: str
    matched_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OpenIssueItem:
    type: str
    requirement_id: str = ""
    title: str = ""
    status: str = ""
    reason: str = ""
    severity: str = ""
    rule: str = ""
    recommendation: str = ""
    raw_id: str = ""
    matched_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type}
        if self.requirement_id:
            payload["requirement_id"] = self.requirement_id
        if self.title:
            payload["title"] = self.title
        if self.status:
            payload["status"] = self.status
        if self.reason:
            payload["reason"] = self.reason
        if self.severity:
            payload["severity"] = self.severity
        if self.rule:
            payload["rule"] = self.rule
        if self.recommendation:
            payload["recommendation"] = self.recommendation
        if self.raw_id:
            payload["raw_id"] = self.raw_id
        if self.matched_requirements:
            payload["matched_requirements"] = self.matched_requirements
        return payload


@dataclass(frozen=True)
class RawGateSummary:
    counts: dict[str, int] = field(default_factory=dict)
    formal_requirement_items: list[GateItem] = field(default_factory=list)
    constraint_items: list[GateItem] = field(default_factory=list)
    capability_items: list[GateItem] = field(default_factory=list)
    evidence_items: list[GateItem] = field(default_factory=list)
    metadata_items: list[GateItem] = field(default_factory=list)
    architecture_seed_items: list[GateItem] = field(default_factory=list)
    test_seed_items: list[GateItem] = field(default_factory=list)
    open_issue_items: list[GateItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts,
            "formal_requirement_items": [item.to_dict() for item in self.formal_requirement_items],
            "constraint_items": [item.to_dict() for item in self.constraint_items],
            "capability_items": [item.to_dict() for item in self.capability_items],
            "evidence_items": [item.to_dict() for item in self.evidence_items],
            "metadata_items": [item.to_dict() for item in self.metadata_items],
            "architecture_seed_items": [item.to_dict() for item in self.architecture_seed_items],
            "test_seed_items": [item.to_dict() for item in self.test_seed_items],
            "open_issue_items": [item.to_dict() for item in self.open_issue_items],
        }


@dataclass(frozen=True)
class InterfaceCandidate:
    requirement_id: str
    function_name: str
    purpose: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConfigCandidate:
    requirement_id: str
    name: str
    constraint: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TimingConstraintItem:
    requirement_id: str
    title: str
    constraint: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConcernItem:
    requirement_id: str
    title: str
    description: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PendingConfirmItem:
    requirement_id: str
    title: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArchitectureSeed:
    module_name: str
    layer: str
    external_interface_candidates: list[InterfaceCandidate] = field(default_factory=list)
    config_item_candidates: list[ConfigCandidate] = field(default_factory=list)
    timing_constraints: list[TimingConstraintItem] = field(default_factory=list)
    state_concerns: list[ConcernItem] = field(default_factory=list)
    diagnostic_concerns: list[ConcernItem] = field(default_factory=list)
    pending_confirm_items: list[PendingConfirmItem] = field(default_factory=list)
    constraint_items: list[GateItem] = field(default_factory=list)
    architecture_only_items: list[GateItem] = field(default_factory=list)
    capability_notes: list[GateItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_name": self.module_name,
            "layer": self.layer,
            "external_interface_candidates": [item.to_dict() for item in self.external_interface_candidates],
            "config_item_candidates": [item.to_dict() for item in self.config_item_candidates],
            "timing_constraints": [item.to_dict() for item in self.timing_constraints],
            "state_concerns": [item.to_dict() for item in self.state_concerns],
            "diagnostic_concerns": [item.to_dict() for item in self.diagnostic_concerns],
            "pending_confirm_items": [item.to_dict() for item in self.pending_confirm_items],
            "constraint_items": [item.to_dict() for item in self.constraint_items],
            "architecture_only_items": [item.to_dict() for item in self.architecture_only_items],
            "capability_notes": [item.to_dict() for item in self.capability_notes],
        }


@dataclass(frozen=True)
class VerificationItem:
    requirement_id: str
    title: str
    verification: str
    trigger: str
    input: str
    expected_output: str
    exception_path: str
    acceptance_basis: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TestSeed:
    module_name: str
    verification_items: list[VerificationItem] = field(default_factory=list)
    test_only_items: list[GateItem] = field(default_factory=list)
    excluded_nonfunctional_items: list[GateItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_name": self.module_name,
            "verification_items": [item.to_dict() for item in self.verification_items],
            "test_only_items": [item.to_dict() for item in self.test_only_items],
            "excluded_nonfunctional_items": [item.to_dict() for item in self.excluded_nonfunctional_items],
        }


class RequirementBundleBuilder:
    def build(
        self,
        *,
        module: str,
        input_document: str,
        engineering_requirements: list[EngineeringRequirement],
        findings: list[ValidationFinding],
        traceability: TraceabilityPackage,
        raw_document: RawRequirementDocument | None = None,
        raw_coverage_detail: list[dict[str, Any]] | None = None,
        source_root: str | Path | None = None,
    ) -> RequirementBundle:
        source_root_path = Path(source_root).resolve() if source_root else None
        module_identity = _module_identity(
            module=module,
            input_document=input_document,
            raw_document=raw_document,
            source_root=source_root_path,
        )
        source_inventory = _source_inventory(
            input_document=input_document,
            raw_document=raw_document,
            source_root=source_root_path,
        )
        coverage_matrix = _coverage_matrix_items(raw_coverage_detail or [])
        grounding_summary = _grounding_summary(module, source_root_path)
        requirements = _bundle_requirements(engineering_requirements, findings, traceability, coverage_matrix)
        requirement_dicts = [item.to_dict() for item in requirements]
        raw_gate_summary = _raw_gate_summary(raw_document, coverage_matrix, requirement_dicts)
        open_issues = _open_issues(requirement_dicts, findings, coverage_matrix, raw_gate_summary)
        architecture_seed = _architecture_seed(requirement_dicts, module_identity, raw_gate_summary)
        test_seed = _test_seed(requirement_dicts, module_identity, raw_gate_summary)
        generation_notes = _generation_notes(
            source_root=source_root_path,
            raw_document=raw_document,
            coverage_matrix=coverage_matrix,
            raw_gate_summary=raw_gate_summary,
        )
        return RequirementBundle(
            module_identity=module_identity,
            source_inventory=source_inventory,
            grounding_summary=grounding_summary,
            requirements=requirements,
            raw_gate_summary=raw_gate_summary,
            coverage_matrix=coverage_matrix,
            open_issues=open_issues,
            architecture_seed=architecture_seed,
            test_seed=test_seed,
            generation_notes=generation_notes,
        )


def render_bundle_json(bundle: RequirementBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, RequirementBundle) else bundle
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_bundle_yaml(bundle: RequirementBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, RequirementBundle) else bundle
    return _yaml_dump(payload).rstrip() + "\n"


def render_architecture_seed_yaml(bundle: RequirementBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, RequirementBundle) else bundle
    return _yaml_dump(payload["architecture_seed"]).rstrip() + "\n"


def render_test_seed_yaml(bundle: RequirementBundle | dict[str, Any]) -> str:
    payload = bundle.to_dict() if isinstance(bundle, RequirementBundle) else bundle
    return _yaml_dump(payload["test_seed"]).rstrip() + "\n"


def _module_identity(
    *,
    module: str,
    input_document: str,
    raw_document: RawRequirementDocument | None,
    source_root: Path | None,
) -> ModuleIdentity:
    layer = raw_document.layer if raw_document else _infer_layer_from_path(source_root)
    return ModuleIdentity(
        module_name=raw_document.module_name if raw_document else module,
        module_abbr=raw_document.module_abbr if raw_document else _module_token(module),
        layer=layer or "IoExtDev",
        project=raw_document.project if raw_document else "FcStack",
        safety_level=raw_document.safety_level if raw_document else "QM",
        input_document=input_document,
        source_root=str(source_root) if source_root else "",
    )


def _source_inventory(
    *,
    input_document: str,
    raw_document: RawRequirementDocument | None,
    source_root: Path | None,
) -> list[SourceInventoryEntry]:
    entries = [
        SourceInventoryEntry(
            source_type="markdown",
            source_name=input_document,
            role="datasheet_or_reference_input",
            confidence="high",
            notes="Primary parsed markdown input for the planned SRS pipeline.",
        )
    ]
    if raw_document is not None:
        entries.append(
            SourceInventoryEntry(
                source_type="raw_requirement_input",
                source_name=raw_document.source or raw_document.doc_id,
                role="project_requirement_input",
                confidence="medium",
                notes="User-provided raw requirement input merged into the planned requirements.",
            )
        )
    if source_root is not None:
        module_hits = _module_source_hits(source_root)
        entries.append(
            SourceInventoryEntry(
                source_type="codebase",
                source_name=str(source_root),
                role="implemented_evidence",
                confidence="medium",
                notes=f"Project source root used as implemented evidence; discovered {module_hits} relevant source/config files.",
            )
        )
    return entries


def _grounding_summary(module: str, source_root: Path | None) -> GroundingSummary:
    references: list[str] = []
    patterns: list[str] = []
    if source_root is not None:
        names = _nearby_module_names(source_root)
        references = [name for name in names if name != module][:6]
        lowered = {name.lower() for name in names}
        if any("iomcu" in name for name in lowered):
            patterns.append("iomcu_dependency_integration")
        if any("tpt1145" in name for name in lowered):
            patterns.append("ioextdev_callout_and_register_pattern")
        if any("drv8889" in name for name in lowered):
            patterns.append("ioextdev_fault_and_state_pattern")
    return GroundingSummary(
        grounding_mode="codebase_and_current_artifacts",
        reference_modules=references,
        adopted_patterns=patterns,
        rejected_patterns=[],
        notes=(
            "Current grounding is inferred from the accessible project codebase and the accepted artifact set. "
            "It should be tightened with dedicated FC grounding summaries in the next phase."
        ),
    )


def _bundle_requirements(
    requirements: list[EngineeringRequirement],
    findings: list[ValidationFinding],
    traceability: TraceabilityPackage,
    coverage_matrix: list[CoverageMatrixItem] | None = None,
) -> list[BundleRequirement]:
    findings_by_req: dict[str, list[ValidationFinding]] = {}
    global_findings: list[ValidationFinding] = []
    for finding in findings:
        if finding.requirement_ids:
            for req_id in finding.requirement_ids:
                findings_by_req.setdefault(req_id, []).append(finding)
        else:
            global_findings.append(finding)
    global_findings = [
        finding for finding in global_findings
        if not _is_stale_global_finding(finding, requirements)
    ]

    trace_by_req = {item.requirement_id: item for item in traceability.trace_links}
    coverage_by_req = {item.requirement_id: item for item in traceability.coverage}
    raw_links_by_requirement = _raw_links_by_requirement(coverage_matrix or [])

    items: list[BundleRequirement] = []
    for req in requirements:
        req_findings = findings_by_req.get(req.semantic_id, [])
        status = _requirement_status(req, req_findings)
        items.append(
            BundleRequirement(
                requirement_id=req.requirement_id,
                semantic_id=req.semantic_id,
                type=req.requirement_type,
                bundle_type=_bundle_type(req),
                title=req.title,
                shall=req.description,
                pre_condition=req.pre_condition,
                trigger=req.trigger,
                input=req.input,
                output=req.output,
                exception=req.exception,
                constraint=req.constraint,
                verification=req.verification,
                function_name=req.function_name,
                source=req.source,
                status=status,
                decision=_decision_label(status, req_findings),
                decision_reason=_decision_reason(req_findings),
                trace=RequirementTraceInfo(
                    source_ids=trace_by_req.get(req.requirement_id).source if req.requirement_id in trace_by_req else [],
                    tests=trace_by_req.get(req.requirement_id).test if req.requirement_id in trace_by_req else [],
                    verification_levels=trace_by_req.get(req.requirement_id).verification if req.requirement_id in trace_by_req else [],
                    coverage_status=coverage_by_req.get(req.requirement_id).status if req.requirement_id in coverage_by_req else "uncovered",
                    linked_raw_items=raw_links_by_requirement.get(req.requirement_id, []),
                ),
                validation=[finding.to_dict() for finding in req_findings],
                global_validation_context=[finding.to_dict() for finding in global_findings],
            )
        )
    return items


def _is_stale_global_finding(
    finding: ValidationFinding,
    requirements: list[EngineeringRequirement],
) -> bool:
    text = " ".join(
        " ".join(
            [
                req.title,
                req.description,
                req.constraint,
                req.input,
                req.output,
                req.exception,
                req.function_name,
            ]
        ).lower()
        for req in requirements
    )
    if finding.message == "Mandatory DET requirement is missing.":
        return ("det" in text) or ("开发错误" in text)
    if finding.message == "PWM dependency is incomplete.":
        return ("setduty" in text) and ("getduty" in text)
    if finding.message == "Fault/diagnostic behavior exists without a readable fault or diagnostic interface.":
        return any(token in text for token in ("getdevfault", "getdiag", "故障读取", "诊断读取"))
    if finding.message == "SPI communication exists without SPI dependency requirement.":
        return any(token in text for token in ("spi dependency", "spi communication dependency", "spi 服务", "spi 服务依赖"))
    return False


def _open_issues(
    requirements: list[dict[str, Any]],
    findings: list[ValidationFinding],
    coverage_matrix: list[CoverageMatrixItem],
    raw_gate_summary: RawGateSummary,
) -> list[OpenIssueItem]:
    issues: list[OpenIssueItem] = []
    for req in requirements:
        if req["status"] in {"draft", "open_issue"}:
            issues.append(
                OpenIssueItem(
                    type="requirement_status",
                    requirement_id=req["requirement_id"],
                    title=req["title"],
                    status=req["status"],
                    reason=req["decision_reason"],
                )
            )
    for finding in findings:
        if not finding.requirement_ids and finding.status == "failed":
            issues.append(
                OpenIssueItem(
                    type="global_validation",
                    rule=finding.rule,
                    severity=finding.severity,
                    reason=finding.message,
                    recommendation=finding.recommendation,
                )
            )
    for row in coverage_matrix:
        status = row.status
        if status not in {"covered", "excluded_by_gate"}:
            issues.append(
                OpenIssueItem(
                    type="coverage_gap",
                    raw_id=row.raw_id,
                    title=row.title,
                    status=status or "uncovered",
                    matched_requirements=row.matched_requirements,
                )
            )
    for item in raw_gate_summary.open_issue_items:
        issues.append(
            OpenIssueItem(
                type="raw_open_issue",
                raw_id=item.raw_id,
                title=item.title,
                reason=item.gate_reason,
            )
        )
    return issues


def _architecture_seed(
    requirements: list[dict[str, Any]],
    module_identity: ModuleIdentity,
    raw_gate_summary: RawGateSummary,
) -> ArchitectureSeed:
    interfaces = _dedupe_interface_candidates(requirements)
    return ArchitectureSeed(
        module_name=module_identity.module_name,
        layer=module_identity.layer,
        external_interface_candidates=interfaces,
        config_item_candidates=[
            ConfigCandidate(
                requirement_id=req["requirement_id"],
                name=req["title"],
                constraint=req["constraint"],
                status=req["status"],
            )
            for req in requirements
            if req["type"] == "configuration"
        ],
        timing_constraints=[
            TimingConstraintItem(
                requirement_id=req["requirement_id"],
                title=req["title"],
                constraint=req["shall"],
                status=req["status"],
            )
            for req in requirements
            if req["type"] == "timing"
        ],
        state_concerns=[
            ConcernItem(
                requirement_id=req["requirement_id"],
                title=req["title"],
                description=req["shall"],
                status=req["status"],
            )
            for req in requirements
            if req["type"] == "state"
        ],
        diagnostic_concerns=[
            ConcernItem(
                requirement_id=req["requirement_id"],
                title=req["title"],
                description=req["shall"],
                status=req["status"],
            )
            for req in requirements
            if _is_diagnostic_requirement(req)
        ],
        pending_confirm_items=[
            PendingConfirmItem(
                requirement_id=req["requirement_id"],
                title=req["title"],
                reason=req["decision_reason"],
            )
            for req in requirements
            if req["status"] != "ready"
        ],
        constraint_items=raw_gate_summary.constraint_items,
        architecture_only_items=raw_gate_summary.architecture_seed_items,
        capability_notes=raw_gate_summary.capability_items,
    )


def _test_seed(
    requirements: list[dict[str, Any]],
    module_identity: ModuleIdentity,
    raw_gate_summary: RawGateSummary,
) -> TestSeed:
    return TestSeed(
        module_name=module_identity.module_name,
        verification_items=[
            VerificationItem(
                requirement_id=req["requirement_id"],
                title=req["title"],
                verification=req["verification"],
                trigger=req["trigger"],
                input=req["input"],
                expected_output=req["output"],
                exception_path=req["exception"],
                acceptance_basis=req["constraint"] or req["shall"],
                status=req["status"],
            )
            for req in requirements
            if _is_test_candidate(req)
        ],
        test_only_items=raw_gate_summary.test_seed_items,
        excluded_nonfunctional_items=raw_gate_summary.constraint_items,
    )


def _generation_notes(
    *,
    source_root: Path | None,
    raw_document: RawRequirementDocument | None,
    coverage_matrix: list[CoverageMatrixItem],
    raw_gate_summary: RawGateSummary,
) -> GenerationNotes:
    return GenerationNotes(
        source_root_used=bool(source_root),
        raw_requirement_input_used=bool(raw_document),
        coverage_gap_count=sum(1 for row in coverage_matrix if row.status not in {"covered", "excluded_by_gate"}),
        raw_gate_counts=raw_gate_summary.counts,
        notes=[
            "This bundle is the structured source-of-truth candidate for the requirement skill.",
            "Current grounding uses accessible project source code as implemented evidence, not as unconditional normative truth.",
        ],
    )


def _infer_layer_from_path(source_root: Path | None) -> str:
    if source_root is None:
        return "IoExtDev"
    text = str(source_root)
    if "IoMcu" in text:
        return "IoMcu"
    if "Cdd" in text:
        return "Cdd"
    return "IoExtDev"


def _module_source_hits(source_root: Path) -> int:
    names = _nearby_module_names(source_root)
    return len(names)


def _nearby_module_names(source_root: Path) -> list[str]:
    if not source_root.exists():
        return []
    names: set[str] = set()
    for path in source_root.rglob("Gp_*"):
        if path.is_dir():
            names.add(path.name)
    return sorted(names)


def _module_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]", "", value)
    return token.upper() or "FC"


def _requirement_status(
    requirement: EngineeringRequirement,
    findings: list[ValidationFinding],
) -> str:
    return compute_requirement_status(requirement, findings)


def _decision_label(status: str, findings: list[ValidationFinding]) -> str:
    if status == "ready":
        return "accepted_for_downstream"
    if status == "open_issue":
        return "hold_for_resolution"
    if findings:
        return "needs_refinement"
    return "needs_confirmation"


def _decision_reason(findings: list[ValidationFinding]) -> str:
    if not findings:
        return "Requirement currently has no requirement-level validation findings."
    parts = []
    for finding in findings[:3]:
        parts.append(f"{finding.rule}: {finding.message}")
    return " | ".join(parts)


def _is_diagnostic_requirement(requirement: dict[str, Any]) -> bool:
    text = " ".join(
        [
            requirement.get("title", ""),
            requirement.get("shall", ""),
            requirement.get("function_name", ""),
        ]
    ).lower()
    return any(token in text for token in ("fault", "diag", "error", "故障", "诊断", "det"))


def _bundle_type(requirement: EngineeringRequirement) -> str:
    text = " ".join([requirement.title, requirement.description]).lower()
    if any(token in text for token in ("asil", "安全", "safety")):
        return "safety"
    if any(token in text for token in ("misra", "编码规范", "coding")):
        return "coding"
    if any(token in text for token in ("rom/ram", "resource budget", "资源消耗")):
        return "resource"
    return requirement.requirement_type


def _dedupe_interface_candidates(requirements: list[dict[str, Any]]) -> list[InterfaceCandidate]:
    selected: dict[str, InterfaceCandidate] = {}
    for req in requirements:
        if req["type"] != "interface":
            continue
        name = req["function_name"] or req["title"]
        candidate = InterfaceCandidate(
            requirement_id=req["requirement_id"],
            function_name=name,
            purpose=req["shall"],
            status=req["status"],
        )
        current = selected.get(name)
        if current is None:
            selected[name] = candidate
            continue
        current_score = _interface_candidate_score(current)
        new_score = _interface_candidate_score(candidate)
        if new_score > current_score:
            selected[name] = candidate
    return list(selected.values())


def _interface_candidate_score(candidate: InterfaceCandidate) -> int:
    score = 0
    purpose = candidate.purpose
    name = candidate.function_name
    if candidate.status == "ready":
        score += 10
    if any(token in name for token in ("Init", "MainFunction", "GetDevFaultSig", "GetInSig", "SetOutSig")):
        score += 3
    if "通过 uint16 Id" in purpose or "返回指定芯片实例" in purpose:
        score += 2
    return score


def _is_test_candidate(requirement: dict[str, Any]) -> bool:
    if requirement.get("bundle_type") in {"safety", "coding", "resource"}:
        return False
    title = str(requirement.get("title", ""))
    if any(token in title for token in ("MISRA", "资源", "安全等级", "ROM/RAM")):
        return False
    return True


def _raw_gate_summary(
    raw_document: RawRequirementDocument | None,
    coverage_matrix: list[CoverageMatrixItem],
    requirements: list[dict[str, Any]],
) -> RawGateSummary:
    if raw_document is None:
        return RawGateSummary()

    groups: dict[str, list[GateItem]] = {
        "formal_requirement": [],
        "constraint": [],
        "capability": [],
        "evidence": [],
        "metadata": [],
        "architecture_seed_only": [],
        "test_seed_only": [],
        "open_issue": [],
    }
    coverage_map = {
        row.raw_id: row.matched_requirements
        for row in coverage_matrix
    }
    for item in _raw_document_items(raw_document):
        linked_requirements = coverage_map.get(item.id, [])
        if not linked_requirements and item.disposition in {"capability", "constraint", "architecture_seed_only", "open_issue"}:
            linked_requirements = _suggest_requirement_links(item.title, item.description, requirements)
        promoted = _promotion_candidate(item, linked_requirements, requirements)
        groups.setdefault(item.disposition, []).append(
            GateItem(
                raw_id=item.id,
                category=item.category,
                title=item.title,
                description=item.description,
                gate_reason=item.gate_reason,
                source_detail=item.source_detail,
                linked_formal_requirements=linked_requirements,
                promotion_candidate=promoted,
                promotion_reason=_promotion_reason(item, linked_requirements, item.gate_reason, requirements, promoted),
            )
        )
    return RawGateSummary(
        counts={key: len(value) for key, value in groups.items()},
        formal_requirement_items=groups["formal_requirement"],
        constraint_items=groups["constraint"],
        capability_items=groups["capability"],
        evidence_items=groups["evidence"],
        metadata_items=groups["metadata"],
        architecture_seed_items=groups["architecture_seed_only"],
        test_seed_items=groups["test_seed_only"],
        open_issue_items=groups["open_issue"],
    )


def _raw_document_items(raw_document: RawRequirementDocument) -> list[Any]:
    return (
        list(raw_document.functional_reqs)
        + list(raw_document.interface_reqs)
        + list(raw_document.config_reqs)
        + list(raw_document.nfr_reqs)
    )


def _raw_links_by_requirement(coverage_matrix: list[CoverageMatrixItem]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in coverage_matrix:
        raw_ref = {
            "raw_id": row.raw_id,
            "title": row.title,
            "category": row.category,
            "status": row.status,
        }
        for requirement_id in row.matched_requirements:
            result.setdefault(requirement_id, []).append(raw_ref)
    return result


def _coverage_matrix_items(rows: list[dict[str, Any]]) -> list[CoverageMatrixItem]:
    return [
        CoverageMatrixItem(
            raw_id=row.get("raw_id", ""),
            category=row.get("category", ""),
            title=row.get("title", ""),
            source=row.get("source", ""),
            status=row.get("status", ""),
            matched_requirements=list(row.get("matched_requirements", [])),
        )
        for row in rows
    ]


def _promotion_candidate(item: Any, linked_requirements: list[str], requirements: list[dict[str, Any]]) -> bool:
    if item.disposition != "capability":
        return False
    if _is_capability_promoted(item.title, item.description, linked_requirements, requirements):
        return False
    return bool(linked_requirements)


def _promotion_reason(
    item: Any,
    linked_requirements: list[str],
    gate_reason: str,
    requirements: list[dict[str, Any]],
    promoted: bool,
) -> str:
    if item.disposition != "capability":
        return gate_reason
    if _is_capability_promoted(item.title, item.description, linked_requirements, requirements):
        return "This capability already has a sufficiently specific downstream formal requirement and no longer needs promotion warning."
    if linked_requirements:
        return "This capability already links to downstream formal requirements and should be reviewed for explicit promotion or refinement."
    return gate_reason


def _is_capability_promoted(
    title: str,
    description: str,
    linked_requirements: list[str],
    requirements: list[dict[str, Any]],
) -> bool:
    capability_text = f"{title} {description}".lower()
    requirement_texts = [
        f"{req.get('title', '')} {req.get('shall', '')}".lower()
        for req in requirements
    ]
    if "极性反转" in capability_text and any("极性反转" in text for text in requirement_texts):
        return True
    if ("故障清除" in capability_text or "看门狗" in capability_text) and any(
        ("故障清除" in text or "看门狗" in text) for text in requirement_texts
    ):
        return True
    if "spi" in capability_text and any(("spi" in text and "依赖" in text) for text in requirement_texts):
        return True
    if not linked_requirements:
        return False
    req_by_id = {req.get("requirement_id", ""): req for req in requirements}
    for req_id in linked_requirements:
        req = req_by_id.get(req_id)
        if not req:
            continue
        req_text = f"{req.get('title', '')} {req.get('shall', '')}".lower()
        if "极性反转" in capability_text and "极性反转" in req_text:
            return True
        if ("故障清除" in capability_text or "看门狗" in capability_text) and ("故障清除" in req_text or "看门狗" in req_text):
            return True
        if "spi" in capability_text and "spi" in req_text and "依赖" in req_text:
            return True
    return False


def _suggest_requirement_links(title: str, description: str, requirements: list[dict[str, Any]]) -> list[str]:
    text = _normalize_relation_text(f"{title} {description}")
    suggestions: list[tuple[float, str]] = []
    for req in requirements:
        req_text = _normalize_relation_text(f"{req.get('title', '')} {req.get('shall', '')}")
        score = _relation_score(text, req_text)
        if score >= 0.4:
            suggestions.append((score, req.get("requirement_id", "")))
    suggestions.sort(key=lambda item: (-item[0], item[1]))
    return [req_id for _, req_id in suggestions[:3] if req_id]


def _normalize_relation_text(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", " ", text).strip().lower()


def _relation_score(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left in right or right in left:
        return 1.0
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    return overlap / max(1, min(len(left_tokens), len(right_tokens)))


def _yaml_dump(value: Any, indent: int = 0) -> str:
    prefix = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_yaml_dump(item, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(_yaml_dump(item, indent + 1))
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
        return "\n".join(lines) if lines else f"{prefix}[]"
    return f"{prefix}{_yaml_scalar(value)}"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "":
        return '""'
    return json.dumps(text, ensure_ascii=False)
