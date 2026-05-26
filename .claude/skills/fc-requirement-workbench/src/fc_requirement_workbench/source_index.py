"""Source index and extraction record generators.

Produces standalone source index tables and unified extraction records
for the FC SRS generation workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SourceEntry:
    source_id: str
    file_name: str
    file_type: str
    chapter: str = ""
    version: str = ""
    applicable: str = "是"
    applicability_note: str = ""
    expected_categories: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "chapter": self.chapter,
            "version": self.version,
            "applicable": self.applicable,
            "applicability_note": self.applicability_note,
            "expected_categories": self.expected_categories,
        }


@dataclass
class ExtractRecord:
    extract_id: str
    source_id: str
    summary: str
    content_type: str
    software_relevance: str
    certainty: str  # 确定/待确认/冲突/不适用
    notes: str = ""


@dataclass
class DerivationRecord:
    derivation_id: str
    extract_ids: list[str]
    conclusion: str  # 生成需求/合并需求/拆分需求/N/A/开放项
    category: str  # FUNC/INTF/CFG/DIAG/TIM/SAFE/CODE/RES
    target_srs_id: str = ""
    explanation: str = ""
    risk: str = ""


# ---------------------------------------------------------------------------
# Source Index Generator
# ---------------------------------------------------------------------------

class SourceIndexGenerator:
    """Generate a source index from input documents and parsed chunks."""

    def __init__(self, module: str = "FC") -> None:
        self.module = module

    def generate(
        self,
        input_file: str = "",
        datasheet_chapters: list[str] | None = None,
        has_raw_requirements: bool = False,
        has_project_constraints: bool = False,
    ) -> list[SourceEntry]:
        entries: list[SourceEntry] = []
        counter = 1

        # Datasheet chapters
        if datasheet_chapters:
            for chapter in datasheet_chapters:
                entries.append(SourceEntry(
                    source_id=f"SRC-{self.module}-DS-{counter:04d}",
                    file_name=input_file or "Datasheet.md",
                    file_type="技术手册",
                    chapter=chapter,
                    version="Rev1.0",
                    applicable="是",
                    expected_categories=["FUNC", "INTF", "CFG", "DIAG", "TIM"],
                ))
                counter += 1
        elif input_file:
            entries.append(SourceEntry(
                source_id=f"SRC-{self.module}-DS-{counter:04d}",
                file_name=input_file,
                file_type="技术手册",
                applicable="是",
                expected_categories=["FUNC", "INTF", "CFG", "DIAG", "TIM", "SAFE", "CODE", "RES"],
            ))
            counter += 1

        # Raw requirements
        if has_raw_requirements:
            entries.append(SourceEntry(
                source_id=f"SRC-{self.module}-REQ-{counter:04d}",
                file_name="原始开发需求",
                file_type="原始需求",
                applicable="是",
                expected_categories=["FUNC", "INTF", "CFG", "SAFE"],
            ))
            counter += 1

        # Platform standards
        entries.append(SourceEntry(
            source_id=f"SRC-{self.module}-STD-{counter:04d}",
            file_name="aurix2g-normative-patterns.md",
            file_type="标准规范",
            chapter="AURIX 2G IoExtDev 平台规范",
            applicable="是",
            applicability_note="接口命名分类、MainFunction 判定、安全分层",
            expected_categories=["INTF", "DIAG", "CFG", "SAFE"],
        ))
        counter += 1

        # Construction rules
        entries.append(SourceEntry(
            source_id=f"SRC-{self.module}-STD-{counter:04d}",
            file_name="construction-rules.md",
            file_type="编写规范",
            applicable="是",
            applicability_note="各类需求最小必填项和缺失处理",
            expected_categories=["FUNC", "INTF", "CFG", "DIAG", "TIM", "RES", "SAFE", "CODE"],
        ))
        counter += 1

        # Authoring standard
        entries.append(SourceEntry(
            source_id=f"SRC-{self.module}-STD-{counter:04d}",
            file_name="authoring-standard.md",
            file_type="编写规范",
            applicable="是",
            applicability_note="语言、字段、粒度、单位规范",
            expected_categories=["FUNC", "INTF", "CFG", "DIAG", "TIM", "RES", "SAFE", "CODE"],
        ))
        counter += 1

        # Calibration rules
        entries.append(SourceEntry(
            source_id=f"SRC-{self.module}-STD-{counter:04d}",
            file_name="calibration-rules.md",
            file_type="校准规则",
            applicable="是",
            applicability_note="写作偏好、颗粒度校准、历史习惯",
            expected_categories=["FUNC", "INTF", "CFG", "DIAG", "TIM"],
        ))

        # Project constraints
        if has_project_constraints:
            counter += 1
            entries.append(SourceEntry(
                source_id=f"SRC-{self.module}-CTR-{counter:04d}",
                file_name="项目约束文档",
                file_type="项目约束",
                applicable="是",
                expected_categories=["CFG", "SAFE", "TIM"],
            ))

        return entries

    def render_markdown(self, entries: list[SourceEntry], module: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# 输入资料索引 — {module}",
            "",
            f"**生成时间**: {now}",
            f"**模块**: {module}",
            f"**来源条目总数**: {len(entries)}",
            "",
            "## 来源清单",
            "",
            "| 来源ID | 文件名称 | 文件类型 | 章节/位置 | 版本/日期 | 是否适用 | 适用说明 | 预期需求类别 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for entry in entries:
            categories = ", ".join(entry.expected_categories) if entry.expected_categories else "-"
            note = entry.applicability_note if entry.applicability_note else "-"
            lines.append(
                f"| {entry.source_id} | {entry.file_name} | {entry.file_type} | "
                f"{entry.chapter or '-'} | {entry.version or '-'} | {entry.applicable} | "
                f"{note} | {categories} |"
            )
        lines.append("")

        lines.append("## 来源类型统计")
        lines.append("")
        type_counts: dict[str, int] = {}
        for entry in entries:
            type_counts[entry.file_type] = type_counts.get(entry.file_type, 0) + 1
        lines.append("| 文件类型 | 数量 |")
        lines.append("| --- | --- |")
        for ftype, count in sorted(type_counts.items()):
            lines.append(f"| {ftype} | {count} |")
        lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Extract Record Generator
# ---------------------------------------------------------------------------

class ExtractRecordGenerator:
    """Generate unified extraction records from feature extraction and raw inputs."""

    def generate_from_features(
        self,
        feature_groups: list[dict[str, Any]],
        source_index: list[SourceEntry],
        module: str,
    ) -> list[ExtractRecord]:
        records: list[ExtractRecord] = []
        counter = 1

        if not source_index:
            return records

        primary_source = source_index[0].source_id

        for fg in feature_groups:
            summary = fg.get("name", "") or fg.get("summary", "")
            if not summary:
                continue
            records.append(ExtractRecord(
                extract_id=f"EXT-{module}-{counter:04d}",
                source_id=primary_source,
                summary=summary,
                content_type=_map_feature_type(fg),
                software_relevance=_map_software_relevance(fg),
                certainty="确定" if fg.get("evidence_level", "").startswith("L1") or fg.get("evidence_level", "").startswith("L2") or fg.get("evidence_level", "").startswith("L3") else "待确认",
                notes=fg.get("notes", ""),
            ))
            counter += 1

        return records

    def render_markdown(self, records: list[ExtractRecord], module: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# 来源内容抽取表 — {module}",
            "",
            f"**生成时间**: {now}",
            f"**模块**: {module}",
            f"**抽取条目总数**: {len(records)}",
            "",
            "## 抽取记录",
            "",
            "| 抽取ID | 来源ID | 原文/摘要 | 内容类型 | 软件相关性 | 确定性 | 备注 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for rec in records:
            lines.append(
                f"| {rec.extract_id} | {rec.source_id} | {rec.summary[:80]} | "
                f"{rec.content_type} | {rec.software_relevance} | {rec.certainty} | "
                f"{rec.notes[:60]} |"
            )
        lines.append("")

        lines.append("## 内容类型分布")
        lines.append("")
        type_counts: dict[str, int] = {}
        for rec in records:
            type_counts[rec.content_type] = type_counts.get(rec.content_type, 0) + 1
        lines.append("| 内容类型 | 数量 |")
        lines.append("| --- | --- |")
        for ctype, count in sorted(type_counts.items()):
            lines.append(f"| {ctype} | {count} |")
        lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Derivation Matrix Generator
# ---------------------------------------------------------------------------

class DerivationMatrixGenerator:
    """Generate requirement derivation matrix linking extracts to SRS IDs."""

    def generate(
        self,
        extract_records: list[ExtractRecord],
        engineering_requirements: list[EngineeringRequirement],
        module: str,
    ) -> list[DerivationRecord]:
        records: list[DerivationRecord] = []
        counter = 1

        for req in engineering_requirements:
            extracts = [
                rec.extract_id for rec in extract_records
                if _matches_requirement(rec, req)
            ]
            records.append(DerivationRecord(
                derivation_id=f"DRV-{module}-{counter:04d}",
                extract_ids=extracts[:3],
                conclusion="生成需求",
                category=_requirement_type_to_category(req.requirement_type),
                target_srs_id=req.requirement_id,
                explanation=f"从抽取内容推导为 {req.requirement_type} 需求",
                risk="项目配置值待补充" if "需项目输入确认" in req.constraint else "",
            ))
            counter += 1

        return records

    def render_markdown(self, records: list[DerivationRecord], module: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# 需求推导矩阵 — {module}",
            "",
            f"**生成时间**: {now}",
            f"**模块**: {module}",
            f"**推导条目总数**: {len(records)}",
            "",
            "## 推导记录",
            "",
            "| 推导ID | 抽取ID | 推导结论 | 需求类别 | 拟定 SRS ID | 推导说明 | 风险/待确认 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for rec in records:
            extracts = ", ".join(rec.extract_ids) if rec.extract_ids else "N/A"
            lines.append(
                f"| {rec.derivation_id} | {extracts} | {rec.conclusion} | "
                f"{rec.category} | {rec.target_srs_id} | {rec.explanation[:60]} | "
                f"{rec.risk or '-'} |"
            )
        lines.append("")

        return "\n".join(lines)


def _map_feature_type(fg: dict[str, Any]) -> str:
    name = (fg.get("name", "") or "").lower()
    if any(kw in name for kw in ("gpio", "input", "output", "port")):
        return "功能"
    if any(kw in name for kw in ("i2c", "register", "interface", "控制")):
        return "接口"
    if any(kw in name for kw in ("interrupt", "reset", "fault", "diag", "诊断", "复位", "中断")):
        return "诊断"
    if any(kw in name for kw in ("timing", "时序")):
        return "时序"
    if any(kw in name for kw in ("configuration", "polarity", "direction", "配置", "极性", "方向")):
        return "配置"
    return "功能"


def _map_software_relevance(fg: dict[str, Any]) -> str:
    name = (fg.get("name", "") or "").lower()
    if any(kw in name for kw in ("gpio", "input", "output", "polarity", "direction", "interrupt", "mode", "reset")):
        return "直接影响 FC 对外行为和接口语义"
    if any(kw in name for kw in ("i2c", "register")):
        return "定义通信协议和寄存器访问方式"
    if any(kw in name for kw in ("timing", "electrical")):
        return "约束软件时序和电气边界"
    return "支撑需求理解和完整性"


def _matches_requirement(rec: ExtractRecord, req: EngineeringRequirement) -> bool:
    desc = req.description.lower() + req.title.lower()
    rec_text = rec.summary.lower()
    keywords = desc.split()
    return any(kw in rec_text for kw in keywords if len(kw) > 2)


def _requirement_type_to_category(req_type: str) -> str:
    mapping = {
        "functional": "FUNC",
        "interface": "INTF",
        "configuration": "CFG",
        "diagnostic": "DIAG",
        "timing": "TIM",
        "state": "FUNC",
        "safety": "SAFE",
        "coding": "CODE",
        "resource": "RES",
    }
    return mapping.get(req_type, "FUNC")
