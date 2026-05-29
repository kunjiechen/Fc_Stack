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
    # Structured fault rows extracted from datasheet protection/fault summary tables.
    # Each row is a pipe-delimited string matching the builder's fault table format:
    #   | 故障名称 | 分类 | 触发条件 | 检测方式 | 确认策略 | 芯片行为 | 恢复类型 | 软件动作 |
    fault_rows: list[str] = field(default_factory=list)

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
    # Structured fault rows flowing from datasheet fault summary tables.
    fault_rows: list[str] = field(default_factory=list)

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
    # Structured fault rows from datasheet fault summary tables.
    fault_rows: tuple[str, ...] = ()


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
        all_extractors = (
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
        with ThreadPoolExecutor(max_workers=min(8, len(all_extractors))) as executor:
            batches = list(executor.map(lambda fn: fn(parsed, chunks), all_extractors))

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
                    fault_rows=list(candidate.fault_rows),
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

    # ------------------------------------------------------------------
    # Data-driven feature group builder
    # ------------------------------------------------------------------

    def _build_feature_groups(self, records: list[FeatureRecord]) -> list[FeatureRecord]:
        """Build feature groups from extracted records using data-driven clustering.

        Discovers patterns from whatever record types are actually present rather
        than checking against hardcoded GPIO/I2C/register templates.
        """
        counters: Counter[str] = Counter()
        groups: list[FeatureRecord] = []

        # ---- Step 1: Index by type ----
        by_type = self._index_by_type(records)
        pins = by_type["pin"]
        registers = by_type["register"] + by_type["configuration"]
        interfaces = by_type["interface"]
        states = by_type["state_machine"]
        diagnostics = by_type["diagnostic"]
        timing = by_type["timing"]
        constraints = by_type["constraint"] + by_type["prohibited"]
        capabilities = by_type["capability"]
        pin_map = {r.name.upper(): r for r in pins}

        # ---- Step 2: Discover pin clusters ----
        pin_clusters = self._discover_pin_clusters(pins)

        # ---- Step 3: Build pin-centric feature groups (skip hardware-only) ----
        _HW_ONLY_CLUSTERS = {"电源与接地引脚", "电荷泵引脚", "散热引脚"}
        for cluster_name, cluster_pins in pin_clusters.items():
            if cluster_name in _HW_ONLY_CLUSTERS:
                continue
            group = self._build_pin_cluster_group(
                counters, cluster_name, cluster_pins, by_type,
            )
            if group:
                groups.append(group)

        # ---- Step 4: Build register groups (if registers exist) ----
        reg_clusters = self._discover_register_clusters(registers)
        for cluster_name, cluster_regs in reg_clusters.items():
            group = self._build_register_cluster_group(
                counters, cluster_name, cluster_regs,
            )
            if group:
                groups.append(group)

        # ---- Step 5: Build interface group ----
        if interfaces:
            group = self._build_interface_group(counters, interfaces, pin_map)
            if group:
                groups.append(group)

        # ---- Step 6: Build state group ----
        if states:
            group = self._build_state_group(counters, states)
            if group:
                groups.append(group)

        # ---- Step 7: Build diagnostic group ----
        if diagnostics:
            group = self._build_diagnostic_group(counters, diagnostics, pin_map)
            if group:
                groups.append(group)

        # ---- Step 8: Build timing group ----
        if timing:
            group = self._build_timing_group(counters, timing)
            if group:
                groups.append(group)

        # ---- Step 9: Build constraint group ----
        if constraints:
            group = self._build_constraint_group(counters, constraints)
            if group:
                groups.append(group)

        # ---- Step 10: Remaining capabilities (skip catch-all, they don't map to specific requirements) ----

        return groups

    # ------------------------------------------------------------------
    # Indexing & clustering helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _index_by_type(records: list[FeatureRecord]) -> dict[str, list[FeatureRecord]]:
        indexed: dict[str, list[FeatureRecord]] = {
            "pin": [], "register": [], "configuration": [], "interface": [],
            "state_machine": [], "diagnostic": [], "timing": [],
            "constraint": [], "prohibited": [], "capability": [],
            "identity": [], "electrical": [], "bitfield": [],
            "project_mapping": [], "resource": [],
        }
        for r in records:
            bucket = indexed.get(r.type)
            if bucket is not None:
                bucket.append(r)
        return indexed

    def _discover_pin_clusters(
        self, pins: list[FeatureRecord],
    ) -> dict[str, list[FeatureRecord]]:
        """Cluster pins by their functional role inferred from descriptions."""
        if not pins:
            return {}

        clusters: dict[str, list[FeatureRecord]] = {}
        for pin in pins:
            func = self._pin_functional_signature(pin)
            clusters.setdefault(func, []).append(pin)

        merged: dict[str, list[FeatureRecord]] = {}
        others: list[FeatureRecord] = []
        for name, cluster in clusters.items():
            if len(cluster) == 1 and len(clusters) > 3:
                others.extend(cluster)
            else:
                merged[name] = cluster
        if others:
            merged["其他设备引脚"] = others

        return merged

    @staticmethod
    def _pin_functional_signature(pin: FeatureRecord) -> str:
        """Derive a Chinese functional category name from a pin's description."""
        text = f"{pin.name} {pin.content}".lower()

        if _contains_any(text, ("i2c", "scl", "sda", "serial clock", "serial data")):
            return "I2C 总线引脚"
        if _contains_any(text, ("spi", "sck", "mosi", "miso", "cs", "chip select", "sdi", "sdo")):
            return "SPI 总线引脚"

        if _contains_any(text, ("enable", "disable", "sleep", "wake", "shutdown",
                                  "nsleep", "standby", "mode select", "control input",
                                  "启用", "禁用", "睡眠", "唤醒", "控制输入", "模式选择")):
            return "控制输入引脚"

        if _contains_any(text, ("fault", "error", "diagnostic", "nfault", "alert",
                                  "warning", "status flag", "open-drain output",
                                  "interrupt output", "故障", "诊断", "错误")):
            return "故障诊断输出引脚"

        if _contains_any(text, ("current sense", "current monitor", "sense output",
                                  "proportional", "ipropi", "current feedback",
                                  "analog current", "电流检测", "电流监测")):
            return "电流检测输出引脚"

        if _contains_any(text, ("h-bridge", "half-bridge", "motor output",
                                  "driver output", "high-side", "low-side",
                                  "switch output", "out1", "out2",
                                  "h 桥", "电机输出", "功率输出")):
            return "功率输出引脚"

        if _contains_any(text, ("reference", "vref", "analog input",
                                  "comparator", "adc", "基准电压", "参考电压")):
            return "模拟参考引脚"

        if _contains_any(text, ("reset", "por", "power-on reset", "复位")):
            return "复位引脚"

        if _contains_any(text, ("gpio", "general purpose", "i/o", "bidirectional")):
            return "通用 I/O 引脚"

        if _contains_any(text, ("power supply", "vm", "vdd", "vcc", "ground",
                                  "gnd", "pgnd", "vss", "电源", "接地", "功率地")):
            return "电源与接地引脚"

        if _contains_any(text, ("charge pump", "vcp", "cph", "cpl", "bootstrap", "电荷泵")):
            return "电荷泵引脚"

        if _contains_any(text, ("thermal", "heat", "pad", "exposed", "散热")):
            return "散热引脚"

        return "其他设备引脚"

    @staticmethod
    def _discover_register_clusters(
        registers: list[FeatureRecord],
    ) -> dict[str, list[FeatureRecord]]:
        """Group registers by functional keywords in their names/content."""
        if not registers:
            return {}
        clusters: dict[str, list[FeatureRecord]] = {}
        for reg in registers:
            text = f"{reg.name} {reg.content}".lower()
            if _contains_any(text, ("input", "read", "status", "flag")):
                key = "Input/Status Registers"
            elif _contains_any(text, ("output", "write", "control", "command")):
                key = "Output/Control Registers"
            elif _contains_any(text, ("configuration", "direction", "polarity", "mode")):
                key = "Configuration Registers"
            elif _contains_any(text, ("fault", "diagnostic", "interrupt", "error")):
                key = "Diagnostic Registers"
            elif _contains_any(text, ("identification", "id", "version", "device")):
                key = "Identification Registers"
            else:
                key = "General Registers"
            clusters.setdefault(key, []).append(reg)
        return clusters

    @staticmethod
    def _discover_capability_groups(
        capabilities: list[FeatureRecord],
        pin_clusters: dict[str, list[FeatureRecord]],
        reg_clusters: dict[str, list[FeatureRecord]],
    ) -> dict[str, list[FeatureRecord]]:
        """Group capabilities not already covered by pin/register clusters."""
        if not capabilities:
            return {}
        covered_terms: set[str] = set()
        for name in pin_clusters:
            covered_terms.update(name.lower().replace(" pins", "").split())
        for name in reg_clusters:
            covered_terms.update(name.lower().replace(" registers", "").split())

        unmatched: dict[str, list[FeatureRecord]] = {}
        for cap in capabilities:
            text = f"{cap.name} {cap.content}".lower()
            # Check if already covered by a pin/register cluster
            if any(term in text for term in covered_terms if len(term) > 3):
                continue
            unmatched.setdefault("其他芯片能力", []).append(cap)
        return unmatched

    # ------------------------------------------------------------------
    # Group builders (data-driven)
    # ------------------------------------------------------------------

    def _build_pin_cluster_group(
        self, counters: Counter[str], cluster_name: str,
        cluster_pins: list[FeatureRecord],
        by_type: dict[str, list[FeatureRecord]],
    ) -> FeatureRecord | None:
        """Build a feature group for a discovered pin cluster."""
        if not cluster_pins:
            return None

        # Derive category and responsibility from the pin cluster
        sw_relations = [r.software_responsibility for r in cluster_pins]
        responsibility = max(set(sw_relations), key=sw_relations.count)

        # Infer requirement types from pin roles
        req_types = self._infer_requirement_types(cluster_name, cluster_pins)

        # Build subfunctions from the pins' actual functions
        subfuncs = self._build_pin_subfunctions(cluster_name, cluster_pins)

        # Collect related registers and capabilities
        pin_names = {p.name.upper() for p in cluster_pins}
        related_regs = [
            r for r in by_type.get("register", []) + by_type.get("configuration", [])
            if any(pn.lower() in (r.name + " " + r.content).lower() for pn in pin_names)
        ]
        related_caps = [
            c for c in by_type.get("capability", [])
            if any(pn.lower() in c.content.lower() for pn in pin_names)
        ]

        evidence = list(cluster_pins) + related_regs + related_caps

        return self._group_record(
            counters,
            cluster_name,
            self._generate_group_summary(cluster_name, cluster_pins),
            evidence if evidence else list(cluster_pins),
            f"Pin Group / {cluster_name}",
            responsibility,
            req_types,
            self._generate_application_scheme(cluster_name, cluster_pins),
            self._generate_missing_inputs(cluster_name, cluster_pins),
            subfuncs,
            related_pins=[p.name for p in cluster_pins],
            related_registers=_unique(r.name for r in related_regs),
        )

    def _build_register_cluster_group(
        self, counters: Counter[str], cluster_name: str,
        cluster_regs: list[FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a feature group for a discovered register cluster."""
        if not cluster_regs:
            return None

        sw_relations = [r.software_responsibility for r in cluster_regs]
        responsibility = max(set(sw_relations), key=sw_relations.count)

        reg_names = [r.name for r in cluster_regs]
        subfunc = SubfunctionRecord(
            name=f"{cluster_name} Access",
            summary=f"Access and manage {cluster_name.lower()}.",
            inputs="Register address; access parameters.",
            outputs="Register data or error status.",
            boundary="Invalid register, access failure.",
            related_registers=reg_names,
            application_scheme=f"Use for accessing the {cluster_name.lower()} group.",
            candidate_requirement_types=["接口需求", "配置需求"],
            missing_inputs=["寄存器地址映射", "访问权限"],
        )

        return self._group_record(
            counters,
            cluster_name,
            f"提供 {cluster_name} 功能的寄存器组。",
            list(cluster_regs),
            f"Register Group / {cluster_name}",
            responsibility,
            ["接口需求", "配置需求"],
            f"Define register access patterns for {cluster_name.lower()}.",
            ["确认寄存器默认值", "确认保留位处理"],
            [subfunc],
            related_registers=reg_names,
        )

    def _build_interface_group(
        self, counters: Counter[str], interfaces: list[FeatureRecord],
        pin_map: dict[str, FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a communication interface group from extracted interface records."""
        if not interfaces:
            return None

        # Detect bus types
        bus_types: set[str] = set()
        for iface in interfaces:
            text = f"{iface.name} {iface.content}".lower()
            if _contains_any(text, ("i2c", "scl", "sda")):
                bus_types.add("I2C")
            if _contains_any(text, ("spi", "sck", "mosi", "miso")):
                bus_types.add("SPI")
            if _contains_any(text, ("pwm", "duty cycle", "frequency")):
                bus_types.add("PWM")
            if _contains_any(text, ("analog", "adc", "voltage", "current sense")):
                bus_types.add("Analog")

        if not bus_types:
            # No recognised bus.  The chip is either pin-controlled (CAN
            # transceiver, GPIO expander) or uses an interface the extractor
            # does not yet recognise.  Skip the generic "Control Interface"
            # group — pin-controlled chips get their semantics from mode,
            # diagnostic, and configuration groups instead.
            return None

        bus_label = "/".join(sorted(bus_types))

        # Find related bus pins
        bus_pins: list[str] = []
        for name, pin in pin_map.items():
            text = f"{name} {pin.content}".lower()
            if any(bt.lower() in text for bt in bus_types):
                bus_pins.append(pin.name)
            elif _contains_any(text, ("scl", "sda", "sck", "mosi", "miso", "cs")):
                bus_pins.append(pin.name)

        subfuncs: list[SubfunctionRecord] = []
        if "I2C" in bus_types or "SPI" in bus_types:
            subfuncs.append(SubfunctionRecord(
                name="Register Read Transaction",
                summary=f"Read data through the {bus_label} interface.",
                inputs="Device address; register address; length.",
                outputs="Read data or error status.",
                boundary="NACK, timeout, invalid register, bus busy.",
                related_pins=bus_pins,
                application_scheme=f"Use for reading device state and configuration via {bus_label}.",
                candidate_requirement_types=["接口需求", "诊断需求"],
                missing_inputs=["底层总线 API", "错误码映射"],
            ))
            subfuncs.append(SubfunctionRecord(
                name="Register Write Transaction",
                summary=f"Write data through the {bus_label} interface.",
                inputs="Device address; register address; write data.",
                outputs="Write result status.",
                boundary="NACK, timeout, invalid register, write-protected field.",
                related_pins=bus_pins,
                application_scheme=f"Use for configuring device and controlling outputs via {bus_label}.",
                candidate_requirement_types=["接口需求", "功能需求"],
                missing_inputs=["写后验证策略", "错误恢复策略"],
            ))
        elif "PWM" in bus_types:
            subfuncs.append(SubfunctionRecord(
                name="PWM Signal Control",
                summary="Control PWM duty cycle and frequency for output signals.",
                inputs="Channel identifier; duty cycle; frequency.",
                outputs="Updated PWM signal parameters or error.",
                boundary="Invalid duty cycle, frequency out of range.",
                related_pins=bus_pins,
                application_scheme="Use for software-controlled PWM outputs.",
                candidate_requirement_types=["接口需求", "功能需求"],
                missing_inputs=["PWM 分辨率", "频率范围"],
            ))
        elif "Analog" in bus_types:
            subfuncs.append(SubfunctionRecord(
                name="Analog Signal Acquisition",
                summary="Sample analog feedback signals for current/voltage monitoring.",
                inputs="Channel identifier; sampling parameters.",
                outputs="Sampled analog value or error.",
                boundary="Invalid channel, ADC failure.",
                related_pins=bus_pins,
                application_scheme="Use for monitoring analog feedback like current sense or voltage reference.",
                candidate_requirement_types=["接口需求", "诊断需求"],
                missing_inputs=["ADC 分辨率", "采样率"],
            ))
        return self._group_record(
            counters,
            f"{bus_label} Control Interface",
            f"器件通过 {bus_label} 接口进行控制和状态反馈。",
            interfaces + [pin_map[p] for p in bus_pins if p in pin_map],
            f"Interface / {bus_label}",
            "software_constraint",
            ["接口需求", "功能需求"],
            f"Define {bus_label.lower()} access patterns and error handling.",
            ["确认总线访问归属", "确认错误恢复策略"],
            subfuncs,
            related_pins=bus_pins,
        )

    def _build_state_group(
        self, counters: Counter[str], states: list[FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a mode/state management group from extracted state records."""
        if not states:
            return None

        # Normalise and dedup state names.  Raw regex extraction produces
        # duplicates (e.g. "Normal" and "Normal mode", "sleep" and "Sleep mode")
        # and false positives ("Reset", "Active") that must be cleaned before
        # they reach the SRS overview section.
        _mode_blocklist = {"reset", "por", "active"}  # too broad, not device modes
        _seen: set[str] = set()
        _clean: list[str] = []
        for raw in sorted({s.name.strip() for s in states}):
            key = raw.lower().rstrip(" mode")
            if key in _mode_blocklist or key in _seen:
                continue
            # Prefer the capitalised form for display
            if key == "normal mode":
                _clean.append("Normal mode")
            elif key == "standby mode":
                _clean.append("Standby mode")
            elif key == "sleep mode":
                _clean.append("Sleep mode")
            else:
                _clean.append(raw)
            _seen.add(key)
        state_list = ", ".join(_clean) if _clean else "待数据手册补充"

        subfuncs = [
            SubfunctionRecord(
                name="模式切换控制",
                summary=f"Control transitions between device modes: {state_list}.",
                trigger="API call or hardware condition.",
                inputs="Target mode identifier.",
                outputs="Updated mode or error status.",
                boundary="Invalid mode, transition not allowed, device not ready.",
                application_scheme="Use for managing device operating modes based on system requirements.",
                candidate_requirement_types=["功能需求", "状态需求", "接口需求"],
                missing_inputs=["模式切换策略", "过渡时间约束"],
            ),
            SubfunctionRecord(
                name="当前模式观测",
                summary=f"Read the current operating mode from available states: {state_list}.",
                inputs="Observation request.",
                outputs="Current mode identifier.",
                boundary="Device not accessible, mode ambiguous.",
                application_scheme="Use for monitoring device state during operation and fault recovery.",
                candidate_requirement_types=["状态需求", "诊断需求"],
                missing_inputs=["模式读取方式", "模式确认策略"],
            ),
        ]

        return self._group_record(
            counters,
            "器件工作模式",
            f"器件定义了以下工作模式：{state_list}。",
            list(states),
            "状态 / 模式管理",
            "software_action",
            ["功能需求", "状态需求", "接口需求"],
            "Define mode transition control and observation interfaces based on project requirements.",
            ["确认项目使用哪些模式。", "确认模式切换触发条件。"],
            subfuncs,
        )

    def _build_diagnostic_group(
        self, counters: Counter[str], diagnostics: list[FeatureRecord],
        pin_map: dict[str, FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a diagnostic/fault handling group from extracted diagnostic records."""
        if not diagnostics:
            return None

        # Find fault-related pins
        fault_pins: list[str] = []
        for name, pin in pin_map.items():
            text = f"{name} {pin.content}".lower()
            if _contains_any(text, ("fault", "error", "diagnostic", "nfault",
                                      "alert", "warning", "interrupt", "status flag")):
                fault_pins.append(pin.name)

        diag_content = " ".join(d.name + " " + d.content for d in diagnostics).lower()

        # Collect structured fault rows from datasheet fault summary tables.
        # Dedup by fault name (first |...| field) because overlapping chunks
        # may produce identical rows from the same source table.
        all_fault_rows: list[str] = []
        seen_faults: set[str] = set()
        for d in diagnostics:
            for row in d.fault_rows:
                parts = row.split("|")
                if len(parts) >= 2:
                    fname = parts[1].strip().lower()
                    if fname in seen_faults:
                        continue
                    seen_faults.add(fname)
                all_fault_rows.append(row)

        subfuncs: list[SubfunctionRecord] = []
        if _contains_any(diag_content, ("fault", "error", "overcurrent", "ocp",
                                          "thermal", "tsd", "undervoltage", "uvlo",
                                          "cpuv", "charge pump")):
            subfuncs.append(SubfunctionRecord(
                name="故障状态读取",
                summary="Read fault status to detect device-level fault conditions.",
                inputs="Fault query request.",
                outputs="Fault status bitmask or individual fault flags.",
                boundary="Fault pin not connected, device not accessible.",
                related_pins=fault_pins,
                application_scheme="Use for detecting and categorizing device fault conditions in operation.",
                candidate_requirement_types=["诊断需求", "接口需求"],
                missing_inputs=["故障清除条件", "故障恢复策略"],
                fault_rows=list(all_fault_rows),
            ))
            subfuncs.append(SubfunctionRecord(
                name="故障恢复处理",
                summary="Execute recovery actions after fault conditions are detected.",
                trigger="Fault detection or status change.",
                inputs="Fault type; recovery parameters.",
                outputs="Recovery result or reinitialization status.",
                boundary="Persistent fault, recovery not supported.",
                related_pins=fault_pins,
                application_scheme="Use for automatic or controlled recovery from device fault states.",
                candidate_requirement_types=["诊断需求", "功能需求"],
                missing_inputs=["自动/手动恢复策略", "重试次数"],
            ))
        else:
            subfuncs.append(SubfunctionRecord(
                name="Diagnostic Status Observation",
                summary="Observe diagnostic indicators and map to software status.",
                inputs="Diagnostic query or pin state.",
                outputs="Software status or event.",
                boundary="Diagnostic signal not connected or not applicable.",
                related_pins=fault_pins,
                application_scheme="Use when diagnostic signals are connected to the MCU.",
                candidate_requirement_types=["诊断需求", "状态需求"],
                missing_inputs=["硬件连接确认", "轮询/中断策略"],
            ))

        return self._group_record(
            counters,
            "故障与诊断处理",
            "诊断与故障信号提供软件可观测的器件状态。",
            diagnostics + [pin_map[p] for p in fault_pins if p in pin_map],
            "Diagnostic / Fault",
            "open_issue",
            ["诊断需求", "接口需求", "状态需求"],
            "Define fault detection, reporting, and recovery based on project hardware connections.",
            ["确认故障 pin 是否连接 MCU。", "确认故障恢复策略。"],
            subfuncs,
            related_pins=fault_pins,
        )

    def _build_timing_group(
        self, counters: Counter[str], timing: list[FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a timing constraints group from extracted timing records."""
        if not timing:
            return None

        # Group timings by category
        by_category: dict[str, list[FeatureRecord]] = {}
        for t in timing:
            cat = _timing_name(t.content)
            by_category.setdefault(cat, []).append(t)

        subfuncs: list[SubfunctionRecord] = []
        for cat_name, cat_records in by_category.items():
            # Collect actual timing values from child records so they survive
            # through the pipeline into the final requirement description.
            timing_values: list[str] = []
            for cr in cat_records:
                if cr.content:
                    timing_values.append(cr.content[:200])
            timing_text = "; ".join(timing_values[:8]) if timing_values else ""
            subfuncs.append(SubfunctionRecord(
                name=f"{cat_name} Guard",
                summary=f"Apply timing constraints for {cat_name.lower()} operations.",
                inputs="Operation trigger; timing parameter.",
                outputs="Timed operation result or timeout indication.",
                boundary="No software trigger, no timeout policy.",
                timing=timing_text,
                application_scheme=f"Use when software must observe {cat_name.lower()} timing constraints.",
                candidate_requirement_types=["时序需求", "诊断需求"],
                missing_inputs=["软件是否负责等待", "超时值"],
            ))

        return self._group_record(
            counters,
            "时序约束",
            "数据手册中约束软件操作的时序参数。",
            list(timing),
            "Timing / Verification",
            "hardware_constraint",
            ["时序需求", "验证策略"],
            "Apply software timing guards only where the driver owns the wait or timeout.",
            ["确认哪些时序需要软件处理。", "确认验证测量点。"],
            subfuncs,
        )

    def _build_constraint_group(
        self, counters: Counter[str], constraints: list[FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a boundary/constraint group from extracted constraint records."""
        if not constraints:
            return None

        # Build subfunctions from actual constraint records, not from a
        # hard-coded generic placeholder.  Each constraint gets its own
        # subfunction named after the source datasheet heading so that
        # requirements carry concrete, traceable names instead of
        # nonsensical labels like "非法输入拒绝".
        subfuncs: list[SubfunctionRecord] = []
        seen_names: set[str] = set()
        for c in constraints:
            cname = (c.name or "").strip()
            if not cname or cname in seen_names:
                continue
            seen_names.add(cname)
            subfuncs.append(
                SubfunctionRecord(
                    name=f"{cname}约束",
                    summary=f"Validate and enforce documented constraints for {cname.lower()}.",
                    inputs="Configuration item, API parameter.",
                    outputs="Validation result or error status.",
                    boundary="Constraint not reachable through software input path.",
                    application_scheme="Use when software accepts or configures values subject to this constraint.",
                    candidate_requirement_types=["配置需求", "约束"],
                    missing_inputs=["软件输入路径", "错误返回语义"],
                ),
            )
        if not subfuncs:
            subfuncs.append(
                SubfunctionRecord(
                    name="数据手册约束校验",
                    summary="Validate and enforce documented datasheet constraints.",
                    inputs="Configuration item, API parameter.",
                    outputs="Validation result or error status.",
                    boundary="Constraint not reachable through software input path.",
                    application_scheme="Use when software must enforce datasheet boundary conditions.",
                    candidate_requirement_types=["配置需求", "约束"],
                    missing_inputs=["具体约束项清单", "错误返回语义"],
                ),
            )

        return self._group_record(
            counters,
            "边界与约束行为",
            "数据手册约束项定义有效操作的边界条件。",
            list(constraints),
            "Constraint / Boundary",
            "open_issue",
            ["接口需求", "配置需求", "约束"],
            "Generate rejection requirements only for constraints reachable through software.",
            ["确认软件是否能触发该约束条件。", "确认非法值返回语义。"],
            subfuncs,
        )

    def _build_capability_group(
        self, counters: Counter[str], cluster_name: str,
        capabilities: list[FeatureRecord],
    ) -> FeatureRecord | None:
        """Build a group for remaining capabilities not covered by other groups."""
        if not capabilities:
            return None

        cap_text = " ".join(c.name + " " + c.content for c in capabilities)

        subfuncs = [
            SubfunctionRecord(
                name=f"{cluster_name} Support",
                summary=f"Enable and manage {cluster_name.lower()}.",
                inputs="Project configuration; capability parameters.",
                outputs="Operational capability or error status.",
                boundary="Capability not supported by hardware connection.",
                application_scheme="Use when the project requires this capability.",
                candidate_requirement_types=["功能需求", "接口需求"],
                missing_inputs=["项目是否使用该能力", "参数范围"],
            ),
        ]

        return self._group_record(
            counters,
            cluster_name,
            f"其他器件能力：{_summary(cap_text, 200)}",
            list(capabilities),
            f"Capability / {cluster_name}",
            "open_issue",
            ["功能需求"],
            "Confirm project scope and usage of this capability.",
            ["确认项目是否使用该能力。"],
            subfuncs,
        )

    # ------------------------------------------------------------------
    # Subfunction & metadata helpers
    # ------------------------------------------------------------------

    def _build_pin_subfunctions(
        self, cluster_name: str, cluster_pins: list[FeatureRecord],
    ) -> list[SubfunctionRecord]:
        """Build subfunction records from a pin cluster's actual functions."""
        subfuncs: list[SubfunctionRecord] = []
        pin_names = [p.name for p in cluster_pins]

        text_all = " ".join(p.name + " " + p.content for p in cluster_pins).lower()

        # Control/input pins → set/configure subfunctions
        if _contains_any(text_all, ("enable", "disable", "sleep", "wake", "control",
                                      "mode select", "nsleep")):
            subfuncs.append(SubfunctionRecord(
                name="器件启停与模式控制",
                summary="控制器件使能状态和工作模式选择。",
                trigger="API call or system state change.",
                inputs="Enable signal; mode selection parameters.",
                outputs="Updated device state.",
                boundary="Invalid mode, device not ready, transition timeout.",
                related_pins=pin_names,
                application_scheme="Use for enabling/disabling the device and selecting operating modes.",
                candidate_requirement_types=["功能需求", "接口需求", "状态需求"],
                missing_inputs=["模式切换策略", "默认状态"],
            ))

        # Power output pins → output control subfunctions
        if _contains_any(text_all, ("h-bridge", "half-bridge", "motor output",
                                      "driver output", "switch output", "out1", "out2")):
            subfuncs.append(SubfunctionRecord(
                name="输出状态控制",
                summary="控制功率输出引脚的电平、方向和 PWM 占空比。",
                trigger="Output control API call.",
                inputs="Output channel; target state (forward/reverse/brake/coast).",
                outputs="Updated output state.",
                boundary="Invalid output state, overcurrent, thermal shutdown.",
                related_pins=pin_names,
                application_scheme="Use for controlling motor direction, speed, and braking.",
                candidate_requirement_types=["功能需求", "接口需求"],
                missing_inputs=["输出状态映射", "PWM 配置"],
            ))

        # Current sense pins → read/monitor subfunctions
        if _contains_any(text_all, ("current sense", "current monitor", "proportional",
                                      "ipropi", "current feedback")):
            subfuncs.append(SubfunctionRecord(
                name="负载电流监测",
                summary="读取并解析电流检测反馈，用于负载监测和堵转检测。",
                trigger="周期采样或按需读取。",
                inputs="ADC 通道；采样参数。",
                outputs="负载电流值或过载指示。",
                boundary="ADC 未配置、检测电阻未焊接。",
                related_pins=pin_names,
                application_scheme="用于监测电机负载电流、堵转检测和过载保护。",
                candidate_requirement_types=["接口需求", "诊断需求", "功能需求"],
                missing_inputs=["电流采样率", "过流阈值"],
            ))

        # Analog reference pins → configuration subfunctions
        if _contains_any(text_all, ("reference", "vref", "comparator", "threshold")):
            subfuncs.append(SubfunctionRecord(
                name="参考电压与阈值配置",
                summary="配置基准电压以设置电流调节的斩波阈值。",
                trigger="初始化或运行时配置。",
                inputs="基准电压值或来源。",
                outputs="配置后的调节阈值。",
                boundary="电压超出有效范围、调节功能禁用。",
                related_pins=pin_names,
                application_scheme="用于通过 VREF 设置电流调节跳变点。",
                candidate_requirement_types=["配置需求", "功能需求"],
                missing_inputs=["VREF 电压范围", "默认阈值"],
            ))

        # Fault pins → diagnostic subfunctions
        if _contains_any(text_all, ("fault", "error", "nfault", "diagnostic", "alert")):
            subfuncs.append(SubfunctionRecord(
                name="故障信号监测",
                summary="监测故障指示信号以获取器件保护状态。",
                trigger="GPIO 中断或周期轮询。",
                inputs="故障引脚状态。",
                outputs="故障状态分类。",
                boundary="故障引脚未连接、GPIO 未配置。",
                related_pins=pin_names,
                application_scheme="用于实时故障检测与响应。",
                candidate_requirement_types=["诊断需求", "接口需求"],
                missing_inputs=["中断/轮询策略", "故障响应时间"],
            ))

        # If no specific subfunctions matched, create a generic one
        if not subfuncs:
            subfuncs.append(SubfunctionRecord(
                name=f"{cluster_name}处理",
                summary=f"Manage {cluster_name.lower()} according to project requirements.",
                inputs="Project-defined parameters.",
                outputs="Expected behavior or status.",
                boundary="Hardware connection not confirmed.",
                related_pins=pin_names,
                application_scheme="Use according to project hardware configuration.",
                candidate_requirement_types=["功能需求"],
                missing_inputs=["项目使用方式", "接口定义"],
            ))

        return subfuncs

    @staticmethod
    def _infer_requirement_types(
        cluster_name: str, cluster_pins: list[FeatureRecord],
    ) -> list[str]:
        """Infer applicable requirement types from pin functional roles."""
        req_types: list[str] = []
        text_all = " ".join(p.name + " " + p.content for p in cluster_pins).lower()

        if _contains_any(text_all, ("control", "enable", "disable", "output", "drive",
                                      "set", "write", "mode select")):
            if "接口需求" not in req_types:
                req_types.append("接口需求")
            if "功能需求" not in req_types:
                req_types.append("功能需求")
        if _contains_any(text_all, ("sense", "read", "monitor", "input", "feedback",
                                      "measure", "sample", "fault", "status", "nfault")):
            if "接口需求" not in req_types:
                req_types.append("接口需求")
            if "诊断需求" not in req_types:
                req_types.append("诊断需求")
        if _contains_any(text_all, ("reference", "vref", "configure", "mode",
                                      "current regulation", "threshold")):
            if "配置需求" not in req_types:
                req_types.append("配置需求")
        if _contains_any(text_all, ("sleep", "wake", "standby", "mode", "state",
                                      "transition")):
            if "状态需求" not in req_types:
                req_types.append("状态需求")
        if not req_types:
            req_types = ["功能需求"]
        return req_types

    @staticmethod
    def _generate_group_summary(cluster_name: str, cluster_pins: list[FeatureRecord]) -> str:
        """Generate a Chinese one-line summary from the pin cluster."""
        funcs = sorted({p.content[:80] for p in cluster_pins if p.content})
        pin_list = "、".join(p.name for p in cluster_pins[:5])
        if len(cluster_pins) > 5:
            pin_list += f"等{len(cluster_pins)}个引脚"
        if funcs:
            return f"器件提供 {cluster_name}（{pin_list}）：{'；'.join(funcs[:2])}"
        return f"器件提供 {cluster_name}（{pin_list}）。"

    @staticmethod
    def _generate_application_scheme(cluster_name: str, cluster_pins: list[FeatureRecord]) -> str:
        """Generate an application scheme description."""
        pin_list = ", ".join(p.name for p in cluster_pins[:6])
        if len(cluster_pins) > 6:
            pin_list += f" (+{len(cluster_pins) - 6} more)"
        return (
            f"Use the {cluster_name.lower()} ({pin_list}) according to project hardware "
            "configuration. Project inputs must confirm which pins are connected and their "
            "software ownership."
        )

    @staticmethod
    def _generate_missing_inputs(cluster_name: str, cluster_pins: list[FeatureRecord]) -> list[str]:
        """Generate missing-input hints from pin roles."""
        hints = ["确认项目硬件连接和 pin 使用范围。"]
        text_all = " ".join(p.content for p in cluster_pins).lower()
        if _contains_any(text_all, ("control", "enable", "disable", "mode")):
            hints.append("确认默认控制状态和模式。")
        if _contains_any(text_all, ("output", "drive", "motor")):
            hints.append("确认输出驱动配置和默认电平。")
        if _contains_any(text_all, ("sense", "monitor", "feedback", "adc")):
            hints.append("确认采样率和阈值配置。")
        if _contains_any(text_all, ("fault", "diagnostic", "interrupt")):
            hints.append("确认故障响应策略和恢复机制。")
        return hints

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
            if not re.search(r"\b(feature|overview|general description|description|function|特性|概述|说明|功能|描述|应用)\b", heading, re.I):
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
            # Skip chunks that have table headings about external components
            heading = " ".join(chunk.heading_path).lower()
            text = _plain_text(chunk.text)
            if _contains_any(heading, ("外部组件", "外部元件", "external component", "recommended")):
                continue

            rows_from_tables = list(_table_rows(chunk))
            if rows_from_tables:
                # Process structured table rows
                for rows in rows_from_tables:
                    if not rows:
                        continue
                    header = [cell.strip().lower() for cell in rows[0]]
                    header_joined = " ".join(header)
                    en_match = (("symbol" in header and "function" in header)
                                or ("pin" in header and "description" in header))
                    cn_match = any(kw in header_joined for kw in ("名称", "引脚", "端子"))
                    if not (en_match or cn_match):
                        continue
                    symbol_index = self._resolve_symbol_index(header)
                    function_index = self._resolve_function_index(header)
                    direction_index = (header.index("direction") if "direction" in header
                                       else header.index("类型") if "类型" in header
                                       else -1)
                    for row in rows[1:]:
                        rec = self._make_pin_candidate(row, symbol_index, function_index, direction_index, chunk)
                        if rec:
                            records.append(rec)
            elif _contains_any(heading, ("引脚功能", "pin function", "pin configur", "引脚配置")):
                # Fallback: parse pin table from raw markdown text when structured parsing fails
                # Use chunk.text directly (not _plain_text which collapses newlines)
                raw_pins = self._parse_pin_table_raw(chunk.text)
                for symbol, function, direction in raw_pins:
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

    @staticmethod
    def _resolve_symbol_index(header: list[str]) -> int:
        for kw in ("名称", "symbol", "pin", "端子"):
            if kw in header:
                return header.index(kw)
        return next((i for i, h in enumerate(header) if h and h not in ("", "引脚", "类型", "说明", "功能", "方向")), 0)

    @staticmethod
    def _resolve_function_index(header: list[str]) -> int:
        for kw in ("说明", "功能", "function", "description"):
            if kw in header:
                return header.index(kw)
        return len(header) - 1

    @staticmethod
    def _make_pin_candidate(row: list[str], symbol_index: int, function_index: int,
                            direction_index: int, chunk: DocumentChunk) -> Any:
        if symbol_index >= len(row) or function_index >= len(row):
            return None
        symbol = _clean_symbol(row[symbol_index])
        if not symbol or symbol in {"VDD", "VSS", "VCC", "GND", "PGND", "NC", "PAD", "EP"}:
            return None
        direction = row[direction_index].strip() if 0 <= direction_index < len(row) else ""
        function = row[function_index].strip()
        relation = _pin_software_relation(symbol, function)
        return _Candidate(
            type="pin", name=symbol,
            content=f"{direction + '. ' if direction else ''}{function}",
            chunk=chunk, software_responsibility=relation,
            status="Open Issue", can_generate_requirement="Needs Review",
            gap="Project software ownership is not confirmed.",
            extractor="pin_extractor", feature_category="Pin",
            functional_summary=f"Pin {symbol} provides a hardware connection point.",
            related_pins=(symbol,),
            candidate_requirement_types=("接口需求", "配置需求", "资源需求"),
            application_scheme="Use pin facts to build interface/resource mapping.",
            missing_inputs=("Pin 所有权", "硬件连接", "软件是否控制/采样"),
        )

    @staticmethod
    def _parse_pin_table_raw(text: str) -> list[tuple[str, str, str]]:
        """Fallback: parse pin definitions from raw markdown table text.

        Handles tables that the structured parser can't process (e.g., multi-row
        headers, empty columns, Chinese table formats).
        """
        results: list[tuple[str, str, str]] = []
        # Match rows like: | CPH | 11 | 13 | PWR | charge pump... |
        # or Chinese: | EN/IN1 | 15 | 1 | I | H桥控制输入... |
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line.startswith("|") or not line.endswith("|"):
                continue
            if "---" in line:  # skip separator rows
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 3:
                continue
            # First non-empty cell is the pin name
            first_cell = cells[0] if cells[0] else ""
            if not first_cell or len(first_cell) > 15:
                continue
            # Skip header rows (cells contain structural keywords)
            first_lower = first_cell.lower()
            if first_lower in ("名称", "引脚", "端子", "pin", "symbol", "name", "组件"):
                continue
            # Skip rows that look like component descriptions
            if any(kw in " ".join(cells[:3]).lower() for kw in ("电容", "电阻", "µf", "nf", "kω", "mω")):
                continue
            # The last non-empty cell is usually the function description
            func_parts = [c for c in cells[2:] if c and len(c) > 3]
            function = func_parts[-1] if func_parts else " ".join(cells[1:])
            # Extract direction/type from middle cells
            direction = ""
            for c in cells[1:]:
                cu = c.upper()
                if cu in ("I", "O", "IO", "PWR", "OD", "NC", "GND", "POWER", "INPUT", "OUTPUT"):
                    direction = c
                    break
            results.append((_clean_symbol(first_cell), function, direction))
        return results

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
                        # English mode names: require "mode" suffix for generic
                        # terms (Normal/Standby/Sleep) to avoid matching section
                        # headings and non-mode usages.  Standalone "POR" and
                        # "Reset" are dropped — they fire in too many non-mode
                        # contexts (e.g. "reset the timer").
                        r"\b(?:Normal mode|Standby mode|Sleep mode|"
                        r"Listen-only mode|Listen only mode|"
                        r"Go-to-Sleep mode|Go to Sleep mode|"
                        r"Power-On Reset|Power On Reset|"
                        r"Operating mode|Active mode)\b"
                        # Chinese mode names
                        r"|(?:正常模式|待机模式|睡眠模式|活动模式|"
                        r"只听模式|休眠模式|"
                        r"上电复位|运行模式|工作模式)",
                        text,
                        flags=re.IGNORECASE,
                    )
                )
            ):
                content = _sentence_with(text, mode) or mode
                # Skip if content is raw table markup (>30% pipes)
                if content.count("|") > len(content) * 0.3:
                    continue
                records.append(
                    _Candidate(
                        type="state_machine",
                        name=mode,
                        content=content,
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
        # Cross-chunk dedup: track fault names across ALL chunks so that
        # split tables (e.g. Table 5 parts 1 & 2 in TJA1043) don't produce
        # duplicate rows.
        seen_fault_names: set[str] = set()
        for chunk in chunks:
            heading = " ".join(chunk.heading_path)
            heading_lower = heading.lower()
            # Skip chunks that are about electrical specs, packaging, or general descriptions
            if _contains_any(heading_lower, ("绝对最大", "建议运行", "电气特性", "典型特性",
                                               "热性能", "esd", "封装", "packag", "mechanical",
                                               "tape and reel", "订购", "特性", "应用",
                                               "引脚功能", "引脚配置", "外部元", "简化原理图")):
                continue
            text = _plain_text(chunk.text)
            diagnostic_heading = re.search(r"\b(interrupts?|int\b|faults?|failures?|errors?|status|flags?|diagnostic|"
                                           r"中断|故障|错误|状态|标志|诊断|保护)\b", heading, re.I)
            diagnostic_text = re.search(r"\b(INT|ERR|faults?|failures?|errors?|status flag|interrupt output|diagnostic|"
                                        r"中断|故障|错误|状态标志|诊断|保护|nFAULT|n?fault|flags?)\b", text)
            if not (diagnostic_heading or diagnostic_text):
                continue

            # ---- Fault summary table parsing ----
            # Datasheets often have a structured fault summary table (e.g. §7.3.4.5).
            # Parse each row into a pipe-delimited string matching the builder's
            # fault table format so it flows through to the planner.
            fault_rows: list[str] = []
            for rows in _table_rows(chunk):
                if not rows:
                    continue
                header = [cell.strip() for cell in rows[0]]
                if not _is_fault_summary_header(header):
                    continue
                for row in rows[1:]:
                    parsed_row = _parse_fault_summary_row(row, header)
                    if not parsed_row:
                        continue
                    # Dedup by fault name (first |...| field) across chunks
                    parts = parsed_row.split("|")
                    if len(parts) >= 2:
                        fname = parts[1].strip().lower()
                        if fname in seen_fault_names:
                            continue
                        seen_fault_names.add(fname)
                    fault_rows.append(parsed_row)

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
                    fault_rows=tuple(fault_rows),
                )
            )
        return records

    def _extract_timing(self, parsed: ParsedDocument, chunks: list[DocumentChunk]) -> list[_Candidate]:
        records: list[_Candidate] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            # Skip non-technical sections that may contain timing units in boilerplate.
            # Also skip TOC, cross-reference, legal, and revision-history sections
            # which frequently contain timing-unit strings in non-timing contexts.
            if _contains_any(heading, ("packag", "mechanical", "tape and reel",
                                         "legal", "disclaimer", "order", "revision",
                                         "封装", "机械", "订购", "法律", "免责",
                                         "content", "cross-reference", "trademark",
                                         "revision history", "revision_history",
                                         "附录", "附录a", "appendix", "contents",
                                         "soldering", "焊接")):
                continue
            text = _plain_text(chunk.text)
            _has_timing_text = re.search(r"\b(us|µs|μs|ms|s|khz|mhz|hz|ns)\b", text, flags=re.IGNORECASE)
            if _has_timing_text:
                # Only extract sentences that contain BOTH a timing unit AND a
                # timing-relevant keyword (parameter name, constraint, or behavior).
                # This filters out boilerplate, TOC entries, legal text, and
                # cross-references that happen to mention time units.
                _timing_keywords = (
                    r"\b(delay|timeout|time-out|time out|hold time|"
                    r"wake-up|wake up|wakeup|detection time|recovery time|"
                    r"bit time|bit width|propagation|rise time|fall time|"
                    r"turn-on|turn-off|startup|power-up|settling|ramp|"
                    r"deglitch|debounce|filter|blanking|"
                    r"dominant.*time|recessive.*time|"
                    r"undervoltage.*time|mode.*time|"
                    r"switch.*time|transition.*time|"
                    r"stabil|guard|min.*time|max.*time)\b"
                )
                for sentence in re.split(r"(?<=[.!?。；;])\s+", text):
                    if not re.search(r"\b(us|µs|μs|ms|s|khz|mhz|hz|ns)\b", sentence, flags=re.IGNORECASE):
                        continue
                    if not re.search(_timing_keywords, sentence, re.I):
                        continue
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

            # Also extract timing parameters from TABLE blocks (e.g. Dynamic
            # characteristics tables).  Table rows carry structured parameter
            # names with min/typ/max values and units that the sentence-based
            # extraction above cannot reach.  This runs independently of the
            # text-based extraction.
            _timing_units_pat = re.compile(r"\b(us|µs|μs|ms|s|khz|mhz|hz|ns)\b", re.I)
            for rows in _table_rows(chunk):
                if not rows or len(rows) < 2:
                    continue
                hdr_text = " ".join(cell.strip().lower() for cell in rows[0])
                has_param = any(kw in hdr_text for kw in ("parameter", "symbol", "参数", "timing", "time"))
                has_unit = any(kw in hdr_text for kw in ("unit", "单位", "min", "max", "typ"))
                if not (has_param or has_unit):
                    continue
                for row in rows[1:]:
                    if len(row) < 2:
                        continue
                    row_text = " ".join(cell.strip() for cell in row)
                    if not _timing_units_pat.search(row_text):
                        continue
                    param_name = row[1].strip() if len(row) > 1 and row[1].strip() else row[0].strip()
                    symbol = row[0].strip() if len(row) > 0 else ""
                    min_val = row[3].strip() if len(row) > 3 else ""
                    typ_val = row[4].strip() if len(row) > 4 else ""
                    max_val = row[5].strip() if len(row) > 5 else ""
                    unit = row[6].strip() if len(row) > 6 else ""
                    content = f"{symbol} — {param_name}: typ={typ_val}, min={min_val}, max={max_val} {unit}".strip()
                    records.append(
                        _Candidate(
                            type="timing",
                            name=_timing_name(param_name),
                            content=content,
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
                # Limit per-table rows to avoid flooding
                if len(records) > 60:
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
    """Determine software relationship from pin function description text.

    Analyzes the function description for semantic categories rather than
    matching against a hardcoded pin name list.  Supports both English and
    Chinese datasheet descriptions.
    """
    text = f"{symbol} {function}".lower()
    upper = symbol.upper()

    # Power/ground/thermal/no-connect pins are hardware-only
    if upper in {"VDD", "VSS", "VCC", "GND", "PGND", "NC", "EP", "PAD"}:
        return "hardware_constraint"

    # Communication bus pins constrain software access
    if _contains_any(text, ("clock", "data bus", "serial clock", "serial data",
                              "scl", "sda", "sdi", "sdo", "sck", "miso", "mosi",
                              "cs", "chip select", "bus")):
        return "software_constraint"

    # Address/configuration pins are typically hardware-tied
    if _contains_any(text, ("address", "addr", "chip select config")):
        return "hardware_constraint"

    # ---------- Chinese + English combined matches ----------

    # Fault/diagnostic output pins: software MUST read them to detect faults
    if _contains_any(text, ("fault", "error", "diagnostic", "alert", "warning",
                              "status", "flag", "open-drain output",
                              "interrupt output", "nfault",
                              "故障", "诊断", "报警", "警告", "状态指示")):
        return "software_action"

    # Control inputs: software MUST drive them
    if _contains_any(text, ("enable", "disable", "reset input", "sleep", "wake",
                              "mode select", "control input", "nsleep",
                              "使能", "禁用", "睡眠", "唤醒", "复位",
                              "控制输入", "控制模式", "模式选择",
                              "三电平输入", "四电平输入")):
        return "software_action"

    # Sense/monitor outputs: software MUST sample them (ADC / GPIO input)
    if _contains_any(text, ("current sense", "current monitor", "sense output",
                              "proportional", "monitor", "feedback", "ipropi",
                              "analog current output",
                              "电流检测", "电流监测", "电流输出", "比例电流",
                              "模拟电流", "反馈", "检测输出")):
        return "software_action"

    # Motor/power control outputs: software drives the H-bridge
    if _contains_any(text, ("h-bridge", "half-bridge", "motor output", "driver output",
                              "high-side", "low-side", "switch output",
                              "h 桥", "半桥", "电机输出", "驱动输出",
                              "功率输出", "开关输出")):
        return "software_action"

    # Analog reference inputs: software may set or sample
    if _contains_any(text, ("reference", "vref", "analog input", "comparator",
                              "基准电压", "参考电压", "模拟输入")):
        return "software_action"

    # Charge pump pins are hardware support
    if _contains_any(text, ("charge pump", "vcp", "cph", "cpl", "bootstrap",
                              "电荷泵")):
        return "hardware_constraint"

    # Generic I/O: need project confirmation for exact usage
    if _contains_any(text, ("input", "output", "i/o", "io ", "bidirectional",
                              "port", "gpio")):
        return "open_issue"

    return "open_issue"


def _clean_symbol(value: str) -> str:
    # Preserve pin name semantics: keep / for dual-function pins, keep leading n/n prefix
    result = re.sub(r"[^A-Za-z0-9_/]", "", value)
    return result


def _clean_symbol_upper(value: str) -> str:
    """Aggressive cleaning for register names (upper-case, no special chars)."""
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
    """Derive a timing category name from the surrounding context.

    Checks common timing domains and builds a category name reflecting what
    the constraint applies to, rather than hardcoding I2C/Reset/Interrupt.
    """
    text = sentence.lower()
    categories = [
        (r"\bi2c|scl|sda|i2s\b", "I2C"),
        (r"\bspi|sck|mosi|miso|cs\b", "SPI"),
        (r"\breset|por|power-on|power on", "复位"),
        (r"\binterrupt|int|fault|n?fault", "中断/故障"),
        (r"\bwake|sleep|standby|shutdown", "电源模式切换"),
        (r"\bpwm|duty|period|frequency|khz|mhz|hz\b", "PWM/开关"),
        (r"\bpropagation|rise time|fall time|turn-on|turn-off|delay\b", "信号传播"),
        (r"\bstartup|power-up|power up|ramp|settling", "启动/稳定"),
        (r"\bcharge pump|bootstrap|cpuv", "电荷泵"),
        (r"\bovercurrent|over-current|ocp|thermal|tsd|protection", "保护响应"),
        (r"\bdeglitch|debounce|filter|blanking", "信号调理"),
    ]
    for pattern, label in categories:
        if re.search(pattern, text, re.I):
            return f"{label}时序值"
    return "时序值"


def _is_fault_summary_header(header: list[str]) -> bool:
    """Detect whether a table header row describes a fault/protection summary.

    Datasheets often have tables like:
      | 故障 | 条件 | 报告 | H桥 | 恢复 |
      | Fault | Condition | Report | Recovery |
    """
    joined = " ".join(header).lower()
    fault_cols = ("故障", "fault", "error", "错误", "protection", "保护", "flag", "failure", "fail")
    cond_cols = ("条件", "condition", "触发", "trigger", "threshold")
    recovery_cols = ("恢复", "recovery", "reset", "清除", "clear")
    has_fault = any(kw in joined for kw in fault_cols)
    has_cond = any(kw in joined for kw in cond_cols)
    has_recovery = any(kw in joined for kw in recovery_cols)
    # Need at least a fault/name column + one of condition or recovery
    return has_fault and (has_cond or has_recovery)


def _parse_fault_summary_row(row: list[str], header: list[str]) -> str:
    """Parse one row of a fault summary table into a pipe-delimited fault string.

    Returns a string matching the builder's fault table format:
      | 故障名称 | hardware_chip | 触发条件 | 检测方式 | 确认策略 | 芯片行为 | 恢复类型 | 软件动作 |

    Unlike the previous H-bridge-centric implementation, this version
    infers detection, behavior, recovery, and software action from the
    actual row and header content rather than hard-coding motor-driver
    defaults.  This makes it work across CAN transceivers, SBCs, and
    other chip types without producing misleading output.
    """
    if not row or all(not cell.strip() for cell in row):
        return ""

    # Filter out separator and boilerplate rows (e.g. "------------------")
    first_cell = row[0].strip() if row else ""
    if re.match(r"^[-=_]{3,}$", first_cell):
        return ""
    if first_cell.lower() in ("internal flag", "internal<br>flag"):
        return ""  # repeated header row

    def _col(keywords: tuple[str, ...], fallback_idx: int = -1) -> str:
        for kw in keywords:
            for i, h in enumerate(header):
                if kw in h.lower():
                    return row[i].strip() if i < len(row) else ""
        if 0 <= fallback_idx < len(row):
            return row[fallback_idx].strip()
        return ""

    name = _col(("故障", "fault", "名称", "name", "item", "flag", "internal"), 0)
    if not name:
        return ""

    fault_class = "hardware_chip"

    # ---- trigger ----
    # Look for an explicit trigger/condition column.  Fallback to column 1
    # only when the content looks like a real condition (not a boolean flag
    # like "no" / "yes" that indicates pin availability).
    trigger = _col(("条件", "condition", "触发", "trigger", "threshold"), -1)
    if not trigger:
        trigger = _col(("description", "说明", "detail"), 1)
    trigger = trigger.replace("<br>", " ").replace("\n", " ").strip()
    # If the fallback column is clearly NOT a trigger (short boolean, pin
    # availability, or ERR_N indicator), produce a descriptive fallback
    # instead of misleading content like "no".
    if not trigger or trigger.lower() in ("no", "yes", "n/a", "-", "—"):
        flag_desc = _col(("恢复", "recovery", "flag is cleared", "清除", "clear"), 2)
        if flag_desc and len(flag_desc) > 10:
            trigger = f"条件见数据手册（清除方式: {flag_desc[:120]}）"
        else:
            trigger = "详见数据手册对应章节"

    # ---- detection: infer from the report / ERR_N / nFAULT column ----
    report = _col(("报告", "report", "指示", "indicator", "nfa", "nfault",
                    "err_n", "available on pin"), 2)
    report_lower = report.lower()
    if "err_n" in report_lower or "err" in report_lower:
        detection = "轮询 ERR_N 引脚状态"
    elif "rxnfx" in report_lower or "rxn" in report_lower:
        detection = "轮询 RXD/ERR_N 引脚状态"
    elif report and report != "no":
        detection = f"读取 {report} 状态"
    else:
        # Flag not directly readable via a status pin — infer from mode changes
        detection = "通过模式变化或关联标志间接反映"

    # ---- confirmation ----
    confirmation = "连续 2 次 MainFunction 周期确认"

    # ---- chip behavior: use the recovery / clear column as behavior proxy ----
    behavior_col = _col(("行为", "behavior", "action", "动作", "h桥", "h-bridge"), 3)
    recovery_text = _col(("恢复", "recovery", "flag is cleared", "清除", "clear"), -1)
    recovery_text = recovery_text or "".join(row[2:]) if len(row) > 2 else ""

    # Derive chip behavior from recovery text instead of hard-coding H-bridge.
    recovery_lower = recovery_text.lower()
    if behavior_col:
        chip_behavior = behavior_col.replace("<br>", " ").replace("\n", " ")
    elif "sleep mode" in recovery_lower or "inh" in recovery_lower:
        chip_behavior = "进入 Sleep 模式，INH 浮空，关闭外部稳压器"
    elif "standby" in recovery_lower or "zero load" in recovery_lower:
        chip_behavior = "进入 Standby 模式，总线零负载"
    elif "transmitter" in recovery_lower or "disable" in recovery_lower:
        chip_behavior = "禁用发送器"
    else:
        chip_behavior = "标志置位，通过 ERR_N 或 RXD 反映（详见数据手册）"

    # ---- recovery type ----
    if any(kw in recovery_lower for kw in ("锁存", "latch", "nsleep", "power-on reset")):
        recovery = "manual_reset（需软件复位或重新上电）"
    elif any(kw in recovery_lower for kw in ("enter normal mode", "entering normal",
                                               "clear", "清除", "pwon", "wake flag")):
        recovery = "manual_clear（需软件切换模式或清除标志）"
    elif any(kw in recovery_lower for kw in ("自动", "auto", "retry", "重试",
                                               "recover", "recessive")):
        recovery = "auto（芯片自动恢复）"
    elif "vbatt" in recovery_lower and "recover" in recovery_lower:
        recovery = "auto（VBAT 恢复后自动清除）"
    else:
        recovery = "manual_clear（详见数据手册恢复条件）"

    # ---- software action — inferred from name + recovery semantics ----
    name_lower = name.lower()
    if any(kw in name_lower for kw in ("uv", "uvnom", "uvbat", "undervoltage",
                                         "欠压", "vcc", "vio", "vbat")):
        if "uvbat" in name_lower or "vbat" in name_lower:
            sw_action = "记录 VBAT 欠压事件；等待 VBAT 恢复后重新配置工作模式"
        else:
            sw_action = "记录供电欠压事件；等待供电恢复或 Wake 源触发后重新初始化"
    elif any(kw in name_lower for kw in ("pwon", "power-on", "power on", "上电")):
        sw_action = "在 Listen-only 模式轮询 ERR_N 确认冷启动；进入 Normal 模式清除标志"
    elif any(kw in name_lower for kw in ("wake", "唤醒")):
        sw_action = "读取 ERR_N/RXD 识别唤醒源；切换至 Normal 模式处理唤醒事件"
    elif any(kw in name_lower for kw in ("bus failure", "总线故障", "short")):
        sw_action = "记录总线故障事件；重新进入 Normal 模式或通过 Pwon 清除"
    elif any(kw in name_lower for kw in ("local failure", "本地故障")):
        sw_action = "在 Listen-only 模式轮询 ERR_N 获取故障类型；确认恢复后重新进入 Normal"
    elif any(kw in name_lower for kw in ("overtemp", "thermal", "tsd", "过温", "热")):
        sw_action = "记录过温事件；暂停高负载操作；等待降温后清除 Local failure 标志"
    elif any(kw in name_lower for kw in ("txd", "dominant", "显性", "timeout", "超时")):
        sw_action = "记录 TXD 异常事件；检查 MCU 端 GPIO 状态；清除 Local failure 标志恢复"
    elif any(kw in name_lower for kw in ("ocp", "overcurrent", "过流")):
        sw_action = "记录过流事件并累计次数；连续过流则上报；锁存模式需执行软件复位序列"
    elif any(kw in name_lower for kw in ("cpuv", "charge pump", "电荷泵")):
        sw_action = "记录故障事件；检查外部电容是否异常"
    elif "indicator" in name_lower or "指示" in name_lower:
        sw_action = "正常电流调节行为非故障；频繁触发则表明负载过大或堵转"
    else:
        sw_action = "记录故障事件；根据恢复类型执行对应清除或上报操作"

    return (
        f"| {name} | {fault_class} | {trigger} | {detection} | {confirmation} "
        f"| {chip_behavior} | {recovery} | {sw_action} |"
    )


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    haystack = text.lower()
    return any(needle.lower() in haystack for needle in needles)


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
