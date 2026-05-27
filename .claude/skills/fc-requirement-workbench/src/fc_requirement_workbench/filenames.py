"""Centralized output filenames for requirement workflow artefacts."""

from __future__ import annotations


def srs_doc(module: str) -> str:
    return f"{module}_软件需求规范.md"


def source_index_doc(module: str) -> str:
    return f"{module}_SRS输入资料索引.md"


def source_extract_doc(module: str) -> str:
    return f"{module}_SRS来源内容抽取表.md"


def derivation_doc(module: str) -> str:
    return f"{module}_SRS需求推导矩阵.md"


def open_items_doc(module: str) -> str:
    return f"{module}_SRS开放项登记表.md"


def gate_report_doc(module: str) -> str:
    return f"{module}_SRSGate自检报告.md"


def check_list_doc(module: str) -> str:
    return f"Check_{module}_软件需求规范.md"


def review_doc(module: str) -> str:
    return f"Review_{module}_软件需求规范.md"


def trace_matrix_doc(module: str) -> str:
    return f"Trace_{module}_软件需求规范.md"


def operation_steps_doc(module: str) -> str:
    return f"{module}_SRS操作步骤.md"


def post_generation_guide_doc(module: str) -> str:
    return f"{module}_SRS生成后引导.md"


def next_step_message_doc(module: str) -> str:
    return f"{module}_SRS下一步操作提示.md"
