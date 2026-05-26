# Gp_NCA95xx 架构自检清单

## 1. 说明

本文档是 `Gp_NCA95xx_软件架构设计.md` V1 Draft 的架构自检清单，用于在架构评审前确认架构完整性、一致性和规则合规性。

## 2. 检查项

### 2.1 接口完整性

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| Init 接口已定义 | PASS | `Gp_NCA95xx_Init`，含完整属性。 |
| MainFunction 接口已定义 | PASS | `Gp_NCA95xx_MainFunction`，含完整属性。 |
| 所有 SRS INTF 需求均有对应外部接口 | PASS | INTF-0001 ~ INTF-0006 全部覆盖。 |
| Get/Set 语义 API（非 Generic Read/Write） | PASS | GetGpioInSig、SetGpioOutSig、GetDevFaultSig、GetDevModeInSig。 |
| 故障/诊断查询接口已包含 | PASS | GetDevFaultSig + GetDevModeInSig。 |
| 接口原型使用 Std_ReturnType（Init/MainFunction 除外） | PASS | 所有 Get/Set 接口返回 Std_ReturnType。 |
| Getter 接口使用输出指针 | PASS | State_pu8、Fault_pu32、DevMode_pu8。 |
| 不存在对外全局变量暴露 | PASS | 全局变量章节为 Empty。 |
| 函数命名保留 FC 名前缀 | PASS | 所有接口使用 `Gp_NCA95xx_` 前缀。 |

### 2.2 配置分类

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| 配置宏仅用于编译期行为选择/开关 | PASS | DEV_ERROR_DETECT、REG_READBACK_VERIFY_ENABLE、RUNTIME_DIR_CHANGE_ENABLE、RESET_PIN_OWNED、VERSION。 |
| 阈值/映射表/地址放入 CfgData | PASS | DevAddr、DefaultDir、DefaultOut、SigMapCfg、fault thresholds 均为 config data。 |
| 宏标识符 ALL_CAPS | PASS | 全部 `GP_NCA95xx_CFG_*` 大写。 |
| 无重复接口功能开关宏 | PASS | 无接口级一一对应开关。 |
| 无不必要的子功能宏 | PASS | 仅 4 个功能/行为宏 + 2 个版本宏。 |
| 每个宏有默认值、使用位置、证据 | PASS | 见配置宏参设计章节。 |

### 2.3 依赖接口

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| FC 不直接调用 MCAL API | PASS | 全部 I2C/DIO/平台操作通过 Callout 抽象。 |
| FC 不直接操作寄存器 | PASS | 寄存器地址定义在 Reg.h，I2C 操作通过 Callout。 |
| Callout 原型不使用数组形参 | PASS | 全部使用指针形参（`uint8*`、`const uint8*`）。 |
| I2C callout 使用 uint8* + uint16 Size | PASS | I2cWrite: `const uint8* Data_pcu8, uint16 Size_u16`; I2cRead: `uint8* Data_pu8, uint16 Size_u16`。 |
| Callout 有清晰实现边界 | PASS | Project Adaptation / IoMcu / MCAL / Platform Adaptation。 |
| Callout 不在外部 FC API 中混排 | PASS | 依赖接口单独成章。 |
| 依赖接口必要性检查通过 | PASS | 每个 Callout 对应明确的硬件/平台操作需求。 |

### 2.4 运行态与 MemMap

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| 内部运行态容器明确定义 | PASS | 9 个运行态区域均定义了 owner、r/w side、lifecycle、memory section、concurrency。 |
| 默认 RAM 段为 CLEAR_FAR_DATA | PASS | 不使用 NO_CLEAR 或 NEAR（无需求依据）。 |
| CONST 段区分 GLOBAL 和 PER-CORE | PASS | GLOBAL 用于共享定义；COREx 用于每核配置表。 |
| CALIB 段无虚构参数 | PASS | 当前无标定参数，标记 Empty。 |
| MemMap 段数量合理 | PASS | CODE + RUNTIME RAM + CONST GLOBAL + CONST PER-CORE + CALIB(预留)。 |
| MemMap 解释了选段理由 | PASS | 每段均有 Notes 说明。 |

### 2.5 文件结构

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| 标准 FC 文件集完整 | PASS | .c/.h/Types.h/Cfg.h/Cfg.c/CfgData.h/MemMap.h。 |
| Reg.h 已包含（I2C 外设） | PASS | I2C 寄存器地址、位定义、设备地址常量。 |
| Callout.h + Callout.c 已包含 | PASS | 存在 Callout 依赖。 |
| 文件关系表完整 | PASS | 包含外部头文件依赖（Std_Types.h）。 |
| MemMap.h 在所有 section-managed 文件中体现 | PASS | .c、Cfg.c、Callout.c。 |

### 2.6 命名规范

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| 函数前缀保留 FC 名 | PASS | `Gp_NCA95xx_`。 |
| 宏标识符 ALL_CAPS | PASS | `GP_NCA95xx_CFG_*`。 |
| 文件前缀一致 | PASS | 全部 `Gp_NCA95xx_*`。 |
| Callout 前缀一致 | PASS | `Gp_NCA95xx_Callout*`。 |

### 2.7 追溯性

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| 每条 SRS 需求有架构覆盖 | PASS | 35/35 全部覆盖。 |
| 每个架构对象有 SRS 来源 | PASS | 反向追溯矩阵完整。 |
| 无未覆盖的 FUNC/INTF/DIAG/SAFE 需求 | PASS | 全部 Covered 或 Partially Covered（含说明）。 |

### 2.8 风险与发布门禁

| 检查项 | 结果 | 备注 |
| --- | --- | --- |
| 风险表包含稳定索引 | PASS | R1-R7 + R-OTHER。 |
| 风险表有 R-OTHER 行 | PASS | 供用户补充建议。 |
| 架构状态为 Draft | PASS | 存在待评审项。 |
| 发布了下一步引导 | PASS | 评审与发布引导章节。 |

## 3. 总结

- 总检查项: 38
- PASS: 38
- FAIL: 0
- 架构就绪状态: **就绪，可进入评审**

所有检查项均已通过。架构处于 `V1 Draft` 状态，待 7 项风险（R1-R7）评审通过后可发布为 `V1 Released`。
