#!/usr/bin/env python3
"""Gate classification regression — verifies raw item → disposition mapping.

Each test case is a (category, title, description) tuple with an expected
disposition.  When the gate rules change, this catches unintended regressions
before they reach the full pipeline.

Usage:
  python3.11 scripts/check_gate_regression.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the skill src/ is on the path
_SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SKILL_ROOT / "src"))

from fc_requirement_workbench.raw_classification import classify_raw_item

# (category, title, description, expected_disposition, source_section)
# fmt: off
CASES = [
    # ---- Metadata exclusions ----
    ("FUNC", "模块名称", "模块名称 Gp_IoMcuDio", "metadata", ""),
    ("FUNC", "文档编号", "文档编号 REQ-001", "metadata", ""),
    ("FUNC", "项目编号", "项目编号 P2024", "metadata", ""),

    # ---- Open issues ----
    ("FUNC", "待确认项", "待确认的功能描述", "open_issue", ""),
    ("INTF", "需确认接口", "需确认的接口定义", "open_issue", ""),

    # ---- Resource constraints ----
    ("NFR", "ROM/RAM资源", "ROM/RAM 资源消耗需要评估", "constraint", ""),
    ("FUNC", "资源约束", "资源消耗需在预算内", "constraint", ""),

    # ---- Coding standard constraints ----
    ("NFR", "MISRA", "MISRA C 编码规范要求", "constraint", ""),
    ("FUNC", "编码规范", "编码规范检查", "constraint", ""),

    # ---- Memory section constraints ----
    ("NFR", "MemMap", "需要保留 MemMap 分段", "constraint", ""),
    ("FUNC", "代码段布局", "代码段组织约束", "constraint", ""),

    # ---- Evidence / review records ----
    ("NFR", "评估记录", "评估记录需要保留", "evidence", ""),
    ("FUNC", "结论项", "保留本次评审结论", "evidence", "评审记录"),

    # ---- Architecture seed only ----
    ("CFG", "多核使能", "多核使能配置（每核独立开关）", "architecture_seed_only", ""),
    ("FUNC", "独立运行时", "每个核独立运行时容器", "architecture_seed_only", ""),

    # ---- Sync/async constraints ----
    ("NFR", "同步接口", "同步接口，无 MainFunction", "constraint", ""),
    ("NFR", "异步接口", "异步接口调用策略", "constraint", ""),

    # ---- DET/diagnostic constraints (INTF/FUNC only) ----
    ("INTF", "参数有效性检查", "所有接口必须支持参数有效性检查", "constraint", ""),
    ("FUNC", "DET错误检测", "DET 错误检测开关", "constraint", ""),
    # NFR DET items correctly pass through (category guard)
    ("NFR", "DET错误检测", "DET 错误检测：未初始化访问返回 E_NOT_OK", "formal_requirement", ""),

    # ---- Safety-level constraints (NFR only) ----
    ("NFR", "安全等级", "安全等级 QM", "constraint", ""),
    ("NFR", "ASIL", "ASIL B 安全要求", "constraint", ""),
    ("NFR", "安全机制", "安全机制约束", "constraint", ""),

    # ---- Chip capability detection ----
    ("FUNC", "配置管理", "驱动需要支持通过 uint16 信号 ID 访问 DIO 通道", "capability", ""),
    ("CFG", "能力声明", "支持通过 SPI 总线访问寄存器", "capability", ""),

    # ---- Formal requirement (no gate matches) ----
    ("FUNC", "初始化", "支持上电初始化，对已配置 DIO 通道设置初始默认值", "formal_requirement", ""),
    ("INTF", "Init", "Init(void) - 初始化当前核所有已配置 DIO 通道", "formal_requirement", ""),
    ("INTF", "SetDioSigDir", "SetDioSigDir(uint16 Id, Dir) - 返回 E_OK/E_NOT_OK", "formal_requirement", ""),
    ("INTF", "GetDioSigLvlIn", "GetDioSigLvlIn(uint16 Id, boolean* LvlIn) - 返回 E_OK/E_NOT_OK", "formal_requirement", ""),
    ("INTF", "SetDioSigLvlOut", "SetDioSigLvlOut(uint16 Id, boolean LvlOut) - 返回 E_OK/E_NOT_OK", "formal_requirement", ""),
    ("CFG", "信号映射", "信号 ID 映射表（信号 ID → 物理端口/Pin）", "formal_requirement", ""),
    ("CFG", "默认方向", "默认方向配置（输入/输出）", "formal_requirement", ""),
]
# fmt: on


def main() -> int:
    failures: list[str] = []
    passed = 0

    for category, title, description, expected, source_section in CASES:
        disposition, reason = classify_raw_item(
            category=category,
            title=title,
            description=description,
            source_section=source_section,
        )
        if disposition == expected:
            passed += 1
        else:
            failures.append(
                f"  [{category}] \"{title}\" → {disposition} (expected {expected})\n"
                f"    reason: {reason}"
            )

    if failures:
        print(f"Gate regression: {len(failures)} failure(s) out of {len(CASES)} cases:\n")
        for f in failures:
            print(f)
        return 1

    print(f"Gate regression: all {passed} cases passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
