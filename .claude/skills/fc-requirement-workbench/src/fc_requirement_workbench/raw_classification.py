"""Raw requirement gate classification.

This module decides whether a raw extracted item should enter the formal
requirement pool or stay as constraint/capability/evidence metadata.
"""

from __future__ import annotations

from typing import Literal
import re


RawDisposition = Literal[
    "formal_requirement",
    "constraint",
    "capability",
    "metadata",
    "evidence",
    "architecture_seed_only",
    "test_seed_only",
    "open_issue",
]


def classify_raw_item(
    *,
    category: str,
    title: str,
    description: str,
) -> tuple[RawDisposition, str]:
    text = f"{title} {description}".strip()
    lowered = text.lower()

    if any(token in lowered for token in ("模块名称", "模块简称", "文档编号", "项目编号")):
        return ("metadata", "Module/document metadata should not enter the formal requirement pool.")

    if "待确认" in text or "需确认" in text:
        return ("open_issue", "The raw item still depends on unresolved confirmation or project decision.")

    if any(token in lowered for token in ("rom/ram", "资源", "resource")):
        return ("constraint", "Resource budget statements should stay as nonfunctional constraints.")
    if any(token in lowered for token in ("misra", "编码规范", "coding standard")):
        return ("constraint", "Coding-standard statements should stay as compliance constraints, not functional requirements.")
    if any(token in lowered for token in ("memmap", "代码段", "常量区", "段布局")):
        return ("constraint", "Memory-section organization should stay as implementation and architecture constraint.")
    if any(token in lowered for token in ("评估记录", "review record", "记录")):
        return ("evidence", "Review/evaluation recording statements are evidence obligations, not formal software behavior.")
    if any(token in lowered for token in ("多核", "per-core", "独立运行时", "独立数据区", "运行时容器")):
        return ("architecture_seed_only", "Multi-core ownership statements should directly guide architecture freezing.")
    if any(token in lowered for token in ("参数有效性检查", "det错误检测", "det ", "e_ok/e_not_ok", "同步接口", "异步接口")):
        return ("constraint", "Interface contract and diagnostic policy statements should stay as governing constraints.")

    if category == "NFR":
        if any(token in lowered for token in ("asil", "qm", "安全等级", "安全要求")):
            return ("constraint", "Safety level statements are governing constraints rather than direct functional requirements.")
        if any(token in lowered for token in ("安全机制", "安全约束")):
            return ("constraint", "Safety-governance statements are constraints and should not silently become formal behavior.")

    if category in {"FUNC", "CFG"}:
        if _looks_like_chip_capability(text):
            return ("capability", "The statement currently looks like a chip/project capability summary rather than an implementation-ready formal requirement.")

    return ("formal_requirement", "The raw item is currently eligible to enter the formal requirement pool.")


def _looks_like_chip_capability(text: str) -> bool:
    lowered = text.lower()
    capability_patterns = (
        "能力",
        "支持通过",
        "支持中断检测和响应机制",
        "支持极性反转配置",
        "支持通过i2c总线访问",
        "支持通过spi访问",
        "支持通过spi总线访问",
        "支持读取设备模式",
        "支持故障清除和看门狗相关模式控制",
    )
    if any(pattern in text for pattern in capability_patterns):
        return True
    if re.search(r"支持.+能力", text):
        return True
    if re.search(r"支持通过(?:i2c|spi).+访问", lowered):
        return True
    if "chip" in lowered and "support" in lowered:
        return True
    return False
