"""Requirement planning layer for author-quality SRS generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, TYPE_CHECKING

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

if TYPE_CHECKING:
    from .normative_rules import DriverTypeProfile


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
    """Plan a compact set of SRS requirements from pruned candidates.

    When a normative driver profile is provided, mandatory lifecycle and
    domain-specific interface requirements are injected automatically.
    """

    def __init__(self, module: str = "FC", profile: "DriverTypeProfile | None" = None) -> None:
        self.display_module = module
        self.module = _module_token(module)
        self.profile = profile

    def plan(self, pruning: CandidatePruningResult | None) -> RequirementPlanningResult:
        required_inputs = pruning.required_inputs if pruning else []
        candidates = pruning.retained_candidates if pruning else []
        by_family = _candidate_index(candidates)

        items = _generic_plan_items(by_family)

        # Collect datasheet-extracted fault rows from retained candidates.
        # Dedup by fault name because pruner-keeper merging may concatenate
        # the same rows from different subfunctions into one candidate.
        datasheet_fault_rows: list[str] = []
        _seen_fr: set[str] = set()
        for c in candidates:
            fault_rows_str = c.target_requirement_fields.get("FaultRows", "")
            if not fault_rows_str:
                continue
            for row in fault_rows_str.split("\n"):
                row = row.strip()
                if not row.startswith("|"):
                    continue
                parts = row.split("|")
                if len(parts) >= 2:
                    fname = parts[1].strip().lower()
                    if fname and fname not in _seen_fr:
                        _seen_fr.add(fname)
                        datasheet_fault_rows.append(row)

        # Collect datasheet-extracted timing parameter data from candidates.
        # The Timing field is populated by _build_timing_group from actual
        # timing value sentences in the datasheet.
        datasheet_timing_data: dict[str, list[str]] = {}
        for c in candidates:
            timing_str = c.target_requirement_fields.get("Timing", "")
            if not timing_str or timing_str == "Project timing responsibility required":
                continue
            domain = _domain_name(_family(c))
            datasheet_timing_data.setdefault(domain, []).append(timing_str)

        # Inject mandatory interface requirements from normative profile
        if self.profile:
            items = _inject_profile_interfaces(items, self.profile, self.module, datasheet_fault_rows)

        requirements = _generic_requirements(self.module, items, datasheet_fault_rows, datasheet_timing_data)

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


def _inject_profile_interfaces(
    items: list[RequirementPlanItem],
    profile: "DriverTypeProfile",
    module: str,
    datasheet_fault_rows: list[str] | None = None,
) -> list[RequirementPlanItem]:
    """Inject mandatory interfaces from the normative profile with semantic dedup.

    Two items with different Chinese names but the same normative semantic
    (e.g. "器件启停与模式控制" vs "芯片模式设置" → both mode_set) are
    collapsed — the data-extracted item is replaced by the profile-named one.
    Generic leftovers ("输入采集", "输出控制") are removed when a specific
    item covers the same semantic category.
    """
    # ---- Phase 1: classify every existing item by its normative semantic ----
    domain_map = {
        "init": "驱动初始化",
        "mainfunction": "周期主函数",
        "hb_output": "H桥输出控制",
        "mode_set": "芯片模式设置",
        "mode_get": "芯片模式获取",
        "fault_read": "故障状态读取",
        "fault_recover": "故障恢复处理",
        "current_sense": "负载电流监测",
    }
    # Reverse: domain name → semantic
    domain_to_semantic = {v: k for k, v in domain_map.items()}

    # Classify each existing item
    item_semantics: dict[int, str] = {}  # index → semantic
    for i, item in enumerate(items):
        sem = _infer_semantic_from_domain(item.domain)
        # Profile-specific overrides: motor driver "输出状态控制" → hb_output
        if (sem == "output_write" and profile.driver_type == "motor_driver"
                and ("输出" in item.domain or "H桥" in item.domain or "电机" in item.domain)):
            sem = "hb_output"
        item_semantics[i] = sem

    # ---- Phase 2: collapse — dedup, rename, and remove noise ----
    # Items dropped only when they carry NO source candidates (pure generic templates).
    # Items backed by real datasheet evidence are preserved even if their domain
    # looks generic — dropping them would lose legitimate mode/state and timing reqs.
    generic_domains_no_source: set[str] = set()
    profile_semantics = {iface.semantic for iface in profile.required_interfaces}

    # Same-domain dedup: keep only the last (typically most specific) item per domain
    deduped_items: list[RequirementPlanItem] = []
    seen_domains: set[str] = set()
    for item in reversed(items):  # Reverse to keep later items
        if item.domain in seen_domains:
            continue
        seen_domains.add(item.domain)
        deduped_items.append(item)
    items = list(reversed(deduped_items))  # Restore original order

    kept: list[RequirementPlanItem] = []
    seen_semantics: set[str] = set()
    for i, item in enumerate(items):
        domain = item.domain
        sem = item_semantics.get(i, "")

        # Drop items only when they carry NO source candidates AND look generic.
        # Items backed by real datasheet evidence (mode/state, timing, etc.) must
        # be preserved so sections 5.1 and 6.1 are populated.
        _generic_no_source = {"输入采集", "输出控制", "边界与异常处理",
                              "配置控制", "复位与默认状态"}
        has_source = bool(item.source_candidates)
        if domain in _generic_no_source and not has_source:
            continue

        # If a data-extracted item shares a semantic with a profile interface,
        # rename it to the canonical profile domain name
        if sem and sem in profile_semantics:
            canonical = domain_map.get(sem)
            if canonical and canonical != domain:
                if sem in seen_semantics:
                    continue  # Already have a canonical item for this semantic
                # Replace with canonical name
                item = RequirementPlanItem(
                    domain=canonical,
                    include_in_srs=item.include_in_srs,
                    planned_requirements=[f"1 条{canonical}需求"],
                    merge_strategy=item.merge_strategy,
                    authoring_strategy=item.authoring_strategy,
                    verification_strategy=item.verification_strategy,
                    source_candidates=item.source_candidates,
                )
                domain = canonical

        if sem:
            if sem in seen_semantics:
                continue  # Dedup: same semantic already covered
            seen_semantics.add(sem)

        kept.append(item)

    # ---- Phase 3: inject missing profile interfaces ----
    # Profile interfaces ALWAYS win over datasheet-produced items with the
    # same semantic.  The profile carries correct AUTOSAR naming (e.g.
    # SetDevModeOutSig) and canonical descriptions; datasheet-produced items
    # rely on the builder's generic inference and may produce wrong function
    # names or descriptions for non-motor-driver chips.
    profile_semantics: set[str] = {iface.semantic for iface in profile.required_interfaces}

    # Step A: remove ALL datasheet-produced items whose semantic conflicts
    # with a profile interface — regardless of whether they have source
    # candidates.  This prevents generic items like "器件启停与模式控制"
    # from blocking the profile's correct SetDevModeOutSig.
    removed: set[int] = set()
    for i, item in enumerate(kept):
        if item.source_candidates and _infer_semantic_from_domain(item.domain) in profile_semantics:
            removed.add(i)
    kept = [item for i, item in enumerate(kept) if i not in removed]

    # Step B: inject profile interfaces not yet covered by remaining items
    covered_semantics: set[str] = set()
    for item in kept:
        sem = _infer_semantic_from_domain(item.domain)
        if sem:
            covered_semantics.add(sem)
    for iface in profile.required_interfaces:
        if iface.semantic in covered_semantics:
            continue
        domain = domain_map.get(iface.semantic, iface.description)
        kept.append(RequirementPlanItem(
            domain=domain,
            include_in_srs="是",
            planned_requirements=[f"1 条{iface.description}需求"],
            merge_strategy="按规范模板注入，不可合并。",
            authoring_strategy="按条件、行为、边界、异常和验证方法编写。",
            verification_strategy="按输入输出和异常路径设计评审/测试验证。",
            source_candidates=[],
        ))
        covered_semantics.add(iface.semantic)

    # ---- Phase 4: inject configuration & diagnostic items from profile ----
    # Configuration items: one plan item with structured config list
    if profile.required_config_items:
        config_domain = "驱动配置项"
        if config_domain not in {item.domain for item in kept}:
            # Serialize config items as structured text for the builder
            config_lines: list[str] = []
            for ci in profile.required_config_items:
                config_lines.append(
                    f"| {ci.name} | {ci.config_type} | {ci.options} | {ci.default} | {ci.description} | {ci.affects} |"
                )
            kept.append(RequirementPlanItem(
                domain=config_domain,
                include_in_srs="是",
                planned_requirements=config_lines,
                merge_strategy="按芯片手册和项目经验逐项定义，区分静态固化(cfg.h)/动态可配(cfg.c)/PCB硬件固定。",
                authoring_strategy="每项需明确：名称、类型(static/dynamic/hardware)、选项、默认值、变更影响范围。",
                verification_strategy="通过配置评审和边界测试验证。",
                source_candidates=[],
            ))

    # Chip + software fault enumeration
    # Merge: datasheet-extracted faults first, then profile chip_faults,
    # then shared software_faults.  Dedup by fault name.
    ds_rows = datasheet_fault_rows or []
    profile_chip = [
        f"| {f.name} | {f.fault_class} | {f.trigger} | {f.detection} | {f.confirmation} | {f.chip_behavior} | {f.recovery} | {f.software_action} |"
        for f in profile.chip_faults
    ]
    profile_sw = [
        f"| {f.name} | {f.fault_class} | {f.trigger} | {f.detection} | {f.confirmation} | {f.chip_behavior} | {f.recovery} | {f.software_action} |"
        for f in profile.software_faults
    ]
    # Dedup: datasheet rows first (highest priority), profile chip second, profile sw last
    seen_fault_names: set[str] = set()
    merged_fault_lines: list[str] = []
    for row in ds_rows + profile_chip + profile_sw:
        # Extract fault name (first pipe-delimited field)
        parts = row.split("|")
        if len(parts) < 3:
            continue
        name = parts[1].strip()
        if name.lower() in seen_fault_names:
            continue
        seen_fault_names.add(name.lower())
        merged_fault_lines.append(row)

    if merged_fault_lines:
        fault_domain = "故障枚举与恢复策略"
        if fault_domain not in {item.domain for item in kept}:
            fault_lines: list[str] = [
                "| 故障名称 | 分类 | 触发条件 | 检测方式 | 确认策略 | 芯片行为 | 恢复类型 | 软件动作 |"
            ]
            fault_lines.extend(merged_fault_lines)
            kept.append(RequirementPlanItem(
                domain=fault_domain,
                include_in_srs="是",
                planned_requirements=fault_lines,
                merge_strategy="逐项列出硬件芯片故障和软件故障，包含检测、确认、恢复策略。",
                authoring_strategy="每项故障需完整定义：分类 → 触发 → 检测 → 确认 → 芯片行为 → 恢复 → 软件动作。",
                verification_strategy="通过故障注入验证每项故障的检测、上报和恢复行为。",
                source_candidates=[],
            ))

    # ---- Phase 5: final same-domain dedup ----
    final: list[RequirementPlanItem] = []
    seen: set[str] = set()
    for item in kept:
        if item.domain in seen:
            continue
        seen.add(item.domain)
        final.append(item)

    return final


def _infer_semantic_from_domain(domain: str) -> str:
    """Infer the normative interface semantic from a Chinese domain name.

    Returns "" if the domain cannot be reliably classified.
    """
    text = domain.lower()
    # Lifecycle
    if any(kw in text for kw in ("初始化", "init")):
        return "init"
    if any(kw in text for kw in ("mainfunction", "周期主函数", "周期调度")):
        return "mainfunction"
    # Fault / diagnostic
    if any(kw in text for kw in ("故障", "诊断", "fault", "diag", "error")):
        return "fault_read"
    # Mode set — includes 模式切换 (mode transition control)
    if any(kw in text for kw in ("模式设置", "模式控制", "模式切换", "芯片模式",
                                   "启停", "mode set", "sleep", "wake", "睡眠", "唤醒")):
        return "mode_set"
    # Mode get
    if any(kw in text for kw in ("模式获取", "模式观测", "模式读取", "mode get")):
        return "mode_get"
    # H-bridge output — matches "输出状态控制" when from motor output pins
    if any(kw in text for kw in ("h桥", "h-bridge", "半桥", "half-bridge",
                                   "电机输出", "功率输出")):
        return "hb_output"
    # Current sense
    if any(kw in text for kw in ("电流", "current", "负载", "load")):
        return "current_sense"
    # Generic input
    if any(kw in text for kw in ("输入采集", "输入读取", "input_read", "监测", "采集")):
        return "input_acquisition"
    # Generic output
    if any(kw in text for kw in ("输出控制", "输出状态", "output", "驱动输出")):
        return "output_write"
    return ""


def _generic_plan_items(by_family: dict[str, list[str]]) -> list[RequirementPlanItem]:
    """Build plan items from grouped candidates, with dedup of same-family items.

    Keys are in format ``family::type_key`` or ``family__sf__subfunc::type_key``.
    Interface candidates split by subfunction produce separate plan items, each
    named after the subfunction to preserve domain semantics (e.g. "负载电流监测").
    """
    # Group by composite key directly — no cross-subfunction merging for interfaces
    items: list[RequirementPlanItem] = []
    for composite_key, candidates in sorted(by_family.items()):
        family, type_key = _parse_composite_key(composite_key)
        if family == "other":
            continue
        # Extract subfunction name for interface candidates
        subfunc_name = ""
        if "__sf__" in composite_key:
            subfunc_name = composite_key.split("__sf__")[-1].rsplit("::", 1)[0]
        domain = subfunc_name if subfunc_name else _domain_name(family)
        planned = _domain_planned(family, len(candidates)) if not subfunc_name else [f"1 条{subfunc_name}接口需求"]
        items.append(RequirementPlanItem(
            domain=domain,
            include_in_srs="是",
            planned_requirements=planned,
            merge_strategy=_domain_merge_strategy(family),
            authoring_strategy="按条件、行为、边界、异常和验证方法编写。",
            verification_strategy="按输入输出和异常路径设计评审/测试验证。",
            source_candidates=candidates,
        ))
    return items


def _parse_composite_key(composite: str) -> tuple[str, str]:
    """Parse ``family::type_key`` or ``family__sf__subfunc::type_key`` into (family, type_key).

    The subfunction annotation ``__sf__<name>`` is stripped from the family
    during parsing; it is recovered from candidate data during domain naming.
    """
    if "::" in composite:
        family, type_key = composite.rsplit("::", 1)
        # Strip subfunction annotation for family grouping
        if "__sf__" in family:
            family = family.split("__sf__")[0]
        return family, type_key
    return composite, "func"


def _type_for_key(type_key: str) -> str:
    """Map short type key to requirement object type."""
    return {"if": "interface", "cfg": "configuration", "diag": "diagnostic",
            "state": "state", "time": "timing"}.get(type_key, "functional")


def _domain_name_for(family: str, type_key: str) -> str:
    """Derive a Chinese domain name from family + type context."""
    base = _domain_name(family)
    # For non-functional types, prefix with type context for clarity
    prefixes = {"if": "接口：", "cfg": "配置：", "diag": "诊断：",
                "state": "状态：", "time": "时序："}
    prefix = prefixes.get(type_key, "")
    if prefix and not base.startswith(prefix):
        return f"{prefix}{base}"
    return base


def _generic_requirements(
    module: str,
    items: list[RequirementPlanItem],
    datasheet_fault_rows: list[str] | None = None,
    datasheet_timing_data: dict[str, list[str]] | None = None,
) -> list[RequirementObject]:
    source = _source("PLAN-GENERIC")
    result: list[RequirementObject] = []
    for index, item in enumerate(items, start=1):
        # Derive type from domain prefix first, then family
        req_type = _type_from_domain(item.domain)
        result.append(_build_typed_requirement(
            module, index, item, req_type, source,
            datasheet_fault_rows, datasheet_timing_data,
        ))
    return result


def _type_from_domain(domain: str) -> str:
    """Derive requirement object type from domain name prefix or family.

    Domain names that don't match any standard family reverse-mapping are
    treated as subfunction interface names (e.g. "负载电流监测", "故障状态读取").
    Profile-injected domains for config/diagnostic are recognized explicitly.
    """
    prefix_map = {
        "接口：": "interface", "配置：": "configuration",
        "诊断：": "diagnostic", "状态：": "state", "时序：": "timing",
    }
    for prefix, rtype in prefix_map.items():
        if domain.startswith(prefix):
            return rtype
    # Profile-injected domain types
    if domain == "驱动配置项":
        return "configuration"
    if domain == "故障枚举与恢复策略":
        return "diagnostic"
    family = _family_for_domain(domain)
    if family == "other":
        return "interface"
    return _domain_type(family)


def _family_for_domain(domain: str) -> str:
    """Reverse mapping: Chinese domain name → family key for type resolution.

    Handles both bare names ("输出控制") and prefixed names ("接口：输出控制").
    """
    # Strip type prefix if present
    for prefix in ("接口：", "配置：", "诊断：", "状态：", "时序："):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
            break
    reverse: dict[str, str] = {
        "边界与异常处理": "boundary_exception",
        "故障与诊断处理": "fault_diagnostic",
        "复位与默认状态": "reset_default",
        "时序约束": "timing_guard",
        "配置控制": "configuration_control",
        "输入采集": "input_acquisition",
        "输出控制": "output_control",
        "寄存器访问": "register_access",
        "模式与状态控制": "mode_state_control",
        "其他功能": "other",
    }
    return reverse.get(domain, "other")


def _candidate_index(candidates: list[Any]) -> dict[str, list[str]]:
    """Group candidates by (family, candidate_type) to preserve granularity.

    Each unique (family, type) combination gets its own plan item, so that
    interface, configuration, and diagnostic requirements from the same
    feature group are not crushed into a single generic requirement.

    Interface candidates from different subfunctions are kept separate so
    that each distinct chip function (e.g. "负载电流监测", "故障状态读取")
    becomes its own interface requirement rather than being merged into a
    generic "输入采集" abstraction.
    """
    result: dict[str, list[str]] = {}
    for candidate in candidates:
        family = _family(candidate)
        ctype = getattr(candidate, "candidate_type", "功能需求")
        type_key = _type_short_key(ctype)
        # Interface candidates: split by subfunction to preserve domain semantics
        if type_key == "if":
            subfunc = getattr(candidate, "source_subfunction", "")
            if subfunc:
                family = f"{family}__sf__{subfunc}"
        key = f"{family}::{type_key}"
        result.setdefault(key, []).append(candidate.candidate_id)
    return result


def _type_short_key(candidate_type: str) -> str:
    """Map Chinese candidate type label to a short grouping key."""
    if "接口" in candidate_type:
        return "if"
    if "配置" in candidate_type:
        return "cfg"
    if "诊断" in candidate_type:
        return "diag"
    if "状态" in candidate_type:
        return "state"
    if "时序" in candidate_type:
        return "time"
    return "func"


def _family(candidate: Any) -> str:
    """Derive behavior family from candidate content (data-driven)."""
    text = f"{candidate.source_feature} {candidate.source_subfunction}".lower()
    if any(kw in text for kw in ("invalid", "reserved", "unsupported",
                                   "prohibited", "rejection", "非法", "拒绝")):
        return "boundary_exception"
    if any(kw in text for kw in ("interrupt", "diagnostic", "fault",
                                   "error flag", "status flag",
                                   "故障", "诊断", "中断")):
        return "fault_diagnostic"
    if any(kw in text for kw in ("reset", "power-on", "power on",
                                   "default state", "复位")):
        return "reset_default"
    if any(kw in text for kw in ("timing", "timeout", "wait", "delay",
                                   "frequency", "khz", "mhz", "us", "ms",
                                   "时序")):
        return "timing_guard"
    # Mode/state lifecycle — check before output_control but use specific
    # keywords to avoid capturing "输出状态控制" (which is output, not lifecycle).
    if any(kw in text for kw in ("mode select", "mode transition", "state transition",
                                   "operating mode", "device mode",
                                   "sleep", "standby", "active mode",
                                   "init", "生命周期",
                                   "模式选择", "模式切换", "模式控制", "睡眠模式",
                                   "器件启停", "工作模式", "活动模式")):
        return "mode_state_control"
    if any(kw in text for kw in ("configuration", "direction", "polarity",
                                   "mode config", "reference",
                                   "vref", "threshold", "配置", "参考", "阈值")):
        return "configuration_control"
    if any(kw in text for kw in ("write", "输出", "set", "control",
                                   "drive", "enable", "disable", "控制")):
        return "output_control"
    if any(kw in text for kw in ("register", "address", "bus", "i2c",
                                   "spi", "transaction", "寄存器")):
        return "register_access"
    if any(kw in text for kw in ("read", "input", "sample", "sense",
                                   "measure", "monitor", "feedback",
                                   "监测", "采集", "读取", "检测")):
        return "input_acquisition"
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
# Dynamic domain mapping (data-driven, no hardcoded per-family tables)
# ---------------------------------------------------------------------------

def _domain_name(family: str) -> str:
    """Derive a Chinese domain name from the family key."""
    defaults = {
        "boundary_exception": "边界与异常处理",
        "fault_diagnostic": "故障与诊断处理",
        "reset_default": "复位与默认状态",
        "timing_guard": "时序约束",
        "configuration_control": "配置控制",
        "input_acquisition": "输入采集",
        "output_control": "输出控制",
        "register_access": "寄存器访问",
        "mode_state_control": "模式与状态控制",
        "other": "其他功能",
    }
    return defaults.get(family, family.replace("_", " ").title())


def _domain_planned(family: str, candidate_count: int) -> list[str]:
    """Generate planned requirement items from family and candidate count."""
    count = max(1, (candidate_count + 2) // 3)
    templates: dict[str, list[str]] = {
        "input_acquisition": [f"{count} 条输入采集接口需求"],
        "output_control": [f"{count} 条输出控制接口需求"],
        "configuration_control": [f"{count} 条配置需求"],
        "fault_diagnostic": [f"{count} 条诊断读取需求", f"{count} 条故障处理需求"],
        "reset_default": [f"{count} 条复位行为需求", f"{count} 条默认状态需求"],
        "timing_guard": [f"{count} 条时序约束需求"],
        "boundary_exception": [f"{count} 条异常拒绝需求"],
        "register_access": [f"{count} 条寄存器访问接口需求"],
        "mode_state_control": [f"{count} 条状态转换需求"],
    }
    return templates.get(family, [f"{count} 条功能需求"])


def _domain_merge_strategy(family: str) -> str:
    """Derive merge strategy from family semantics."""
    strategies = {
        "boundary_exception": "合并同族异常拒绝候选，统一错误返回语义。",
        "fault_diagnostic": "合并故障与诊断候选，区分芯片级故障与信号级诊断。",
        "reset_default": "合并复位与默认状态候选。",
        "timing_guard": "合并时序候选为统一时序约束。",
        "configuration_control": "合并同族配置候选为统一配置接口，保留可验证的软件行为。",
        "input_acquisition": "合并同族输入采集候选，统一寻址语义。",
        "output_control": "合并同族输出控制候选，确保原子性。",
        "register_access": "合并寄存器访问候选，定义统一访问模式。",
        "mode_state_control": "合并模式状态候选，定义完整状态机。",
    }
    return strategies.get(family, "合并同族候选，保留可验证的软件行为。")


def _domain_type(family: str) -> str:
    """Derive the requirement object type from family semantics."""
    type_map = {
        "boundary_exception": "functional",
        "fault_diagnostic": "diagnostic",
        "reset_default": "state",
        "timing_guard": "timing",
        "configuration_control": "configuration",
        "input_acquisition": "interface",
        "output_control": "interface",
        "register_access": "interface",
        "mode_state_control": "state",
        "other": "functional",
    }
    return type_map.get(family, "functional")


def _build_typed_requirement(
    module: str,
    index: int,
    item: RequirementPlanItem,
    req_type: str,
    source: SourceRef,
    datasheet_fault_rows: list[str] | None = None,
    datasheet_timing_data: dict[str, list[str]] | None = None,
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
        # Pass planned_requirements as dependency for profile-injected config items
        dep_text = "\n".join(item.planned_requirements) if item.planned_requirements else ""
        if not dep_text:
            dep_text = f"软件应支持 {item.domain} 的可配置能力，并定义默认值、取值范围和非法值处理规则。"
        return ConfigurationRequirementObject(
            id=req_id,
            type="configuration",
            config_name=item.domain,
            range="",
            default="",
            dependency=dep_text,
            source=[source],
        )

    if req_type == "timing":
        # Build a concrete constraint string from datasheet-extracted timing data.
        # Falls back to the item domain name if no datasheet timing data is available.
        timing_params = (datasheet_timing_data or {}).get(item.domain, [])
        if timing_params:
            constraint = "; ".join(timing_params)
        else:
            constraint = item.domain
        return TimingRequirementObject(
            id=req_id,
            type="timing",
            constraint=constraint,
            minimum="",
            maximum="",
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
        # Build description from planned requirements and datasheet fault rows.
        items_text = "\n".join(item.planned_requirements) if item.planned_requirements else ""
        desc = f"软件应支持 {item.domain} 相关的诊断、故障观测或错误处理行为。"
        if items_text:
            desc = f"{desc}\n\n{items_text}"
        # Embed datasheet-extracted fault table rows when available
        if datasheet_fault_rows:
            fault_table = "\n".join(datasheet_fault_rows)
            desc = f"{desc}\n\n**数据手册故障汇总：**\n\n{fault_table}"
        return FunctionalRequirementObject(
            id=req_id,
            type="diagnostic",
            name=item.domain,
            description=desc,
            constraints=["诊断覆盖目标、故障读取接口粒度和上报路径由项目安全计划定义"],
            source=[source],
        )

    # functional (default)
    return FunctionalRequirementObject(
        id=req_id,
        type="functional",
        name=item.domain,
        description=f"软件应实现 {item.domain} 相关行为，并定义输入、输出、边界条件和异常处理。",
        constraints=["项目使用范围、接口粒度、错误返回语义和验证方法由项目需求定义"],
        source=[source],
    )


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
