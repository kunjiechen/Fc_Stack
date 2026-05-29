"""Chip-view extraction engine — deterministically extracts structured chip data
from a parsed datasheet Markdown document and generates the two chip-view files:

- ``<FC>_芯片架构输入.md``  (architecture view)
- ``<FC>_芯片详细设计输入.md``  (detailed-design view)

The extractor works with the structured output of `.parser.MarkdownStructureParser`
and does NOT rely on an LLM to produce the files.  Sections that cannot be
reliably auto-extracted are rendered with ``<!-- LLM_SUPPLEMENT -->`` markers so
the downstream skill can fill them in.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from .parser import DocumentChunk, ParsedDocument


# ---------------------------------------------------------------------------
# Lightweight in-memory models for extracted chip data
# ---------------------------------------------------------------------------

@dataclass
class ChipIdentity:
    model: str = ""
    manufacturer: str = ""
    doc_version: str = ""
    summary_cn: str = ""
    comm_interface: str = ""
    comm_max_rate: str = ""
    safety_level: str = "手册未说明"


@dataclass
class ChipPin:
    name: str = ""
    direction_mcu: str = ""
    function_cn: str = ""
    active_level: str = "—"
    pull: str = "手册未说明"
    required: str = "按需"


@dataclass
class ChipMode:
    name: str = ""
    entry: str = ""
    exit: str = ""
    available_functions: str = ""
    power_on_default: str = "—"


@dataclass
class RegisterOverview:
    name: str = ""
    address: str = ""
    width: str = "8"
    access: str = "R/W"
    category: str = ""
    summary_cn: str = ""


@dataclass
class RegisterBitField:
    bit: str = ""
    field_name: str = ""
    mask_hex: str = ""
    shift: str = ""
    access: str = "R/W"
    reset_hex: str = ""
    semantics_cn: str = ""
    enum_values: str = ""
    constraints: str = ""


@dataclass
class RegisterDetail:
    name: str = ""
    address: str = ""
    bit_fields: list[RegisterBitField] = field(default_factory=list)
    read_side_effect: str = "无"
    rmw_required: str = "否"
    reserved_write_policy: str = "忽略"
    write_wait_time: str = "0"
    mode_access_limit: str = "无"


@dataclass
class FrameProtocol:
    bit_width: str = ""
    cmd_structure: str = ""
    resp_structure: str = ""
    address_space: str = ""
    burst_read: str = "手册未说明"
    burst_write: str = "手册未说明"
    crc: str = "无"
    cs_min_high: str = ""
    extra: dict[str, str] = field(default_factory=dict)


@dataclass
class InterruptSource:
    name: str = ""
    trigger: str = ""
    flag_bit: str = ""
    clear_method: str = ""
    maskable: str = ""


@dataclass
class ClockReset:
    clock_source: str = ""
    reset_sources: str = ""
    reset_scope: str = ""
    default_mode_after_reset: str = ""
    reset_recovery_time: str = ""


@dataclass
class StateTransition:
    current: str = ""
    next: str = ""
    trigger: str = ""
    detect_method: str = ""
    delay: str = ""


@dataclass
class FaultSource:
    name: str = ""
    fault_type: str = ""
    hw_trigger: str = ""
    observable_flag: str = ""
    hw_response: str = ""
    clear_method: str = ""
    clear_precondition: str = ""
    self_recovery: str = ""


@dataclass
class TimingParam:
    symbol: str = ""
    meaning_cn: str = ""
    typical: str = ""
    min_val: str = ""
    max_val: str = ""
    unit: str = ""
    usage: str = ""


@dataclass
class InitStep:
    seq: str = ""
    operation: str = ""
    precondition: str = ""
    success_criteria: str = ""
    wait_time: str = ""
    expected_readback: str = ""
    retry_limit: str = ""
    failure_behavior: str = ""


@dataclass
class DataAssembly:
    logical_name: str = ""
    source_registers: str = ""
    bit_segments: str = ""
    total_width: str = ""
    signed: str = "无符号"
    sign_bit_pos: str = ""
    order_constraint: str = ""


@dataclass
class CommandEncoding:
    cmd_byte_hex: str = ""
    bit_segments: str = ""
    target_register: str = ""
    operation: str = ""


@dataclass
class CrossRegisterConstraint:
    item: str = ""
    description: str = ""
    update_order: str = ""
    burst_boundary: str = ""


# ---------------------------------------------------------------------------
# Extraction engine
# ---------------------------------------------------------------------------

class ChipViewExtractor:
    """Extract chip architecture and detailed-design views from a parsed datasheet.

    The extractor scans structured markdown tables and headings and populates
    the two output files deterministically.  Sections that cannot be filled are
    emitted with ``<!-- LLM_SUPPLEMENT -->`` markers.
    """

    def __init__(self, module: str):
        self.module = module

    # ---- public API ---------------------------------------------------------

    def extract(
        self,
        parsed: ParsedDocument,
        *,
        doc: str = "",
        manufacturer: str = "",
        doc_version: str = "",
    ) -> tuple[str, str]:
        """Return (arch_md, design_md) strings for the two chip-view files."""
        chunks = parsed.chunks

        identity = self._extract_identity(chunks, doc, manufacturer, doc_version)
        pins = self._extract_pins(chunks)
        modes = self._extract_modes(chunks)
        registers = self._extract_register_overview(chunks)
        protocol = self._extract_frame_protocol(chunks)
        interrupts = self._extract_interrupts(chunks)
        clock_reset = self._extract_clock_reset(chunks)

        reg_details = self._extract_register_details(chunks, registers)
        transitions = self._extract_state_transitions(chunks)
        faults = self._extract_fault_sources(chunks)
        timing_params = self._extract_timing_params(chunks)
        init_steps = self._extract_init_steps(chunks)
        data_assembly = self._extract_data_assembly(chunks, registers)
        cmd_encoding = self._extract_command_encoding(chunks, protocol)
        cross_register = self._extract_cross_register(chunks)

        arch_md = self._render_architecture_view(
            identity, pins, modes, registers, protocol, interrupts, clock_reset,
        )
        design_md = self._render_design_view(
            identity, reg_details, transitions, faults, timing_params,
            init_steps, data_assembly, cmd_encoding, cross_register,
        )
        return arch_md, design_md

    # ---- identity -----------------------------------------------------------

    def _extract_identity(
        self, chunks: list[DocumentChunk], doc: str, manufacturer: str, doc_version: str,
    ) -> ChipIdentity:
        identity = ChipIdentity(manufacturer=manufacturer, doc_version=doc_version)

        # Extract model from filename
        # e.g. "Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN"
        if doc:
            stem = Path(doc).stem
            # Try to find part number pattern in the filename
            part_match = re.search(r'([A-Z]+\d+[A-Z]?(?:-[A-Z]+\d*)?)', stem, re.IGNORECASE)
            if part_match:
                identity.model = part_match.group(1)
            else:
                identity.model = stem.split("_")[0] if "_" in stem else stem
            # Try doc version from filename
            ver_match = re.search(r'Rev\s*(\d+[\.\d]*)', stem, re.IGNORECASE)
            if ver_match and not doc_version:
                identity.doc_version = f"Rev {ver_match.group(1)}"

        # Find the first substantive heading (skip TOC, INDEX, page markers)
        skip_headings = {"index", "table of contents", "toc", "revision history",
                         "product overview", "applications", "device information"}
        for chunk in chunks:
            if not chunk.heading_path:
                continue
            h0 = self._clean_html(chunk.heading_path[0]).strip().lower()
            # Skip table-of-contents style headings
            if any(skip in h0 for skip in skip_headings):
                # Still check for device info tables
                text_lower = chunk.text.lower()
                if "part number" in text_lower or "device information" in text_lower:
                    for block in chunk.blocks:
                        rows = block.metadata.get("rows", [])
                        for row in rows:
                            row_text = " ".join(self._clean_html(c) for c in row).lower()
                            if "part number" in row_text or "型号" in row_text:
                                if len(row) >= 2:
                                    identity.model = self._clean_html(row[1])
                continue
            if h0 and h0 not in ("", "revision history"):
                if not identity.summary_cn:
                    # First real heading is the document title
                    clean = self._clean_html(chunk.heading_path[0]).strip()
                    if len(clean) <= 100 and not clean.startswith("{"):
                        identity.summary_cn = clean[:50]
                break

        # Scan for communication interface from key features or description
        full_text = " ".join(self._clean_html(chunk.text).lower() for chunk in chunks)
        if "i2c" in full_text or "i²c" in full_text:
            identity.comm_interface = "I2C"
        if "spi" in full_text:
            identity.comm_interface = "SPI" if not identity.comm_interface else identity.comm_interface

        # Communication rate
        if identity.comm_interface == "I2C" and ("400" in full_text or "fast" in full_text):
            if "khz" in full_text or "fast-mode" in full_text:
                identity.comm_max_rate = "400 kHz (Fast-mode)"
        elif identity.comm_interface == "SPI":
            m = re.search(r"(\d+(?:\.\d+)?)\s*mhz", full_text)
            if m:
                identity.comm_max_rate = f"{m.group(1)} MHz"

        # Safety level
        asil_match = re.search(r"asil[\s-]*([abcd])", full_text, re.IGNORECASE)
        if asil_match:
            identity.safety_level = f"ASIL-{asil_match.group(1).upper()}"

        # Scan for manufacturer from title or filename
        if doc and not manufacturer:
            stem = Path(doc).stem.lower()
            for mfr in ("novosense", "ti", "texas", "infineon", "nxp", "stmicro", "microchip", "analog"):
                if mfr in stem:
                    identity.manufacturer = mfr.capitalize()
                    break

        return identity

    # ---- pins ---------------------------------------------------------------

    def _extract_pins(self, chunks: list[DocumentChunk]) -> list[ChipPin]:
        pins: list[ChipPin] = []
        seen: set[str] = set()
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            # Match headings containing "pin" (including numbered: "1. pin configuration")
            if not any(kw in heading for kw in ("pin", "引脚")):
                continue
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                # Clean HTML from header cells
                header = [self._clean_html(c).lower().strip() for c in rows[0]]
                # Try to map columns
                col_map = self._map_columns(header, {
                    "name": ("symbol", "pin name", "pin", "name", "引脚名"),
                    "pin_no": ("pin no.", "pin number", "#", "no."),
                    "function": ("function", "description", "功能", "说明"),
                    "type": ("type", "i/o", "direction"),
                })
                name_idx = col_map["name"]
                func_idx = col_map["function"]
                if name_idx < 0 or func_idx < 0:
                    continue
                for row in self._data_rows(rows):
                    if not row or all(c.strip() in ("", "-", "—") for c in row):
                        continue
                    name = self._clean_html(self._cell(row, name_idx))
                    func = self._clean_html(self._cell(row, func_idx))
                    if not name or name in seen:
                        continue
                    seen.add(name)
                    pin = ChipPin(name=name, function_cn=func)
                    # Infer direction
                    func_lower = func.lower()
                    name_lower = name.lower()
                    if any(kw in name_lower for kw in ("vdd", "vss", "vcc", "gnd", "ground")):
                        pin.direction_mcu = "Power"
                        pin.required = "必须"
                    elif any(kw in func_lower for kw in ("supply", "ground", "电源", "地")):
                        pin.direction_mcu = "Power"
                        pin.required = "必须"
                    elif any(kw in name_lower for kw in ("sda",)):
                        pin.direction_mcu = "Bidir"
                        pin.pull = "无，需外部上拉" if "pull" in func_lower else "手册未说明"
                        pin.required = "必须"
                    elif any(kw in name_lower for kw in ("scl",)):
                        pin.direction_mcu = "Input"
                        pin.required = "必须"
                        pin.pull = "无，需外部上拉" if "pull" in func_lower else "手册未说明"
                    elif any(kw in name_lower for kw in ("int", "nint")):
                        pin.direction_mcu = "Output"
                        pin.active_level = "Low有效"
                        pin.pull = "无，需外部上拉"
                    elif any(kw in name_lower for kw in ("reset", "nrst", "rst")):
                        pin.direction_mcu = "Input"
                        pin.active_level = "Low有效"
                        pin.pull = "无，需外部上拉" if "pull" in func_lower else "手册未说明"
                        pin.required = "必须"
                    elif "input" in func_lower and "output" in func_lower:
                        pin.direction_mcu = "Bidir"
                    elif "input" in func_lower:
                        pin.direction_mcu = "Input"
                    elif "output" in func_lower:
                        pin.direction_mcu = "Output"
                    elif "address input" in func_lower:
                        pin.direction_mcu = "Input"
                        pin.required = "必须"
                    else:
                        pin.direction_mcu = "Bidir"

                    # Active level
                    if pin.active_level == "—":
                        if "active-low" in func_lower or "active low" in func_lower or "低有效" in func:
                            pin.active_level = "Low有效"
                        elif "active-high" in func_lower or "active high" in func_lower:
                            pin.active_level = "High有效"

                    # Pull
                    if "pull-up" in func_lower or "pull up" in func_lower:
                        pin.pull = "内部Pull-up"
                    elif "pull-down" in func_lower or "pull down" in func_lower:
                        pin.pull = "内部Pull-down"
                    elif pin.pull == "手册未说明" and ("open-drain" in func_lower or "open drain" in func_lower):
                        pin.pull = "无，需外部上拉"

                    pins.append(pin)
        return pins

    # ---- modes --------------------------------------------------------------

    def _extract_modes(self, chunks: list[DocumentChunk]) -> list[ChipMode]:
        modes: list[ChipMode] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if not any(kw in heading for kw in ("mode", "operating mode", "functional mode", "工作模式")):
                continue
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                header = [c.lower().strip() for c in rows[0]]
                col_map = self._map_columns(header, {
                    "name": ("mode", "mode name", "模式", "状态"),
                    "entry": ("entry", "进入", "进入方式"),
                    "exit": ("exit", "退出", "退出方式"),
                    "functions": ("available", "functions", "可用功能"),
                })
                if col_map["name"] >= 0:
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        modes.append(ChipMode(
                            name=self._cell(row, col_map.get("name", 0)),
                            entry=self._cell(row, col_map.get("entry", 1)),
                            exit=self._cell(row, col_map.get("exit", 2)),
                            available_functions=self._cell(row, col_map.get("functions", 3)),
                        ))
        return modes

    # ---- register overview --------------------------------------------------

    def _extract_register_overview(self, chunks: list[DocumentChunk]) -> list[RegisterOverview]:
        registers: list[RegisterOverview] = []
        seen_names: set[str] = set()

        # ---- Phase 1: Extract from register description headings ----
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if not any(kw in heading for kw in ("register", "寄存器")):
                continue
            h_text = self._clean_html(" ".join(chunk.heading_path))
            reg_match = re.search(r'registers?\s+(\d+)\s*(?:and|&)\s*(\d+)\s*:\s*(.+)', h_text, re.IGNORECASE)
            if reg_match:
                addr1 = f"0x{int(reg_match.group(1)):02X}"
                addr2 = f"0x{int(reg_match.group(2)):02X}"
                desc = reg_match.group(3).strip()
                for addr, suffix in [(addr1, "0"), (addr2, "1")]:
                    rname = f"{desc} {suffix}"
                    if rname.lower() not in seen_names:
                        seen_names.add(rname.lower())
                        registers.append(RegisterOverview(
                            name=rname, address=addr, width="8",
                            category=self._infer_register_category(rname),
                            summary_cn=desc,
                        ))
            else:
                reg_match = re.search(r'registers?\s+(\d+)\s*:\s*(.+)', h_text, re.IGNORECASE)
                if reg_match:
                    addr = f"0x{int(reg_match.group(1)):02X}"
                    desc = reg_match.group(2).strip()
                    if desc.lower() not in seen_names:
                        seen_names.add(desc.lower())
                        registers.append(RegisterOverview(
                            name=desc, address=addr, width="8",
                            category=self._infer_register_category(desc),
                            summary_cn=desc,
                        ))

        # ---- Phase 2: Supplement with table-based extraction ----
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            # Match register map, register description, control register, command byte sections
            if not any(kw in heading for kw in ("register", "寄存器", "command byte", "control register")):
                continue
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                header = [self._clean_html(c).lower().strip() for c in rows[0]]

                # Try standard register map column mapping
                col_map = self._map_columns(header, {
                    "name": ("register", "register name", "name", "寄存器", "寄存器名", "target register"),
                    "address": ("address", "addr", "地址", "offset"),
                    "width": ("width", "bits", "位宽", "size"),
                    "access": ("access", "r/w", "访问", "type", "operation"),
                    "category": ("category", "function", "分类", "功能分类"),
                    "summary": ("description", "function", "功能", "说明"),
                })
                if col_map["name"] >= 0 and col_map["address"] >= 0:
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        name = self._cell(row, col_map.get("name", 0))
                        if not name or name.lower() in ("reserved", ""):
                            continue
                        if name.lower() in seen_names:
                            continue
                        seen_names.add(name.lower())
                        addr = self._cell(row, col_map.get("address", 1))
                        registers.append(RegisterOverview(
                            name=name,
                            address=addr,
                            width=self._cell(row, col_map.get("width", 2), "8"),
                            access=self._cell(row, col_map.get("access", 3), "R/W"),
                            category=self._infer_register_category(name),
                            summary_cn=self._cell(row, col_map.get("summary", 5)),
                        ))

        return registers

    # ---- register details (D1) ----------------------------------------------

    def _extract_register_details(
        self, chunks: list[DocumentChunk], reg_overview: list[RegisterOverview],
    ) -> list[RegisterDetail]:
        addr_map = {r.address.lower().replace("0x", ""): r for r in reg_overview}
        name_map = {r.name.lower(): r for r in reg_overview}
        details: list[RegisterDetail] = []

        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            # Look for register description sections
            if not any(kw in heading for kw in ("register", "寄存器")):
                continue
            # Only process sections that describe individual registers
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                header = [c.lower().strip() for c in rows[0]]
                # Check if this is a bit-field table
                bit_col_map = self._map_columns(header, {
                    "bit": ("bit", "bits", "位"),
                    "field_name": ("name", "field", "field name", "位段", "位段名", "bit name"),
                    "access": ("access", "r/w", "type", "访问"),
                    "reset": ("reset", "default", "复位值", "复位"),
                    "semantics": ("description", "function", "功能", "说明", "功能语义"),
                })
                if bit_col_map["bit"] >= 0 and bit_col_map["field_name"] >= 0:
                    # Try to associate with a register from the heading
                    reg_name = ""
                    for r in reg_overview:
                        if r.name.lower() in heading:
                            reg_name = r.name
                            break
                    if not reg_name and chunk.heading_path:
                        for r in reg_overview:
                            if r.name.lower() in heading.replace("register", "").replace("registers", ""):
                                reg_name = r.name
                                break
                    if not reg_name:
                        # Fallback: use the last heading element as register name hint
                        reg_name = chunk.heading_path[-1] if chunk.heading_path else ""

                    bit_fields: list[RegisterBitField] = []
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        bit_str = self._cell(row, bit_col_map.get("bit", 0))
                        field_name = self._cell(row, bit_col_map.get("field_name", 1))
                        if not bit_str or not field_name:
                            continue
                        shift = self._compute_shift(bit_str)
                        mask = self._compute_mask(bit_str)
                        reset_val = self._cell(row, bit_col_map.get("reset", 3), "")
                        semantics = self._cell(row, bit_col_map.get("semantics", 4))
                        access = self._cell(row, bit_col_map.get("access", 2), "R/W")
                        bit_fields.append(RegisterBitField(
                            bit=bit_str,
                            field_name=field_name,
                            mask_hex=mask,
                            shift=shift,
                            access=access,
                            reset_hex=reset_val if reset_val else "手册未说明",
                            semantics_cn=semantics,
                        ))
                    if bit_fields:
                        # Find register overview for address
                        addr = ""
                        for r in reg_overview:
                            if r.name.lower() in reg_name.lower() or reg_name.lower() in r.name.lower():
                                addr = r.address
                                reg_name = r.name
                                break
                        details.append(RegisterDetail(
                            name=reg_name, address=addr, bit_fields=bit_fields,
                        ))
        return details

    # ---- frame protocol (A5) ------------------------------------------------

    def _extract_frame_protocol(self, chunks: list[DocumentChunk]) -> FrameProtocol:
        proto = FrameProtocol()
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            text = chunk.text.lower()
            if any(kw in heading for kw in ("i2c", "i²c", "iic", "interface", "通信", "接口")):
                if "i2c" in heading or "i²c" in heading or "iic" in heading:
                    proto.bit_width = "8 bit"
                    proto.cmd_structure = "器件地址(7bit) + R/W(1bit) + 命令字节(8bit)"
                    proto.resp_structure = "ACK后紧跟数据字节(8bit)，MSB优先"
                    proto.crc = "无"
                elif "spi" in heading:
                    proto.bit_width = "手册未说明"
                    proto.crc = "无"

            # Look for burst and address space info
            if "burst" in text or "address" in text:
                if "burst read" in text or "连续读" in text:
                    proto.burst_read = "支持"
                if "burst write" in text or "连续写" in text:
                    proto.burst_write = "支持"

            # Extract address space from register address range
            # This is handled later from register overview

            # Device address from address tables
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                for row in rows:
                    row_text = " ".join(str(c) for c in row).lower()
                    if "device address" in row_text or "器件地址" in row_text:
                        proto.extra["device_address"] = " ".join(str(c) for c in row)

        return proto

    # ---- interrupts (A6) ----------------------------------------------------

    def _extract_interrupts(self, chunks: list[DocumentChunk]) -> list[InterruptSource]:
        interrupts: list[InterruptSource] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if not any(kw in heading for kw in ("interrupt", "中断", "int")):
                continue
            # Parse interrupt description tables or text
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                header = [c.lower().strip() for c in rows[0]]
                col_map = self._map_columns(header, {
                    "name": ("source", "interrupt", "中断源", "name"),
                    "trigger": ("trigger", "condition", "触发", "触发条件"),
                    "flag": ("flag", "标志", "标志位"),
                    "clear": ("clear", "清除", "清除机制"),
                    "mask": ("mask", "maskable", "可屏蔽", "屏蔽"),
                })
                if col_map["name"] >= 0:
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        interrupts.append(InterruptSource(
                            name=self._cell(row, col_map.get("name", 0)),
                            trigger=self._cell(row, col_map.get("trigger", 1)),
                            flag_bit=self._cell(row, col_map.get("flag", 2)),
                            clear_method=self._cell(row, col_map.get("clear", 3)),
                            maskable=self._cell(row, col_map.get("mask", 4)),
                        ))
        return interrupts

    # ---- clock & reset (A7) -------------------------------------------------

    def _extract_clock_reset(self, chunks: list[DocumentChunk]) -> ClockReset:
        cr = ClockReset()
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            text = chunk.text.lower()
            if any(kw in heading for kw in ("clock", "osc", "时钟", "reset", "复位", "por", "power-on")):
                if "i2c" in text or "scl" in text:
                    cr.clock_source = "I2C总线时钟(SCL)，由主控提供"
                elif "spi" in text or "sck" in text:
                    cr.clock_source = "SPI总线时钟(SCK)，由主控提供"
                elif "internal osc" in text or "内部振荡" in text:
                    cr.clock_source = "内部OSC"
                if "por" in text or "power-on reset" in text or "上电复位" in text:
                    cr.reset_sources = "POR (内部上电复位)"
                if "reset" in heading and "pin" in text:
                    if "reset" not in cr.reset_sources:
                        cr.reset_sources += (", " if cr.reset_sources else "") + "RESET 引脚(外部低有效)"
                if "全量" in text or "all register" in text:
                    cr.reset_scope = "全量复位：所有寄存器恢复默认值，状态机初始化"
                if "恢复" in text and ("ns" in text or "us" in text or "ms" in text):
                    m = re.search(r"(\d+(?:\.\d+)?)\s*(ns|us|ms|µs)", text)
                    if m:
                        cr.reset_recovery_time = f">= {m.group(1)} {m.group(2)}"
        return cr

    # ---- timing parameters (D4) ---------------------------------------------

    def _extract_timing_params(self, chunks: list[DocumentChunk]) -> list[TimingParam]:
        params: list[TimingParam] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if not any(kw in heading for kw in ("timing", "dynamic", "时序", "ac character", "electrical character", "dynamic character")):
                continue
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                header = [self._clean_html(c).lower().strip() for c in rows[0]]
                col_map = self._map_columns(header, {
                    "symbol": ("symbol", "parameter", "参数", "parameters", "符号"),
                    "min": ("min", "min.", "最小值", "standard-mode", "fast-mode"),
                    "typ": ("typ", "typ.", "典型值"),
                    "max": ("max", "max.", "最大值"),
                    "unit": ("unit", "单位", "units"),
                    "meaning": ("parameter", "parameters", "含义", "description"),
                })
                if col_map["symbol"] >= 0 and (col_map["min"] >= 0 or col_map["max"] >= 0):
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        symbol = self._cell(row, col_map.get("symbol", 0))
                        if not symbol or symbol.lower() in ("parameters", "parameter", "supplies"):
                            continue
                        if re.match(r'^[-–—=|]+$', symbol):
                            continue  # Skip separator rows
                        # Clean HTML from symbol
                        symbol = self._clean_html(symbol)
                        params.append(TimingParam(
                            symbol=symbol,
                            meaning_cn=self._cell(row, col_map.get("meaning", 0) if col_map.get("meaning", 0) != col_map.get("symbol", 0) else 0),
                            min_val=self._cell(row, col_map.get("min", 1)),
                            typical=self._cell(row, col_map.get("typ", 2)),
                            max_val=self._cell(row, col_map.get("max", 3)),
                            unit=self._cell(row, col_map.get("unit", 4)),
                        ))
        return params

    # ---- state transitions (D2) ---------------------------------------------

    def _extract_state_transitions(self, chunks: list[DocumentChunk]) -> list[StateTransition]:
        transitions: list[StateTransition] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if "state" in heading and ("transition" in heading or "转换" in heading):
                for block in chunk.blocks:
                    rows = block.metadata.get("rows", [])
                    if not rows:
                        continue
                    header = [c.lower().strip() for c in rows[0]]
                    col_map = self._map_columns(header, {
                        "current": ("current", "当前状态", "from"),
                        "next": ("next", "下一状态", "to"),
                        "trigger": ("trigger", "触发", "触发条件", "condition"),
                        "detect": ("detect", "判定", "判定方式"),
                        "delay": ("delay", "延迟", "转换延迟"),
                    })
                    if col_map["current"] >= 0 and col_map["next"] >= 0:
                        for row in self._data_rows(rows):
                            if not row or all(c.strip() in ("", "-", "—") for c in row):
                                continue
                            transitions.append(StateTransition(
                                current=self._cell(row, col_map.get("current", 0)),
                                next=self._cell(row, col_map.get("next", 1)),
                                trigger=self._cell(row, col_map.get("trigger", 2)),
                                detect_method=self._cell(row, col_map.get("detect", 3)),
                                delay=self._cell(row, col_map.get("delay", 4)),
                            ))
        return transitions

    # ---- fault sources (D3) -------------------------------------------------

    def _extract_fault_sources(self, chunks: list[DocumentChunk]) -> list[FaultSource]:
        faults: list[FaultSource] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if any(kw in heading for kw in ("fault", "error", "diagnostic", "故障", "诊断")):
                for block in chunk.blocks:
                    rows = block.metadata.get("rows", [])
                    if not rows:
                        continue
                    header = [c.lower().strip() for c in rows[0]]
                    col_map = self._map_columns(header, {
                        "name": ("fault", "fault name", "故障名", "name", "error"),
                        "type_cls": ("type", "fault type", "故障类型", "类型"),
                        "trigger": ("trigger", "触发条件", "condition"),
                        "flag": ("flag", "标志位", "indicator"),
                        "response": ("response", "动作", "响应"),
                        "clear": ("clear", "清除", "清除方式"),
                        "precondition": ("precondition", "前置条件", "清除前置条件"),
                        "self_recovery": ("recovery", "自恢复", "是否自恢复"),
                    })
                    if col_map["name"] >= 0 and col_map["trigger"] >= 0:
                        for row in self._data_rows(rows):
                            if not row or all(c.strip() in ("", "-", "—") for c in row):
                                continue
                            faults.append(FaultSource(
                                name=self._cell(row, col_map.get("name", 0)),
                                fault_type=self._cell(row, col_map.get("type_cls", 1)),
                                hw_trigger=self._cell(row, col_map.get("trigger", 2)),
                                observable_flag=self._cell(row, col_map.get("flag", 3)),
                                hw_response=self._cell(row, col_map.get("response", 4)),
                                clear_method=self._cell(row, col_map.get("clear", 5)),
                                clear_precondition=self._cell(row, col_map.get("precondition", 6)),
                                self_recovery=self._cell(row, col_map.get("self_recovery", 7)),
                            ))
        return faults

    # ---- init steps (D5) ----------------------------------------------------

    def _extract_init_steps(self, chunks: list[DocumentChunk]) -> list[InitStep]:
        return []  # Rarely available as structured tables in datasheets

    # ---- data assembly (D6) -------------------------------------------------

    def _extract_data_assembly(
        self, chunks: list[DocumentChunk], reg_overview: list[RegisterOverview],
    ) -> list[DataAssembly]:
        return []  # Requires semantic understanding of register pairs

    # ---- command encoding (D7) ----------------------------------------------

    def _extract_command_encoding(
        self, chunks: list[DocumentChunk], protocol: FrameProtocol,
    ) -> tuple[list[dict[str, str]], list[CommandEncoding]]:
        addr_table: list[dict[str, str]] = []
        cmd_bytes: list[CommandEncoding] = []
        for chunk in chunks:
            heading = " ".join(chunk.heading_path).lower()
            if not any(kw in heading for kw in ("address", "command", "地址", "命令", "device address", "control register")):
                continue
            for block in chunk.blocks:
                rows = block.metadata.get("rows", [])
                if not rows:
                    continue
                header = [c.lower().strip() for c in rows[0]]
                # Device address table
                if any("a0" in c or "a1" in c or "address" in c for c in header):
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        if len(row) >= 3:
                            addr_table.append({c: v for c, v in zip(header, row)})
                # Command byte table
                cmd_col_map = self._map_columns(header, {
                    "cmd_byte": ("command byte", "cmd", "命令字节", "command"),
                    "target": ("target", "register", "目标寄存器"),
                    "operation": ("operation", "操作", "r/w"),
                })
                if cmd_col_map["cmd_byte"] >= 0:
                    for row in self._data_rows(rows):
                        if not row or all(c.strip() in ("", "-", "—") for c in row):
                            continue
                        cmd_bytes.append(CommandEncoding(
                            cmd_byte_hex=self._cell(row, cmd_col_map.get("cmd_byte", 0)),
                            target_register=self._cell(row, cmd_col_map.get("target", 1)),
                            operation=self._cell(row, cmd_col_map.get("operation", 2)),
                        ))
        return addr_table, cmd_bytes

    # ---- cross-register (D8) ------------------------------------------------

    def _extract_cross_register(self, chunks: list[DocumentChunk]) -> list[CrossRegisterConstraint]:
        return []  # Requires semantic understanding

    # ---- helpers ------------------------------------------------------------

    @staticmethod
    def _map_columns(header: list[str], candidates: dict[str, tuple[str, ...]]) -> dict[str, int]:
        """Map column names to their indices based on keyword matching.

        Always returns all keys from *candidates*; unmapped keys get ``-1``.
        """
        mapping: dict[str, int] = {key: -1 for key in candidates}
        for idx, col in enumerate(header):
            col_clean = col.strip().strip("*").strip().lower()
            for key, keywords in candidates.items():
                if mapping[key] >= 0:
                    continue
                if any(kw in col_clean for kw in keywords):
                    mapping[key] = idx
        return mapping

    @staticmethod
    def _is_separator_row(row: list[str]) -> bool:
        """Check if a row is a Markdown table separator (|---|----|)."""
        return all(re.match(r'^[\s\-:=|]*$', c) for c in row)

    @staticmethod
    def _data_rows(rows: list[list[str]]) -> list[list[str]]:
        """Return only data rows, skipping the header and separator rows."""
        if len(rows) < 2:
            return []
        result: list[list[str]] = []
        for row in rows[1:]:
            if ChipViewExtractor._is_separator_row(row):
                continue
            if not row or all(c.strip() in ("", "-", "—") for c in row):
                continue
            result.append(row)
        return result

    @staticmethod
    def _cell(row: list[str], idx: int, default: str = "") -> str:
        if idx < 0 or idx >= len(row):
            return default
        val = ChipViewExtractor._clean_html(row[idx]).strip()
        if val in ("-", "—", ""):
            return default
        return val

    @staticmethod
    def _clean_html(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def _compute_shift(bit_str: str) -> str:
        """e.g. '7' → '7', '6:5' → '5', '7:0' → '0'"""
        parts = bit_str.replace(" ", "").split(":")
        if len(parts) == 1:
            return parts[0]
        return parts[-1]  # lowest bit

    @staticmethod
    def _compute_mask(bit_str: str) -> str:
        """e.g. '7' → '0x80', '6:5' → '0x60', '7:0' → '0xFF'"""
        parts = bit_str.replace(" ", "").split(":")
        if len(parts) == 1:
            try:
                val = 1 << int(parts[0])
                return f"0x{val:02X}"
            except (ValueError, OverflowError):
                return ""
        try:
            hi, lo = int(parts[0]), int(parts[1])
            if hi < lo:
                hi, lo = lo, hi
            val = ((1 << (hi - lo + 1)) - 1) << lo
            return f"0x{val:02X}"
        except (ValueError, OverflowError):
            return ""

    @staticmethod
    def _infer_register_category(name: str) -> str:
        name_lower = name.lower()
        if any(kw in name_lower for kw in ("input", "输入")):
            return "数据"
        if any(kw in name_lower for kw in ("output", "输出")):
            return "数据"
        if any(kw in name_lower for kw in ("config", "配置", "direction", "方向")):
            return "配置"
        if any(kw in name_lower for kw in ("polarity", "极性", "inversion", "反转")):
            return "配置"
        if any(kw in name_lower for kw in ("control", "控制", "cmd", "command")):
            return "控制"
        if any(kw in name_lower for kw in ("status", "状态", "fault", "diag")):
            return "状态"
        if any(kw in name_lower for kw in ("id", "身份", "device id", "chip id", "version")):
            return "身份"
        return "配置"

    # ---- renderers ----------------------------------------------------------

    def _render_architecture_view(
        self,
        identity: ChipIdentity,
        pins: list[ChipPin],
        modes: list[ChipMode],
        registers: list[RegisterOverview],
        protocol: FrameProtocol,
        interrupts: list[InterruptSource],
        clock_reset: ClockReset,
    ) -> str:
        out: list[str] = []
        out.append(f"# {self.module} 芯片架构输入")
        out.append("")
        out.append("> 本文档从芯片手册提取，服务于架构生成阶段。只描述\"芯片提供了什么资源，资源长什么样\"，不做分类、分组、归并等架构决策。")
        out.append("")

        # A1
        out.append("## A1. 模块身份")
        out.append("")
        out.append("| 字段 | 值 |")
        out.append("|------|-----|")
        out.append(f"| 芯片型号 | {identity.model or '手册未说明'} |")
        out.append(f"| 制造商 | {identity.manufacturer or '手册未说明'} |")
        out.append(f"| 数据手册版本 | {identity.doc_version or '手册未说明'} |")
        out.append(f"| 功能一句话 | {identity.summary_cn or '手册未说明'} |")
        out.append(f"| 通信接口类型 | {identity.comm_interface or '手册未说明'} |")
        out.append(f"| 通信接口最大速率 | {identity.comm_max_rate or '手册未说明'} |")
        out.append(f"| 功能安全等级 | {identity.safety_level} |")
        out.append("")

        # A2
        out.append("## A2. 引脚清单")
        out.append("")
        if pins:
            out.append("| 引脚名 | 方向(Mcu视角) | 功能 | 有效电平 | 内部上下拉 | 是否必须连接 |")
            out.append("|--------|--------------|------|---------|-----------|-------------|")
            for p in pins:
                out.append(f"| {p.name} | {p.direction_mcu} | {p.function_cn} | {p.active_level} | {p.pull} | {p.required} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的引脚定义表格 -->")
        out.append("")

        # A3
        out.append("## A3. 工作模式")
        out.append("")
        if modes:
            out.append("| 模式名 | 进入方式 | 退出方式 | 该模式下可用功能 | 上电默认 |")
            out.append("|--------|---------|---------|----------------|---------|")
            for m in modes:
                out.append(f"| {m.name} | {m.entry} | {m.exit} | {m.available_functions} | {m.power_on_default} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的模式定义表格。请从手册中提取工作模式信息。 -->")
        out.append("")

        # A4
        out.append("## A4. 寄存器空间概览")
        out.append("")
        if registers:
            out.append("| 寄存器名 | 地址 | 位宽 | 访问属性 | 功能分类 | 一句话功能 |")
            out.append("|----------|------|------|---------|---------|-----------|")
            for r in registers:
                out.append(f"| {r.name} | {r.address} | {r.width} | {r.access} | {r.category} | {r.summary_cn} |")
            out.append("")
            out.append("### 寄存器分类统计表")
            out.append("")
            cats: dict[str, list[str]] = {}
            for r in registers:
                cats.setdefault(r.category, []).append(r.name)
            out.append("| 功能分类 | 寄存器数量 | 寄存器列表 |")
            out.append("|----------|-----------|-----------|")
            for cat, names in cats.items():
                out.append(f"| {cat} | {len(names)} | {', '.join(names)} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的寄存器定义表格 -->")
        out.append("")

        # A5
        out.append("## A5. 通信帧协议")
        out.append("")
        out.append("| 字段 | 值 |")
        out.append("|------|-----|")
        out.append(f"| 帧位宽 | {protocol.bit_width or '手册未说明'} |")
        out.append(f"| 命令结构 | {protocol.cmd_structure or '手册未说明'} |")
        out.append(f"| 响应结构 | {protocol.resp_structure or '手册未说明'} |")
        out.append(f"| 地址空间范围 | {protocol.address_space or '手册未说明'} |")
        out.append(f"| Burst Read | {protocol.burst_read} |")
        out.append(f"| Burst Write | {protocol.burst_write} |")
        out.append(f"| CRC | {protocol.crc} |")
        out.append(f"| 帧间最小间隔 | {protocol.cs_min_high or '手册未说明'} |")
        for k, v in protocol.extra.items():
            out.append(f"| {k} | {v} |")
        out.append("")

        # A6
        out.append("## A6. 中断资源")
        out.append("")
        if interrupts:
            out.append("| 中断源名 | 触发条件 | 标志位 | 清除机制 | 是否可屏蔽 |")
            out.append("|----------|---------|--------|---------|-----------|")
            for irq in interrupts:
                out.append(f"| {irq.name} | {irq.trigger} | {irq.flag_bit} | {irq.clear_method} | {irq.maskable} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的中断定义表格 -->")
        out.append("")

        # A7
        out.append("## A7. 时钟与复位")
        out.append("")
        out.append("| 字段 | 值 |")
        out.append("|------|-----|")
        out.append(f"| 时钟源 | {clock_reset.clock_source or '手册未说明'} |")
        out.append(f"| 复位源列表 | {clock_reset.reset_sources or '手册未说明'} |")
        out.append(f"| 各复位源影响范围 | {clock_reset.reset_scope or '手册未说明'} |")
        out.append(f"| 复位后默认模式 | {clock_reset.default_mode_after_reset or '手册未说明'} |")
        out.append(f"| 复位恢复时间 | {clock_reset.reset_recovery_time or '手册未说明'} |")
        out.append("")

        return "\n".join(out)

    def _render_design_view(
        self,
        identity: ChipIdentity,
        reg_details: list[RegisterDetail],
        transitions: list[StateTransition],
        faults: list[FaultSource],
        timing_params: list[TimingParam],
        init_steps: list[InitStep],
        data_assembly: list[DataAssembly],
        cmd_encoding: tuple[list[dict[str, str]], list[CommandEncoding]],
        cross_register: list[CrossRegisterConstraint],
    ) -> str:
        addr_table, cmd_bytes = cmd_encoding
        out: list[str] = []
        out.append(f"# {self.module} 芯片详细设计输入")
        out.append("")
        out.append(f"> 本文档从芯片手册提取，服务于详细设计 + 代码生成阶段。在架构视图基础上追加：寄存器行为语义与精确常量、状态转换条件、故障源行为、操作时序参数、初始化约束、数据组装规则、命令/响应编码和跨寄存器关系。不含 `#define` 宏名、C 变量名或代码片段。")
        out.append("")

        # D1
        out.append("## D1. 寄存器完整行为与常量表")
        out.append("")
        out.append("> 每条 bit 同时提供行为语义和精确常量。每个寄存器后附寄存器级约束摘要。")
        out.append("")
        if reg_details:
            for rd in reg_details:
                addr_label = f" (地址 {rd.address})" if rd.address else ""
                out.append(f"### {rd.name}{addr_label}")
                out.append("")
                out.append("| bit | 位段名 | 位段掩码(hex) | 移位量 | 访问属性 | 复位值(hex) | 功能语义 | 枚举值 | 行为约束 |")
                out.append("|-----|--------|-------------|--------|---------|------------|--------|--------|---------|")
                for bf in rd.bit_fields:
                    out.append(f"| {bf.bit} | {bf.field_name} | {bf.mask_hex} | {bf.shift} | {bf.access} | {bf.reset_hex} | {bf.semantics_cn} | {bf.enum_values} | {bf.constraints} |")
                out.append("")
                out.append("**寄存器级约束**：")
                out.append("")
                out.append("| 寄存器(地址) | 读副作用 | RMW是否必须 | 保留位写策略 | 写后等待时间 | 模式访问限制 |")
                out.append("|-------------|---------|------------|------------|------------|------------|")
                out.append(f"| {rd.name}{addr_label} | {rd.read_side_effect} | {rd.rmw_required} | {rd.reserved_write_policy} | {rd.write_wait_time} | {rd.mode_access_limit} |")
                out.append("")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的 bit 段定义表格。请从寄存器说明章节逐寄存器提取 bit 段信息。 -->")
            out.append("")

        # D2
        out.append("## D2. 状态转换条件")
        out.append("")
        if transitions:
            out.append("| 当前状态 | 下一状态 | 触发条件 | 判定方式 | 转换延迟 |")
            out.append("|----------|---------|---------|---------|---------|")
            for t in transitions:
                out.append(f"| {t.current} | {t.next} | {t.trigger} | {t.detect_method} | {t.delay} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 请从芯片手册的模式/状态描述章节提取状态转换条件。 -->")
        out.append("")

        # D3
        out.append("## D3. 故障源行为")
        out.append("")
        if faults:
            out.append("| 故障名 | 故障类型 | 硬件触发条件 | 可观测标志位 | 芯片硬件自动响应动作 | 清除方式 | 清除前置条件 | 是否自恢复 |")
            out.append("|--------|---------|-------------|-------------|-------------------|---------|-------------|-----------|")
            for f in faults:
                out.append(f"| {f.name} | {f.fault_type} | {f.hw_trigger} | {f.observable_flag} | {f.hw_response} | {f.clear_method} | {f.clear_precondition} | {f.self_recovery} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 请从芯片手册的诊断/故障/中断章节提取故障源行为。 -->")
        out.append("")

        # D4
        out.append("## D4. 操作时序参数")
        out.append("")
        if timing_params:
            out.append("| 参数符号 | 含义 | 典型值 | 最小值 | 最大值 | 单位 | 用途场景 |")
            out.append("|----------|------|--------|--------|--------|------|---------|")
            for tp in timing_params:
                out.append(f"| {tp.symbol} | {tp.meaning_cn} | {tp.typical} | {tp.min_val} | {tp.max_val} | {tp.unit} | {tp.usage} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的时序参数表格 -->")
        out.append("")

        # D5
        out.append("## D5. 初始化约束")
        out.append("")
        if init_steps:
            out.append("| 序号 | 操作 | 前置条件 | 判定成功标准 | 精确等待时间 | 期望读回值(hex) | 失败重试次数上限 | 失败行为 |")
            out.append("|------|------|---------|-------------|------------|----------------|----------------|---------|")
            for s in init_steps:
                out.append(f"| {s.seq} | {s.operation} | {s.precondition} | {s.success_criteria} | {s.wait_time} | {s.expected_readback} | {s.retry_limit} | {s.failure_behavior} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 请从芯片手册的初始化/上电/POR 章节提取初始化约束。 -->")
        out.append("")

        # D6
        out.append("## D6. 读回数据组装规则")
        out.append("")
        if data_assembly:
            out.append("| 逻辑值名称 | 源寄存器 | 各寄存器取值 bit 段 | 组装后总位宽 | 有无符号 | 符号位位置 | 组装顺序约束 |")
            out.append("|-----------|---------|--------------------|------------|---------|-----------|------------|")
            for da in data_assembly:
                out.append(f"| {da.logical_name} | {da.source_registers} | {da.bit_segments} | {da.total_width} | {da.signed} | {da.sign_bit_pos} | {da.order_constraint} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 请从芯片手册的多寄存器数据读取章节提取数据组装规则。 -->")
        out.append("")

        # D7
        out.append("## D7. 命令/响应编码")
        out.append("")
        if addr_table:
            out.append("### 器件地址")
            out.append("")
            # Use keys from first row
            keys = list(addr_table[0].keys())
            out.append("| " + " | ".join(keys) + " |")
            out.append("|" + "|".join("----" for _ in keys) + "|")
            for row in addr_table:
                out.append("| " + " | ".join(str(row.get(k, "")) for k in keys) + " |")
            out.append("")
        if cmd_bytes:
            out.append("### 命令字节")
            out.append("")
            out.append("| 命令字节(hex) | 目标寄存器 | 操作 |")
            out.append("|--------------|-----------|------|")
            for cb in cmd_bytes:
                out.append(f"| {cb.cmd_byte_hex} | {cb.target_register} | {cb.operation} |")
            out.append("")
        if not addr_table and not cmd_bytes:
            out.append("<!-- LLM_SUPPLEMENT: 请从芯片手册的设备地址/命令字节章节提取命令编码。 -->")
        out.append("")

        # D8
        out.append("## D8. 跨寄存器关系")
        out.append("")
        if cross_register:
            out.append("| 约束项 | 描述 | 更新顺序要求 | Burst地址递增边界 |")
            out.append("|--------|------|-------------|-----------------|")
            for cr in cross_register:
                out.append(f"| {cr.item} | {cr.description} | {cr.update_order} | {cr.burst_boundary} |")
        else:
            out.append("<!-- LLM_SUPPLEMENT: 请从芯片手册的 Burst/多字节访问/寄存器更新顺序等章节提取跨寄存器约束。 -->")
        out.append("")

        return "\n".join(out)


# ---------------------------------------------------------------------------
# Convenience entry points
# ---------------------------------------------------------------------------

def generate_chip_views(
    parsed: ParsedDocument,
    module: str,
    output_dir: Path,
    *,
    doc: str = "",
    manufacturer: str = "",
    doc_version: str = "",
) -> tuple[Path, Path]:
    """Generate both chip-view files and return their paths.

    Returns (arch_path, design_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    extractor = ChipViewExtractor(module)
    arch_md, design_md = extractor.extract(
        parsed, doc=doc, manufacturer=manufacturer, doc_version=doc_version,
    )
    arch_path = output_dir / f"{module}_芯片架构输入.md"
    design_path = output_dir / f"{module}_芯片详细设计输入.md"
    arch_path.write_text(arch_md, encoding="utf-8")
    design_path.write_text(design_md, encoding="utf-8")
    return arch_path, design_path
