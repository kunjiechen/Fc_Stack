"""Phase-4 requirement-level traceability and ASPICE evidence infrastructure."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Literal

from .builder import EngineeringRequirement
from .schema import RawRequirementDocument


VerificationLevel = Literal["Review", "UT", "IT", "ST"]
CoverageStatus = Literal["covered", "partial_covered", "uncovered"]
LifecycleStatus = Literal["draft", "reviewed", "approved", "verified"]


@dataclass(frozen=True)
class TraceLink:
    requirement_id: str
    source: list[str] = field(default_factory=list)
    test: list[str] = field(default_factory=list)
    verification: list[VerificationLevel] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoverageRecord:
    requirement_id: str
    source: list[str] = field(default_factory=list)
    ut: list[str] = field(default_factory=list)
    it: list[str] = field(default_factory=list)
    st: list[str] = field(default_factory=list)
    status: CoverageStatus = "uncovered"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationObject:
    requirement_id: str
    verification: list[VerificationLevel] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LifecycleObject:
    requirement_id: str
    status: LifecycleStatus
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ImpactRecord:
    requirement_id: str
    impacted_tests: list[str] = field(default_factory=list)
    impacted_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AspiceEvidence:
    requirement_evidence: list[dict[str, Any]]
    test_evidence: list[dict[str, Any]]
    coverage_matrix: list[dict[str, Any]]
    verification_report: list[dict[str, Any]]
    lifecycle: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TraceabilityPackage:
    trace_links: list[TraceLink]
    coverage: list[CoverageRecord]
    verification: list[VerificationObject]
    lifecycle: list[LifecycleObject]
    evidence: AspiceEvidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_links": [item.to_dict() for item in self.trace_links],
            "coverage": [item.to_dict() for item in self.coverage],
            "verification": [item.to_dict() for item in self.verification],
            "lifecycle": [item.to_dict() for item in self.lifecycle],
            "aspice_evidence": self.evidence.to_dict(),
        }


class TraceabilityEngine:
    """Build Source -> Requirement -> Verification/Test links."""

    def build_trace_links(
        self,
        requirements: list[EngineeringRequirement],
        tests: dict[str, Any] | None = None,
    ) -> list[TraceLink]:
        tests = tests or {}
        links: list[TraceLink] = []
        for req in requirements:
            test_items = _lookup_mapping(tests, req.requirement_id, "test")
            verification = _verification_levels(req, test_items)
            links.append(
                TraceLink(
                    requirement_id=req.requirement_id,
                    source=_source_ids(req),
                    test=test_items,
                    verification=verification,
                )
            )
        return links


class CoverageEngine:
    def build_coverage(self, trace_links: list[TraceLink]) -> list[CoverageRecord]:
        records: list[CoverageRecord] = []
        for link in trace_links:
            ut = [item for item in link.test if _test_level(item) == "UT"]
            it = [item for item in link.test if _test_level(item) == "IT"]
            st = [item for item in link.test if _test_level(item) == "ST"]
            has_test = bool(ut or it or st)
            has_source = bool(link.source)
            status: CoverageStatus = "uncovered"
            if has_source and has_test:
                status = "covered"
            elif has_source or has_test:
                status = "partial_covered"
            records.append(
                CoverageRecord(
                    requirement_id=link.requirement_id,
                    source=link.source,
                    ut=ut,
                    it=it,
                    st=st,
                    status=status,
                )
            )
        return records


class VerificationEngine:
    def build_verification(self, trace_links: list[TraceLink]) -> list[VerificationObject]:
        return [
            VerificationObject(
                requirement_id=link.requirement_id,
                verification=link.verification or ["Review"],
            )
            for link in trace_links
        ]


class LifecycleManager:
    def build_lifecycle(
        self,
        requirements: list[EngineeringRequirement],
        coverage: list[CoverageRecord],
    ) -> list[LifecycleObject]:
        coverage_by_id = {item.requirement_id: item for item in coverage}
        lifecycle: list[LifecycleObject] = []
        for req in requirements:
            record = coverage_by_id.get(req.requirement_id)
            if record and record.status == "covered":
                status: LifecycleStatus = "verified"
                reason = "Source and verification evidence are available."
            elif req.validation:
                status = "draft"
                reason = "Validation findings remain open."
            else:
                status = "reviewed"
                reason = "Requirement is generated and has no open validation finding."
            lifecycle.append(LifecycleObject(req.requirement_id, status, reason))
        return lifecycle


class ChangeImpactAnalyzer:
    def analyze(
        self,
        trace_links: list[TraceLink],
        changed_requirement_ids: list[str],
    ) -> list[ImpactRecord]:
        by_test: dict[str, set[str]] = {}
        for link in trace_links:
            for test in link.test:
                by_test.setdefault(test, set()).add(link.requirement_id)

        impacts: list[ImpactRecord] = []
        for link in trace_links:
            if link.requirement_id not in changed_requirement_ids:
                continue
            related_requirements: set[str] = set()
            for test in link.test:
                related_requirements.update(by_test.get(test, set()))
            related_requirements.discard(link.requirement_id)
            impacts.append(
                ImpactRecord(
                    requirement_id=link.requirement_id,
                    impacted_tests=link.test,
                    impacted_requirements=sorted(related_requirements),
                )
            )
        return impacts


class AspiceEvidenceGenerator:
    def build(
        self,
        requirements: list[EngineeringRequirement],
        trace_links: list[TraceLink],
        coverage: list[CoverageRecord],
        verification: list[VerificationObject],
        lifecycle: list[LifecycleObject],
    ) -> AspiceEvidence:
        by_req = {req.requirement_id: req for req in requirements}
        return AspiceEvidence(
            requirement_evidence=[
                {
                    "requirement_id": link.requirement_id,
                    "source": link.source,
                    "description": by_req[link.requirement_id].description,
                }
                for link in trace_links
            ],
            test_evidence=[
                {
                    "requirement_id": link.requirement_id,
                    "test": link.test,
                    "verification": link.verification,
                }
                for link in trace_links
            ],
            coverage_matrix=[item.to_dict() for item in coverage],
            verification_report=[item.to_dict() for item in verification],
            lifecycle=[item.to_dict() for item in lifecycle],
        )


class TraceabilityPipeline:
    def build(
        self,
        requirements: list[EngineeringRequirement],
        tests: dict[str, Any] | None = None,
    ) -> TraceabilityPackage:
        trace_links = TraceabilityEngine().build_trace_links(
            requirements,
            tests=tests,
        )
        coverage = CoverageEngine().build_coverage(trace_links)
        verification = VerificationEngine().build_verification(trace_links)
        lifecycle = LifecycleManager().build_lifecycle(requirements, coverage)
        evidence = AspiceEvidenceGenerator().build(
            requirements,
            trace_links,
            coverage,
            verification,
            lifecycle,
        )
        return TraceabilityPackage(trace_links, coverage, verification, lifecycle, evidence)


class TraceabilityMarkdownRenderer:
    def render(
        self,
        package: TraceabilityPackage,
        *,
        module: str,
        raw_document: RawRequirementDocument | None = None,
        raw_coverage: list[dict[str, Any]] | None = None,
    ) -> str:
        lines = [
            f"# {module} 追溯与覆盖矩阵",
            "",
            "## Source -> Requirement Trace Matrix",
            "",
            "| Requirement ID | Source | Trace Status |",
            "| --- | --- | --- |",
        ]
        for link in package.trace_links:
            lines.append(
                f"| {link.requirement_id} | {', '.join(link.source) or '-'} | {'Covered' if link.source else 'Missing Source'} |"
            )

        lines.extend(
            [
                "",
                "## Requirement -> Verification Intent Coverage Matrix",
                "",
                "| Requirement ID | Verification Method | Coverage Status |",
                "| --- | --- | --- |",
            ]
        )
        verification_by_id = {item.requirement_id: item for item in package.verification}
        for item in package.coverage:
            verification = verification_by_id.get(item.requirement_id)
            lines.append(
                f"| {item.requirement_id} | {', '.join((verification.verification if verification else ['Review']))} | {item.status} |"
            )

        if raw_document is not None and raw_coverage is not None:
            total = len(raw_coverage)
            covered = sum(1 for item in raw_coverage if item.get("status") == "covered")
            rate = (covered / total) if total else 1.0
            lines.extend(
                [
                    "",
                    "## Raw Requirement Coverage Matrix",
                    "",
                    "| Metric | Value |",
                    "| --- | --- |",
                    f"| Raw Requirements | {total} |",
                    f"| Covered | {covered} |",
                    f"| Coverage Rate | {rate:.0%} |",
                    "",
                    "| Raw Requirement ID | Category | Title | Coverage Status | Covered By SRS | Source |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for item in raw_coverage:
                lines.append(
                    f"| {item.get('raw_id', '')} | {item.get('category', '')} | {item.get('title', '')} | "
                    f"{item.get('status', '')} | {', '.join(item.get('matched_requirements', [])) or '-'} | {item.get('source', '-') or '-'} |"
                )

        lines.extend(
            [
                "",
                "## ASPICE Evidence Summary",
                "",
                "| Lifecycle Status | Count |",
                "| --- | --- |",
            ]
        )
        lifecycle_counts: dict[str, int] = {}
        for item in package.lifecycle:
            lifecycle_counts[item.status] = lifecycle_counts.get(item.status, 0) + 1
        for status, count in sorted(lifecycle_counts.items()):
            lines.append(f"| {status} | {count} |")
        lines.append("")
        return "\n".join(lines)


def load_trace_mapping(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return parse_trace_mapping_markdown(text)


def parse_trace_mapping_markdown(text: str) -> dict[str, Any]:
    mappings: dict[str, dict[str, list[str]]] = {}
    for line in text.splitlines():
        requirement_ids = re.findall(r"SRS-[A-Z0-9]+-[A-Z]+-[0-9]{4}", line)
        if not requirement_ids:
            continue
        for req_id in requirement_ids:
            entry = mappings.setdefault(req_id, {})
            if re.search(r"\b(UT|IT|ST)_[A-Z0-9_]+", line):
                entry.setdefault("test", []).extend(re.findall(r"\b(?:UT|IT|ST)_[A-Z0-9_]+", line))
    return {"mappings": {key: _dedupe_mapping(value) for key, value in mappings.items()}}


def _lookup_mapping(mapping: dict[str, Any], requirement_id: str, field: str) -> list[str]:
    item = mapping.get("mappings", {}).get(requirement_id, {})
    values = item.get(field, [])
    if isinstance(values, str):
        return [values]
    return sorted(set(str(value) for value in values if value))


def _source_ids(req: EngineeringRequirement) -> list[str]:
    return [
        source.get("chunk_id") or source.get("document", "")
        for source in req.source
        if source.get("chunk_id") or source.get("document")
    ]


def _verification_levels(req: EngineeringRequirement, tests: list[str]) -> list[VerificationLevel]:
    levels: set[VerificationLevel] = set()
    if not tests:
        levels.add("Review")
    for test in tests:
        level = _test_level(test)
        if level:
            levels.add(level)
    if "review" in req.verification.lower():
        levels.add("Review")
    return sorted(levels, key=["Review", "UT", "IT", "ST"].index)


def _test_level(test: str) -> VerificationLevel | str:
    upper = test.upper()
    if upper.startswith("UT_"):
        return "UT"
    if upper.startswith("IT_"):
        return "IT"
    if upper.startswith("ST_"):
        return "ST"
    return ""


def _dedupe_mapping(mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    return {key: sorted(set(value)) for key, value in mapping.items()}
