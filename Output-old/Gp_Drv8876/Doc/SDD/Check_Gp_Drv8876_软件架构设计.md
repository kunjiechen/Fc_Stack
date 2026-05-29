# Check_Gp_Drv8876_软件架构设计

## 检查元信息

- **关联架构文档**: `Gp_Drv8876_软件架构设计.md`
- **架构版本**: V1
- **架构状态**: Draft
- **检查日期**: 2026-05-27
- **检查人**: FC Architecture Workbench (自动)

---

## Gate 检查清单

### Gate 1: 需求覆盖

| 检查项 | 结果 | 证据 | 问题 |
| --- | --- | --- | --- |
| 所有 SRS Func 需求已覆盖 | 通过 | FUNC-0001~0005 全部覆盖 | 无 |
| 所有 SRS 接口需求已覆盖 | 通过 | INTF-0001~0007 全部有对应外部接口 | INTF-0005 (SetHalfBridgeOutSig) 为 Pending Confirmation |
| 所有 SRS 配置需求已覆盖 | 通过 | CFG-0001~0005 均有配置宏或配置表承载 | 无 |
| 所有 SRS 诊断需求已覆盖 | 通过 | DIAG-0001~0004 由 DET 宏 + 接口校验 + MainFunction 采样覆盖 | 无 |
| 所有 SRS 时序需求已覆盖 | 通过 | TIM-0001~0003 由 MainFunction + Delay Callout + 配置约束覆盖 | 无 |
| 所有 SRS 非功能需求已覆盖 | 通过 | SAFE/CODE/RES/COMP 均在架构中体现 | 无 |

### Gate 2: 架构一致性

| 检查项 | 结果 | 证据 | 问题 |
| --- | --- | --- | --- | --- |
| FC 名前缀一致 | 通过 | `Gp_Drv8876` 前缀在所有接口/文件/宏中保持一致 | 无 |
| 配置宏全大写 | 通过 | `GP_DRV8876_CFG_*` 全部大写 + 下划线 | 无 |
| Callout 参数为指针形式 | 通过 | `Raw_pu16`, `RawVld_pb` 等均为指针形参，无数组声明式 | 无 |
| MemMap 包含 per-core CONST | 通过 | CONST (per-core) + CONST (global) 分别列出 | 无 |
| 文件关系包含 MemMap.h | 通过 | `Gp_Drv8876_MemMap.h` 关联到所有 section-managed 文件 | 无 |
| 无 Reg.h 不必要出现 | 通过 | DRV8876 由 DIO/PWM/ADC 控制，无 SPI/I2C 寄存器操作 | 无 |
| Callout.h/.c 成对出现 | 通过 | 依赖接口存在 → 两者均为 Required | 无 |
| 架构版本为整数 | 通过 | `V1` | 无 |

### Gate 3: 架构完备性

| 检查项 | 结果 | 证据 | 问题 |
| --- | --- | --- | --- | --- |
| 外部接口全部列出 | 通过 | 3.1~3.8 每个接口独立描述，含原型/约束/同步性/可重入性 | 无 |
| 依赖接口全部列出 | 通过 | 8.1~8.6 每个 Callout 独立描述，含实现边界/证据/状态 | 无 |
| 配置宏参数已必要性检查 | 部分通过 | DEV_ERROR_DETECT / 版本宏为 Formal；MAINFUNCTION_ENABLE / HALF_BRIDGE_ENABLE 为 Conditional | 条件宏依赖 R2/R3 确认 |
| 运行时状态完整 | 通过 | 7 个内部运行态区域覆盖所有状态机/缓存/去抖/DET 需求 | 无 |
| MemMap 段覆盖所有对象 | 通过 | CODE / CLEAR_FAR_DATA / CONST(per-core+global) 覆盖所有数据 | 无 |
| 风险表完整 | 通过 | R1~R8 + R-OTHER 共 9 个条目 | 无 |
| 输出路径正确 | 通过 | `Output/Gp_Drv8876/Doc/SDD/` | 无 |

### Gate 4: 文件族完整性

| 检查项 | 结果 | 证据 | 问题 |
| --- | --- | --- | --- | --- |
| 必需文件全部列出 | 通过 | .c/.h/Types.h/Cfg.h/Cfg.c/CfgData.h/MemMap.h 共 7 个 Required | 无 |
| 条件文件正确标记 | 通过 | Callout.h/.c 标记为 Required（依赖存在） | 无 |
| 无多余文件 | 通过 | 无 Reg.h（非 SPI/I2C）、无 Cali.c（无标定）、无 Desc 族（简单 FC） | 无 |

---

## 主要问题

| 序号 | 严重度 | 描述 | 关联风险 |
| --- | --- | --- | --- |
| 1 | 高 | PMODE/IMODE 控制方式未确认，影响 Callout 通道数和锁存逻辑 | R1 |
| 2 | 高 | MainFunction 调度策略未确认，影响接口同步语义 | R2 |
| 3 | 中 | 独立半桥模式待确认，影响接口集 | R3 |
| 4 | 中 | 默认安全状态待确认，影响 Init 行为 | R4 |
| 5 | 低 | 电流反馈接口形态待确认 | R5 |
| 6 | 低 | nFAULT 故障位定义待确认 | R6 |
| 7 | 低 | PWM 参数单位待确认 | R7 |
| 8 | 低 | Delay Callout 必要性待确认 | R8 |

---

## 下一步动作

1. 项目确认 R1~R8 各风险项
2. 根据确认结果更新架构文档第 10 章风险表
3. 所有风险项 `已评审` 后更新本检查清单为最终结论
4. 通过后允许进入 SDS/详细设计阶段
