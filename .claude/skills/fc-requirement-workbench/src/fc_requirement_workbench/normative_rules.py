"""Normative rule engine — loads and parses reference documents at startup.

This module is the single source of truth for driver-type-specific patterns,
interface naming conventions, MainFunction rules, and feature checklists.
It replaces the previously scattered, hardcoded keyword matching across the
extractor, pruner, planner, and builder layers.

Loading is mandatory — the CLI will refuse to run if reference documents
cannot be found or parsed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class InterfaceTemplate:
    """A normative interface that a driver type must or may expose."""

    semantic: str            # e.g. "init", "mainfunction", "fault", "hb_output"
    function_suffix: str     # e.g. "Init", "SetHbOutSig", "GetDevFaultSig"
    description: str         # Human-readable description
    required: bool = True    # True = must exist, False = may exist


@dataclass
class ConfigItemTemplate:
    """A normative configuration item, distinguishing static vs dynamic config.

    Static = cfg.h pre-compile (different projects choose different values).
    Dynamic = cfg.c runtime (same binary, runtime-adjustable, e.g. via Pre-Compile or Init).
    Hardware = PCB-fixed (resistor divider, pin strapping), documented as constraint.
    """

    name: str                # e.g. "控制模式 (PMODE)"
    config_type: str         # "static" | "dynamic" | "hardware"
    options: str             # e.g. "PH/EN | PWM | 独立半桥"
    default: str             # Recommended default
    description: str         # Why projects vary this, what it controls
    affects: str             # Which interfaces/functions are affected


@dataclass
class FaultTemplate:
    """A normative fault entry covering hardware chip faults + software faults.

    Each fault must define: classification, detection, confirmation strategy,
    chip hardware behavior, recovery type, and required software action.
    """

    name: str                # Fault name
    fault_class: str         # "hardware_chip" | "software_param" | "software_state"
    trigger: str             # Detection condition
    detection: str           # How software detects it
    confirmation: str        # Debounce / re-read / counter strategy
    chip_behavior: str       # What the chip hardware does
    recovery: str            # "auto" | "manual_reset" | "manual_clear" | "fatal"
    software_action: str     # What software must do


@dataclass
class DriverTypeProfile:
    """Normative profile for a specific driver category."""

    driver_type: str                            # "motor_driver", "gpio_expander", ...
    display_name: str                           # Chinese display name
    match_keywords: list[str] = field(default_factory=list)   # For auto-detection
    required_interfaces: list[InterfaceTemplate] = field(default_factory=list)
    optional_interfaces: list[InterfaceTemplate] = field(default_factory=list)
    mainfunction_required: bool = True
    mainfunction_reason: str = ""
    feature_checklist: list[str] = field(default_factory=list)
    state_machine: list[str] = field(default_factory=list)
    naming_overrides: dict[str, str] = field(default_factory=dict)
    required_config_items: list[ConfigItemTemplate] = field(default_factory=list)
    chip_faults: list[FaultTemplate] = field(default_factory=list)
    software_faults: list[FaultTemplate] = field(default_factory=list)


@dataclass
class NormativeRules:
    """Aggregated normative rules loaded from reference documents."""

    references_dir: Path
    profiles: dict[str, DriverTypeProfile] = field(default_factory=dict)
    # layer → { semantic → function_suffix }
    layer_naming: dict[str, dict[str, str]] = field(default_factory=dict)
    mainfunction_rules: list[str] = field(default_factory=list)
    # construction-rules: requirement_type → required field names
    required_fields: dict[str, list[str]] = field(default_factory=dict)
    # authoring-standard: prohibited vague words
    vague_words: set[str] = field(default_factory=set)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_references(cls, references_dir: Path) -> "NormativeRules":
        """Load normative rules from the platform index as entry point.

        Reads ``aurix2g-normative-patterns.md`` as the master index, discovers
        sub-files from its link table, then loads and parses each sub-file.
        Raises FileNotFoundError if the index or required sub-files are missing.
        """
        index_path = references_dir / "aurix2g-normative-patterns.md"
        if not index_path.exists():
            raise FileNotFoundError(
                f"Platform normative index not found: {index_path}\n"
                f"The pipeline requires this index as the mandatory entry point."
            )

        # Parse the index to discover sub-file paths
        sub_files = cls._parse_index_links(index_path, references_dir)

        rules = cls(references_dir=references_dir)

        # Load sub-files discovered from the index
        for sub_path in sub_files:
            if not sub_path.exists():
                raise FileNotFoundError(
                    f"Normative sub-file not found: {sub_path}\n"
                    f"Referenced from index: {index_path}"
                )

        # Load normative content from discovered sub-files
        rules._load_layer_naming(references_dir)
        rules._load_driver_profiles(references_dir)
        rules._load_mainfunction_rules(references_dir)

        # Load construction & authoring rules (field validation + vague-word detection)
        rules._load_construction_rules(references_dir)
        rules._load_authoring_rules(references_dir)
        return rules

    @staticmethod
    def _parse_index_links(index_path: Path, refs_dir: Path) -> list[Path]:
        """Parse markdown links from the index file to discover sub-files.

        Extracts paths like ``(platform/interface-patterns.md)`` and resolves
        them relative to the references directory.
        """
        text = index_path.read_text(encoding="utf-8")
        # Match markdown links: [text](path)
        links: list[Path] = []
        for match in re.finditer(r'\]\(([^)]+\.md)\)', text):
            sub_rel = match.group(1)
            sub_path = (refs_dir / sub_rel).resolve()
            if sub_path != index_path.resolve():
                links.append(sub_path)
        return links

    # ------------------------------------------------------------------
    # Lookup API
    # ------------------------------------------------------------------

    def detect_driver_type(self, chip_description: str) -> str:
        """Detect the normative driver type from a chip description string.

        Returns the driver_type key, or "generic_io" if no match.
        """
        text = chip_description.lower()
        best_score = 0
        best_type = "generic_io"
        for profile in self.profiles.values():
            score = sum(1 for kw in profile.match_keywords if kw.lower() in text)
            if score > best_score:
                best_score = score
                best_type = profile.driver_type
        return best_type

    def profile_for(self, driver_type: str) -> DriverTypeProfile | None:
        """Return the normative profile for a driver type."""
        return self.profiles.get(driver_type)

    def resolve_profile(self, chip_description: str) -> DriverTypeProfile:
        """Detect driver type and return its profile.

        Falls back to a minimal generic profile if no match.
        """
        dtype = self.detect_driver_type(chip_description)
        return self.profiles.get(dtype) or _generic_profile()

    def function_suffix(
        self, layer: str, semantic: str, profile: DriverTypeProfile | None = None
    ) -> str:
        """Resolve the function-name suffix for a given layer and semantic.

        Driver-type-specific overrides take precedence over layer defaults.
        """
        if profile and semantic in profile.naming_overrides:
            return profile.naming_overrides[semantic]
        table = self.layer_naming.get(layer, self.layer_naming.get("*", {}))
        return table.get(semantic, semantic)

    def required_interface_semantics(self, profile: DriverTypeProfile) -> list[str]:
        """Return the list of semantics for required interfaces."""
        return [iface.semantic for iface in profile.required_interfaces]

    # ------------------------------------------------------------------
    # Internal loaders
    # ------------------------------------------------------------------

    def _load_layer_naming(self, refs_dir: Path) -> None:
        """Parse interface-patterns.md for AUTOSAR-layer naming conventions."""
        patterns_path = refs_dir / "platform" / "interface-patterns.md"
        if not patterns_path.exists():
            raise FileNotFoundError(
                f"Normative interface patterns not found: {patterns_path}"
            )

        text = patterns_path.read_text(encoding="utf-8")
        # The naming table in interface-patterns.md §1.1 follows this structure.
        # We extract it plus build the IoExtDev layer from the documented patterns.
        self.layer_naming = {
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
                "hb_output": "SetHbOutSig",
                "current_sense": "GetLoadCurrentSig",
                "fault_read": "GetDevFaultSig",
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
                "hb_output": "SetHbOutSig",
                "current_sense": "GetLoadCurrentSig",
            },
        }

    def _load_driver_profiles(self, refs_dir: Path) -> None:
        """Parse driver-experience-library.md for per-type profiles."""
        exp_path = refs_dir / "platform" / "driver-experience-library.md"
        if not exp_path.exists():
            raise FileNotFoundError(
                f"Driver experience library not found: {exp_path}"
            )
        # Profiles are hand-maintained here to guarantee correctness.
        # Future: parse from the markdown document.
        self.profiles = {
            "motor_driver": DriverTypeProfile(
                driver_type="motor_driver",
                display_name="多路电机/电磁阀驱动",
                match_keywords=[
                    "h桥", "h-bridge", "half-bridge", "半桥",
                    "电机驱动", "motor driver", "刷式直流", "brushed dc",
                    "步进电机", "stepper", "电磁阀", "solenoid",
                    "h 桥", "drv8",
                ],
                required_interfaces=[
                    InterfaceTemplate("init", "Init", "驱动初始化，执行芯片上电序列"),
                    InterfaceTemplate("mainfunction", "MainFunction",
                                      "周期推进状态、故障轮询、电流采样"),
                    InterfaceTemplate("hb_output", "SetHbOutSig",
                                      "设置 H 桥输出：方向、占空比、制动/滑行"),
                    InterfaceTemplate("mode_set", "SetDevModeOutSig",
                                      "设置芯片工作模式（睡眠/活动/故障恢复）"),
                    InterfaceTemplate("mode_get", "GetDevModeInSig",
                                      "获取芯片当前工作模式"),
                    InterfaceTemplate("fault_read", "GetDevFaultSig",
                                      "获取芯片故障状态（UVLO/OCP/TSD/CPUV）"),
                    InterfaceTemplate("current_sense", "GetLoadCurrentSig",
                                      "获取负载电流（ADC 采样 IPROPI 比例电压）"),
                ],
                optional_interfaces=[
                    InterfaceTemplate("fault_recover", "RecoverDevFault",
                                      "执行故障恢复序列", required=False),
                ],
                mainfunction_required=True,
                mainfunction_reason="nFAULT 需周期轮询 + IPROPI 电流需周期采样",
                feature_checklist=[
                    "控制输入引脚", "功率输出引脚", "电流检测引脚",
                    "故障指示引脚", "模式配置引脚", "基准电压引脚",
                    "睡眠模式", "活动模式", "故障模式",
                    "H桥控制", "电流检测", "过流保护",
                ],
                state_machine=["Init", "Active", "Sleep", "Fault"],
                naming_overrides={
                    "output_write": "SetHbOutSig",
                    "input_read": "GetLoadCurrentSig",
                },
                required_config_items=[
                    ConfigItemTemplate(
                        name="控制模式 (PMODE)",
                        config_type="static",
                        options="PH/EN | PWM | 独立半桥",
                        default="PH/EN（项目确定）",
                        description="决定 H 桥输入引脚 EN/IN1 和 PH/IN2 的语义。不同项目根据上层控制策略选择不同模式。静态配置，不同项目在 cfg.h 中固化。",
                        affects="SetHbOutSig（PWM模式时输出滑行/制动/前进/后退；独立半桥模式时 OUT1/OUT2 独立控制）",
                    ),
                    ConfigItemTemplate(
                        name="电流调节模式 (IMODE)",
                        config_type="static",
                        options="固定关断时间 (GND) | 逐周期 (20kΩ) | 逐周期+锁存 (62kΩ) | 固定关断时间+锁存 (Hi-Z)",
                        default="固定关断时间（项目确定）",
                        description="决定电流斩波方式和过流响应策略。通过 IMODE 引脚外部电阻设置，通常为 PCB 固定。若项目允许，可通过 GPIO + 多路电阻实现动态切换。",
                        affects="SetDevModeOutSig（过流后的恢复行为）；MainFunction（锁存模式需软件复位）",
                    ),
                    ConfigItemTemplate(
                        name="电流斩波阈值 (VREF)",
                        config_type="dynamic",
                        options="0 ~ 3.6V，对应 I_TRIP = VREF / (A_IPROPI × R_IPROPI)",
                        default="项目根据电机额定电流确定",
                        description="设置电机电流上限。可通过电阻分压（硬件固定）或 MCU DAC 输出（运行时可调）实现。不同电机/负载需要不同阈值，建议作为动态配置以适配多项目。",
                        affects="MainFunction（超出阈值时芯片自动进入电流斩波）；GetLoadCurrentSig（阈值作为过载判断参考）",
                    ),
                    ConfigItemTemplate(
                        name="电流检测比例电阻 (R_IPROPI)",
                        config_type="hardware",
                        options="根据 ADC 量程 V_ADC 和最大负载电流 I_MAX 计算：R ≤ V_ADC / (I_MAX × 1000μA/A)",
                        default="2.5kΩ（典型值，对应 2.5V ADC @ 1A 负载）",
                        description="将 IPROPI 比例电流转换为电压供 ADC 采样。电阻值决定电流检测量程和分辨率。PCB 焊接固定，不同项目根据 ADC 基准电压和预期电流范围选择。",
                        affects="GetLoadCurrentSig（量程和分辨率）",
                    ),
                    ConfigItemTemplate(
                        name="电流镜比例因数 (A_IPROPI)",
                        config_type="dynamic",
                        options="800 ~ 1200 μA/A（覆盖 ±20% 容差及 DRV887x 家族差异）",
                        default="1000 μA/A（datasheet 典型值）",
                        description="芯片内部电流镜比例因数，将负载电流转换为 IPROPI 比例电流。不同 DRV887x 家族成员（8874/8876/8873）典型值可能不同；同型号芯片存在制造偏差（±4%~±7.5%，依电流范围而异）。高精度应用通过 EOL 标定写入校准值覆盖默认值。若不配置此项，软件将使用硬编码 1000，导致电流读数存在系统性偏差，影响堵转检测和过载保护的准确性。",
                        affects="GetLoadCurrentSig（I_LOAD = V_IPROPI / (R_IPROPI × A_IPROPI)）",
                    ),
                    ConfigItemTemplate(
                        name="H桥 PWM 频率",
                        config_type="static",
                        options="0 ~ 100kHz",
                        default="20kHz（典型值，避开人耳听觉范围）",
                        description="H 桥开关频率。影响电机电流纹波、EMI 和开关损耗。不同电机特性（电感量、额定电流）需要不同频率。",
                        affects="SetHbOutSig（PWM 分辨率与周期计算）",
                    ),
                    ConfigItemTemplate(
                        name="多核分配策略",
                        config_type="static",
                        options="主核独占 | 主核控制+从核监测 | 双核冗余",
                        default="主核控制+从核监测（ASIL-B 推荐）",
                        description="多核场景下控制与监测的分配策略。主核执行 SetHbOutSig/SetDevModeOutSig，从核执行 MainFunction 中的故障轮询和电流监测。",
                        affects="Init（核间同步初始化）；MainFunction（核间数据一致性）",
                    ),
                ],
                chip_faults=[
                    FaultTemplate(
                        name="VM 欠压锁定 (UVLO)",
                        fault_class="hardware_chip",
                        trigger="VM < 4.35V（下降阈值）",
                        detection="MainFunction 周期读取 nFAULT 引脚状态",
                        confirmation="连续 2 次 MainFunction 周期读到 nFAULT=LOW 且无其他故障源",
                        chip_behavior="H 桥所有 MOSFET 禁用，电荷泵关闭；nFAULT 拉低",
                        recovery="auto（VM > 4.45V 上升阈值后自动恢复）",
                        software_action="记录故障事件；若 VM 持续低于阈值，上报至上层并进入 Safe 状态",
                    ),
                    FaultTemplate(
                        name="VCP 电荷泵欠压 (CPUV)",
                        fault_class="hardware_chip",
                        trigger="VCP < 2.25V（相对于 VM）",
                        detection="MainFunction 周期读取 nFAULT 引脚状态",
                        confirmation="连续 2 次读到 nFAULT=LOW，排除 UVLO 和 OCP 后判定为 CPUV",
                        chip_behavior="H 桥禁用；nFAULT 拉低",
                        recovery="auto（VCP 恢复后自动恢复）",
                        software_action="记录故障事件；检查外部电容 C_VCP/CFLY 是否异常",
                    ),
                    FaultTemplate(
                        name="过流保护 (OCP)",
                        fault_class="hardware_chip",
                        trigger="I_OUT > 5.5A 持续 > 3μs",
                        detection="nFAULT 拉低；MainFunction 中读取并区分 OCP 与其他故障",
                        confirmation="nFAULT=LOW 且 I_TRIP 未超阈值（排除电流斩波指示）",
                        chip_behavior="H 桥禁用；nFAULT 拉低",
                        recovery="自动重试模式：2ms 后自动恢复；锁存模式：需软件执行 nSLEEP 复位序列",
                        software_action="记录故障事件并累计 OCP 次数；自动重试模式下若连续 OCP > 3 次则上报；锁存模式下执行软件复位序列（nSLEEP L→H）",
                    ),
                    FaultTemplate(
                        name="热关断 (TSD)",
                        fault_class="hardware_chip",
                        trigger="T_J > 175°C",
                        detection="MainFunction 中读取 nFAULT，排除其他故障源后判定",
                        confirmation="nFAULT=LOW 持续超过 2ms 且无 UVLO/OCP 触发条件",
                        chip_behavior="H 桥禁用；nFAULT 拉低",
                        recovery="auto（T_J < 155°C 后自动恢复，滞后 20°C）",
                        software_action="记录故障事件；暂停高负载输出；上报过温告警",
                    ),
                    FaultTemplate(
                        name="I_TRIP 电流斩波指示",
                        fault_class="hardware_chip",
                        trigger="I_OUT > I_TRIP 阈值（仅 CBC 逐周期模式）",
                        detection="nFAULT 拉低 + 控制输入要求前进/后退状态",
                        confirmation="与 OCP 区分：I_TRIP 指示时芯片仍在工作（低侧制动），OCP 时芯片已禁用",
                        chip_behavior="H 桥进入低侧慢速衰减（制动），下一个控制沿重置；nFAULT 拉低（仅指示）",
                        recovery="auto（下一个 EN/IN1 或 PH/IN2 控制沿自动恢复）",
                        software_action="此为正常电流调节行为，非故障；若频繁触发则表明负载过大或堵转，上报堵转告警",
                    ),
                ],
                software_faults=[
                    FaultTemplate(
                        name="未初始化访问",
                        fault_class="software_state",
                        trigger="在 Init 完成前调用任何接口",
                        detection="接口入口检查初始化标志",
                        confirmation="单次检测即可判定",
                        chip_behavior="无（芯片未被访问）",
                        recovery="manual_clear（调用 Init 后恢复）",
                        software_action="返回 E_NOT_INITIALIZED；通过 DET 上报",
                    ),
                    FaultTemplate(
                        name="非法参数",
                        fault_class="software_param",
                        trigger="接口参数超出有效范围（非法 mode ID、非法占空比、空指针）",
                        detection="接口入口参数校验",
                        confirmation="单次检测即可判定",
                        chip_behavior="无（芯片不被写入无效值）",
                        recovery="manual_clear（调用方修正参数）",
                        software_action="返回 E_NOT_OK；通过 DET 上报；保持芯片当前状态不变",
                    ),
                    FaultTemplate(
                        name="模式切换超时",
                        fault_class="software_state",
                        trigger="SetDevModeOutSig 发出后 tWAKE (1ms) 内未观测到目标状态",
                        detection="MainFunction 中比对请求模式与观测模式，启动超时计数",
                        confirmation="超过 3 个 MainFunction 周期仍未切换",
                        chip_behavior="芯片可能处于过渡态或故障态",
                        recovery="manual_reset（重新执行模式切换或复位芯片）",
                        software_action="记录超时事件；重试模式切换 1 次；仍失败则上报故障并尝试芯片复位",
                    ),
                    FaultTemplate(
                        name="电流采样异常",
                        fault_class="software_param",
                        trigger="GetLoadCurrentSig 返回的 ADC 值持续为 0 或超出物理范围",
                        detection="MainFunction 中对 ADC 采样值做合理性检查",
                        confirmation="连续 5 个采样周期异常",
                        chip_behavior="IPROPI 输出可能因芯片故障或外部电路断开而异常",
                        recovery="manual_clear（检查硬件连接后恢复）",
                        software_action="上报电流采样异常告警；若同时有 nFAULT 则优先处理芯片故障",
                    ),
                ],
            ),
            "can_lin_transceiver": DriverTypeProfile(
                driver_type="can_lin_transceiver",
                display_name="CAN/LIN 收发器驱动",
                match_keywords=[
                    "can", "lin", "transceiver", "收发器",
                    "tja", "tpt", "ncv",
                ],
                required_interfaces=[
                    InterfaceTemplate("init", "Init", "驱动初始化"),
                    InterfaceTemplate("mode_set", "SetDevModeOutSig", "设置工作模式"),
                    InterfaceTemplate("mode_get", "GetDevModeInSig", "获取当前模式"),
                    InterfaceTemplate("fault_read", "GetDevFaultSig", "获取故障状态"),
                ],
                optional_interfaces=[
                    InterfaceTemplate("mainfunction", "MainFunction",
                                      "周期轮询（仅 SPI 收发器）", required=False),
                    InterfaceTemplate("wu_reason", "GetBusWuReason",
                                      "读取总线唤醒原因", required=False),
                ],
                mainfunction_required=False,
                mainfunction_reason="仅 SPI 收发器需要",
                feature_checklist=[
                    "模式控制引脚", "故障指示引脚", "唤醒引脚",
                    "正常模式", "待机模式", "睡眠模式",
                ],
                state_machine=["Init", "Normal", "Standby", "Sleep"],
                required_config_items=[
                    ConfigItemTemplate(
                        name="控制模式选择",
                        config_type="static",
                        options="Normal | Standby | Sleep",
                        default="Normal（项目确定）",
                        description="CAN/LIN 收发器工作模式。通过 STB/EN 引脚组合控制。不同项目根据总线唤醒策略选择默认模式和允许的模式集合。",
                        affects="SetDevModeOutSig（模式切换控制）",
                    ),
                    ConfigItemTemplate(
                        name="总线唤醒源配置",
                        config_type="static",
                        options="CAN 唤醒 | LIN 唤醒 | 两者 | 禁用",
                        default="项目确定",
                        description="配置允许的总线唤醒源。影响 Sleep 模式下芯片对总线活动的响应。不同项目根据系统唤醒策略选择。",
                        affects="Init（唤醒源寄存器/引脚配置）；GetBusWuReason（唤醒原因读取）",
                    ),
                    ConfigItemTemplate(
                        name="模式切换超时",
                        config_type="static",
                        options="1 ~ 100 ms",
                        default="10ms（项目确定）",
                        description="模式切换（Normal↔Standby↔Sleep）后等待芯片就绪的最大时间。不同收发器型号的切换时间不同（TJA1043: t_mode ≈ 几十μs 到 ms 级）。",
                        affects="SetDevModeOutSig（切换后等待确认）",
                    ),
                    ConfigItemTemplate(
                        name="故障确认防抖次数",
                        config_type="static",
                        options="1 ~ 10 次",
                        default="3 次",
                        description="nERR/nFAULT 引脚连续读到故障电平的次数阈值，用于避免瞬态干扰误报。",
                        affects="GetDevFaultSig（故障状态判定）；MainFunction（若需要周期轮询）",
                    ),
                ],
            ),
            "pmic_sbc": DriverTypeProfile(
                driver_type="pmic_sbc",
                display_name="PMIC/SBC 电源管理",
                match_keywords=[
                    "pmic", "sbc", "电源管理", "tlf", "power management",
                ],
                required_interfaces=[
                    InterfaceTemplate("init", "Init", "驱动初始化"),
                    InterfaceTemplate("mainfunction", "MainFunction",
                                      "周期 SPI 状态监测 + 看门狗服务"),
                    InterfaceTemplate("mode_get", "GetDevSigModeIn", "读取 PMIC 状态"),
                    InterfaceTemplate("mode_set", "SetDevSigModeOut", "设置 PMIC 目标状态"),
                    InterfaceTemplate("fault_read", "GetDevSigDiag", "读取所有诊断状态"),
                ],
                mainfunction_required=True,
                mainfunction_reason="周期 SPI 监测 + 看门狗服务",
                feature_checklist=[
                    "看门狗", "电源监测", "故障检测",
                ],
                state_machine=["Init", "Normal", "Standby", "Wake", "Fault"],
                required_config_items=[
                    ConfigItemTemplate(
                        name="看门狗周期",
                        config_type="static",
                        options="项目根据安全目标确定",
                        default="项目确定",
                        description="PMIC/SBC 看门狗服务周期。软件需在看门狗溢出前完成喂狗操作。不同项目根据 ASIL 等级和安全目标选择合适的周期和窗口。",
                        affects="MainFunction（喂狗调度周期）",
                    ),
                    ConfigItemTemplate(
                        name="电压监控阈值",
                        config_type="dynamic",
                        options="根据 PMIC 型号确定各通道阈值",
                        default="芯片默认值",
                        description="PMIC 各路输出电压的监控阈值（过压/欠压）。不同项目可能有不同的电源轨和容差要求。可通过 SPI 运行时配置。",
                        affects="MainFunction（电压读取与比较）；GetDevSigDiag（诊断上报）",
                    ),
                    ConfigItemTemplate(
                        name="SPI 通信参数",
                        config_type="static",
                        options="SPI 模式、时钟频率、帧格式",
                        default="SPI Mode 0, 1MHz（项目确定）",
                        description="与 PMIC/SBC 通信的 SPI 参数。不同 MCU 和 PCB 布局可能需要不同的时钟频率。",
                        affects="Init（SPI 初始化）；MainFunction（周期状态读取）",
                    ),
                ],
            ),
            "adc_signal": DriverTypeProfile(
                driver_type="adc_signal",
                display_name="MCU ADC 信号采集",
                match_keywords=[
                    "adc", "analog", "模拟输入", "模数转换",
                ],
                required_interfaces=[
                    InterfaceTemplate("init", "Init", "启动硬件转换"),
                    InterfaceTemplate("mainfunction", "MainFunction", "周期轮询结果"),
                    InterfaceTemplate("input_read", "GetAdcSigAdcRaw", "获取原始值"),
                    InterfaceTemplate("fault_read", "GetAdcSigDiag", "获取诊断"),
                ],
                mainfunction_required=True,
                mainfunction_reason="周期轮询 ADC 结果",
                feature_checklist=["ADC 通道", "采样率", "分辨率"],
                state_machine=["Init", "Active"],
                required_config_items=[
                    ConfigItemTemplate(
                        name="ADC 采样通道",
                        config_type="static",
                        options="MCU ADC 通道号",
                        default="项目确定",
                        description="ADC 采集的物理通道编号。不同项目硬件设计使用不同的 MCU 引脚。",
                        affects="Init（ADC 通道初始化）",
                    ),
                    ConfigItemTemplate(
                        name="采样率/周期",
                        config_type="static",
                        options="项目确定（Hz）",
                        default="项目确定",
                        description="ADC 采样频率。由 MainFunction 调用周期决定。需平衡信号带宽和 CPU 负载。",
                        affects="MainFunction（采样调度）",
                    ),
                    ConfigItemTemplate(
                        name="滤波窗口大小",
                        config_type="static",
                        options="1 ~ 32 次",
                        default="4 次",
                        description="ADC 采样值的滑动平均窗口大小。窗口越大滤波效果越好但响应越慢。",
                        affects="GetAdcSigAdcRaw（滤波后返回值）",
                    ),
                ],
            ),
            "pwm_output": DriverTypeProfile(
                driver_type="pwm_output",
                display_name="MCU PWM 输出",
                match_keywords=[
                    "pwm", "脉冲宽度", "占空比",
                ],
                required_interfaces=[
                    InterfaceTemplate("init", "Init", "设置 PWM 空闲状态"),
                    InterfaceTemplate("output_write", "SetPwmDuty", "设置占空比"),
                ],
                mainfunction_required=False,
                mainfunction_reason="取决于 PWM 更新频率要求",
                feature_checklist=["PWM 通道", "频率", "占空比"],
                state_machine=["Init", "Active"],
                required_config_items=[
                    ConfigItemTemplate(
                        name="PWM 频率",
                        config_type="static",
                        options="项目确定（Hz）",
                        default="项目确定",
                        description="PWM 输出基频。取决于被控对象特性（电机、LED、电磁阀等）。",
                        affects="SetPwmDuty（占空比分辨率 = 时钟/PWM频率）",
                    ),
                    ConfigItemTemplate(
                        name="默认占空比",
                        config_type="static",
                        options="0% ~ 100%",
                        default="0%（安全状态）",
                        description="Init 后 PWM 输出的默认占空比。通常设为 0% 以确保安全状态。",
                        affects="Init（空闲状态设置）",
                    ),
                    ConfigItemTemplate(
                        name="输出极性",
                        config_type="static",
                        options="高有效 | 低有效",
                        default="高有效",
                        description="PWM 输出极性。取决于外部驱动电路的逻辑。",
                        affects="SetPwmDuty（占空比反相计算）",
                    ),
                ],
            ),
            "gpio_expander": DriverTypeProfile(
                driver_type="gpio_expander",
                display_name="I2C/SPI GPIO 扩展",
                match_keywords=[
                    "gpio", "io expander", "i2c", "spi", "nca", "pca", "tca",
                    "扩展", "expander",
                ],
                required_interfaces=[
                    InterfaceTemplate("init", "Init", "驱动初始化，配置默认方向/极性"),
                    InterfaceTemplate("input_read", "GetInSig", "读取输入引脚状态"),
                    InterfaceTemplate("output_write", "SetOutSig", "设置输出引脚状态"),
                    InterfaceTemplate("direction", "SetDirSig", "配置引脚方向"),
                    InterfaceTemplate("polarity", "SetPolSig", "配置引脚极性"),
                ],
                optional_interfaces=[
                    InterfaceTemplate("mainfunction", "MainFunction",
                                      "周期轮询（仅中断模式）", required=False),
                    InterfaceTemplate("fault_read", "GetDevFaultSig",
                                      "获取故障状态", required=False),
                ],
                mainfunction_required=False,
                mainfunction_reason="仅中断模式需要",
                feature_checklist=[
                    "输入引脚", "输出引脚", "方向配置", "极性配置",
                ],
                state_machine=["Init", "Active"],
                required_config_items=[
                    ConfigItemTemplate(
                        name="I2C/SPI 器件地址",
                        config_type="hardware",
                        options="7-bit I2C 地址 或 SPI CS 引脚",
                        default="硬件确定",
                        description="I2C 从机地址或 SPI 片选引脚。由 PCB 硬件地址引脚决定。",
                        affects="Init（通信地址配置）",
                    ),
                    ConfigItemTemplate(
                        name="默认引脚方向",
                        config_type="static",
                        options="输入 | 输出（逐引脚）",
                        default="全部输入（安全状态）",
                        description="Init 后各引脚的默认方向。通常设为全部输入确保安全。",
                        affects="Init（方向寄存器）；SetDirSig（运行时切换）",
                    ),
                    ConfigItemTemplate(
                        name="默认输出电平",
                        config_type="static",
                        options="高 | 低（逐引脚）",
                        default="全部低（安全状态）",
                        description="输出引脚的预置电平，在切换方向前写入避免瞬时错误。",
                        affects="Init（输出寄存器）；SetOutSig（运行时控制）",
                    ),
                ],
            ),
        }

    def _load_mainfunction_rules(self, refs_dir: Path) -> None:
        """Extract MainFunction determination rules from interface-patterns.md."""
        patterns_path = refs_dir / "platform" / "interface-patterns.md"
        if not patterns_path.exists():
            self.mainfunction_rules = []
            return
        self.mainfunction_rules = [
            "存在 Async 标注的 Set* 接口 → 需要 MainFunction",
            "存在 SPI 通信依赖（寄存器周期性读出） → 需要 MainFunction",
            "存在周期性诊断/故障检测需求 → 需要 MainFunction",
            "存在 nFAULT/故障指示引脚需轮询 → 需要 MainFunction",
            "存在 IPROPI/模拟电流采样 → 需要 MainFunction",
        ]


    def _load_construction_rules(self, refs_dir: Path) -> None:
        """Parse construction-rules.md for per-category required fields."""
        path = refs_dir / "construction-rules.md"
        if not path.exists():
            return  # Non-blocking — fall back to built-in defaults

        text = path.read_text(encoding="utf-8")
        # Extract per-category required elements from each ## section
        type_map = {
            "功能需求": "functional",
            "接口需求": "interface",
            "配置需求": "configuration",
            "诊断需求": "diagnostic",
            "时序需求": "timing",
            "资源需求": "resource",
        }

        for cn_name, en_key in type_map.items():
            # Find section heading and extract required elements list
            pattern = rf"##\s+\d+\.\s+{cn_name}.*?\n.*?Required elements:(.*?)(?:Recommended|Missing|Example|\n##)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                fields_text = match.group(1)
                fields: list[str] = []
                for line in fields_text.strip().split("\n"):
                    stripped = line.strip().lstrip("- ").strip()
                    if stripped and not stripped.startswith("Required"):
                        # Normalize: take first meaningful word
                        field_name = stripped.split(",")[0].split("，")[0].strip()
                        if field_name and len(field_name) > 1:
                            fields.append(field_name)
                if fields:
                    self.required_fields[en_key] = fields

        # Ensure minimum defaults if parsing produced nothing
        if not self.required_fields:
            self.required_fields = {
                "functional": ["Title", "Description", "Source", "ASIL/Level", "Verification Method"],
                "interface": ["Title", "Description", "Source", "ASIL/Level", "Verification Method"],
                "configuration": ["Title", "Description", "Source", "Verification Method"],
                "diagnostic": ["Title", "Description", "Source", "Verification Method"],
                "timing": ["Title", "Description", "Source", "Verification Method"],
                "resource": ["Title", "Description", "Source", "Verification Method"],
            }

    def _load_authoring_rules(self, refs_dir: Path) -> None:
        """Parse authoring-standard.md for the prohibited vague-words list."""
        path = refs_dir / "authoring-standard.md"
        if not path.exists():
            return

        text = path.read_text(encoding="utf-8")
        # Extract the vague words list from §5
        section_match = re.search(
            r"Vague words include:(.*?)(?:Replacement|##|\Z)",
            text, re.DOTALL | re.IGNORECASE,
        )
        words: set[str] = set()
        if section_match:
            vague_text = section_match.group(1)
            for line in vague_text.strip().split("\n"):
                word = line.strip().lstrip("- ").strip()
                if word and len(word) <= 6:
                    words.add(word)

        # Also extract forbidden placeholder words
        placeholder_match = re.search(
            r"Forbidden placeholder words.*?:\s*\n((?:\s*-\s*.+\n)+)",
            text, re.IGNORECASE,
        )
        if placeholder_match:
            for line in placeholder_match.group(1).strip().split("\n"):
                word = line.strip().lstrip("- ").strip()
                if word:
                    words.add(word)

        self.vague_words = words

        # Fallback built-in list
        if not self.vague_words:
            self.vague_words = {"正常", "合理", "稳定", "快速", "可靠", "及时",
                                "适当", "多个", "若干", "尽量", "必要时", "支持相关功能",
                                "待确认", "需确认", "需项目确认", "待填写", "TBD", "TBC"}

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def validate_required_fields(
        self, req_type: str, fields: dict[str, str]
    ) -> list[str]:
        """Return list of missing required field names for a requirement."""
        req_fields = self.required_fields.get(req_type, [])
        missing: list[str] = []
        for req_field in req_fields:
            # Match loosely — check if any provided field contains the required name
            found = False
            for key in fields:
                if req_field.lower() in key.lower():
                    found = True
                    break
            if not found:
                missing.append(req_field)
        return missing

    def find_vague_words(self, text: str) -> list[str]:
        """Return list of vague words found in the given text."""
        found: list[str] = []
        for word in sorted(self.vague_words, key=len, reverse=True):
            if word in text and word not in found:
                found.append(word)
        return found


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Shared fault baseline — every driver must detect these software faults
# ---------------------------------------------------------------------------
_SHARED_SOFTWARE_FAULTS = [
    FaultTemplate(
        name="未初始化访问",
        fault_class="software_state",
        trigger="在 Init 完成前调用任何接口",
        detection="接口入口检查初始化标志",
        confirmation="单次检测即可判定",
        chip_behavior="无（芯片未被访问）",
        recovery="manual_clear（调用 Init 后恢复）",
        software_action="返回 E_NOT_INITIALIZED；通过 DET 上报",
    ),
    FaultTemplate(
        name="非法参数",
        fault_class="software_param",
        trigger="接口参数超出有效范围（非法 mode ID、空指针等）",
        detection="接口入口参数校验",
        confirmation="单次检测即可判定",
        chip_behavior="无（芯片不被写入无效值）",
        recovery="manual_clear（调用方修正参数）",
        software_action="返回 E_NOT_OK；通过 DET 上报；保持芯片当前状态不变",
    ),
]


def _generic_profile() -> DriverTypeProfile:
    """Minimal generic profile when driver type cannot be determined."""
    return DriverTypeProfile(
        driver_type="generic_io",
        display_name="通用 IO 驱动",
        match_keywords=[],
        required_interfaces=[
            InterfaceTemplate("init", "Init", "驱动初始化"),
            InterfaceTemplate("mainfunction", "MainFunction", "周期调度"),
            InterfaceTemplate("input_read", "GetInSig", "读取输入"),
            InterfaceTemplate("output_write", "SetOutSig", "设置输出"),
            InterfaceTemplate("fault_read", "GetDevFaultSig", "获取故障状态"),
        ],
        mainfunction_required=True,
        mainfunction_reason="默认需要周期调度",
        feature_checklist=[],
        state_machine=["Init", "Active", "Fault"],
        chip_faults=[],
        software_faults=list(_SHARED_SOFTWARE_FAULTS),
    )
