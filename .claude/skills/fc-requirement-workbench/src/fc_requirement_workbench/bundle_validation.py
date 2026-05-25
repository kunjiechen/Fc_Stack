"""Validation helpers for requirement bundle quality gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class BundleValidationFinding:
    rule: str
    severity: Severity
    message: str
    requirement_ids: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementBundleValidator:
    def validate(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        findings: list[BundleValidationFinding] = []
        findings.extend(self._check_global_validation_context(bundle))
        findings.extend(self._check_coverage_gaps(bundle))
        findings.extend(self._check_duplicate_architecture_interfaces(bundle))
        findings.extend(self._check_capability_promotion(bundle))
        findings.extend(self._check_gate_leakage(bundle))
        findings.extend(self._check_ready_requirement_quality(bundle))
        findings.extend(self._check_nonfunctional_misclassification(bundle))
        return findings

    def _check_global_validation_context(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        seen: set[tuple[str, str, str]] = set()
        results: list[BundleValidationFinding] = []
        for requirement in bundle.get("requirements", []):
            for finding in requirement.get("global_validation_context", []):
                key = (finding.get("rule", ""), finding.get("severity", ""), finding.get("message", ""))
                if key in seen:
                    continue
                seen.add(key)
                results.append(
                    BundleValidationFinding(
                        rule="global_validation_context",
                        severity=finding.get("severity", "warning"),
                        message=finding.get("message", ""),
                        details={"upstream_rule": finding.get("rule", "")},
                        recommendation=finding.get("recommendation", ""),
                    )
                )
        return results

    def _check_coverage_gaps(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        uncovered = [
            row for row in bundle.get("coverage_matrix", [])
            if row.get("status") not in {"covered", "excluded_by_gate"}
        ]
        if not uncovered:
            return []
        return [
            BundleValidationFinding(
                rule="coverage_gap",
                severity="warning",
                message=f"Found {len(uncovered)} uncovered or partially covered raw requirement items.",
                details={
                    "raw_ids": [row.get("raw_id", "") for row in uncovered[:12]],
                    "statuses": {row.get("raw_id", ""): row.get("status", "") for row in uncovered[:12]},
                },
                recommendation="Review the uncovered raw requirements and decide whether to add formal requirements or record explicit exclusions.",
            )
        ]

    def _check_duplicate_architecture_interfaces(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        seen: dict[str, list[str]] = {}
        for item in bundle.get("architecture_seed", {}).get("external_interface_candidates", []):
            name = item.get("function_name", "")
            if not name:
                continue
            seen.setdefault(name, []).append(item.get("requirement_id", ""))
        duplicates = {name: ids for name, ids in seen.items() if len(ids) > 1}
        if not duplicates:
            return []
        return [
            BundleValidationFinding(
                rule="duplicate_interface_candidate",
                severity="warning",
                message="Architecture seed contains duplicated external interface candidate names.",
                details=duplicates,
                requirement_ids=sorted({req_id for ids in duplicates.values() for req_id in ids if req_id}),
                recommendation="Tighten interface semantic classification or deduplicate interface candidates before using the seed for architecture freeze.",
            )
        ]

    def _check_capability_promotion(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        findings: list[BundleValidationFinding] = []
        for item in bundle.get("raw_gate_summary", {}).get("capability_items", []):
            if not item.get("promotion_candidate"):
                continue
            linked = item.get("linked_formal_requirements", [])
            findings.append(
                BundleValidationFinding(
                    rule="capability_promotion_candidate",
                    severity="warning",
                    message=f"Capability `{item.get('raw_id', '')}` now links to downstream formal requirements and should be reviewed for explicit promotion or refinement.",
                    details={
                        "title": item.get("title", ""),
                        "linked_formal_requirements": linked,
                    },
                    recommendation="Decide whether this capability should remain a note, be refined into one or more explicit formal requirements, or be marked as project-excluded capability.",
                )
            )
        return findings

    def _check_gate_leakage(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        findings: list[BundleValidationFinding] = []
        requirements = bundle.get("requirements", [])
        for requirement in requirements:
            title = str(requirement.get("title", ""))
            text = f"{title} {requirement.get('shall', '')}".lower()
            if "支持通过" in title or "能力" in title or "capability" in text:
                findings.append(
                    BundleValidationFinding(
                        rule="formal_requirement_gate_leakage",
                        severity="info",
                        message=f"Formal requirement `{requirement.get('requirement_id', '')}` still looks capability-like and may need stronger software-action refinement.",
                        requirement_ids=[requirement.get("requirement_id", "")],
                        details={"title": title},
                        recommendation="Rewrite this item into explicit software-owned behavior with clear trigger, input/output, and verification, or keep it outside the formal pool until refined.",
                    )
                )
        return findings

    def _check_ready_requirement_quality(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        results: list[BundleValidationFinding] = []
        for requirement in bundle.get("requirements", []):
            if requirement.get("status") != "ready":
                continue
            missing = []
            if not requirement.get("source"):
                missing.append("source")
            if not requirement.get("verification"):
                missing.append("verification")
            if not requirement.get("shall"):
                missing.append("shall")
            if requirement.get("type") in {"interface", "functional"}:
                if not any(requirement.get(field) for field in ("input", "output", "exception", "constraint", "trigger")):
                    missing.append("execution_detail")
            title = str(requirement.get("title", ""))
            shall = str(requirement.get("shall", ""))
            capability_like = ("支持通过" in title) or ("能力" in title) or ("capability" in f"{title} {shall}".lower())
            bundle_type = requirement.get("bundle_type", "")
            if capability_like:
                missing.append("gate_refinement")
            if bundle_type in {"safety", "coding", "resource"}:
                missing.append("nonfunctional_gate")
            if missing:
                results.append(
                    BundleValidationFinding(
                        rule="ready_gate_weak",
                        severity="warning",
                        message=f"Ready requirement `{requirement.get('requirement_id', '')}` is missing strong execution detail.",
                        requirement_ids=[requirement.get("requirement_id", "")],
                        details={"missing": missing, "title": requirement.get("title", "")},
                        recommendation="Do not treat this item as fully downstream-ready until source, verification, and execution detail are sufficiently explicit.",
                    )
                )
        return results

    def _check_nonfunctional_misclassification(self, bundle: dict[str, Any]) -> list[BundleValidationFinding]:
        results: list[BundleValidationFinding] = []
        keywords = ("ASIL", "MISRA", "ROM/RAM", "资源", "安全等级", "编码规范")
        for requirement in bundle.get("requirements", []):
            if requirement.get("type") != "functional":
                continue
            title = str(requirement.get("title", ""))
            if any(keyword.lower() in title.lower() for keyword in keywords):
                results.append(
                    BundleValidationFinding(
                        rule="nonfunctional_misclassification",
                        severity="warning",
                        message=f"Requirement `{requirement.get('requirement_id', '')}` looks like a nonfunctional item but is currently classified as functional.",
                        requirement_ids=[requirement.get("requirement_id", "")],
                        details={"title": title},
                        recommendation="Consider introducing richer semantic types such as safety, coding, or resource in the requirement bundle contract.",
                    )
                )
        return results


def build_validation_report(bundle: dict[str, Any]) -> dict[str, Any]:
    findings = RequirementBundleValidator().validate(bundle)
    severity_count = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        severity_count[finding.severity] = severity_count.get(finding.severity, 0) + 1
    return {
        "summary": {
            "total": len(findings),
            "error": severity_count["error"],
            "warning": severity_count["warning"],
            "info": severity_count["info"],
            "is_passed": severity_count["error"] == 0,
        },
        "findings": [finding.to_dict() for finding in findings],
    }
