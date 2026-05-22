"""Multi-view feature extraction for SRS generation intermediate output."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
import re
from typing import Any, Literal

from .parser import DocumentChunk, ParsedDocument


FeatureType = Literal[
    "identity",
    "capability",
    "mode",
    "pin",
    "interface",
    "register",
    "bitfield",
    "configuration",
    "state_machine",
    "diagnostic",
    "timing",
    "prohibited",
    "resource",
    "electrical",
    "constraint",
    "project_mapping",
    "feature_group",
]


@dataclass(frozen=True)
class SubfunctionRecord:
    name: str
    summary: str
    trigger: str = ""
    inputs: str = ""
    outputs: str = ""
    preconditions: str = ""
    postconditions: str = ""
    boundary: str = ""
    timing: str = ""
    related_pins: list[str] = field(default_factory=list)
    related_registers: list[str] = field(default_factory=list)
    application_scheme: str = ""
    candidate_requirement_types: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    can_generate_requirement: str = "Needs Review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FeatureRecord:
    id: str
    type: FeatureType
    name: str
    content: str
    software_responsibility: str
    source: str
    source_priority: str
    merged_from: list[str]
    gap: str
    status: str
    can_generate_requirement: str
    notes: str = ""
    extractor: str = ""
    feature_category: str = ""
    functional_summary: str = ""
    evidence: list[str] = field(default_factory=list)
    related_pins: list[str] = field(default_factory=list)
    related_registers: list[str] = field(default_factory=list)
    candidate_requirement_types: list[str] = field(default_factory=list)
    application_scheme: str = ""
    missing_inputs: list[str] = field(default_factory=list)
    subfunctions: list[SubfunctionRecord] = field(default_factory=list)
    evidence_level: str = ""
    software_actions: list[str] = field(default_factory=list)
    ready_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class _Candidate:
    type: FeatureType
    name: str
    content: str
    chunk: DocumentChunk | None
    software_responsibility: str
    status: str
    can_generate_requirement: str
    gap: str = ""
    notes: str = ""
    extractor: str = ""
    feature_category: str = ""
    functional_summary: str = ""
    evidence: tuple[str, ...] = ()
    related_pins: tuple[str, ...] = ()
    related_registers: tuple[str, ...] = ()
    candidate_requirement_types: tuple[str, ...] = ()
    application_scheme: str = ""
    missing_inputs: tuple[str, ...] = ()
    subfunctions: tuple[SubfunctionRecord, ...] = ()
    merged_from: tuple[str, ...] = ()
    evidence_level: str = ""
    software_actions: tuple[str, ...] = ()
    ready_conditions: tuple[str, ...] = ()


class FeatureExtractor:
    """Extract feature candidates before SRS requirement construction.

    The extractor follows the skill's multi-view design: independent extractors
    read the same parsed document from different angles, then the results are
    deduplicated, aggregated into feature groups, and classified for SRS use.
    """

    def __init__(self, module: str = "FC") -> None:
        self.module = _module_token(module)

    def extract(self, parsed: ParsedDocument) -> list[FeatureRecord]:
        chunks = [chunk for chunk in parsed.chunks if not _skip_chunk(chunk)]
        extractors = (
            self._extract_identity,
            self._extract_capabilities,
            self._extract_pins,
            self._extract_interfaces,
            self._extract_registers,
            self._extract_bitfields,
            self._extract_states,
            self._extract_diagnostics,
            self._extract_timing,
            self._extract_electrical,
            self._extract_constraints,
            self._extract_project_mapping,
        )
        with ThreadPoolExecutor(max_workers=min(8, len(extractors))) as executor:
            batches = list(executor.map(lambda fn: fn(parsed, chunks), extractors))

        candidates = [candidate for batch in batches for candidate in batch]
        raw_records = self._materialize(_dedupe_candidates(candidates))
        grouped_records = self._build_feature_groups(raw_records)
        return _dedupe_records([*grouped_records, *raw_records])

    def _materialize(self, candidates: list[_Candidate]) -> list[FeatureRecord]:
        counters: Counter[str] = Counter()
        records: list[FeatureRecord] = []
        for candidate in candidates:
            counters[candidate.type] += 1
            records.append(
                # Keep inferred quality gates on every record so the renderer and
                # later construction stage can distinguish evidence from action.
                FeatureRecord(
                    id=f"EXT-{self.module}-{_type_code(candidate.type)}-{counters[candidate.type]:04d}",
                    type=candidate.type,
                    name=candidate.name,
                    content=_summary(candidate.content, 360),
                    software_responsibility=candidate.software_responsibility,
                    source=_source_ref(candidate.chunk) if candidate.chunk else "aggregated",
                    source_priority=_source_priority(candidate.chunk) if candidate.chunk else "aggregated",
                    merged_from=list(candidate.merged_from),
                    gap=candidate.gap,
                    status=candidate.status,
                    can_generate_requirement=candidate.can_generate_requirement,
                    notes=candidate.notes,
                    extractor=candidate.extractor,
                    feature_category=candidate.feature_category,
                    functional_summary=candidate.functional_summary or _summary(candidate.content, 220),
                    evidence=list(candidate.evidence),
                    related_pins=list(candidate.related_pins),
                    related_registers=list(candidate.related_registers),
                    candidate_requirement_types=list(candidate.candidate_requirement_types),
                    application_scheme=candidate.application_scheme,
                    missing_inputs=list(candidate.missing_inputs),
                    subfunctions=list(candidate.subfunctions),
                    evidence_level=candidate.evidence_level
                    or _evidence_level_from_priority(
                        _source_priority(candidate.chunk) if candidate.chunk else "aggregated",
                        candidate.software_responsibility,
                    ),
                    software_actions=list(candidate.software_actions)
                    or _infer_software_actions(
                        candidate.name,
                        candidate.content,
                        candidate.software_responsibility,
                        list(candidate.subfunctions),
                    ),
                    ready_conditions=list(candidate.ready_conditions)
                    or _ready_conditions(
                        list(candidate.missing_inputs),
                        candidate.can_generate_requirement,
                    ),
                )
            )
        return records

    def _group_record(
        self,
        counters: Counter[str],
        name: str,
        summary: str,
        evidence_records: list[FeatureRecord],
        category: str,
        responsibility: str,
        requirement_types: list[str],
        application_scheme: str,
        missing_inputs: list[str],
        subfunctions: list[SubfunctionRecord],
        can_generate_requirement: str = "Needs Review",
        status: str = "Open Issue",
        gap: str = "",
        related_pins: list[str] | None = None,
        related_registers: list[str] | None = None,
    ) -> FeatureRecord:
        counters["feature_group"] += 1
        evidence = [_compact_source(record) for record in evidence_records[:8]]
        actions = _infer_software_actions(name, summary, responsibility, subfunctions)
        return FeatureRecord(
            id=f"EXT-{self.module}-GROUP-{counters['feature_group']:04d}",
            type="feature_group",
            name=name,
            content=summary,
            software_responsibility=responsibility,
            source="; ".join(evidence) or "aggregated",
            source_priority="aggregated",
            merged_from=[record.id for record in evidence_records],
            gap=gap or "; ".join(missing_inputs),
            status=status,
            can_generate_requirement=can_generate_requirement,
            notes="Aggregated feature group generated from multi-view extraction.",
            extractor="feature_aggregator",
            feature_category=category,
            functional_summary=summary,
            evidence=evidence,
            related_pins=related_pins or _unique(pin for record in evidence_records for pin in record.related_pins),
            related_registers=related_registers
            or _unique(reg for record in evidence_records for reg in record.related_registers),
            candidate_requirement_types=requirement_types,
            application_scheme=application_scheme,
            missing_inputs=missing_inputs,
            subfunctions=subfunctions,
            evidence_level=_combined_evidence_level(evidence_records, responsibility),
            software_actions=actions,
            ready_conditions=_ready_conditions(missing_inputs, can_generate_requirement),
        )

    def _build_feature_groups(self, records: list[FeatureRecord]) -> list[FeatureRecord]:
        counters: Counter[str] = Counter()
        groups: list[FeatureRecord] = []
        pins = {record.name.upper(): record for record in records if record.type == "pin"}
        registers = [record for record in records if record.type in {"register", "configuration"}]
        interfaces = [record for record in records if record.type == "interface"]
        states = [record for record in records if record.type == "state_machine"]
        diagnostics = [record for record in records if record.type == "diagnostic"]
        timing = [record for record in records if record.type == "timing"]
        constraints = [record for record in records if record.type in {"constraint", "prohibited"}]
        capabilities = [record for record in records if record.type == "capability"]

        gpio_pins = sorted(pin for pin in pins if re.fullmatch(r"P[0-1][0-7]", pin))
        gpio_registers = [
            record
            for record in registers
            if re.search(r"\b(input|output|polarity|configuration)\b", record.name + " " + record.content, re.I)
        ]
        gpio_evidence = [pins[pin] for pin in gpio_pins] + gpio_registers + capabilities
        if gpio_pins or gpio_registers or _has_text(records, "gpio", "i/o port", "io port"):
            groups.append(
                self._group_record(
                    counters,
                    "16-bit GPIO Port Capability",
                    "The device exposes GPIO pins that can be organized into port-level input, output, polarity, and direction behaviors through the register map.",
                    gpio_evidence,
                    "Capability / GPIO",
                    "open_issue",
                    ["功能需求", "接口需求", "配置需求"],
                    "The driver may expose pin-level and port-level APIs for reading input state, writing output state, and configuring direction or polarity through I2C register access. Project inputs must confirm which pins are used, default states, and whether runtime reconfiguration is allowed.",
                    [
                        "确认项目使用哪些 GPIO pin/port。",
                        "确认默认方向、默认输出电平和默认极性。",
                        "确认是否支持 pin 级、port 级或两者都支持。",
                        "确认运行时方向/极性是否允许变更。",
                    ],
                    [
                        SubfunctionRecord(
                            name="GPIO Input Read",
                            summary="Read pin or port input state from input registers.",
                            trigger="ReadPin / ReadPort candidate API or periodic sampling.",
                            inputs="Pin/port identifier; input register value.",
                            outputs="Logical input level or port bitmap.",
                            boundary="Invalid pin/port ID, uninitialized driver, I2C read failure.",
                            related_pins=gpio_pins,
                            related_registers=["Input Port Register"],
                            application_scheme="Use this subfunction when software needs to sample external digital inputs connected to NCA9539 ports. Project must define pin mapping and returned logical polarity.",
                            candidate_requirement_types=["功能需求", "接口需求"],
                            missing_inputs=["API 命名", "Pin 映射", "错误返回语义"],
                        ),
                        SubfunctionRecord(
                            name="GPIO Output Write",
                            summary="Write output level to output registers for configured output pins.",
                            trigger="WritePin / WritePort candidate API.",
                            inputs="Pin/port identifier; requested level or bitmap.",
                            outputs="Updated output register or cached output state.",
                            boundary="Pin configured as input, invalid ID, I2C write failure.",
                            related_pins=gpio_pins,
                            related_registers=["Output Port Register"],
                            application_scheme="Use this subfunction for software-controlled digital outputs. Project must decide whether write-back cache, readback verification, or output-only pin filtering is required.",
                            candidate_requirement_types=["功能需求", "接口需求", "诊断需求"],
                            missing_inputs=["默认输出", "缓存策略", "写失败处理"],
                        ),
                        SubfunctionRecord(
                            name="GPIO Direction Configuration",
                            summary="Configure each GPIO bit as input or output through configuration registers.",
                            trigger="Initialization or runtime configuration API.",
                            inputs="Pin/port identifier; direction value.",
                            outputs="Updated configuration register.",
                            boundary="Unsupported runtime change, invalid direction value, I2C write failure.",
                            related_pins=gpio_pins,
                            related_registers=["Configuration Register"],
                            application_scheme="Use this subfunction during initialization to enforce project pin direction. Runtime direction change should be generated only if project requirements explicitly allow it.",
                            candidate_requirement_types=["配置需求", "接口需求"],
                            missing_inputs=["默认方向", "运行时配置策略"],
                        ),
                        SubfunctionRecord(
                            name="GPIO Polarity Configuration",
                            summary="Configure whether input polarity is inverted before software interpretation.",
                            trigger="Initialization or polarity configuration API.",
                            inputs="Pin/port identifier; polarity setting.",
                            outputs="Updated polarity inversion register.",
                            boundary="Invalid polarity value, unsupported pin, I2C write failure.",
                            related_pins=gpio_pins,
                            related_registers=["Polarity Inversion Register"],
                            application_scheme="Use this subfunction if project wiring or signal semantics require logical inversion. If the project does not expose polarity control, keep it as initialization configuration only.",
                            candidate_requirement_types=["配置需求", "功能需求"],
                            missing_inputs=["项目是否需要极性反转", "默认极性"],
                        ),
                    ],
                    related_pins=gpio_pins,
                    related_registers=_unique(record.name for record in gpio_registers),
                )
            )

        input_registers = _records_matching(registers, r"\binput\b")
        if input_registers:
            groups.append(
                self._group_record(
                    counters,
                    "Input Port Function",
                    "Input port registers provide the software-visible state of GPIO pins configured or used as inputs.",
                    input_registers + [pins[pin] for pin in gpio_pins[:4] if pin in pins],
                    "Subfunction / GPIO Input",
                    "software_constraint",
                    ["功能需求", "接口需求"],
                    "The driver may provide pin-level or port-level read APIs that translate register values into logical input states. Project inputs must confirm pin mapping, polarity interpretation, and whether input reads are direct register reads or cached values.",
                    ["确认输入 pin 使用范围。", "确认读取接口粒度。", "确认极性转换是否在读接口中体现。"],
                    [
                        SubfunctionRecord(
                            name="Read Input Port",
                            summary="Read a full input port bitmap from the input register group.",
                            inputs="Port identifier.",
                            outputs="Port input bitmap or error status.",
                            boundary="Invalid port, I2C read failure, uninitialized driver.",
                            related_registers=_unique(record.name for record in input_registers),
                            application_scheme="Use for efficient bulk sampling when the project consumes multiple inputs on the same port.",
                            candidate_requirement_types=["功能需求", "接口需求"],
                            missing_inputs=["Port 编号规则", "错误返回语义"],
                        ),
                        SubfunctionRecord(
                            name="Read Input Pin",
                            summary="Read one GPIO input value by masking the corresponding input register bit.",
                            inputs="Pin identifier.",
                            outputs="Logical pin level or error status.",
                            boundary="Invalid pin, pin not configured/used as input, I2C read failure.",
                            related_pins=gpio_pins,
                            related_registers=_unique(record.name for record in input_registers),
                            application_scheme="Use for application-facing single signal reads. Project must define pin mapping and logical polarity.",
                            candidate_requirement_types=["功能需求", "接口需求"],
                            missing_inputs=["Pin 映射", "是否检查方向"],
                        ),
                    ],
                    related_pins=gpio_pins,
                    related_registers=_unique(record.name for record in input_registers),
                )
            )

        output_registers = _records_matching(registers, r"\boutput\b")
        if output_registers:
            groups.append(
                self._group_record(
                    counters,
                    "Output Port Function",
                    "Output port registers define the commanded output level for GPIO pins used as outputs.",
                    output_registers + [pins[pin] for pin in gpio_pins[:4] if pin in pins],
                    "Subfunction / GPIO Output",
                    "software_constraint",
                    ["功能需求", "接口需求", "诊断需求"],
                    "The driver may provide pin-level or port-level write APIs. Project inputs must confirm default output level, whether output state is cached, and how write failures are reported.",
                    ["确认输出 pin 使用范围。", "确认默认输出电平。", "确认写后读回/缓存策略。"],
                    [
                        SubfunctionRecord(
                            name="Write Output Port",
                            summary="Write a full output port bitmap to the output register group.",
                            inputs="Port identifier; output bitmap.",
                            outputs="Write result status.",
                            boundary="Invalid port, I2C write failure, reserved bits if any.",
                            related_registers=_unique(record.name for record in output_registers),
                            application_scheme="Use when the project needs deterministic update of multiple outputs on the same port.",
                            candidate_requirement_types=["功能需求", "接口需求"],
                            missing_inputs=["Port 写入范围", "写失败处理"],
                        ),
                        SubfunctionRecord(
                            name="Write Output Pin",
                            summary="Modify one output bit while preserving other bits in the same output register.",
                            inputs="Pin identifier; output level.",
                            outputs="Updated output register value or error status.",
                            boundary="Invalid pin, pin configured as input, cache mismatch, I2C write failure.",
                            related_pins=gpio_pins,
                            related_registers=_unique(record.name for record in output_registers),
                            application_scheme="Use for application-facing single output control. Project must decide whether read-modify-write uses cache or register readback.",
                            candidate_requirement_types=["功能需求", "接口需求", "诊断需求"],
                            missing_inputs=["方向检查策略", "缓存/读改写策略"],
                        ),
                    ],
                    related_pins=gpio_pins,
                    related_registers=_unique(record.name for record in output_registers),
                )
            )

        polarity_registers = _records_matching(registers, r"\bpolarity\b")
        if polarity_registers:
            groups.append(
                self._group_record(
                    counters,
                    "Polarity Inversion Function",
                    "Polarity inversion registers define whether input values are logically inverted before software interpretation.",
                    polarity_registers,
                    "Subfunction / GPIO Polarity",
                    "software_constraint",
                    ["配置需求", "功能需求"],
                    "The driver may configure input polarity during initialization or expose it as a project configuration item. Project inputs must confirm whether polarity inversion is supported at runtime or fixed by configuration.",
                    ["确认是否使用极性反转。", "确认默认极性。", "确认是否允许运行时修改。"],
                    [
                        SubfunctionRecord(
                            name="Configure Input Polarity",
                            summary="Set polarity inversion bits for selected pins or ports.",
                            inputs="Pin/port identifier; polarity setting.",
                            outputs="Updated polarity inversion register.",
                            boundary="Invalid polarity value, unsupported runtime change, I2C write failure.",
                            related_registers=_unique(record.name for record in polarity_registers),
                            application_scheme="Use when physical signal active level differs from software logical level. Keep as configuration-only if project does not need runtime control.",
                            candidate_requirement_types=["配置需求", "接口需求"],
                            missing_inputs=["默认极性", "运行时修改策略"],
                        )
                    ],
                    related_pins=gpio_pins,
                    related_registers=_unique(record.name for record in polarity_registers),
                )
            )

        direction_registers = _records_matching(registers, r"\bconfiguration\b")
        if direction_registers:
            groups.append(
                self._group_record(
                    counters,
                    "Direction Configuration Function",
                    "Configuration registers define whether each GPIO bit behaves as input or output.",
                    direction_registers,
                    "Subfunction / GPIO Direction",
                    "software_constraint",
                    ["配置需求", "接口需求", "状态需求"],
                    "The driver may apply direction settings during initialization and optionally expose runtime direction changes. Project inputs must confirm default direction, allowed changes, and invalid transition handling.",
                    ["确认每个 pin 默认方向。", "确认是否允许运行时方向切换。", "确认方向与读写接口的约束关系。"],
                    [
                        SubfunctionRecord(
                            name="Apply Direction Configuration",
                            summary="Configure GPIO direction bits according to project configuration.",
                            inputs="Project pin configuration; direction values.",
                            outputs="Updated configuration registers.",
                            boundary="Invalid pin, invalid direction, I2C write failure.",
                            related_registers=_unique(record.name for record in direction_registers),
                            application_scheme="Use in initialization to put all used pins into project-defined direction before application access.",
                            candidate_requirement_types=["配置需求", "状态需求"],
                            missing_inputs=["Pin 默认方向表", "初始化顺序"],
                        ),
                        SubfunctionRecord(
                            name="Runtime Direction Change",
                            summary="Change GPIO direction after initialization only if the project explicitly permits it.",
                            inputs="Pin identifier; requested direction.",
                            outputs="Updated configuration register or rejection status.",
                            boundary="Runtime change not supported, invalid transition, output state undefined.",
                            related_registers=_unique(record.name for record in direction_registers),
                            application_scheme="Generate as a rejection requirement when runtime changes are not supported; generate as an interface requirement only if explicitly required.",
                            candidate_requirement_types=["接口需求", "配置需求"],
                            missing_inputs=["是否支持运行时方向切换", "拒绝返回值"],
                        ),
                    ],
                    related_pins=gpio_pins,
                    related_registers=_unique(record.name for record in direction_registers),
                )
            )

        i2c_evidence = [
            record
            for record in interfaces + list(pins.values()) + capabilities
            if re.search(r"\b(i2c|i2c-bus|scl|sda|address|command byte)\b", record.name + " " + record.content, re.I)
        ]
        if i2c_evidence:
            groups.append(
                self._group_record(
                    counters,
                    "I2C Control Interface",
                    "The device is accessed through an I2C control interface using bus pins, address selection, and register read/write transactions.",
                    i2c_evidence,
                    "Interface / Communication",
                    "software_constraint",
                    ["接口需求", "时序需求", "诊断需求"],
                    "The driver may wrap I2C read/write transactions behind register-level APIs. Project architecture must define whether this module directly owns I2C access or calls a lower-level I2C service.",
                    [
                        "确认 I2C 访问归属和底层依赖。",
                        "确认设备地址配置来源。",
                        "确认 NACK、超时、总线错误的返回语义。",
                    ],
                    [
                        SubfunctionRecord(
                            name="Register Read Transaction",
                            summary="Read one or more registers through the I2C interface.",
                            inputs="Device address; register address; length.",
                            outputs="Read data or error status.",
                            boundary="NACK, timeout, invalid register, bus busy.",
                            related_pins=["SCL", "SDA"],
                            related_registers=_unique(record.name for record in registers),
                            application_scheme="Use for input sampling, configuration readback, and diagnostic confirmation. Return mapping must follow project error handling rules.",
                            candidate_requirement_types=["接口需求", "诊断需求"],
                            missing_inputs=["底层 I2C API", "错误码映射", "同步/异步策略"],
                        ),
                        SubfunctionRecord(
                            name="Register Write Transaction",
                            summary="Write register values through the I2C interface.",
                            inputs="Device address; register address; write data.",
                            outputs="Write result status.",
                            boundary="NACK, timeout, invalid register, write-protected or reserved field.",
                            related_pins=["SCL", "SDA"],
                            related_registers=_unique(record.name for record in registers),
                            application_scheme="Use for output control, direction configuration, and polarity configuration. Project must decide whether readback verification is required.",
                            candidate_requirement_types=["接口需求", "功能需求"],
                            missing_inputs=["写后验证策略", "错误恢复策略"],
                        ),
                    ],
                    related_pins=_unique(record.name for record in i2c_evidence if record.type == "pin"),
                    related_registers=_unique(record.name for record in registers),
                )
            )

        if registers:
            groups.append(
                self._group_record(
                    counters,
                    "Register Map",
                    "The register map provides the data model for input sampling, output control, polarity inversion, and direction configuration.",
                    registers,
                    "Register / Data Model",
                    "software_constraint",
                    ["接口需求", "配置需求", "功能需求"],
                    "The driver should model register addresses, default values, and valid bit behavior as the basis for register access and validation. Project inputs must define which register groups are exposed through public APIs.",
                    [
                        "确认寄存器默认值是否作为初始化验收准则。",
                        "确认保留位和非法地址处理策略。",
                        "确认是否需要寄存器缓存。",
                    ],
                    [
                        SubfunctionRecord(
                            name="Register Address Mapping",
                            summary="Map functional operations to register addresses and port indexes.",
                            inputs="Operation type; port index; register group.",
                            outputs="Register address used by I2C transaction.",
                            boundary="Invalid port index, unsupported register group.",
                            related_registers=_unique(record.name for record in registers),
                            application_scheme="Use as the internal contract between high-level GPIO operations and low-level I2C transactions. Keep generated SRS at behavior level, not implementation table level unless project requires traceable register mapping.",
                            candidate_requirement_types=["接口需求", "配置需求"],
                            missing_inputs=["公开接口是否暴露寄存器级访问", "非法寄存器处理"],
                        )
                    ],
                    related_registers=_unique(record.name for record in registers),
                )
            )

        if diagnostics:
            groups.append(
                self._group_record(
                    counters,
                    "Interrupt and Diagnostic Signaling",
                    "Diagnostic or interrupt-related signals provide software-observable status only when the project connects and uses the relevant pins or flags.",
                    diagnostics + [pins[name] for name in pins if name in {"INT", "ERR_N"}],
                    "Diagnostic / Status",
                    "open_issue",
                    ["诊断需求", "状态需求", "接口需求"],
                    "The driver may expose interrupt/status handling only if the hardware connection and project ownership are confirmed. Otherwise this feature remains a chip capability note.",
                    ["确认 INT/诊断 pin 是否连接到 MCU。", "确认中断清除条件和软件响应策略。"],
                    [
                        SubfunctionRecord(
                            name="Interrupt Status Handling",
                            summary="Observe interrupt/status indication and map it to software status.",
                            inputs="Interrupt pin or status evidence.",
                            outputs="Software status or callback trigger.",
                            boundary="Pin not connected, ownership outside driver, unclear clear condition.",
                            related_pins=["INT", "ERR_N"],
                            application_scheme="Use when project hardware routes the diagnostic/interrupt signal to software. Do not generate Ready requirements from datasheet-only interrupt capability.",
                            candidate_requirement_types=["诊断需求", "状态需求"],
                            missing_inputs=["硬件连接", "回调/轮询策略", "清除条件"],
                        )
                    ],
                )
            )

        reset_evidence = [
            record
            for record in states + list(pins.values())
            if re.search(r"\b(reset|por|power-on)\b", record.name + " " + record.content, re.I)
        ]
        if reset_evidence:
            groups.append(
                self._group_record(
                    counters,
                    "Reset and Default State",
                    "Power-on or reset behavior defines default register and pin state that the driver may need to account for during initialization.",
                    reset_evidence,
                    "State / Initialization",
                    "software_constraint",
                    ["状态需求", "配置需求", "时序需求"],
                    "The driver may use reset/default facts to define initialization expectations and post-reset reconfiguration behavior. Project must confirm whether software controls RESET and whether reinitialization is required after reset.",
                    ["确认 RESET pin 是否由软件控制。", "确认复位后是否自动重新初始化。", "确认默认状态验收准则。"],
                    [
                        SubfunctionRecord(
                            name="Post-reset Reinitialization",
                            summary="Recover default chip state into project runtime configuration after reset.",
                            trigger="Power-on reset, external reset, or detected device reset.",
                            inputs="Project configuration; reset indication.",
                            outputs="Configured runtime register state.",
                            boundary="RESET not controlled by software, I2C unavailable, default values unknown.",
                            application_scheme="Use if project requires robust recovery after power-on or external reset. If reset is hardware-only, record as a constraint and confirmation item.",
                            candidate_requirement_types=["状态需求", "配置需求"],
                            missing_inputs=["RESET 所有权", "复位检测方式", "重初始化策略"],
                        )
                    ],
                )
            )

        if timing:
            groups.append(
                self._group_record(
                    counters,
                    "Timing Constraints",
                    "Timing values constrain bus access, reset handling, signal stabilization, or verification timing.",
                    timing,
                    "Timing / Verification",
                    "hardware_constraint",
                    ["时序需求", "非功能需求", "验证策略"],
                    "Use timing values only when software must wait, timeout, poll, or verify behavior. Pure electrical timing remains evidence for review unless mapped to a software action.",
                    ["确认哪些时序需要软件等待或超时处理。", "确认验证环境是否可测量该时序。"],
                    [
                        SubfunctionRecord(
                            name="Software Timing Guard",
                            summary="Apply wait, timeout, or sampling guards around operations that depend on datasheet timing.",
                            inputs="Operation trigger; timing value and unit.",
                            outputs="Delayed read/write, timeout result, or verification criterion.",
                            boundary="No software-observable trigger, no project timeout policy.",
                            application_scheme="Generate timing requirements only where the driver owns the wait or timeout. Otherwise keep the value as verification evidence.",
                            candidate_requirement_types=["时序需求", "诊断需求"],
                            missing_inputs=["软件是否负责等待", "超时值策略", "测试测量点"],
                        )
                    ],
                )
            )

        if constraints:
            groups.append(
                self._group_record(
                    counters,
                    "Prohibited and Boundary Behavior",
                    "Reserved, invalid, unsupported, or cautionary statements define boundaries that may require rejection behavior or project exclusions.",
                    constraints,
                    "Constraint / Boundary",
                    "open_issue",
                    ["接口需求", "配置需求", "约束"],
                    "Generate rejection requirements only when software receives or configures the invalid value. Hardware-only cautions should remain constraints or review notes.",
                    ["确认软件是否能接收该非法输入。", "确认非法值返回语义。"],
                    [
                        SubfunctionRecord(
                            name="Invalid Input Rejection",
                            summary="Reject or report unsupported values that enter through software interfaces.",
                            inputs="API value, register address, configuration item.",
                            outputs="Error status or Open Issue if behavior is undefined.",
                            boundary="Datasheet-only limitation with no software input path.",
                            application_scheme="Use when project APIs expose configurable values. If no software entry exists, mark NotApplicable or keep as constraint.",
                            candidate_requirement_types=["接口需求", "配置需求", "诊断需求"],
                            missing_inputs=["软件输入路径", "错误码", "是否需要诊断上报"],
                        )
                    ],
                )
            )

        return groups

    def _extract_identity(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        if not chunks:
            return []
        first = chunks[0]
        title = first.heading_path[0] if first.heading_path else self.module
        text = _first_meaningful_text(chunks) or _plain_text(first.text)
        return [
            _Candidate(
                type="identity",
                name=self.module,
                content=_summary(text or title, 420),
                chunk=first,
                software_responsibility="hardware_capability",
                status="Open Issue",
                can_generate_requirement="No",
                extractor="identity_extractor",
                feature_category="Identity",
                functional_summary="Identifies the chip/module and high-level device type.",
                candidate_requirement_types=("概述",),
                application_scheme="Use this information to populate SRS cover, overview, and scope. Do not generate functional requirements from identity facts alone.",
            )
        ]

    def _extract_capabilities(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            text = _plain_text(chunk.text)
            if not re.search(r"\b(feature|overview|general description|description|function)\b", heading, re.I):
                continue
            if not re.search(r"\b(gpio|i/o|io|port|interrupt|reset|register|i2c|i2c-bus|input|output)\b", text, re.I):
                continue
            records.append(
                _Candidate(
                    type="capability",
                    name=chunk.heading_path[-1] if chunk.heading_path else "Chip Capability",
                    content=text,
                    chunk=chunk,
                    software_responsibility="hardware_capability",
                    status="Open Issue",
                    can_generate_requirement="Needs Review",
                    gap="Project-supported software scope is not confirmed.",
                    extractor="capability_extractor",
                    feature_category="Capability",
                    functional_summary="Captures chip-level capabilities that may become overview content or candidate requirements after project mapping.",
                    candidate_requirement_types=("概述", "功能需求"),
                    application_scheme="Use as capability evidence. Generate requirements only for capabilities mapped to a software action or project-supported behavior.",
                    missing_inputs=("项目支持范围",),
                )
            )
        return records

    def _extract_pins(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            for rows in _table_rows(chunk):
                if not rows:
                    continue
                header = [cell.strip().lower() for cell in rows[0]]
                if not (("symbol" in header and "function" in header) or ("pin" in header and "description" in header)):
                    continue
                symbol_index = header.index("symbol") if "symbol" in header else header.index("pin")
                function_index = header.index("function") if "function" in header else header.index("description")
                direction_index = header.index("direction") if "direction" in header else -1
                for row in rows[1:]:
                    if symbol_index >= len(row) or function_index >= len(row):
                        continue
                    symbol = _clean_symbol(row[symbol_index])
                    if not symbol or symbol in {"VDD", "VSS", "VCC", "GND"}:
                        continue
                    direction = row[direction_index].strip() if direction_index >= 0 and direction_index < len(row) else ""
                    function = row[function_index].strip()
                    relation = _pin_software_relation(symbol, function)
                    records.append(
                        _Candidate(
                            type="pin",
                            name=symbol,
                            content=f"{direction + '. ' if direction else ''}{function}",
                            chunk=chunk,
                            software_responsibility=relation,
                            status="Open Issue",
                            can_generate_requirement="Needs Review",
                            gap="Project software ownership is not confirmed.",
                            notes="Datasheet pin fact; confirm whether software controls, samples, configures, or ignores this pin.",
                            extractor="pin_extractor",
                            feature_category="Pin",
                            functional_summary=f"Pin {symbol} provides a hardware connection point that may affect software behavior.",
                            related_pins=(symbol,),
                            candidate_requirement_types=("接口需求", "配置需求", "资源需求"),
                            application_scheme="Use pin facts to build interface/resource mapping. Generate requirements only after ownership and project wiring are confirmed.",
                            missing_inputs=("Pin 所有权", "硬件连接", "软件是否控制/采样"),
                        )
                    )
        return records

    def _extract_interfaces(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            text = _plain_text(chunk.text)
            if "i2c interface" in heading or "i2c interface" in text or "i2c-bus" in text or "i2c bus" in text:
                records.append(
                    _Candidate(
                        type="interface",
                        name="I2C Interface",
                        content=_sentence_with(text, "i2c") or text,
                        chunk=chunk,
                        software_responsibility="software_constraint",
                        status="Open Issue",
                        can_generate_requirement="Needs Review",
                        gap="Project API responsibility for I2C read/write access is not confirmed.",
                        extractor="interface_extractor",
                        feature_category="Interface / Bus",
                        functional_summary="Captures I2C bus access facts that constrain register read/write behavior.",
                        related_pins=("SCL", "SDA"),
                        candidate_requirement_types=("接口需求", "时序需求", "诊断需求"),
                        application_scheme="Use this information to define candidate register read/write contracts if the driver owns or wraps I2C access.",
                        missing_inputs=("底层 I2C API", "错误码", "同步/异步访问策略"),
                    )
                )
            for api in re.findall(r"\b(?:Init|Set[A-Za-z0-9_]+|Get[A-Za-z0-9_]+|Read[A-Za-z0-9_]+|Write[A-Za-z0-9_]+)\b", chunk.text):
                records.append(
                    _Candidate(
                        type="interface",
                        name=api,
                        content=_sentence_with(text, api) or api,
                        chunk=chunk,
                        software_responsibility="software_action",
                        status="Draft",
                        can_generate_requirement="Needs Review",
                        gap="Input/output and return semantics must be confirmed.",
                        extractor="interface_extractor",
                        feature_category="Interface / API",
                        functional_summary=f"Candidate API or software entry point: {api}.",
                        candidate_requirement_types=("接口需求",),
                        application_scheme="Use only after confirming API ownership, parameters, return values, and error behavior.",
                        missing_inputs=("输入参数", "输出/返回值", "错误语义"),
                    )
                )
        return records

    def _extract_registers(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path)
            text = _plain_text(chunk.text)
            chunk_register_rows = _register_rows(chunk)
            register_heading = re.search(r"\b(register|registers|register map|command byte)\b", heading, re.I)
            if chunk_register_rows or register_heading:
                for record_name, record_content in chunk_register_rows:
                    records.append(
                        _Candidate(
                            type="register",
                            name=record_name,
                            content=record_content,
                            chunk=chunk,
                            software_responsibility="software_constraint",
                            status="Open Issue",
                            can_generate_requirement="Needs Review",
                            gap="Project register access ownership and exposed API mapping are not confirmed.",
                            extractor="register_extractor",
                            feature_category="Register",
                            functional_summary=f"Register fact for {record_name}; may support GPIO, configuration, status, or control behavior.",
                            related_registers=(record_name,),
                            candidate_requirement_types=("接口需求", "配置需求", "功能需求"),
                            application_scheme="Use register facts as evidence for behavior-level requirements. Avoid generating register-table requirements unless project asks for register-level traceability.",
                            missing_inputs=("API 映射", "缓存策略", "非法地址处理"),
                        )
                    )
                if not chunk_register_rows and register_heading:
                    records.append(
                        _Candidate(
                            type="configuration",
                            name=chunk.heading_path[-1] if chunk.heading_path else "Register Configuration",
                            content=text,
                            chunk=chunk,
                            software_responsibility="software_constraint",
                            status="Open Issue",
                            can_generate_requirement="Needs Review",
                            gap="Project configuration ownership, defaults, and API mapping are not confirmed.",
                            extractor="register_extractor",
                            feature_category="Register / Configuration",
                            functional_summary="Captures register-related configuration facts.",
                            candidate_requirement_types=("配置需求", "接口需求"),
                            application_scheme="Use to build configuration requirements only after project default values and access policy are confirmed.",
                            missing_inputs=("默认配置", "访问策略"),
                        )
                    )
        return records

    def _extract_bitfields(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            for rows in _table_rows(chunk):
                if not rows:
                    continue
                header = [cell.strip().lower() for cell in rows[0]]
                if not any(token in header for token in ("bit", "bits", "field")):
                    continue
                bit_index = next((header.index(token) for token in ("bit", "bits", "field") if token in header), -1)
                desc_index = next((idx for idx, value in enumerate(header) if value in {"description", "function"}), -1)
                if bit_index < 0 or desc_index < 0:
                    continue
                for row in rows[1:]:
                    if bit_index >= len(row) or desc_index >= len(row):
                        continue
                    bit_name = row[bit_index].strip()
                    desc = row[desc_index].strip()
                    if not bit_name or not desc:
                        continue
                    records.append(
                        _Candidate(
                            type="bitfield",
                            name=bit_name,
                            content=desc,
                            chunk=chunk,
                            software_responsibility="software_constraint",
                            status="Open Issue",
                            can_generate_requirement="Needs Review",
                            gap="Project bit-level configuration or validation responsibility is not confirmed.",
                            extractor="bitfield_extractor",
                            feature_category="Bitfield",
                            functional_summary=f"Bitfield {bit_name} defines a fine-grained register behavior or value.",
                            candidate_requirement_types=("配置需求", "接口需求"),
                            application_scheme="Use bitfield facts to define valid values, defaults, and boundary checks where software exposes the field.",
                            missing_inputs=("是否暴露 bit 级配置", "保留位处理"),
                        )
                    )
        return records

    def _extract_states(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            text = _plain_text(chunk.text)
            for mode in sorted(
                set(
                    re.findall(
                        r"\b(?:Normal|Standby|Sleep|Power-On Reset|Power On Reset|POR|Reset|Operating mode)\b",
                        text,
                        flags=re.IGNORECASE,
                    )
                )
            ):
                records.append(
                    _Candidate(
                        type="state_machine",
                        name=mode,
                        content=_sentence_with(text, mode) or mode,
                        chunk=chunk,
                        software_responsibility="hardware_capability",
                        status="Open Issue",
                        can_generate_requirement="Needs Review",
                        gap="Project-supported software mode/state responsibility is not confirmed.",
                        extractor="state_extractor",
                        feature_category="State",
                        functional_summary=f"State or mode fact: {mode}.",
                        candidate_requirement_types=("状态需求", "配置需求"),
                        application_scheme="Use only after separating chip state from driver state and confirming whether software observes, controls, or reacts to this state.",
                        missing_inputs=("驱动状态机", "状态观测方式", "触发条件"),
                    )
                )
        return records

    def _extract_diagnostics(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path)
            text = _plain_text(chunk.text)
            diagnostic_heading = re.search(r"\b(interrupt|int\b|fault|error|status|flag|diagnostic)\b", heading, re.I)
            diagnostic_text = re.search(r"\b(INT|ERR|fault|error|status flag|interrupt output|diagnostic)\b", text)
            if not (diagnostic_heading or diagnostic_text):
                continue
            records.append(
                _Candidate(
                    type="diagnostic",
                    name=chunk.heading_path[-1] if chunk.heading_path else "Diagnostic or Interrupt",
                    content=_summary(text, 420),
                    chunk=chunk,
                    software_responsibility="open_issue",
                    status="Open Issue",
                    can_generate_requirement="Needs Review",
                    gap="Software observability, clear condition, and diagnostic reporting responsibility are not confirmed.",
                    extractor="diagnostic_extractor",
                    feature_category="Diagnostic / Interrupt",
                    functional_summary="Captures diagnostic, interrupt, status, or flag behavior that may be observable by software.",
                    candidate_requirement_types=("诊断需求", "状态需求", "接口需求"),
                    application_scheme="Use only if the signal/status is connected to software and project requires observation, reporting, or callback behavior.",
                    missing_inputs=("硬件连接", "清除条件", "诊断上报策略"),
                )
            )
        return records

    def _extract_timing(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            text = _plain_text(chunk.text)
            if not re.search(r"\b(us|µs|μs|ms|s|khz|mhz|hz|ns)\b", text, flags=re.IGNORECASE):
                continue
            for sentence in re.split(r"(?<=[.!?。；;])\s+", text):
                if re.search(r"\b(us|µs|μs|ms|s|khz|mhz|hz|ns)\b", sentence, flags=re.IGNORECASE):
                    records.append(
                        _Candidate(
                            type="timing",
                            name=_timing_name(sentence),
                            content=sentence,
                            chunk=chunk,
                            software_responsibility="hardware_constraint",
                            status="Open Issue",
                            can_generate_requirement="Needs Review",
                            gap="Project timing responsibility must be confirmed.",
                            extractor="timing_extractor",
                            feature_category="Timing",
                            functional_summary="Captures measurable timing, frequency, or delay values.",
                            candidate_requirement_types=("时序需求", "验证策略"),
                            application_scheme="Use as timing requirement evidence only where software owns waiting, timeout, sampling, or verification behavior.",
                            missing_inputs=("软件是否负责等待/超时", "测量点", "验证方式"),
                        )
                    )
                    if len([record for record in records if record.chunk == chunk]) >= 4:
                        break
        return records

    def _extract_electrical(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path)
            text = _plain_text(chunk.text)
            if re.search(r"\b(electrical|voltage|current|supply|power|pull-up|pullup|drive|leakage)\b", heading + " " + text, re.I):
                records.append(
                    _Candidate(
                        type="electrical",
                        name=chunk.heading_path[-1] if chunk.heading_path else "Electrical Constraint",
                        content=_summary(text, 360),
                        chunk=chunk,
                        software_responsibility="hardware_constraint",
                        status="Open Issue",
                        can_generate_requirement="No",
                        gap="Usually hardware constraint; project must identify any software-controlled implication.",
                        extractor="electrical_extractor",
                        feature_category="Electrical / Resource",
                        functional_summary="Captures electrical limits and resource constraints.",
                        candidate_requirement_types=("资源需求", "约束"),
                        application_scheme="Use as resource/constraint evidence. Generate software requirements only if software must configure, monitor, or limit behavior based on the value.",
                        missing_inputs=("是否存在软件控制影响",),
                    )
                )
        return records

    def _extract_constraints(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            text = _plain_text(chunk.text)
            if not re.search(r"\b(reserved|unsupported|not supported|invalid|illegal|must not|shall not|caution|note)\b", text, re.I):
                continue
            records.append(
                _Candidate(
                    type="constraint",
                    name=chunk.heading_path[-1] if chunk.heading_path else "Boundary Constraint",
                    content=_summary(text, 360),
                    chunk=chunk,
                    software_responsibility="open_issue",
                    status="Open Issue",
                    can_generate_requirement="Needs Review",
                    gap="Need to confirm whether this boundary has a software input path.",
                    extractor="constraint_extractor",
                    feature_category="Constraint / Prohibited",
                    functional_summary="Captures restrictions, forbidden values, reserved fields, or caution notes.",
                    candidate_requirement_types=("接口需求", "配置需求", "约束"),
                    application_scheme="Use to generate rejection requirements only where software accepts or configures the value. Otherwise keep it as a constraint or review note.",
                    missing_inputs=("软件输入路径", "错误返回语义"),
                )
            )
        return records

    def _extract_project_mapping(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            document = chunk.document.lower()
            text = _plain_text(chunk.text)
            if "datasheet" in document:
                continue
            if re.search(r"\b(project|shall|support|configured|default|instance|api|asil|qm|test)\b", text, re.I):
                records.append(
                    _Candidate(
                        type="project_mapping",
                        name=chunk.heading_path[-1] if chunk.heading_path else "Project Mapping",
                        content=text,
                        chunk=chunk,
                        software_responsibility="software_action",
                        status="Draft",
                        can_generate_requirement="Needs Review",
                        extractor="project_mapping_extractor",
                        feature_category="Project Mapping",
                        functional_summary="Captures project-specific scope, configuration, API, safety, or verification decisions.",
                        candidate_requirement_types=("功能需求", "接口需求", "配置需求", "非功能需求"),
                        application_scheme="Use project mapping evidence to promote datasheet candidates from Needs Review to Ready.",
                    )
                )
        return records


class FeatureExtractionMarkdownRenderer:
    def render(self, records: list[FeatureRecord], module: str = "FC") -> str:
        groups = [record for record in records if record.type == "feature_group"]
        raw_records = [record for record in records if record.type != "feature_group"]
        lines = [
            f"# Feature Extraction - {module}",
            "",
            "## Extraction Strategy",
            "",
            "- Extraction follows `feature-extraction-design.md`: multi-view extractors run independently, then results are aggregated and classified.",
            "- Views: identity, capability, pin, interface, register, bitfield, state, diagnostic, timing, electrical, constraint, and project mapping.",
            "- Datasheet facts are captured as hardware capability or hardware constraint first.",
            "- Feature groups summarize scattered evidence and include subfunctions plus application schemes.",
            "- A feature becomes a Ready SRS requirement only after software responsibility and project support are confirmed.",
            "- Back matter such as package, ordering, documentation support, tape/reel, and revision history is ignored.",
            "",
            "## Cross-view Summary",
            "",
            "| 类型 | 数量 |",
            "| --- | ---: |",
        ]
        counts = Counter(record.type for record in records)
        for feature_type in (
            "feature_group",
            "identity",
            "capability",
            "pin",
            "interface",
            "register",
            "bitfield",
            "configuration",
            "state_machine",
            "diagnostic",
            "timing",
            "constraint",
            "electrical",
            "project_mapping",
        ):
            lines.append(f"| {feature_type} | {counts.get(feature_type, 0)} |")

        lines.extend(["", "## Feature Groups", ""])
        if groups:
            for group in groups:
                lines.extend(_feature_group_markdown(group))
        else:
            lines.append("> No aggregated feature groups were produced. Input may lack structured chip data or extractor rules need extension.")
            lines.append("")

        lines.extend(["## Feature-to-Requirement Mapping", ""])
        if groups:
            lines.extend(
                [
                    "| Feature | Evidence Level | Software Responsibility | Software Action Gate | Candidate Requirement Type | Ready 条件 | 当前状态 |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                ]
            )
            for group in groups:
                lines.append(
                    "| "
                    + " | ".join(
                        _escape_table(value)
                        for value in (
                            group.name,
                            group.evidence_level,
                            group.software_responsibility,
                            _software_action_gate(group),
                            ", ".join(group.candidate_requirement_types),
                            "; ".join(group.ready_conditions),
                            group.can_generate_requirement,
                        )
                    )
                    + " |"
                )
            lines.append("")
        else:
            lines.extend(["No feature groups available for requirement mapping.", ""])

        lines.extend(["## Required Inputs for Ready SRS", ""])
        required_inputs = _required_inputs_for_ready_srs(groups or records)
        if required_inputs:
            lines.extend(["| 缺失项 | 影响需求 | 需要谁提供 | 示例 |", "| --- | --- | --- | --- |"])
            for item, affected, owner, example in required_inputs:
                lines.append(
                    "| "
                    + " | ".join(_escape_table(value) for value in (item, affected, owner, example))
                    + " |"
                )
            lines.append("")
        else:
            lines.extend(["No required inputs detected.", ""])

        lines.extend(["## Open Issues and Required Inputs", ""])
        issues = _open_issues(records)
        if issues:
            lines.extend(["| 特征 | 缺失输入/问题 | 可生成需求 |", "| --- | --- | --- |"])
            for record in issues:
                missing = "; ".join(record.missing_inputs) or record.gap
                lines.append(f"| {record.name} | {_escape_table(missing)} | {record.can_generate_requirement} |")
            lines.append("")
        else:
            lines.extend(["No open issues detected.", ""])

        lines.extend(["## Raw Multi-view Records", ""])
        for record in raw_records:
            lines.extend(_record_markdown(record))
        return "\n".join(lines).rstrip() + "\n"


def _feature_group_markdown(record: FeatureRecord) -> list[str]:
    rows = [
        ("Feature Category", record.feature_category),
        ("Functional Summary", record.functional_summary),
        ("Evidence", "; ".join(record.evidence)),
        ("Evidence Level", record.evidence_level),
        ("Related Pins", ", ".join(record.related_pins)),
        ("Related Registers", ", ".join(record.related_registers)),
        ("Software Responsibility", record.software_responsibility),
        ("Software Actions", ", ".join(record.software_actions)),
        ("Candidate Requirement Types", ", ".join(record.candidate_requirement_types)),
        ("Application Scheme", record.application_scheme),
        ("Missing Inputs", "; ".join(record.missing_inputs)),
        ("Ready Conditions", "; ".join(record.ready_conditions)),
        ("Can Generate Requirement", record.can_generate_requirement),
        ("Status", record.status),
    ]
    lines = [f"### {record.id} {record.name}", "", "| 字段 | 内容 |", "| --- | --- |"]
    for key, value in rows:
        if value:
            lines.append(f"| {key} | {_escape_table(value)} |")
    if record.subfunctions:
        lines.extend(["", "#### Subfunctions", "", "| Subfunction | Summary | Inputs | Outputs | Boundary | Application Scheme | Can Generate Requirement |", "| --- | --- | --- | --- | --- | --- | --- |"])
        for sub in record.subfunctions:
            lines.append(
                "| "
                + " | ".join(
                    _escape_table(value)
                    for value in (
                        sub.name,
                        sub.summary,
                        sub.inputs,
                        sub.outputs,
                        sub.boundary,
                        sub.application_scheme,
                        sub.can_generate_requirement,
                    )
                )
                + " |"
            )
    lines.append("")
    return lines


def _record_markdown(record: FeatureRecord) -> list[str]:
    rows = [
        ("提取器", record.extractor),
        ("类型", record.type),
        ("名称", record.name),
        ("特征类别", record.feature_category),
        ("功能总结", record.functional_summary),
        ("提取内容", record.content),
        ("软件责任判断", record.software_responsibility),
        ("证据强度等级", record.evidence_level),
        ("软件动作", ", ".join(record.software_actions)),
        ("候选需求类别", ", ".join(record.candidate_requirement_types)),
        ("应用方案", record.application_scheme),
        ("来源", record.source),
        ("来源优先级", record.source_priority),
        ("合并依据", "; ".join(record.merged_from)),
        ("冲突/缺口", record.gap),
        ("缺失输入", "; ".join(record.missing_inputs)),
        ("Ready 条件", "; ".join(record.ready_conditions)),
        ("建议状态", record.status),
        ("可生成需求", record.can_generate_requirement),
        ("备注", record.notes),
    ]
    lines = [f"### {record.id} {record.name}", "", "| 字段 | 内容 |", "| --- | --- |"]
    for key, value in rows:
        if value:
            lines.append(f"| {key} | {_escape_table(value)} |")
    lines.append("")
    return lines


def _table_rows(chunk: DocumentChunk) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    for block in chunk.blocks:
        rows = block.metadata.get("rows") if block.metadata else None
        if rows:
            tables.append(rows)
    return tables


def _register_rows(chunk: DocumentChunk) -> list[tuple[str, str]]:
    extracted: list[tuple[str, str]] = []
    for rows in _table_rows(chunk):
        if not rows:
            continue
        header = [cell.strip().lower() for cell in rows[0]]
        if not any(token in header for token in ("register", "name", "command", "address", "addr")):
            continue
        name_index = next(
            (idx for idx, value in enumerate(header) if value in {"register", "name", "command", "command byte"}),
            -1,
        )
        address_index = next((idx for idx, value in enumerate(header) if value in {"address", "addr", "command"}), -1)
        desc_index = next((idx for idx, value in enumerate(header) if value in {"description", "function"}), -1)
        default_index = next((idx for idx, value in enumerate(header) if value in {"default", "reset", "default value"}), -1)
        for row in rows[1:]:
            parts = []
            if address_index >= 0 and address_index < len(row) and row[address_index].strip():
                parts.append(f"Address: {row[address_index].strip()}")
            if default_index >= 0 and default_index < len(row) and row[default_index].strip():
                parts.append(f"Default: {row[default_index].strip()}")
            if desc_index >= 0 and desc_index < len(row) and row[desc_index].strip():
                parts.append(row[desc_index].strip())
            if name_index >= 0 and name_index < len(row) and row[name_index].strip():
                name = row[name_index].strip()
            elif address_index >= 0 and address_index < len(row) and row[address_index].strip():
                name = f"Register {row[address_index].strip()}"
            else:
                continue
            extracted.append((name, "; ".join(parts) or "Register table row."))
    return extracted


def _skip_chunk(chunk: DocumentChunk) -> bool:
    heading = " ".join(chunk.heading_path).lower()
    skip_terms = (
        "index",
        "order information",
        "documentation support",
        "package information",
        "tape and reel",
        "revision history",
        "legal",
        "notice",
        "mechanical",
        "soldering",
    )
    return any(term in heading for term in skip_terms)


def _pin_software_relation(symbol: str, function: str) -> str:
    upper = symbol.upper()
    if upper in {"SCL", "SDA"}:
        return "software_constraint"
    if upper in {"INT", "RESET", "ERR_N", "WAKE"}:
        return "open_issue"
    if re.fullmatch(r"P[0-1][0-7]", upper):
        return "open_issue"
    if upper in {"A0", "A1", "A2"}:
        return "hardware_constraint"
    return "open_issue"


def _clean_symbol(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "", value).upper()


def _source_ref(chunk: DocumentChunk) -> str:
    heading = " > ".join(chunk.heading_path)
    return f"{chunk.document}:{heading}:{chunk.id}"


def _source_priority(chunk: DocumentChunk | None) -> str:
    if chunk is None:
        return "aggregated"
    document = chunk.document.lower()
    if "datasheet" in document:
        return "datasheet"
    if "config" in document:
        return "configuration"
    if "test" in document:
        return "test_material"
    if document.endswith((".c", ".h")):
        return "source_code"
    return "project_requirement"


def _evidence_level_from_priority(source_priority: str, software_responsibility: str = "") -> str:
    if source_priority == "project_requirement":
        return "L1 Project Requirement"
    if source_priority in {"configuration", "source_code"}:
        return "L2 Config/Source"
    if source_priority == "datasheet":
        return "L3 Datasheet"
    if source_priority == "test_material":
        return "L4 Test Material"
    if software_responsibility in {"open_issue", "hardware_capability"}:
        return "L5 Inference / Needs Confirmation"
    return "L5 Inference / Needs Confirmation"


def _combined_evidence_level(records: list[FeatureRecord], responsibility: str) -> str:
    priorities = {record.source_priority for record in records}
    if "project_requirement" in priorities:
        return "L1 Project Requirement"
    if priorities.intersection({"configuration", "source_code"}):
        return "L2 Config/Source"
    if "datasheet" in priorities:
        return "L3 Datasheet"
    if "test_material" in priorities:
        return "L4 Test Material"
    return _evidence_level_from_priority("aggregated", responsibility)


def _infer_software_actions(
    name: str,
    content: str,
    responsibility: str,
    subfunctions: list[SubfunctionRecord],
) -> list[str]:
    text = " ".join(
        [
            name,
            content,
            responsibility,
            " ".join(sub.name + " " + sub.summary + " " + sub.boundary for sub in subfunctions),
        ]
    ).lower()
    actions: list[str] = []
    if responsibility == "software_action" or re.search(r"\b(api|init|set|get|read|write)\b", text):
        actions.append("软件需要调用 API")
    if re.search(r"\b(read|input|sample|register read)\b", text):
        actions.append("软件需要读寄存器")
    if re.search(r"\b(write|output|configure|configuration|polarity|direction|register write)\b", text):
        actions.append("软件需要写寄存器")
    if re.search(r"\b(control pin|reset|wake|enable|output pin)\b", text):
        actions.append("软件需要控制 Pin")
    if re.search(r"\b(read pin|input pin|interrupt|int|status pin)\b", text):
        actions.append("软件需要读取 Pin")
    if re.search(r"\b(cache|state|status|ready|initialized|configured)\b", text):
        actions.append("软件需要保存状态")
    if re.search(r"\b(invalid|parameter|range|boundary|reserved|unsupported)\b", text):
        actions.append("软件需要做参数校验")
    if re.search(r"\b(reject|invalid|unsupported|reserved|prohibited)\b", text):
        actions.append("软件需要拒绝非法输入")
    if re.search(r"\b(wait|timeout|timing|delay|sampling|guard)\b", text):
        actions.append("软件需要等待时序")
    if re.search(r"\b(error|fault|diagnostic|report|record|nack|failure)\b", text):
        actions.append("软件需要上报/记录错误")
    return _unique(actions)


def _ready_conditions(missing_inputs: list[str], can_generate_requirement: str) -> list[str]:
    base = [
        "证据达到 L1/L2，或 L3 Datasheet 证据已由项目确认",
        "至少存在一个明确软件动作",
        "需求字段满足 construction-rules.md 必备要素",
    ]
    if can_generate_requirement == "No":
        return ["存在软件动作和项目责任前不得生成需求"]
    if missing_inputs:
        return [*base, *[f"补充：{item}" for item in missing_inputs]]
    return base


def _software_action_gate(record: FeatureRecord) -> str:
    if record.software_actions:
        return "Pass: " + ", ".join(record.software_actions)
    return "Blocked: no software action; keep in overview only"


def _required_inputs_for_ready_srs(records: list[FeatureRecord]) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for record in records:
        affected = ", ".join(record.candidate_requirement_types) or record.name
        for item in record.missing_inputs:
            normalized = item.strip(" 。.;；")
            owner, example = _required_input_owner_and_example(normalized)
            rows.append((normalized, affected, owner, example))
    result: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for row in rows:
        key = row[0].lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result[:30]


def _required_input_owner_and_example(item: str) -> tuple[str, str]:
    if re.search(r"\bapi|接口|返回|错误码|同步|异步|访问归属|底层\b", item, re.I):
        return "软件架构", "Init / ReadPin / WritePin / E_OK / E_NOT_OK"
    if re.search(r"\bpin|硬件|连接|所有权|INT|RESET|GPIO\b", item, re.I):
        return "硬件/软件架构", "INT 是否接 MCU；RESET 是否由本驱动控制"
    if re.search(r"\b默认|配置|方向|极性|输出电平|地址|实例\b", item, re.I):
        return "项目配置", "默认方向、默认输出、I2C 地址、实例数"
    if re.search(r"\b时序|等待|超时|测量|验证\b", item, re.I):
        return "测试/软件架构", "I2C 超时、RESET 后等待时间、HIL 测量点"
    if re.search(r"\b诊断|中断|清除|上报|NACK\b", item, re.I):
        return "诊断/软件架构", "中断清除策略、错误上报 ID、NACK 处理"
    return "项目负责人", "项目级确认材料"


def _compact_source(record: FeatureRecord) -> str:
    return f"{record.id}:{record.name}:{record.source_priority}"


def _type_code(feature_type: str) -> str:
    return {
        "identity": "ID",
        "capability": "CAP",
        "mode": "MODE",
        "pin": "PIN",
        "interface": "IF",
        "register": "REG",
        "bitfield": "BIT",
        "configuration": "CFG",
        "state_machine": "STATE",
        "diagnostic": "DIAG",
        "timing": "TIME",
        "prohibited": "PROHIBIT",
        "resource": "RES",
        "electrical": "ELEC",
        "constraint": "CONST",
        "project_mapping": "MAP",
        "feature_group": "GROUP",
    }.get(feature_type, "EXT")


def _module_token(value: str) -> str:
    token = "".join(ch for ch in value.upper() if ch.isalnum())
    return token or "FC"


def _plain_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    text = re.sub(r"[$*_`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _first_meaningful_text(chunks: list[DocumentChunk]) -> str:
    for chunk in chunks:
        heading = " ".join(chunk.heading_path).lower()
        text = _plain_text(chunk.text)
        if len(text) < 80:
            continue
        if re.search(r"\b(product overview|general description|description|overview)\b", heading, re.I):
            return text
    for chunk in chunks:
        text = _plain_text(chunk.text)
        if len(text) >= 80 and not text.startswith("{"):
            return text
    return ""


def _sentence_with(text: str, needle: str) -> str:
    for sentence in re.split(r"(?<=[.!?。；;])\s+", text):
        if needle.lower() in sentence.lower():
            return sentence
    return ""


def _summary(text: str, limit: int = 240) -> str:
    summary = re.sub(r"\s+", " ", text).strip()
    return summary if len(summary) <= limit else f"{summary[: limit - 3].rstrip()}..."


def _escape_table(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _timing_name(sentence: str) -> str:
    if re.search(r"\bi2c|scl|sda|clock|khz|mhz\b", sentence, re.I):
        return "I2C Timing Value"
    if re.search(r"\breset|por\b", sentence, re.I):
        return "Reset Timing Value"
    if re.search(r"\binterrupt|int\b", sentence, re.I):
        return "Interrupt Timing Value"
    return "Timing Value"


def _has_text(records: list[FeatureRecord], *needles: str) -> bool:
    haystack = " ".join(f"{record.name} {record.content}" for record in records).lower()
    return any(needle.lower() in haystack for needle in needles)


def _records_matching(records: list[FeatureRecord], pattern: str) -> list[FeatureRecord]:
    return [
        record
        for record in records
        if re.search(pattern, f"{record.name} {record.content}", re.IGNORECASE)
    ]


def _unique(items: Any) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = str(item).strip()
        if not value or value.lower() in seen:
            continue
        seen.add(value.lower())
        result.append(value)
    return result


def _dedupe_candidates(candidates: list[_Candidate]) -> list[_Candidate]:
    seen: set[tuple[str, str, str]] = set()
    result: list[_Candidate] = []
    for candidate in candidates:
        source = _source_ref(candidate.chunk) if candidate.chunk else "aggregated"
        identity = (candidate.type, candidate.name.lower(), source)
        if identity in seen:
            continue
        seen.add(identity)
        result.append(candidate)
    return result


def _dedupe_records(records: list[FeatureRecord]) -> list[FeatureRecord]:
    seen: set[tuple[str, str, str]] = set()
    result: list[FeatureRecord] = []
    for record in records:
        identity = (record.type, record.name.lower(), record.source)
        if identity in seen:
            continue
        seen.add(identity)
        result.append(record)
    return result


def _open_issues(records: list[FeatureRecord]) -> list[FeatureRecord]:
    issues: list[FeatureRecord] = []
    groups = [record for record in records if record.type == "feature_group"]
    ordered = groups or [
        record
        for record in records
        if record.type not in {"pin", "capability", "identity", "electrical"}
    ]
    seen: set[str] = set()
    for record in ordered:
        if record.status in {"Open Issue", "Draft"} or record.can_generate_requirement == "Needs Review":
            if record.gap or record.missing_inputs:
                key = record.name.lower()
                if key in seen:
                    continue
                seen.add(key)
                issues.append(record)
    return issues[:30]
