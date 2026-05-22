"""Phase-2 requirement rule engine.

The rule engine consumes Phase-1 requirement semantic objects. It does not
generate SRS content and does not mutate the extracted requirements.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from typing import Any, Literal

from .schema import RequirementObject


FindingSeverity = Literal["error", "warning", "info"]
FindingStatus = Literal["passed", "failed"]


@dataclass(frozen=True)
class ProjectConstraints:
    prohibited_modes: list[str] = field(default_factory=list)
    max_instances: int | None = None
    asil: str | None = None

    @classmethod
    def from_text(cls, text: str) -> "ProjectConstraints":
        prohibited_modes: list[str] = []
        for mode in ("Listen-only", "Sleep", "Standby", "Normal"):
            pattern = rf"\b{re.escape(mode)}\b[^.\n]*(?:prohibited|forbidden|not supported|禁止)"
            if re.search(pattern, text, flags=re.IGNORECASE):
                prohibited_modes.append(mode)

        max_instances: int | None = None
        single_instance = re.search(r"\b(single|one)\s+instance\b|单实例", text, flags=re.IGNORECASE)
        if single_instance:
            max_instances = 1
        instance_range = re.search(r"\binstance[s]?\s*[:=]?\s*([0-9]+)\s*(?:~|-|to)\s*([0-9]+)", text, flags=re.IGNORECASE)
        if instance_range:
            max_instances = int(instance_range.group(2))

        asil: str | None = None
        asil_match = re.search(r"\b(QM|ASIL-[ABCD]|ASIL\s*[ABCD])\b", text, flags=re.IGNORECASE)
        if asil_match:
            asil = asil_match.group(1).upper().replace(" ", "-")

        return cls(
            prohibited_modes=sorted(set(prohibited_modes)),
            max_instances=max_instances,
            asil=asil,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationFinding:
    rule: str
    rule_group: str
    status: FindingStatus
    severity: FindingSeverity
    message: str
    requirement_ids: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    conflict: list[str] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementRule:
    name = "rule"
    group = "generic"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        raise NotImplementedError


class RequirementRuleEngine:
    """Validation pipeline for Phase-2 requirement quality rules."""

    def __init__(self, rules: list[RequirementRule] | None = None) -> None:
        self.rules = rules or [
            CompletenessRule(),
            ConsistencyRule(),
            ConstraintRule(),
            OwnershipRule(),
            DependencyRule(),
            ConfigurationRule(),
            TraceRule(),
        ]

    def validate(
        self,
        requirements: list[RequirementObject],
        constraints: ProjectConstraints | None = None,
    ) -> list[ValidationFinding]:
        project_constraints = constraints or ProjectConstraints()
        findings: list[ValidationFinding] = []
        for rule in self.rules:
            findings.extend(rule.evaluate(requirements, project_constraints))
        return findings


class RequirementIndex:
    def __init__(self, requirements: list[RequirementObject]) -> None:
        self.requirements = requirements
        self.items = [req.to_dict() for req in requirements]

    def by_type(self, requirement_type: str) -> list[dict[str, Any]]:
        return [item for item in self.items if item.get("type") == requirement_type]

    def text(self) -> str:
        return " ".join(self._item_text(item) for item in self.items).lower()

    def has_text(self, *needles: str) -> bool:
        haystack = self.text()
        return any(needle.lower() in haystack for needle in needles)

    def state_names(self) -> set[str]:
        return {item.get("state_name", "") for item in self.by_type("state") if item.get("state_name")}

    def interface_names(self) -> set[str]:
        return {
            item.get("interface_name", "")
            for item in self.by_type("interface")
            if item.get("interface_name")
        }

    def config_items(self) -> list[dict[str, Any]]:
        return self.by_type("configuration")

    def evidence_for(self, item: dict[str, Any]) -> str:
        sources = item.get("source") or []
        return " ".join(str(source.get("evidence", "")) for source in sources).strip()

    def _item_text(self, item: dict[str, Any]) -> str:
        fields = [
            item.get("name", ""),
            item.get("description", ""),
            item.get("interface_name", ""),
            item.get("state_name", ""),
            item.get("config_name", ""),
            item.get("constraint", ""),
            item.get("dependency", ""),
            item.get("evidence", ""),
            " ".join(item.get("transition", [])),
            " ".join(item.get("dependency", []) if isinstance(item.get("dependency"), list) else []),
            self.evidence_for(item),
        ]
        return " ".join(str(field) for field in fields if field)


class CompletenessRule(RequirementRule):
    name = "completeness"
    group = "completeness"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        index = RequirementIndex(requirements)
        findings: list[ValidationFinding] = []

        sleep_items = [
            item for item in index.by_type("state") if item.get("state_name", "").lower() == "sleep"
        ]
        if sleep_items:
            missing = []
            if not (index.has_text("wake") or "WAKE" in index.interface_names()):
                missing.append("Wake")
            transitions = [transition for item in sleep_items for transition in item.get("transition", [])]
            if not transitions:
                missing.append("Transition")
            if not index.has_text("entry", "enter", "from standby", "en is low", "stb_n is low"):
                missing.append("Entry Condition")
            if not index.has_text("exit", "wake activity", "sleep -> standby"):
                missing.append("Exit Condition")
            if missing:
                findings.append(
                    ValidationFinding(
                        rule=self.name,
                        rule_group=self.group,
                        status="failed",
                        severity="error",
                        message="Sleep mode requirement is incomplete.",
                        requirement_ids=[item["id"] for item in sleep_items],
                        missing=missing,
                        recommendation="Add Wake, transition, entry condition, and exit condition semantics for Sleep.",
                    )
                )

        if index.has_text("setmode", "set mode") and not index.has_text("getmode", "get mode"):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="warning",
                    message="SetMode exists without a matching GetMode requirement.",
                    missing=["GetMode"],
                    recommendation="Add GetMode semantics, return value, and error path.",
                )
            )

        if not index.has_text("det", "development error", "开发错误"):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="warning",
                    message="Mandatory DET requirement is missing.",
                    missing=["DET / 开发错误检测"],
                    recommendation="Add a diagnostic requirement covering uninitialized access, invalid parameters, and DET or equivalent development error reporting.",
                )
            )

        if index.has_text("fault", "diagnostic", "interrupt", "error", "故障", "诊断", "中断") and not index.has_text(
            "getdevfault",
            "getdiag",
            "故障读取",
            "诊断读取",
            "故障状态读取",
            "诊断状态读取",
        ):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="warning",
                    message="Fault/diagnostic behavior exists without a readable fault or diagnostic interface.",
                    missing=["GetDevFault / GetDiag / 故障读取接口"],
                    recommendation="Add a requirement for reading fault or diagnostic status when the module detects, reports, or tracks faults.",
                )
            )

        return findings


class ConsistencyRule(RequirementRule):
    name = "consistency"
    group = "consistency"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        index = RequirementIndex(requirements)
        text = index.text()
        findings: list[ValidationFinding] = []

        if (
            re.search(r"\binit(?:ialization)?\b[^.]{0,80}\bnormal\b", text)
            and re.search(r"\bsleep\b[^.]{0,80}\bstartup\b|\bstartup\b[^.]{0,80}\bsleep\b", text)
        ):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="error",
                    message="Startup state conflict: initialization enters Normal while configuration allows Sleep startup.",
                    conflict=["Init -> Normal", "Config -> Sleep Startup"],
                    recommendation="Choose one startup policy or add variant/configuration conditions.",
                )
            )

        if (
            re.search(r"\bgetmode\b[^.]{0,80}\brequested\b", text)
            and re.search(r"\bgetmode\b[^.]{0,80}\bphysical\b", text)
        ):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="error",
                    message="GetMode semantic mismatch.",
                    conflict=["GetMode returns requested mode", "GetMode returns physical state"],
                    recommendation="Define whether GetMode reports requested software mode or observed physical mode.",
                )
            )

        return findings


class ConstraintRule(RequirementRule):
    name = "constraint"
    group = "constraint"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        index = RequirementIndex(requirements)
        findings: list[ValidationFinding] = []

        for mode in constraints.prohibited_modes:
            violating = [
                item
                for item in index.by_type("state")
                if item.get("state_name", "").lower() == mode.lower()
            ]
            if violating:
                findings.append(
                    ValidationFinding(
                        rule=self.name,
                        rule_group=self.group,
                        status="failed",
                        severity="error",
                        message=f"Requirement includes prohibited mode: {mode}.",
                        requirement_ids=[item["id"] for item in violating],
                        conflict=[mode],
                        recommendation="Remove the prohibited mode from final project requirements or mark it as excluded capability.",
                    )
                )

        if constraints.max_instances is not None:
            for item in index.config_items():
                value = _range_upper(item.get("range", ""))
                evidence = index.evidence_for(item)
                if value and value > constraints.max_instances:
                    findings.append(
                        ValidationFinding(
                            rule=self.name,
                            rule_group=self.group,
                            status="failed",
                            severity="error",
                            message="Configuration instance range violates project constraint.",
                            requirement_ids=[item["id"]],
                            conflict=[f"configured max={value}", f"allowed max={constraints.max_instances}"],
                            recommendation="Align instance range with the project constraint.",
                        )
                    )
                elif not item.get("range") and re.search(r"\bmultiple\s+instances\b", evidence, flags=re.IGNORECASE):
                    findings.append(
                        ValidationFinding(
                            rule=self.name,
                            rule_group=self.group,
                            status="failed",
                            severity="warning",
                            message="Multiple-instance configuration has no explicit range.",
                            requirement_ids=[item["id"]],
                            missing=["instance range"],
                            recommendation="Add an explicit instance range.",
                        )
                    )

        if constraints.asil == "QM" and re.search(r"\bASIL[- ]?[ABCD]\b", index.text(), flags=re.IGNORECASE):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="error",
                    message="ASIL requirement violates QM-only project constraint.",
                    conflict=["QM only", "ASIL safety requirement"],
                    recommendation="Remove ASIL-specific requirement or update project safety constraint.",
                )
            )

        return findings


class OwnershipRule(RequirementRule):
    name = "ownership"
    group = "ownership"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        index = RequirementIndex(requirements)
        findings: list[ValidationFinding] = []
        critical = {"TXD", "RXD", "WAKE", "INH", "ERR_N"}

        for item in index.by_type("interface"):
            interface = item.get("interface_name", "")
            if interface not in critical:
                continue
            ownership_text = " ".join(
                [
                    str(item.get("dependency", "")),
                    str(item.get("evidence", "")),
                    index.evidence_for(item),
                ]
            ).lower()
            has_owner = bool(
                re.search(r"\b(mcu|driver|upper layer|lower layer|mcal|ecu|controlled|observed|owned)\b", ownership_text)
            )
            has_direction = item.get("direction") in {"input", "output"}
            if not has_owner or not has_direction:
                missing = []
                if not has_owner:
                    missing.append("owner")
                if not has_direction:
                    missing.append("direction")
                findings.append(
                    ValidationFinding(
                        rule=self.name,
                        rule_group=self.group,
                        status="failed",
                        severity="warning",
                        message=f"Interface ownership is incomplete for {interface}.",
                        requirement_ids=[item["id"]],
                        missing=missing,
                        recommendation=f"Define who controls, observes, or configures {interface}.",
                    )
                )

        return findings


class DependencyRule(RequirementRule):
    name = "dependency"
    group = "dependency"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        index = RequirementIndex(requirements)
        text = index.text()
        findings: list[ValidationFinding] = []

        if "pwm" in text:
            missing = []
            if not index.has_text("setduty", "set duty"):
                missing.append("SetDuty dependency requirement")
            if not index.has_text("getduty", "get duty"):
                missing.append("GetDuty dependency requirement")
            if missing:
                findings.append(
                    ValidationFinding(
                        rule=self.name,
                        rule_group=self.group,
                        status="failed",
                        severity="warning",
                        message="PWM dependency is incomplete.",
                        missing=missing,
                        recommendation="Add requirement-level PWM duty dependency statements.",
                    )
                )

        if "spi" in text and not index.has_text("spi dependency", "spi communication dependency"):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="warning",
                    message="SPI communication exists without SPI dependency requirement.",
                    missing=["SPI dependency requirement"],
                    recommendation="Add requirement-level SPI communication dependency statement.",
                )
            )

        return findings


class ConfigurationRule(RequirementRule):
    name = "configuration"
    group = "configuration"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        index = RequirementIndex(requirements)
        text = index.text()
        findings: list[ValidationFinding] = []

        if "wake" in text and not index.has_text("wake enable", "enable wake", "wake detection"):
            findings.append(
                ValidationFinding(
                    rule=self.name,
                    rule_group=self.group,
                    status="failed",
                    severity="warning",
                    message="Wake behavior exists without Wake Enable Switch configuration.",
                    missing=["Wake Enable Switch"],
                    recommendation="Add a configuration requirement for enabling/disabling wake detection.",
                )
            )

        if "interrupt" in text:
            missing = []
            if not index.has_text("interrupt enable", "enable interrupt"):
                missing.append("Interrupt Enable")
            if not index.has_text("interrupt callback", "callback"):
                missing.append("Interrupt Callback")
            if missing:
                findings.append(
                    ValidationFinding(
                        rule=self.name,
                        rule_group=self.group,
                        status="failed",
                        severity="warning",
                        message="Interrupt configuration is incomplete.",
                        missing=missing,
                        recommendation="Add interrupt enable and callback configuration requirements.",
                    )
                )

        return findings


class TraceRule(RequirementRule):
    name = "trace"
    group = "trace"

    def evaluate(
        self, requirements: list[RequirementObject], constraints: ProjectConstraints
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for req in requirements:
            item = req.to_dict()
            sources = item.get("source") or []
            has_source = any(source.get("document") or source.get("chunk_id") for source in sources)
            if not has_source:
                findings.append(
                    ValidationFinding(
                        rule=self.name,
                        rule_group=self.group,
                        status="failed",
                        severity="error",
                        message="Requirement has no source trace.",
                        requirement_ids=[item["id"]],
                        missing=["source"],
                        recommendation="Attach source document and chunk reference.",
                    )
                )
        return findings


def _range_upper(value: str) -> int | None:
    if not value:
        return None
    if value.isdigit():
        return int(value)
    match = re.search(r"([0-9]+)\s*(?:\.\.|-|~|to)\s*([0-9]+)", value, flags=re.IGNORECASE)
    if match:
        return int(match.group(2))
    return None
