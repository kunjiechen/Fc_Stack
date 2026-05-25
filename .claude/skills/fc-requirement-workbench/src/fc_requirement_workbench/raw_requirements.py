"""Raw requirement extraction and coverage support for text/dialog/spreadsheet inputs."""

from __future__ import annotations

import csv
from datetime import date
import re
from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile
from typing import Any, Iterable

from .raw_classification import classify_raw_item
from .schema import (
    ConfigurationRequirementObject,
    CoverageReport,
    FunctionalRequirementObject,
    InterfaceRequirementObject,
    RawInputEntry,
    RawRequirementDocument,
    RawRequirementEntry,
    RequirementObject,
    SourceRef,
    StateRequirementObject,
    UnifiedRawInput,
)
from .builder import EngineeringRequirement


class RawInputLoader:
    """Normalize user dialog, txt, csv/tsv, or xlsx input into raw entries."""

    def load(
        self,
        source: str | Path,
        *,
        source_type: str = "auto",
        source_name: str | None = None,
    ) -> UnifiedRawInput:
        path = Path(source) if not isinstance(source, Path) else source
        if path.exists():
            name = source_name or path.name
            source_type = self._normalize_source_type(source_type, path.suffix)
            if source_type == "excel":
                return self._load_spreadsheet(path, source_name=name)
            text = path.read_text(encoding="utf-8")
        else:
            text = str(source)
            name = source_name or "dialog-input"
            source_type = self._normalize_source_type(source_type, "")

        entries = [
            RawInputEntry(
                raw_text=item,
                likely_category=explicit_category or _guess_category(item),
                source_ref=name,
            )
            for item, explicit_category in _split_raw_entries(text)
        ]
        hints = _extract_module_hints(text)
        return UnifiedRawInput(
            source_type=source_type,
            source_name=name,
            module_hints=hints,
            entries=entries,
        )

    def _normalize_source_type(self, source_type: str, suffix: str) -> str:
        if source_type and source_type != "auto":
            return source_type
        if suffix.lower() == ".txt":
            return "txt"
        if suffix.lower() in {".xlsx", ".csv", ".tsv"}:
            return "excel"
        return "dialog"

    def _load_spreadsheet(
        self,
        path: Path,
        *,
        source_name: str | None = None,
    ) -> UnifiedRawInput:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            sheets = [("Sheet1", _read_delimited_rows(path, delimiter=","))]
        elif suffix == ".tsv":
            sheets = [("Sheet1", _read_delimited_rows(path, delimiter="\t"))]
        elif suffix == ".xlsx":
            sheets = _read_xlsx_rows(path)
        else:
            raise ValueError(f"Unsupported spreadsheet input: {path}")

        preferred = [
            item for item in sheets if _is_input_sheet_name(item[0])
        ] or [
            item for item in sheets if _looks_like_input_sheet(item[1])
        ] or sheets

        entries: list[RawInputEntry] = []
        module_hints: dict[str, str] = {}
        for sheet_name, rows in preferred:
            if not rows:
                continue
            headers, data_rows = _tabular_headers_and_rows(rows)
            if not headers:
                headers = [f"col_{idx+1}" for idx in range(len(rows[0]))]
                data_rows = rows
            for row_index, row in enumerate(data_rows, start=2):
                structured = _structured_fields_from_row(headers, row)
                if _should_skip_structured_row(structured, row):
                    continue
                if structured.get("module_name"):
                    module_hints["module_name"] = structured["module_name"]
                    module_hints["module_abbr"] = _module_token(structured["module_name"])
                raw_text = _raw_text_from_structured_row(structured, row)
                if not raw_text:
                    continue
                entry = RawInputEntry(
                    raw_text=raw_text,
                    likely_category=_guess_category(raw_text, structured),
                    structured_fields=structured,
                    source_ref=f"{source_name or path.name}#{sheet_name}:{row_index}",
                )
                entries.append(entry)
                module_hints.update(_extract_module_hints(raw_text))

        return UnifiedRawInput(
            source_type="excel",
            source_name=source_name or path.name,
            module_hints=module_hints,
            entries=entries,
        )


class RawRequirementExtractor:
    """Extract原始开发需求文档 from normalized text input."""

    def extract(
        self,
        raw_input: UnifiedRawInput,
        *,
        module: str = "FC",
    ) -> RawRequirementDocument:
        module_name = raw_input.module_hints.get("module_name") or module
        module_abbr = _module_token(raw_input.module_hints.get("module_abbr") or module_name)
        items = {"FUNC": [], "INTF": [], "CFG": [], "NFR": []}
        counters = {"FUNC": 0, "INTF": 0, "CFG": 0, "NFR": 0}

        for entry in raw_input.entries:
            category = _normalize_category(entry.likely_category)
            counters[category] += 1
            item_id = f"RAW-{module_abbr}-{category}-{counters[category]:04d}"
            raw = _entry_from_text(
                item_id=item_id,
                category=category,
                text=entry.raw_text,
                source_ref=entry.source_ref,
                structured_fields=entry.structured_fields,
            )
            items[category].append(raw)

        return RawRequirementDocument(
            doc_id=f"RAWREQ-{module_abbr}-001",
            module_name=module_name,
            module_abbr=module_abbr,
            source=f"{raw_input.source_type}:{raw_input.source_name}",
            date=str(date.today()),
            safety_level=_extract_safety_level(raw_input),
            functional_reqs=items["FUNC"],
            interface_reqs=items["INTF"],
            config_reqs=items["CFG"],
            nfr_reqs=items["NFR"],
        )


class RawRequirementMarkdownRenderer:
    def render(self, document: RawRequirementDocument) -> str:
        lines = [
            f"# 《{document.module_abbr} 模块原始开发需求》",
            "",
            "| 项目 | 内容 |",
            "| --- | --- |",
            f"| 文档编号 | {document.doc_id} |",
            f"| 模块名称 | {document.module_name} |",
            f"| 模块简称 | {document.module_abbr} |",
            f"| 所属层级 | {document.layer} / BSW |",
            f"| 需求来源 | {document.source} |",
            f"| 适用项目/平台 | {document.project} |",
            f"| 安全等级 | {document.safety_level} |",
            f"| 原始需求状态 | {document.status} |",
            f"| 整理日期 | {document.date} |",
            "",
            "---",
            "",
            "## 1 目的",
            "",
            f"本文档用于记录 `{document.module_abbr}` 模块在正式 SRS 编写前的原始开发需求输入。原始需求允许不完整，但应尽量保留输入者原意。",
            "",
            "## 2 模块背景",
            "",
            f"`{document.module_abbr}` 模块的原始需求来自用户对话、txt 或 excel 文本输入。本文档优先记录原始诉求，后续正式 SRS 可结合手册进一步丰富。",
            "",
        ]
        lines.extend(_raw_section_markdown("3 原始功能需求", document.functional_reqs, "功能"))
        lines.extend(_raw_section_markdown("4 原始接口需求", document.interface_reqs, "接口"))
        lines.extend(_raw_section_markdown("5 原始配置需求", document.config_reqs, "配置"))
        lines.extend(_raw_section_markdown("6 原始非功能与约束需求", document.nfr_reqs, "NFR"))
        return "\n".join(lines).rstrip() + "\n"


class RawRequirementSemanticConverter:
    """Convert raw requirements into semantic requirements for SRS generation."""

    def convert(self, document: RawRequirementDocument) -> list[RequirementObject]:
        requirements: list[RequirementObject] = []
        for item in document.functional_reqs:
            if item.disposition != "formal_requirement":
                continue
            requirements.append(
                FunctionalRequirementObject(
                    id=item.id.replace("RAW-", "REQ-"),
                    type="functional",
                    name=item.title,
                    description=_semantic_description(item),
                    inputs=_csv_to_list(item.inputs),
                    outputs=_csv_to_list(item.outputs),
                    constraints=_collect_constraints(item),
                    source=[_raw_source(document, item)],
                )
            )
        for item in document.interface_reqs:
            if item.disposition != "formal_requirement":
                continue
            direction = "input"
            if item.outputs and not item.inputs:
                direction = "output"
            requirements.append(
                InterfaceRequirementObject(
                    id=item.id.replace("RAW-", "REQ-"),
                    type="interface",
                    interface_name=item.title,
                    direction=direction,
                    dependency=item.description,
                    evidence="；".join(
                        part for part in [item.inputs, item.outputs, item.return_value, item.exceptions] if part
                    ),
                    function_name=_extract_explicit_function_name(document.module_name, item.title, item.description),
                    source=[_raw_source(document, item)],
                )
            )
        for item in document.config_reqs:
            if item.disposition != "formal_requirement":
                continue
            requirements.append(
                ConfigurationRequirementObject(
                    id=item.id.replace("RAW-", "REQ-"),
                    type="configuration",
                    config_name=item.title,
                    range=item.valid_range or "待确认",
                    default=item.default_value or "待确认",
                    dependency=item.description,
                    source=[_raw_source(document, item)],
                )
            )
        for item in document.nfr_reqs:
            if item.disposition != "formal_requirement":
                continue
            if item.nfr_category and re.search(r"状态|模式|state|mode", item.nfr_category, re.I):
                requirements.append(
                    StateRequirementObject(
                        id=item.id.replace("RAW-", "REQ-"),
                        type="state",
                        state_name=item.title,
                        transition=[],
                        dependency=_collect_constraints(item),
                        source=[_raw_source(document, item)],
                    )
                )
                continue
            requirements.append(
                FunctionalRequirementObject(
                    id=item.id.replace("RAW-", "REQ-"),
                    type="functional",
                    name=item.title,
                    description=_semantic_description(item),
                    inputs=[],
                    outputs=[],
                    constraints=_collect_constraints(item),
                    source=[_raw_source(document, item)],
                )
            )
        return requirements


class RawRequirementCoverageAnalyzer:
    """Check whether SRS requirements cover raw requirements."""

    def analyze(
        self,
        document: RawRequirementDocument,
        requirements: Iterable[RequirementObject | EngineeringRequirement],
    ) -> CoverageReport:
        details = self.build_detail(document, requirements)
        relevant = [item for item in details if item["status"] != "excluded_by_gate"]
        covered = sum(1 for item in relevant if item["status"] == "covered")
        uncovered = [str(item["raw_id"]) for item in relevant if item["status"] != "covered"]
        total = len(relevant)
        rate = covered / total if total else 1.0
        return CoverageReport(
            total_user_reqs=total,
            covered=covered,
            uncovered=uncovered,
            coverage_rate=rate,
            is_satisfied=not uncovered,
            gaps_detail="; ".join(uncovered),
        )

    def build_detail(
        self,
        document: RawRequirementDocument,
        requirements: Iterable[RequirementObject | EngineeringRequirement],
    ) -> list[dict[str, Any]]:
        requirements = list(requirements)
        requirement_views = [_requirement_view(req) for req in requirements]
        details: list[dict[str, Any]] = []
        for item in _raw_items(document):
            if item.disposition != "formal_requirement":
                details.append(
                    {
                        "raw_id": item.id,
                        "category": item.category,
                        "title": item.title,
                        "source": item.source_detail,
                        "status": "excluded_by_gate",
                        "matched_requirements": [],
                    }
                )
                continue
            matches = _matched_requirement_ids(item, requirement_views)
            details.append(
                {
                    "raw_id": item.id,
                    "category": item.category,
                    "title": item.title,
                    "source": item.source_detail,
                    "status": "covered" if matches else "uncovered",
                    "matched_requirements": matches,
                }
            )
        return details

    def _text_of(self, requirement: RequirementObject) -> str:
        return str(_requirement_view(requirement)["text"])


def merge_requirements(
    base_requirements: list[RequirementObject],
    raw_requirements: list[RequirementObject],
) -> list[RequirementObject]:
    """Append raw requirements unless a similar semantic object already exists."""
    merged = list(base_requirements)
    indexed = [_merge_signature(item) for item in merged]
    for item in raw_requirements:
        key = _merge_signature(item)
        if any(_merge_similarity(key, existing) >= _merge_threshold(key["type"]) for existing in indexed):
            continue
        merged.append(item)
        indexed.append(key)
    return merged


def render_coverage_markdown(report: CoverageReport, module: str) -> str:
    lines = [
        f"# {module} 原始开发需求覆盖检查",
        "",
        "| 指标 | 值 |",
        "| --- | --- |",
        f"| 原始需求总数 | {report.total_user_reqs} |",
        f"| 已覆盖 | {report.covered} |",
        f"| 覆盖率 | {report.coverage_rate:.0%} |",
        f"| 是否满足 | {'是' if report.is_satisfied else '否'} |",
        "",
        "## 未覆盖需求",
        "",
    ]
    if report.uncovered:
        for item in report.uncovered:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")
    lines.append("")
    return "\n".join(lines)


def render_raw_coverage_matrix_markdown(
    document: RawRequirementDocument,
    requirements: Iterable[RequirementObject | EngineeringRequirement],
    *,
    module: str,
) -> str:
    analyzer = RawRequirementCoverageAnalyzer()
    summary = analyzer.analyze(document, requirements)
    details = analyzer.build_detail(document, requirements)
    lines = [
        f"# {module} 原始开发需求覆盖矩阵",
        "",
        "| 指标 | 值 |",
        "| --- | --- |",
        f"| 原始需求总数 | {summary.total_user_reqs} |",
        f"| 已覆盖 | {summary.covered} |",
        f"| 覆盖率 | {summary.coverage_rate:.0%} |",
        f"| 是否满足 | {'是' if summary.is_satisfied else '否'} |",
        "",
        "## 原始开发需求覆盖矩阵",
        "",
        "| 原始需求ID | 类别 | 标题 | 覆盖状态 | 覆盖到的正式需求 | 来源 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in details:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["raw_id"]),
                    str(item["category"]),
                    str(item["title"]),
                    "Covered" if item["status"] == "covered" else ("Excluded" if item["status"] == "excluded_by_gate" else "Uncovered"),
                    ", ".join(item["matched_requirements"]) or "-",
                    str(item["source"] or "-"),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _split_raw_entries(text: str) -> list[tuple[str, str | None]]:
    items: list[tuple[str, str | None]] = []
    current_category: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^(模块名称|模块简称|模块|module)\s*[:：]", line, re.I):
            continue
        if re.match(r"^(安全等级|safety\s*level)\s*[:：]", line, re.I):
            continue
        category = _heading_category(line)
        if category:
            current_category = category
            continue
        line = re.sub(r"^[>\-\*\d\.\)\(（）：:、\s]+", "", line).strip()
        if len(line) < 4:
            continue
        pieces = re.split(r"[；;]\s*", line)
        for piece in pieces:
            value = piece.strip(" ;")
            if len(value) >= 4:
                items.append((value, current_category))
    return items


def _guess_category(text: str, structured_fields: dict[str, str] | None = None) -> str:
    structured_fields = structured_fields or {}
    explicit = (structured_fields.get("category") or structured_fields.get("type") or "").upper()
    if explicit in {"FUNC", "FUNCTIONAL", "功能", "功能需求"}:
        return "FUNC"
    if explicit in {"INTF", "INTERFACE", "接口", "接口需求"}:
        return "INTF"
    if explicit in {"CFG", "CONFIG", "CONFIGURATION", "配置", "配置需求"}:
        return "CFG"
    if explicit in {"NFR", "NONFUNCTIONAL", "CONSTRAINT", "约束", "非功能", "非功能需求"}:
        return "NFR"
    lowered = text.lower()
    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(", text):
        return "INTF"
    if any(token in lowered for token in ("misra", "rom/ram", "memmap", "安全等级", "评估记录", "约束")):
        return "NFR"
    if any(token in lowered for token in ("api", "接口", "初始化", "读取", "查询", "设置", "write", "read", "get", "set")):
        return "INTF"
    if any(token in lowered for token in ("配置", "参数", "默认", "地址", "实例", "核", "enable", "disable")):
        return "CFG"
    if any(token in lowered for token in ("约束", "时序", "性能", "安全", "qm", "asil", "超时", "限制", "覆盖检查")):
        return "NFR"
    return "FUNC"


def _normalize_category(value: str | None) -> str:
    return value if value in {"FUNC", "INTF", "CFG", "NFR"} else "FUNC"


def _heading_category(line: str) -> str | None:
    if re.match(r"^原始(?:功能|功能性).{0,8}[:：]?$", line):
        return "FUNC"
    if re.match(r"^原始接口.{0,8}[:：]?$", line):
        return "INTF"
    if re.match(r"^原始配置.{0,8}[:：]?$", line):
        return "CFG"
    if re.match(r"^原始(?:非功能|约束).{0,8}[:：]?$", line):
        return "NFR"
    return None


def _extract_module_hints(text: str) -> dict[str, str]:
    hints: dict[str, str] = {}
    module_match = re.search(r"(?:模块名称|模块|module)\s*[:：]?\s*([A-Za-z][A-Za-z0-9_-]{1,31})", text, re.I)
    if module_match:
        hints["module_name"] = module_match.group(1)
        hints["module_abbr"] = _module_token(module_match.group(1))
    safety_match = re.search(r"(?:安全等级|safety\s*level)\s*[:：]?\s*(QM|ASIL[- ]?[ABCD])", text, re.I)
    if safety_match:
        hints["safety_level"] = safety_match.group(1).upper().replace(" ", "-")
    return hints


def _extract_safety_level(raw_input: UnifiedRawInput) -> str:
    """Extract ASIL/QM safety level from raw input text."""
    for entry in raw_input.entries:
        match = re.search(r'\b(QM|ASIL[- ]?[ABCD])\b', entry.raw_text, re.IGNORECASE)
        if match:
            return match.group(1).upper().replace(" ", "-")
    for hint_text in raw_input.module_hints.values():
        match = re.search(r'\b(QM|ASIL[- ]?[ABCD])\b', hint_text, re.IGNORECASE)
        if match:
            return match.group(1).upper().replace(" ", "-")
    return "QM"


def _entry_from_text(
    item_id: str,
    category: str,
    text: str,
    source_ref: str,
    structured_fields: dict[str, str] | None = None,
) -> RawRequirementEntry:
    structured_fields = structured_fields or {}
    title = structured_fields.get("title") or _derive_title(text, category)
    disposition, gate_reason = classify_raw_item(
        category=category,
        title=title,
        description=_description_value(text, structured_fields),
    )
    common = dict(
        id=item_id,
        category=category,
        title=title,
        description=_description_value(text, structured_fields),
        source="user",
        source_detail=source_ref,
        priority=structured_fields.get("priority") or _derive_priority(text),
        status=structured_fields.get("status") or ("明确" if _is_explicit(text) else "待澄清"),
        confidence="Explicit" if _is_explicit(text) or structured_fields else "Inferred",
        notes="由对话/txt 原始输入自动抽取。",
        disposition=disposition,
        gate_reason=gate_reason,
    )
    if category == "INTF":
        return RawRequirementEntry(
            **common,
            inputs=structured_fields.get("inputs") or _extract_field(text, ("输入", "参数", "入参")) or "待确认",
            outputs=structured_fields.get("outputs") or _extract_field(text, ("输出", "结果", "出参")) or "待确认",
            return_value=structured_fields.get("return_value") or _extract_field(text, ("返回", "返回值")) or "待确认",
            exceptions=structured_fields.get("exceptions") or _extract_field(text, ("异常", "错误", "失败")) or "待确认",
        )
    if category == "CFG":
        return RawRequirementEntry(
            **common,
            config_timing=structured_fields.get("config_timing") or _extract_field(text, ("配置时机", "初始化", "上电")) or "待确认",
            default_value=structured_fields.get("default_value") or _extract_field(text, ("默认", "缺省")) or "待确认",
            valid_range=structured_fields.get("valid_range") or _extract_range(text) or "待确认",
            error_handling=structured_fields.get("error_handling") or _extract_field(text, ("非法", "无效", "错误")) or "待确认",
        )
    if category == "NFR":
        return RawRequirementEntry(
            **common,
            nfr_category=structured_fields.get("nfr_category") or _derive_nfr_category(text),
            constraint_value=structured_fields.get("constraint_value") or _extract_range(text) or "待确认",
            verification_suggestion=structured_fields.get("verification_suggestion") or _derive_verification(text),
        )
    return RawRequirementEntry(**common)


def _derive_title(text: str, category: str) -> str:
    if category == "CFG":
        cfg_patterns = [
            ("实例数量", "实例数量配置"),
            ("芯片实例数量", "实例数量配置"),
            ("默认gpio方向", "默认方向配置"),
            ("默认输出电平", "默认输出配置"),
            ("方向枚举值", "方向映射配置"),
            ("外部信号id映射", "方向映射配置"),
            ("i2c通信速率", "通信速率配置"),
            ("i2c设备地址", "设备地址配置"),
            ("中断使能", "中断配置"),
            ("去抖时间", "中断配置"),
            ("det错误检测开关", "DET配置"),
            ("mcal适配开关", "MCAL配置"),
            ("使能延时", "初始化时序配置"),
            ("初始化重试次数", "初始化时序配置"),
            ("故障清除后延时", "初始化时序配置"),
            ("看门狗开关", "看门狗配置"),
            ("故障清除模式", "故障清除配置"),
            ("自动清故障开关", "故障清除配置"),
            ("各cpu核使能状态", "多核实例配置"),
            ("每核独立芯片数量", "多核实例配置"),
            ("信号数量配置", "多核实例配置"),
            ("en引脚", "硬件映射配置"),
            ("spi通道", "硬件映射配置"),
            ("spi序列", "硬件映射配置"),
            ("pwm通道映射", "硬件映射配置"),
        ]
        lowered = text.lower()
        for token, title in cfg_patterns:
            if token in lowered:
                return title
    patterns = [
        ("初始化", "初始化"),
        ("读取", "状态读取"),
        ("查询", "状态查询"),
        ("设置", "参数设置"),
        ("模式", "模式控制"),
        ("复位", "复位处理"),
        ("中断", "中断处理"),
        ("多核", "多核支持"),
        ("多实例", "多实例支持"),
        ("配置", "配置管理"),
        ("覆盖", "覆盖检查"),
    ]
    for token, title in patterns:
        if token in text:
            return title if category != "INTF" else f"{title}接口"
    shortened = re.sub(r"[，。,:：].*$", "", text).strip()
    return shortened[:24] if shortened else f"{category}需求"


def _description_value(text: str, structured_fields: dict[str, str]) -> str:
    description = structured_fields.get("description") or text
    return description.rstrip("。") + "。"


def _extract_explicit_function_name(module_name: str, title: str, description: str) -> str:
    text = f"{title} {description}"
    match = re.search(r"\b(Gp_[A-Za-z0-9_]+)\s*(?=\()", text)
    if match:
        return match.group(1)
    match = re.search(r"\b([A-Za-z][A-Za-z0-9_]*)\s*(?=\()", text)
    if not match:
        return ""
    base_name = match.group(1)
    if base_name in {"void", "uint8", "uint16", "uint32", "Std_ReturnType"}:
        return ""
    clean_module = re.sub(r"^Gp_", "", module_name)
    if base_name.startswith(clean_module):
        return f"Gp_{base_name}"
    return f"Gp_{clean_module}_{base_name}"


def _derive_priority(text: str) -> str:
    if any(token in text for token in ("必须", "优先", "首先", "必须覆盖", "高优先级")):
        return "High"
    if "可选" in text or "后续" in text:
        return "Low"
    return "Medium"


def _is_explicit(text: str) -> bool:
    return any(token in text for token in ("必须", "需要", "应", "支持", "提供"))


def _derive_nfr_category(text: str) -> str:
    if "安全" in text or "QM" in text or "ASIL" in text:
        return "安全等级"
    if "时序" in text or "超时" in text:
        return "时序"
    if "性能" in text:
        return "性能"
    if "覆盖" in text:
        return "覆盖约束"
    return "约束"


def _derive_verification(text: str) -> str:
    if "覆盖" in text:
        return "Review/Trace"
    if "时序" in text or "超时" in text:
        return "Analysis/IT"
    return "Review"


def _extract_field(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:：]\s*([^，。；;]+)", text, re.I)
        if match:
            return match.group(1).strip()
    return None


def _extract_range(text: str) -> str | None:
    match = re.search(r"(\d+\s*(?:\.\.\d+|[-~至]\s*\d+)?\s*(?:个|核|ms|us|μs|%|路)?)", text, re.I)
    return match.group(1).replace(" ", "") if match else None


def _raw_section_markdown(title: str, items: list[RawRequirementEntry], category: str) -> list[str]:
    lines = [f"## {title}", ""]
    if category == "功能":
        lines.extend([
            "| 原始需求ID | 需求标题 | 原始需求描述 | 来源/章节 | 优先级 | 状态 | 备注 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ])
        for item in items:
            lines.append(
                f"| {item.id} | {item.title} | {item.description} | {item.source_detail} | {item.priority} | {item.status} | {item.notes or ''} |"
            )
        lines.extend(["", ""])
        return lines
    if category == "接口":
        lines.extend([
            "| 原始需求ID | 接口需求 | 输入 | 输出 | 返回值/状态语义 | 异常条件 | 来源 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ])
        for item in items:
            lines.append(
                f"| {item.id} | {item.title} | {item.inputs or ''} | {item.outputs or ''} | {item.return_value or ''} | {item.exceptions or ''} | {item.source_detail} |"
            )
        lines.extend(["", ""])
        return lines
    if category == "配置":
        lines.extend([
            "| 原始需求ID | 配置项 | 配置时机 | 默认值 | 有效范围 | 无效配置处理 | 来源 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ])
        for item in items:
            lines.append(
                f"| {item.id} | {item.title} | {item.config_timing or ''} | {item.default_value or ''} | {item.valid_range or ''} | {item.error_handling or ''} | {item.source_detail} |"
            )
        lines.extend(["", ""])
        return lines
    lines.extend([
        "| 原始需求ID | 类别 | 约束内容 | 数值/范围 | 验证建议 | 来源 |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for item in items:
        lines.append(
            f"| {item.id} | {item.nfr_category or ''} | {item.description} | {item.constraint_value or ''} | {item.verification_suggestion or ''} | {item.source_detail} |"
        )
    lines.extend(["", ""])
    return lines


def _semantic_description(item: RawRequirementEntry) -> str:
    if item.description.startswith("软件应"):
        return item.description
    return f"软件应支持{item.description.rstrip('。')}。"


def _csv_to_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"[,，/]", value) if part.strip() and part.strip() != "待确认"]


def _collect_constraints(item: RawRequirementEntry) -> list[str]:
    parts = [
        item.return_value,
        item.exceptions,
        item.valid_range,
        item.error_handling,
        item.constraint_value,
        item.verification_suggestion,
    ]
    return [part for part in parts if part and part != "待确认"]


def _raw_source(document: RawRequirementDocument, item: RawRequirementEntry) -> SourceRef:
    return SourceRef(
        document=document.doc_id,
        chunk_id=item.id,
        heading_path=["原始开发需求", item.category],
        content_type="raw_input",
        evidence=item.description,
    )


def _module_token(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "", value).upper()
    return normalized or "FC"


def _normalize_text(text: str) -> str:
    return " ".join(_normalized_terms(text))


def _coverage_score(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left in right or right in left:
        return 1.0
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    base = max(1, min(len(left_tokens), len(right_tokens)))
    recall = overlap / max(1, len(left_tokens))
    precision = overlap / max(1, len(right_tokens))
    phrase_bonus = 0.2 if _longest_common_phrase(left_tokens, right_tokens) >= 2 else 0.0
    return max(overlap / base, (recall * 0.65 + precision * 0.35) + phrase_bonus)


def _tokenize(text: str) -> set[str]:
    return set(_normalized_terms(text))


def _merge_signature(item: RequirementObject) -> dict[str, object]:
    data = item.to_dict()
    name = data.get("function_name") or data.get("name") or data.get("interface_name") or data.get("config_name") or data.get("state_name") or ""
    desc = data.get("description") or data.get("dependency") or data.get("constraint") or ""
    fields = {
        "input": data.get("input") or data.get("inputs") or "",
        "output": data.get("output") or data.get("outputs") or "",
        "default": data.get("default") or "",
        "range": data.get("range") or "",
        "evidence": data.get("evidence") or "",
        "function_name": data.get("function_name") or "",
    }
    return {
        "type": data.get("type", ""),
        "name": _normalize_text(name),
        "body": _normalize_text(f"{name} {desc}"),
        "tokens": _tokenize(f"{name} {desc}"),
        "fields": {key: _normalize_text(str(value)) for key, value in fields.items() if value},
    }


def _merge_similarity(left: dict[str, object], right: dict[str, object]) -> float:
    if left["type"] != right["type"]:
        return 0.0
    if left["name"] and left["name"] == right["name"]:
        field_overlap = _field_overlap(left["fields"], right["fields"])
        return 0.92 + min(0.08, field_overlap * 0.08)
    body_score = _coverage_score(str(left["body"]), str(right["body"]))
    token_score = _token_overlap_score(
        left["tokens"],
        right["tokens"],
    )
    field_score = _field_overlap(left["fields"], right["fields"])
    return max(body_score * 0.75 + token_score * 0.25, body_score * 0.6 + field_score * 0.4)


def _merge_threshold(req_type: object) -> float:
    return {
        "interface": 0.72,
        "configuration": 0.68,
        "functional": 0.74,
        "state": 0.7,
    }.get(str(req_type), 0.72)


TERM_CANONICAL_MAP = {
    "提供": "支持",
    "实现": "支持",
    "能够": "支持",
    "可": "支持",
    "接口": "api",
    "初始化": "init",
    "模式": "mode",
    "状态": "status",
    "读取": "read",
    "查询": "read",
    "获取": "read",
    "设置": "set",
    "配置": "config",
    "参数": "config",
    "实例": "instance",
    "多实例": "multiinstance",
    "多核": "multicore",
    "内核": "core",
    "复位": "reset",
    "中断": "interrupt",
    "错误": "error",
    "异常": "error",
    "失败": "error",
    "覆盖": "coverage",
    "追溯": "trace",
    "时序": "timing",
    "约束": "constraint",
    "默认值": "default",
    "缺省": "default",
    "有效范围": "range",
    "返回值": "return",
    "输入": "input",
    "输出": "output",
    "模式切换": "modeswitch",
    "模式控制": "modeswitch",
    "状态读取": "moderead",
    "当前模式读取": "moderead",
    "normal": "normal",
    "sleep": "sleep",
    "standby": "standby",
    "init": "init",
    "read": "read",
    "write": "write",
    "get": "read",
    "set": "set",
    "configuration": "config",
    "instance": "instance",
}


STOPWORDS = {
    "软件", "模块", "应", "需要", "支持", "进行", "用于", "当前", "后续", "首先", "满足",
    "based", "shall", "the", "and", "for", "with", "to", "of", "a", "an",
}


def _normalized_terms(text: str) -> list[str]:
    lowered = text.lower()
    lowered = re.sub(r"\bthe software shall\b", " ", lowered)
    lowered = re.sub(r"\bshall\b", " ", lowered)
    lowered = lowered.replace("100%", "100percent")
    raw_terms = re.findall(r"[\u4e00-\u9fff]{1,8}|[a-z0-9_.-]{2,}", lowered)
    result: list[str] = []
    for term in raw_terms:
        normalized = TERM_CANONICAL_MAP.get(term, term)
        if normalized in STOPWORDS:
            continue
        if re.fullmatch(r"\d+", normalized):
            result.append(normalized)
            continue
        if len(normalized) >= 2:
            result.append(normalized)
    return result


def _longest_common_phrase(left: set[str], right: set[str]) -> int:
    common = left & right
    if not common:
        return 0
    return max((len(token) for token in common if token), default=0)


def _token_overlap_score(left: object, right: object) -> float:
    left_set = set(left) if isinstance(left, set) else set()
    right_set = set(right) if isinstance(right, set) else set()
    if not left_set or not right_set:
        return 0.0
    overlap = len(left_set & right_set)
    return overlap / max(1, min(len(left_set), len(right_set)))


def _field_overlap(left: object, right: object) -> float:
    left_map = left if isinstance(left, dict) else {}
    right_map = right if isinstance(right, dict) else {}
    common_keys = set(left_map) & set(right_map)
    if not common_keys:
        return 0.0
    matches = 0.0
    for key in common_keys:
        if left_map[key] == right_map[key]:
            matches += 1.0
        else:
            matches += _coverage_score(str(left_map[key]), str(right_map[key])) * 0.6
    return matches / len(common_keys)


def _raw_items(document: RawRequirementDocument) -> list[RawRequirementEntry]:
    return [
        *document.functional_reqs,
        *document.interface_reqs,
        *document.config_reqs,
        *document.nfr_reqs,
    ]


def _requirement_view(req: RequirementObject | EngineeringRequirement) -> dict[str, Any]:
    data = req.to_dict()
    req_id = (
        data.get("requirement_id")
        or data.get("id")
        or ""
    )
    text = " ".join(
        str(data.get(field, ""))
        for field in (
            "title",
            "name",
            "description",
            "interface_name",
            "dependency",
            "config_name",
            "range",
            "default",
            "state_name",
            "constraint",
            "input",
            "output",
            "evidence",
            "verification",
        )
    )
    return {
        "id": str(req_id),
        "text": _normalize_text(text),
        "source": data.get("source", []),
    }


def _matched_requirement_ids(
    item: RawRequirementEntry,
    requirement_views: list[dict[str, Any]],
) -> list[str]:
    matches: list[str] = []
    item_text = _normalize_text(f"{item.title} {item.description}")
    for req in requirement_views:
        if any(source.get("chunk_id") == item.id for source in req.get("source", [])):
            matches.append(str(req["id"]))
            continue
        if _coverage_score(item_text, str(req["text"])) >= 0.45:
            matches.append(str(req["id"]))
    return sorted(dict.fromkeys(match for match in matches if match))


def _read_delimited_rows(path: Path, *, delimiter: str) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [[cell.strip() for cell in row] for row in csv.reader(handle, delimiter=delimiter)]


def _read_xlsx_rows(path: Path) -> list[tuple[str, list[list[str]]]]:
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with zipfile.ZipFile(path) as archive:
        shared_strings = _xlsx_shared_strings(archive, ns)
        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        rel_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rel_root.findall("pkgrel:Relationship", ns)
        }
        sheets: list[tuple[str, list[list[str]]]] = []
        for sheet in workbook_root.findall("main:sheets/main:sheet", ns):
            name = sheet.attrib.get("name", "Sheet")
            rel_id = sheet.attrib.get(f"{{{ns['rel']}}}id")
            target = rel_map.get(rel_id, "")
            if not target:
                continue
            xml_path = f"xl/{target}"
            rows = _xlsx_sheet_rows(archive.read(xml_path), shared_strings, ns)
            sheets.append((name, rows))
        return sheets


def _xlsx_shared_strings(archive: zipfile.ZipFile, ns: dict[str, str]) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall("main:si", ns):
        text = "".join(node.text or "" for node in item.findall(".//main:t", ns))
        values.append(text)
    return values


def _xlsx_sheet_rows(xml_bytes: bytes, shared_strings: list[str], ns: dict[str, str]) -> list[list[str]]:
    root = ET.fromstring(xml_bytes)
    rows: list[list[str]] = []
    for row in root.findall(".//main:sheetData/main:row", ns):
        cells: dict[int, str] = {}
        max_col = 0
        for cell in row.findall("main:c", ns):
            ref = cell.attrib.get("r", "")
            col_index = _excel_col_to_index(re.match(r"([A-Z]+)", ref).group(1)) if ref else max_col + 1
            value_node = cell.find("main:v", ns)
            text = ""
            if value_node is not None and value_node.text is not None:
                raw = value_node.text
                if cell.attrib.get("t") == "s":
                    idx = int(raw)
                    text = shared_strings[idx] if idx < len(shared_strings) else raw
                else:
                    text = raw
            elif cell.attrib.get("t") == "inlineStr":
                text = "".join(node.text or "" for node in cell.findall(".//main:t", ns))
            cells[col_index] = text.strip()
            max_col = max(max_col, col_index)
        rows.append([cells.get(idx, "") for idx in range(1, max_col + 1)])
    return rows


def _excel_col_to_index(value: str) -> int:
    result = 0
    for char in value:
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result


def _tabular_headers_and_rows(rows: list[list[str]]) -> tuple[list[str], list[list[str]]]:
    if not rows:
        return [], []
    header = [cell.strip() for cell in rows[0]]
    if any(_is_header_keyword(cell) for cell in header):
        return header, rows[1:]
    return [], rows


def _is_header_keyword(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered in {
        "模块", "module", "category", "type", "title", "name", "description", "需求描述",
        "priority", "status", "inputs", "outputs", "return", "exception", "default",
        "range", "verification", "配置时机", "默认值", "有效范围", "类别", "标题", "说明",
    }


def _structured_fields_from_row(headers: list[str], row: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for index, header in enumerate(headers):
        if index >= len(row):
            continue
        value = row[index].strip()
        if not value:
            continue
        key = _canonical_header(header)
        if key:
            result[key] = value
    return result


def _canonical_header(header: str) -> str | None:
    lowered = header.strip().lower()
    mapping = {
        "类别": "category",
        "category": "category",
        "type": "type",
        "标题": "title",
        "title": "title",
        "name": "title",
        "需求标题": "title",
        "描述": "description",
        "说明": "description",
        "需求描述": "description",
        "description": "description",
        "优先级": "priority",
        "priority": "priority",
        "状态": "status",
        "status": "status",
        "输入": "inputs",
        "inputs": "inputs",
        "输出": "outputs",
        "outputs": "outputs",
        "返回值": "return_value",
        "return": "return_value",
        "异常": "exceptions",
        "错误处理": "error_handling",
        "exceptions": "exceptions",
        "配置时机": "config_timing",
        "默认值": "default_value",
        "default": "default_value",
        "有效范围": "valid_range",
        "range": "valid_range",
        "验证建议": "verification_suggestion",
        "verification": "verification_suggestion",
        "约束分类": "nfr_category",
        "nfr_category": "nfr_category",
        "约束值": "constraint_value",
        "constraint_value": "constraint_value",
        "模块": "module_name",
        "module": "module_name",
    }
    return mapping.get(lowered)


def _raw_text_from_structured_row(structured: dict[str, str], row: list[str]) -> str:
    if structured.get("module_name") and len(structured) == 1:
        return ""
    if structured.get("description"):
        if structured.get("title"):
            return f"{structured['title']}：{structured['description']}"
        return structured["description"]
    values = [value.strip() for value in row if value.strip()]
    return "；".join(values)


def _is_input_sheet_name(name: str) -> bool:
    lowered = name.strip().lower()
    return lowered in {"需求输入", "input", "inputs", "requirements", "需求"}


def _looks_like_input_sheet(rows: list[list[str]]) -> bool:
    if not rows:
        return False
    sample = [cell.strip() for cell in rows[0] if cell.strip()]
    return any(_is_header_keyword(cell) for cell in sample)


def _should_skip_structured_row(structured: dict[str, str], row: list[str]) -> bool:
    row_text = " ".join(value.strip() for value in row if value.strip())
    if not row_text:
        return True
    if row_text.startswith("<请从这一行开始继续填写>"):
        return True
    if structured.get("module_name", "").startswith("<请"):
        return True
    if not structured and len([value for value in row if value.strip()]) <= 1:
        return True
    return False
