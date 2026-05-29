"""Phase-3 requirement builder.

This module converts Phase-1 semantic objects plus Phase-2 validation findings
into engineering requirement instances. It deliberately stops at SRS document
generation and leaves trace, coverage, and ASPICE evidence to the Phase-4
requirement evidence layer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
import re
from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .normative_rules import DriverTypeProfile, NormativeRules

from .rules import ValidationFinding
from .schema import RequirementObject


EngineeringRequirementType = Literal[
    "functional",
    "interface",
    "configuration",
    "diagnostic",
    "timing",
    "state",
    "safety",
    "coding",
    "resource",
]


TYPE_CODES = {
    "functional": "FUNC",
    "interface": "IF",
    "configuration": "CFG",
    "diagnostic": "DIAG",
    "timing": "TIME",
    "state": "STATE",
    "safety": "SAFE",
    "coding": "CODE",
    "resource": "RES",
}


@dataclass(frozen=True)
class EngineeringRequirement:
    requirement_id: str
    semantic_id: str
    requirement_type: EngineeringRequirementType
    title: str
    description: str
    pre_condition: str = ""
    trigger: str = ""
    input: str = ""
    output: str = ""
    exception: str = ""
    constraint: str = ""
    verification: str = ""
    function_name: str = ""
    source: list[dict[str, Any]] = field(default_factory=list)
    validation: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RequirementIdEngine:
    """Generate stable SRS IDs by module and requirement type."""

    def __init__(self, module: str) -> None:
        self.module = _normalize_module(module)
        self._counters: defaultdict[str, int] = defaultdict(int)
        self._assigned: dict[str, str] = {}

    def id_for(self, semantic_id: str, requirement_type: str) -> str:
        if semantic_id in self._assigned:
            return self._assigned[semantic_id]
        type_code = TYPE_CODES.get(requirement_type, requirement_type.upper())
        self._counters[type_code] += 1
        requirement_id = f"SRS-{self.module}-{type_code}-{self._counters[type_code]:04d}"
        self._assigned[semantic_id] = requirement_id
        return requirement_id


def _normative_function_name(
    rules: "NormativeRules",
    profile: "DriverTypeProfile",
    module: str,
    semantic: str,
    layer: str,
) -> str:
    """Resolve function name using normative rules with driver-type overrides."""
    suffix = rules.function_suffix(layer, semantic, profile)
    clean = _strip_gp_prefix(module)
    return f"Gp_{clean}_{suffix}"


# ---------------------------------------------------------------------------
# Naming classification: semantic category -> correct C function name suffix
# per AUTOSAR layer.  Mirrors aurix2g-normative-patterns 1.1 + 6.1.
# ---------------------------------------------------------------------------
_LAYER_NAMING_TABLE: dict[str, dict[str, str]] = {
    "IoExtDev": {
        "init": "Init",
        "mainfunction": "MainFunction",
        "fault": "GetDevFaultSig",
        "diag": "GetDevFaultSig",
        "input_read": "GetInSig",
        "output_write": "SetOutSig",
        "direction": "SetDirSig",
        "polarity": "SetPolSig",
        "mode_set": "SetDevModeOutSig",
        "mode_get": "GetDevModeInSig",
        "reset": "ResetChip",
    },
    "IoMcu": {
        "init": "Init",
        "mainfunction": "MainFunction",
        "fault": "GetDiag",
        "diag": "GetXxxSigDiag",
        "input_read": "GetXxxRaw",
        "output_write": "SetXxxOutSig",
    },
    "Srv": {
        "init": "Init",
        "mainfunction": "MainFunction",
        "fault": "GetDiag",
        "diag": "GetDiag",
        "input_read": "GetXxxSig",
        "output_write": "SetXxxSig",
    },
    "*": {
        "init": "Init",
        "mainfunction": "MainFunction",
        "fault": "GetDevFaultSig",
        "diag": "GetDevFaultSig",
        "input_read": "GetInSig",
        "output_write": "SetOutSig",
        "direction": "SetDirSig",
        "polarity": "SetPolSig",
        "mode_set": "SetDevModeOutSig",
        "mode_get": "GetDevModeInSig",
        "reset": "ResetChip",
    },
}


def _classify_interface_semantic(interface_name: str, description: str, direction: str) -> str:
    """Classify an interface's semantic category from its content (data-driven)."""
    text = f"{interface_name} {description}".lower()

    # Lifecycle
    if any(kw in text for kw in ("mainfunction", "周期调度", "周期性驱动", "轮询",
                                   "main function", "周期主函数")):
        return "mainfunction"
    if any(kw in text for kw in ("init", "初始化")):
        return "init"

    # Fault/diagnostic — check before generic read/write
    if any(kw in text for kw in ("故障", "诊断", "fault", "diag", "error", "nfault", "status flag")):
        return "fault"

    # Reset
    if any(kw in text for kw in ("复位", "reset", "restart", "reboot")):
        return "reset"

    # Mode/state control — check before generic control
    if any(kw in text for kw in ("模式设置", "模式控制", "模式切换", "mode set",
                                   "mode control", "enable", "disable", "sleep",
                                   "wake", "standby", "模式与状态")):
        return "mode_set"
    if any(kw in text for kw in ("模式读取", "mode get", "模式状态", "状态读取",
                                   "模式获取", "模式观测")):
        return "mode_get"

    # Direction/polarity
    if any(kw in text for kw in ("方向", "direction", "dir")):
        return "direction"
    if any(kw in text for kw in ("极性", "polarity", "pol", "inversion")):
        return "polarity"

    # H-bridge / motor output — check before generic read/write
    if any(kw in text for kw in ("h桥", "h-bridge", "hb", "半桥", "half-bridge",
                                   "电机输出", "motor output", "h 桥", "功率输出")):
        return "hb_output"

    # Current sense — check before generic read
    if any(kw in text for kw in ("电流", "current sense", "current monitor", "ipropi")):
        return "current_sense"

    # Read/sense/monitor/input — check before write/control
    if any(kw in text for kw in ("读取", "read", "获取", "get", "采样", "采集",
                                   "sample", "sense", "measure", "monitor", "检测",
                                   "监测", "输入状态", "反馈")):
        return "input_read"

    # Write/control/output
    if any(kw in text for kw in ("写入", "write", "设置", "set", "输出控制",
                                   "output", "控制", "control", "drive", "驱动")):
        return "output_write"

    # Config — neutral fallback
    if any(kw in text for kw in ("配置", "config", "参数", "阈值")):
        return "mode_set"

    return "output_write"


def _resolve_interface_name(
    module: str,
    semantic: str,
    layer: str,
    interface_name: str,
) -> str:
    """Resolve the correct C function name for an interface.

    Returns the full function name like ``Gp_NCA9539_GetDevFaultSig``.
    Falls back to ``Gp_{module}_{interface_name}`` when no rule matches.
    """
    table = _LAYER_NAMING_TABLE.get(layer, _LAYER_NAMING_TABLE.get("*", {}))
    suffix = table.get(semantic)
    clean = _strip_gp_prefix(module)
    if suffix:
        return f"Gp_{clean}_{suffix}"
    return f"Gp_{clean}_{interface_name}"


def _extract_function_name_hint(module: str, interface_name: str, description: str) -> str:
    text = f"{interface_name} {description}"
    match = re.search(r"\b(Gp_[A-Za-z0-9_]+)\s*(?=\()", text)
    if match:
        return match.group(1)
    match = re.search(r"\b([A-Za-z][A-Za-z0-9_]*)\s*(?=\()", text)
    if not match:
        return ""
    base_name = match.group(1)
    if base_name in {"void", "uint8", "uint16", "uint32", "Std_ReturnType"}:
        return ""
    clean = _strip_gp_prefix(module)
    if base_name.startswith(clean):
        return f"Gp_{base_name}"
    return f"Gp_{clean}_{base_name}"


class RequirementBuilder:
    """Map semantic requirement objects to engineering requirement instances.

    When a normative driver profile is provided, interface naming uses
    domain-specific suffixes (e.g. SetHbOutSig for motor drivers) rather
    than generic fallbacks.
    """

    def __init__(
        self,
        module: str = "FC",
        layer: str = "IoExtDev",
        profile: "DriverTypeProfile | None" = None,
        rules: "NormativeRules | None" = None,
    ) -> None:
        self.module = module
        self.layer = layer
        self.id_engine = RequirementIdEngine(module)
        self.profile = profile
        self.rules = rules

    def build(
        self,
        requirements: list[RequirementObject],
        findings: list[ValidationFinding] | None = None,
    ) -> list[EngineeringRequirement]:
        findings_by_req = _findings_by_requirement(findings or [])
        return [
            self._build_one(req.to_dict(), findings_by_req.get(req.to_dict()["id"], []))
            for req in requirements
        ]

    def _build_one(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        req_type = item["type"]
        if req_type == "functional":
            return self._build_functional(item, findings)
        if req_type == "interface":
            return self._build_interface(item, findings)
        if req_type == "configuration":
            return self._build_configuration(item, findings)
        if req_type == "diagnostic":
            return self._build_diagnostic(item, findings)
        if req_type == "timing":
            return self._build_timing(item, findings)
        if req_type == "state":
            return self._build_state(item, findings)
        raise ValueError(f"Unsupported requirement type: {req_type}")

    def _base(
        self,
        item: dict[str, Any],
        findings: list[ValidationFinding],
        title: str,
        description: str,
        **kwargs: str,
    ) -> EngineeringRequirement:
        req_type = item["type"]
        verification = kwargs.pop("verification", _default_verification(req_type))
        verification = _refine_verification(
            verification,
            trigger=kwargs.get("trigger", ""),
            input_value=kwargs.get("input", ""),
            output_value=kwargs.get("output", ""),
            exception=kwargs.get("exception", ""),
            constraint=kwargs.get("constraint", ""),
        )
        return EngineeringRequirement(
            requirement_id=self.id_engine.id_for(item["id"], req_type),
            semantic_id=item["id"],
            requirement_type=req_type,
            title=title,
            description=description,
            source=item.get("source", []),
            validation=[finding.to_dict() for finding in findings],
            verification=verification,
            **kwargs,
        )

    def _build_functional(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        name = item.get("name") or "Functional Behavior"
        description = item.get("description") or f"The software shall support {name}."
        if not description.lower().startswith("the ") and not description.startswith("软件"):
            description = f"软件应支持{description.rstrip('。.') }。"
        return self._base(
            item,
            findings,
            title=name,
            description=description,
            input=", ".join(item.get("inputs", [])),
            output=", ".join(item.get("outputs", [])),
            constraint=", ".join(item.get("constraints", [])),
            verification=_planned_verification(name, req_type="functional"),
        )

    def _build_interface(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        interface = item.get("interface_name") or "Interface"
        direction = item.get("direction") or "unknown"

        # Resolve the correct C function name — normative rules take priority
        function_name = item.get("function_name", "")
        if not function_name:
            function_name = _extract_function_name_hint(self.module, interface, item.get("dependency", ""))
        if not function_name:
            semantic = _classify_interface_semantic(interface, item.get("dependency", ""), direction)
            # Use normative naming table when available
            if self.rules and self.profile:
                function_name = _normative_function_name(
                    self.rules, self.profile, self.module, semantic, self.layer
                )
            if not function_name:
                function_name = _resolve_interface_name(self.module, semantic, self.layer, interface)

        description = self._resolve_interface_description(interface, function_name)
        return self._base(
            item,
            findings,
            title=_append_suffix(interface, "接口"),
            description=description,
            input=interface if direction == "input" else "",
            output=interface if direction == "output" else "",
            constraint=item.get("dependency", ""),
            verification=_planned_verification(interface, req_type="interface"),
            function_name=function_name,
        )

    def _resolve_interface_description(self, interface: str, function_name: str) -> str:
        """Generate a description for an interface based on its resolved function name."""
        if "Init" in function_name and "init" not in interface.lower():
            return f"软件应提供 `{function_name}` 接口，用于加载项目配置、建立运行时上下文并初始化所依赖的底层访问资源，在配置非法或初始化失败时返回定义错误。"
        if "MainFunction" in function_name and "mainfunction" not in interface.lower():
            return f"软件应提供 `{function_name}` 接口，用于周期推进运行时状态、输出刷新和诊断处理，接口不得执行长时间阻塞操作。"
        if "SetHbOutSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，基于目标 H 桥通道设置周期、占空比和方向输出，并在参数非法或底层访问失败时返回定义错误。"
        if "GetDevModeInSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，读取指定芯片实例的当前设备模式，并在未初始化、非法参数或底层访问失败时返回定义错误。"
        if "SetDevModeOutSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，设置指定芯片实例的目标工作模式，并在模式值非法或底层访问失败时返回定义错误。"
        if "GetDevFaultSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，返回指定芯片实例的诊断状态信息，包括参数合法性错误、未初始化访问和设备故障状态。"
        if "GetLoadCurrentSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，通过 ADC 采样 IPROPI 引脚电压，返回与负载电流成正比的电流值，并在 ADC 未配置或采样失败时返回定义错误。"
        if "GetDevModeInSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，读取指定芯片实例的当前设备模式，并在未初始化、非法参数或底层访问失败时返回定义错误。"
        if "GetInSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，读取指定芯片实例的输入信号状态，对非法参数或底层访问失败返回错误。"
        if "SetOutSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，设置指定芯片实例的输出信号状态，对非法参数或底层访问失败返回错误。"
        if "SetDirSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，配置指定引脚的输入/输出方向，运行时方向变更策略须项目确认。"
        if "SetPolSig" in function_name:
            return f"软件应提供 `{function_name}` 接口，配置指定引脚的信号极性/反转策略。"
        if "ResetChip" in function_name:
            return f"软件应提供 `{function_name}` 接口，对指定芯片实例执行硬件复位，仅当复位引脚归属本驱动时适用。"
        return _interface_description(interface)

    def _build_configuration(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        config = item.get("config_name") or "Configuration"
        # Profile-injected config: dependency carries the table rows
        if config == "驱动配置项":
            dep = item.get("dependency", "")
            # Build markdown table from dep text which has pipe-delimited rows
            header = "| 配置项 | 类型 | 可选值 | 默认值 | 说明 | 影响接口 |"
            sep = "|---|---|---|---|---|---|"
            rows = [line for line in dep.split("\n") if line.startswith("|")]
            table = "\n".join([header, sep] + rows) if rows else dep
            return self._base(
                item, findings,
                title="驱动配置项",
                description=(
                    f"软件应支持以下配置项。static 类型在 cfg.h 中预编译固化，"
                    f"不同项目可选择不同值；dynamic 类型在 cfg.c 中运行时加载，"
                    f"同一二进制可适配不同硬件；hardware 类型为 PCB 固定，"
                    f"作为设计约束记录。\n\n{table}"
                ),
                constraint="配置项默认值在 Init 中加载；dynamic 类型可通过 Pre-Compile 或校准工具修改；超范围或冲突配置应拒绝生效。",
                verification="通过配置评审和边界测试验证每项配置的默认值加载和非法值拒绝。",
            )
        description = f"软件应支持 `{config}`，并定义默认值、取值范围和非法值处理规则。"
        return self._base(
            item, findings,
            title=_append_suffix(config, "配置"),
            description=description,
            constraint=f"范围：{_project_value(item.get('range', ''))}；默认值：{_project_value(item.get('default', ''))}",
            pre_condition=item.get("dependency", ""),
            verification=_planned_verification(config, req_type="configuration"),
        )

    def _build_diagnostic(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        name = item.get("name") or item.get("interface_name") or "Diagnostic Behavior"
        # Profile-injected fault enumeration: table data embedded in description
        if name == "故障枚举与恢复策略":
            dep = item.get("description", "")
            header = "| 故障名称 | 分类 | 触发条件 | 检测方式 | 确认策略 | 芯片行为 | 恢复类型 | 软件动作 |"
            sep = "|---|---|---|---|---|---|---|---|"
            all_rows = [line for line in dep.split("\n") if line.startswith("|")]
            # Skip first row if it's a duplicate header (planner embeds one)
            rows = all_rows[1:] if all_rows and "故障名称" in all_rows[0] else all_rows
            # Final dedup: keep only the first occurrence of each fault name.
            # Upstream dedup may be defeated by overlapping chunks or pruner
            # merging, so this is the safety net.
            seen_faults: set[str] = set()
            unique_rows: list[str] = []
            for row in rows:
                parts = row.split("|")
                if len(parts) >= 2:
                    fname = parts[1].strip().lower()
                    if fname and fname not in seen_faults:
                        seen_faults.add(fname)
                        unique_rows.append(row)
            table = "\n".join([header, sep] + unique_rows) if unique_rows else dep
            return self._base(
                item, findings,
                title="故障枚举与恢复策略",
                description=(
                    f"软件应检测、确认并处理以下故障。恢复类型定义："
                    f"auto=芯片自动恢复无需软件介入；"
                    f"manual_reset=需软件执行芯片复位序列；"
                    f"manual_clear=需软件清除故障标志；"
                    f"fatal=不可恢复需系统级处理。\n\n{table}"
                ),
                constraint="故障检测在 MainFunction 中周期执行；故障恢复不得破坏已建立的运行时上下文；锁存型故障应提供故障清除接口。",
                verification="通过故障注入逐项验证检测、确认、上报和恢复行为。",
            )
        description = item.get("description") or f"软件应支持{name}相关的诊断、故障观测或错误处理行为。"
        if not description.lower().startswith("the ") and not description.startswith("软件"):
            description = f"软件应支持{description.rstrip('。.')}。"
        dependency = item.get("dependency", "")
        if isinstance(dependency, list):
            dependency = ", ".join(str(value) for value in dependency if value)
        return self._base(
            item, findings,
            title=name,
            description=description,
            input=", ".join(item.get("inputs", [])) if isinstance(item.get("inputs"), list) else "",
            output=", ".join(item.get("outputs", [])) if isinstance(item.get("outputs"), list) else "",
            exception=item.get("exception", "") if isinstance(item.get("exception", ""), str) else "",
            constraint=dependency,
            verification=_planned_verification(name, req_type="diagnostic"),
        )

    def _build_timing(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        constraint = item.get("constraint") or "Timing Constraint"
        description = _timing_description(constraint, item.get("minimum", ""), item.get("maximum", ""))
        return self._base(
            item,
            findings,
            title="时序约束",
            description=description,
            constraint=constraint,
            verification=_planned_verification(constraint, req_type="timing"),
        )

    def _build_state(
        self, item: dict[str, Any], findings: list[ValidationFinding]
    ) -> EngineeringRequirement:
        state = item.get("state_name") or "State"
        transitions = item.get("transition", [])
        if transitions:
            description = f"软件应支持 `{state}` 状态行为，状态转换为：{', '.join(transitions)}。"
        else:
            description = f"软件应支持 `{state}` 状态行为，并定义触发条件、观测方式和恢复策略。"
        return self._base(
            item,
            findings,
            title=_append_suffix(state, "状态"),
            description=description,
            trigger=", ".join(transitions),
            constraint=", ".join(item.get("dependency", [])),
            verification=_planned_verification(state, req_type="state"),
        )


def _findings_by_requirement(
    findings: list[ValidationFinding],
) -> dict[str, list[ValidationFinding]]:
    result: dict[str, list[ValidationFinding]] = defaultdict(list)
    for finding in findings:
        for req_id in finding.requirement_ids:
            result[req_id].append(finding)
    return result


def _normalize_module(module: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "", module).upper()
    return normalized or "FC"


def _strip_gp_prefix(module: str) -> str:
    """Strip leading Gp_/gp_ prefix so we don't double it in function names."""
    return re.sub(r"^[Gg][Pp]_", "", module)


def _default_verification(req_type: str) -> str:
    return {
        "functional": "通过功能测试和边界测试验证：对有效输入执行目标行为时，应输出预期结果；对非法输入、失败依赖或前置条件不满足场景，应返回定义错误并保持无关状态不被意外修改。",
        "interface": "通过接口测试和集成测试验证：调用接口后应检查返回值、输出参数和外部可观测结果；对非法参数、未初始化和底层访问失败场景，应返回定义错误且不破坏既有状态。",
        "configuration": "通过配置评审、默认值检查和边界测试验证：加载默认配置后应得到期望配置结果；超出有效范围、缺失配置或非法组合时，应拒绝配置并给出定义结果。",
        "diagnostic": "通过故障注入、异常路径和集成测试验证：故障、非法参数、未初始化访问或底层通信失败时，应产生定义的错误返回、诊断状态或故障信息，并保证软件状态一致。",
        "timing": "通过时序分析、超时注入和集成测试验证：在定义测量点记录开始和结束时刻，确认满足最小/最大时序约束；超时场景应触发定义错误或恢复动作。",
        "state": "通过状态转换测试验证：在有效触发条件下应进入目标状态并更新可观测状态；非法触发、失败依赖或恢复场景下应保持或回退到定义状态。",
        "safety": "通过安全需求评审和失效场景分析验证：确认安全边界、检测机制和失效响应完整，并且异常场景下的系统反应有可审查证据。",
        "coding": "通过编码规范检查和静态分析验证：确认约束适用于目标文件和接口，违规项能够被工具或评审记录识别并产出结果。",
        "resource": "通过资源统计、评审或集成测试验证：在目标构建和典型运行场景下记录资源占用结果，并确认未超出定义预算或限制。",
    }.get(req_type, "通过评审、分析或测试验证，并给出可观测结果。")


def _timing_description(constraint: str, minimum: str, maximum: str) -> str:
    lowered = constraint.lower()
    if constraint.startswith("软件"):
        return constraint.rstrip("。") + "。"
    if "err_n" in lowered and minimum:
        return f"软件应在采样 ERR_N 前至少等待 {minimum}。"
    if minimum and maximum:
        return f"软件应满足 {minimum} 到 {maximum} 的时序约束。"
    if minimum:
        return f"软件应满足最小 {minimum} 的时序约束。"
    if maximum:
        return f"软件应满足最大 {maximum} 的时序约束。"
    return f"软件应满足以下时序约束：{constraint}。"


def _project_value(value: str) -> str:
    if not value or value == "Project input required":
        return ""
    return value


def _append_suffix(value: str, suffix: str) -> str:
    return value if value.endswith(suffix) else f"{value}{suffix}"


def _interface_description(interface: str) -> str:
    if "初始化" in interface or "Init" in interface:
        return "软件应提供初始化接口，用于加载项目配置、建立底层访问上下文、配置默认状态，并在配置非法或初始化失败时返回错误。"
    if "MainFunction" in interface or "周期调度" in interface:
        return "软件应提供 MainFunction 接口，用于周期推进异步请求、处理超时、刷新运行时状态和执行诊断轮询，接口不得执行长时间阻塞操作。"
    if "输入读取" in interface:
        return "软件应提供输入读取接口，用于按项目定义的方式返回输入信号状态，并对非法参数或底层访问失败返回错误。"
    if "输出写入" in interface:
        return "软件应提供输出写入接口，用于按项目定义的方式设置输出信号状态，并对非法参数或底层访问失败返回错误。"
    if "配置" in interface:
        return "软件应提供配置接口，用于设置项目允许的配置参数，并拒绝未授权的运行时配置变更。"
    return f"软件应提供 `{interface}`，并定义输入参数、输出结果、返回值和错误处理。"


def _planned_verification(name: str, req_type: str) -> str:
    if "初始化" in name or "Init" in name:
        return "通过初始化接口测试验证：在加载默认配置时应完成上下文建立和默认状态设置；注入非法配置、底层初始化失败和重复初始化场景时，应返回定义错误，且已建立状态不得被部分破坏。"
    if "MainFunction" in name or "周期调度" in name:
        return "通过周期调度和集成测试验证：周期调用 MainFunction 时应推进异步请求、处理超时并刷新运行时状态；当无待处理任务时不得产生额外状态变化；注入超时和诊断轮询场景时应得到定义结果。"
    if "输入" in name and req_type in {"functional", "interface"}:
        return "通过功能测试和边界测试验证：模拟输入信号和配置后，接口应返回与目标一致的输入状态；非法参数或底层访问失败时，应返回定义错误并保持状态一致。"
    if "输出" in name and req_type in {"functional", "interface"}:
        return "通过功能测试和集成测试验证：对目标执行输出写入后，应产生正确的可观测输出结果；操作过程中无关状态不得被破坏；非法参数或底层访问失败时，应返回定义错误并保持原状态。"
    if "极性" in name:
        return "通过配置测试和边界测试验证：加载默认极性后应得到期望读写语义；切换反转极性时应只影响定义范围内的输入解释结果；未授权运行时修改或非法组合时应被拒绝并保留原配置。"
    if "I2C" in name or "寄存器" in name:
        return "通过接口测试和故障注入测试验证：寄存器读写成功时应返回期望结果并更新相关状态；注入 NACK、timeout 或总线错误时，应返回定义错误并保持软件状态与硬件可观测状态一致。"
    if "默认配置" in name or "地址" in name or req_type == "configuration":
        return "通过配置评审和边界测试验证：默认值加载后应形成定义配置结果；有效范围内的配置应被接受并生效；超范围、缺失或冲突配置时，应拒绝生效并给出定义结果。"
    if "状态" in name or "模式" in name:
        return "通过状态转换测试验证：在定义触发条件下应进入目标状态并更新状态观测结果；无效触发、错误恢复和重新初始化场景下，应保持或回退到定义状态。"
    if "中断" in name or "复位" in name:
        return "通过中断、复位和错误恢复场景测试验证：触发中断或复位后应产生定义状态变化或恢复动作；故障恢复完成前不得误报成功；恢复完成后应能重新进入定义运行状态。"
    if req_type == "timing":
        return "通过时序分析、超时注入和集成测试验证：在定义测量点记录等待、超时或采样间隔，确认满足最小/最大时序要求；超时到达时应触发定义错误处理。"
    return _default_verification(req_type)


def _refine_verification(
    verification: str,
    *,
    trigger: str = "",
    input_value: str = "",
    output_value: str = "",
    exception: str = "",
    constraint: str = "",
) -> str:
    clauses: list[str] = []
    if trigger:
        clauses.append(f"触发条件覆盖 `{trigger}`")
    if input_value:
        clauses.append(f"输入覆盖 `{input_value}`")
    if output_value:
        clauses.append(f"观测 `{output_value}`")
    if exception:
        clauses.append(f"异常场景覆盖 `{exception}`")
    elif constraint and any(token in constraint for token in ("非法", "错误", "拒绝", "范围", "超时", "失败")):
        clauses.append(f"边界/异常覆盖 `{constraint}`")

    if not clauses:
        return verification

    refined = verification.rstrip("。.")
    return f"{refined}；至少覆盖：{'；'.join(clauses)}。"
