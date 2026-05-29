# 《`<FC>` 软件架构设计》

**`<FC>`_软件架构设计**

**`<FC>` Software Architecture Design**

项目编号/Project number: `<FC>`
保密性/Security: 内部

**Document Properties**
Status: **草稿**
架构版本: **V1**
架构状态: **Draft**
Author: FC Architecture Workbench
Created: `<GenerationTime>`

**Approved Versions**

Current Document version **V1** is **Draft**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| V1 | Draft | TBD | TBD | TBD |

## 适用说明

本文档适用于 `<FC>` 模块的软件架构设计定义。本文档描述模块的外部接口、依赖接口、配置宏参、运行时策略、内存分配与文件族设计，不描述详细实现方案、代码细节或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| V1 | `<GenerationDate>` | FC Architecture Workbench | `<ChangeSummary>` | Draft |

---

## 目录

- [1 FC总结介绍](#1-fc总结介绍)
- [2 需求覆盖表](#2-需求覆盖表)
- [3 外部接口设计](#3-外部接口设计)
- [4 配置宏参设计](#4-配置宏参设计)
- [5 全局变量与运行态策略](#5-全局变量与运行态策略)
- [6 内存分配宏定义](#6-内存分配宏定义)
- [7 全局标定参数设计](#7-全局标定参数设计)
- [8 依赖接口设计](#8-依赖接口设计)
- [9 文件列表与文件关系](#9-文件列表与文件关系)
- [10 架构风险与待确认](#10-架构风险与待确认)
- [附录：架构元信息](#附录架构元信息)

---

## 1. FC总结介绍

- **架构版本**: `V1` / `V2` / `V3`
- **架构状态**: `Draft` / `Released`
- **生成时间**: `<GenerationTime>`
- **变更点总结**: (初版写“初版生成”；升级/更新时用一句话概括主要变化)
- **FC名称**: `<FC>`
- **FC功能介绍**: (中文完整段落；层级名、接口名、架构术语可保留英文)
- **应用场景**: (中文完整段落；层级名、接口名、架构术语可保留英文)
- **架构设计思路**: (中文完整段落；层级名、接口名、架构术语可保留英文)
- **AUTOSAR架构层级**:
- **当前软件架构所处层级**: (e.g. `IoExtDev`, `IoHwAb`, `Cdd`, `Srv`)

说明：
- 当前软件架构所处层级填写项目的正式层级名，如 `IoExtDev`、`IoHwAb`、`Srv`、`Cdd` 等。
- 若项目已有固定层级归属，直接落正式结论，不展开过程性讨论。
- 版本号仅使用 `V1`、`V2`、`V3` 这种整数大版本，不使用 `V1.0`、`V1.1`。
- 仅需求文档输入时生成 `V1`；正式架构文件 + 需求文档输入时升级到下一大版本；草稿架构更新不升级版本。

---

## 2. 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| `FC-FR-001` | 中文需求摘要。 | `FC_Init` / configuration / runtime state / dependency / MemMap / file carrier. | Covered | 简要说明覆盖结论。 |

说明：
- 本表是校验结论，不是需求抽取调试表。
- 不展示候选接口、反向追踪过程、低置信度推理过程或遗漏矩阵。
- `Coverage Status` 取值：`Covered`、`Partially Covered`、`Pending Confirmation`。

---

## 3. 外部接口设计

每个函数优先单独描述，避免 PDF 生成时因超宽表格影响可读性。

### 3.x `FC_FunctionName`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType FC_GetXxx(uint16 Id_u16, uint32* Xxx_pu32)` | English description of what this function does, when it should be called, and what it returns. | Synchronous / Asynchronous | Reentrant / Non-reentrant | `E_OK` on success; `E_NOT_OK` if ... | Initialization dependency, parameter validity, core ownership, pointer non-null, state constraints. |

说明：
- 接口原型按项目正式风格展示，写出完整 C 函数原型。
- 函数名前缀必须保留输入中的 FC/驱动名称，不得自动 CamelCase 化。例如驱动名称为 `Gp_DRV8889` 时，应使用 `Gp_DRV8889_Init`，不得使用 `GpDrv8889_Init`。
- `Description` 使用英文完整句子，描述函数做什么、何时调用、返回值含义。
- `Basic Constraints` 简述初始化前置条件、参数范围、输出指针非空、当前核归属、调用时序等。
- `Init` 和 `MainFunction`（如存在）必须列入本节。
- 所有对外接口在此列出，不做接口遗漏。
- 若接口很短，可合并为一个总表；若接口描述、约束或原型较长，必须使用单函数小表。
- 若存在故障检测、诊断判定或异常状态上报，本节默认应包含一个可读取的故障/诊断状态接口。

---

## 4. 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `FC_CFG_DEV_ERROR_DETECT` | Global feature switch for development error detection. Controls DET reporting for invalid parameters, uninitialized access, and null pointer checks. | Macro | `STD_ON` | Requirement/rule evidence for parameter checking or DET. | `FC_Cfg.h`, external API parameter checks. | `Formal` |

说明：
- 仅体现通过必要性检查的正式配置宏参。
- `Macro or Parameter` 必须是全大写 C 宏标识符，只允许 `A-Z`、`0-9`、`_`；FC 名称部分也必须转为大写。
- 不体现各核内配置宏参（如 `CORE0_ENABLE` ~ `CORE5_ENABLE`）、各核实例数、核内映射表、硬件绑定明细。
- 如果某子功能已存在正式外部接口控制，则不再重复体现该子功能配置宏开关，除非需求明确要求编译期开关。
- 行为选择宏不是强制项；只有确实存在编译期实现分支时才保留。
- 不为运行态变量、标定参数、每个外部接口、内部 helper 或硬件映射项生成宏。
- 缺少证据、使用位置或默认值来源的宏应降级为 `Conditional`、`Pending Confirmation` 或 `Not Recommended`。
- `Status` 取值：`Formal`（需求明确确认）、`Conditional`（待条件满足）、`Pending Confirmation`（待确认）、`Not Recommended`。

---

## 5. 全局变量与运行态策略

状态：`Empty` — 架构不允许对外提供全局变量输出。

内部运行态策略：

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Driver state machine (per core) | Internal static variable in `FC.c` | Read by all external APIs for state check; written by Init and MainFunction. | Set to UNINIT at module load; transitions managed by Init and MainFunction. | `CLEAR_FAR_DATA` per core | Per-core ownership; no cross-core access. |
| Runtime data container (per core) | Internal static struct/array in `FC.c` | Read by getter APIs; written by Init, setter APIs, and MainFunction. | Allocated per core; initialized in Init; updated during MainFunction cycles. | `CLEAR_FAR_DATA` per core | Per-core ownership. |

说明：
- 若无用户明确指令，本节对外全局变量保持 `Empty`。
- 内部运行态策略表用于说明运行时数据的归属、读写关系和生命周期。

---

## 6. 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | All external API implementations and internal static helper functions. | `FC_CODE_START` | `FC_CODE_STOP` | `FC.c`, `FC_Callout.c` | Standard CODE section for driver logic. |
| RUNTIME RAM (per core) | All runtime state: driver state machine, runtime data containers, caches, fault counters/state. | `FC_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `FC_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `FC.c` | Default `CLEAR_FAR_DATA`; per-core with `COREx` notation. No `NO_CLEAR` needed unless warm-reset retention is required. No `NEAR` needed unless high-frequency ISR access path exists. |
| CONST (global shared) | Configuration data shared across cores: register default values, address constants, version information. | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `FC_Cfg.c`, `FC_CfgData.h` | For truly shared configuration constants accessible from all cores. |
| CONST (per core) | Per-core configuration tables: SigMapping tables, per-core instance configuration, per-core chip index mapping. | `FC_CONST_FAR_DATA_ALIGN4_COREx_START` | `FC_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `FC_Cfg.c`, `FC_CfgData.h` | Each core has its own configuration data region. `COREx` notation represents the repeated pattern for all managed cores. |
| REG CONST | Register address constants, bit masks, command bytes, and protocol constants for register-based external devices. | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `FC_Reg.h` | Register definitions are shared across all cores. Placed in global CONST section. Required when FC controls SPI/I2C/register-based external devices. |
| CALIB | Calibration constants. | `FC_CONST_FAR_DATA_ALIGN4_CALI_START` | `FC_CONST_FAR_DATA_ALIGN4_CALI_STOP` | `FC_Cali.c` / `FC_CfgData.h` | Only present when real calibration parameters are confirmed; otherwise reserved for future use. |

说明：
- 本节采用完整版 MemMap 输出形态。
- 若存在多核按核分段，可使用 `COREx` 总结同构规律，但不得遗漏判断架构正确性所需的段类别。
- `CONST` 不能默认只给 GLOBAL；若存在按核 const 对象、每核配置表或每核 static const 数据，必须增加 `CONST (per core)`。
- 涉及 SPI/I2C/寄存器通信的外设 FC，必须独立列出 `REG CONST` 行，不得将其合并到 `CONST` 中。
- 不将 `NO_CLEAR`、`NEAR` 等条件段作为默认正式推荐；仅在需求明确要求时才体现，并在 Notes 中说明依据。

---

## 7. 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。阈值和时序参数均归类为编译期项目配置（`Cfg`），不属于标定流程可调参数。 | `Empty` |

说明：
- 若存在正式标定参数，应体现参数名、类型、初始值和描述。
- 若无明确标定需求，不得为填表而虚构标定项；使用上方的 `Empty` 行即可。
- `Status` 取值：`Formal`（需求明确确认）、`Conditional`（待确认）、`Empty`（无标定项）。

---

## 8. 依赖接口设计

每个依赖接口优先单独描述，避免 Callout 原型、约束、证据和实现边界导致表格过宽。

### 8.x `FC_CalloutFunctionName`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType FC_CalloutXxx(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` | English description of what this callout does, when the FC calls it, and what it returns. | Synchronous / Asynchronous | Reentrant / Non-reentrant | `E_OK` on success; `E_NOT_OK` on failure. | Pointer parameters must be non-null. `Size_u16` is the number of bytes/frames. Callout implementation must be reentrant. | MCAL / IoMcu / IoExtDev / Service Layer / Project Adaptation | Requirement or architecture evidence for this dependency. | `Formal` / `Conditional` / `Pending Confirmation` |

说明：
- 本节仅体现依赖接口（Callout 原型、宏替换钩子），不与 FC 对外接口混排。
- `Description` 使用英文完整句子。
- 当 FC 需要操作 DIO、PWM、ADC、SPI、I2C、外部芯片引脚/寄存器或平台资源时，应抽象为依赖接口/Callout。
- 每个依赖接口必须展示完整 C 原型、英文描述、同步/异步、可重入性、返回值语义、基本约束、实现边界、证据和状态。
- 依赖接口/Callout 函数名前缀必须保留输入中的 FC/驱动名称。
- 若依赖接口较多或内容较长，必须使用单函数小表；只有依赖接口很短时才允许合并为一个总表。
- Callout 原型中不允许使用数组形参写法（如 `TxData_au8[]`），必须使用指针形参。
- SPI/I2C transfer size 默认使用 `uint16 Size_u16`；16bit SPI 帧使用 `uint16*` 数据指针，byte-oriented I2C 使用 `uint8*` 数据指针。
- `Implemented By` 可为 `MCAL`、`IoMcu`、`IoExtDev`、`Service Layer` 或 `Project Adaptation`。
- `Status` 取值：`Formal`、`Conditional`、`Pending Confirmation`、`Not Recommended`。
- 不允许 FC 直接调用裸 MCAL API、直接操作寄存器或直接绑定具体驱动。

---

## 9. 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `FC.c` | Required | Driver implementation file. | External API implementations, internal static helper functions, per-core runtime state containers. |
| `FC.h` | Required | External interface header file. | External API prototypes, `CODE_START/STOP` section macros. |
| `FC_Types.h` | Required | Type definitions header file. | State enums, runtime container structs, configuration container structs, mapping entry structs, fault status bit definitions. |
| `FC_Cfg.h` | Required | Configuration macro header file. | Feature switches, version macros, behavior selection macros. Includes `Std_Types.h` and `FC_Reg.h` (when register symbols are referenced). |
| `FC_Cfg.c` | Required | Configuration data implementation file. | Per-core configuration tables (instance count, per-instance config, SigMapping table), const data under MemMap. |
| `FC_CfgData.h` | Required | Configuration data declaration header file. | `extern` declarations for configuration tables and containers, configuration struct type forward references. |
| `FC_Reg.h` | Conditional | Register definition header file for SPI/I2C/register-based external devices. | Register addresses, bit masks, command words, protocol frame constants, register reset default values. Required when FC controls register-based external devices. |
| `FC_Callout.h` | Conditional | Platform adaptation interface header file. | Callout prototypes for hardware and platform dependencies. Required when Callout dependencies exist. |
| `FC_Callout.c` | Conditional | Platform adaptation implementation file. | Callout integration stubs or project adaptation implementations. Required when Callout dependencies exist. |
| `FC_MemMap.h` | Required | Memory section mapping header file. | MemMap macro definitions for CODE, CONST (global and per-core), and RUNTIME RAM sections. Included by all section-managed FC files. |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `FC_Cfg.h` | `Std_Types.h` (external) | References `Std_ReturnType`, `uint8/uint16/uint32`, `boolean`, `STD_ON/STD_OFF`. `Std_Types.h` is an external platform header, not created by this FC. |
| `FC_Reg.h` | `Std_Types.h` (external) | Register address, bit mask, and protocol frame constants use standard integer types. `Std_Types.h` is not created by this FC. |
| `FC_Cfg.h` | `FC_Reg.h` | When configuration macros, register defaults, or config tables reference register symbols, `Cfg.h` includes `Reg.h`. |
| `FC_Types.h` | `FC_Cfg.h` | Type definitions (enums, structs) depend on configuration macros (e.g., instance count for array sizing, feature switches for struct field inclusion). |
| `FC_Callout.h` | `FC_Types.h` | Callout prototypes reference FC public types and standard types. |
| `FC_CfgData.h` | `FC_Types.h` | Configuration data declarations reference types defined in `Types.h` (config container struct, mapping struct). |
| `FC.h` | `FC_CfgData.h` | External API header exposes public APIs and indirectly obtains type visibility through `CfgData.h` → `Types.h` chain. |
| `FC.c` | `FC.h` | Implements external APIs declared in `FC.h`. |
| `FC.c` | `FC_Callout.h` | Calls hardware and platform callouts for all dependencies. |
| `FC.c` | `FC_MemMap.h` | Places code and runtime data into memory sections via MemMap macros. |
| `FC_Cfg.c` | `FC_CfgData.h` | Defines configuration tables declared in `CfgData.h`. |
| `FC_Cfg.c` | `FC_MemMap.h` | Places configuration const data into memory sections. |
| `FC_Callout.c` | `FC_Callout.h` | Implements callout stubs or project adaptation logic. |
| `FC_Callout.c` | `FC_MemMap.h` | Places callout adaptation code into memory sections. |
| `FC_MemMap.h` | All FC-created section-managed files | Included by `FC.c`, `FC_Cfg.c`, and `FC_Callout.c` at section boundaries for CODE, CONST, and RUNTIME RAM placement. |

说明：
- 文件名和 C 标识符中的 `FC` 应替换为实际模块名前缀，并保留输入中的下划线和大小写。
- 不在本节列出内部学习记录、规则文件或 demo 文件。
- `Std_Types.h` 等平台标准头文件应体现在文件关系中，但不列入本 FC 的待创建文件列表。
- 若 FC 涉及 SPI/I2C/寄存器通信，必须增加 `FC_Reg.h`。
- 若 FC 存在 Callout 依赖，必须同时列出 `FC_Callout.h` 与 `FC_Callout.c`。
- `FC_MemMap.h` 应作为所有 section-managed FC 文件的包含关系体现。

---

## 10. 架构风险与待确认

填写说明：
- 可以直接修改下表的 `状态` 和 `备注`，也可以在当前窗口直接回复，例如：`R1、R3 已评审；R4 待修改，备注：按 xxx 方案调整`。
- `状态` 只允许填写：`待评审`、`已评审`、`待修改`。
- 若某条为 `待修改` 且 `备注` 为空，则默认按 `Recommended Action` 执行修改；若 `备注` 不为空，则优先按备注执行。
- 若希望直接发布，请将所有真实风险项标为 `已评审`，并将 `R-OTHER` 填为 `已评审` / `备注：无其他建议`。

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Pending item | 中文描述风险或待确认问题。 | 中文描述影响范围。 | 中文描述建议动作。 | 用户填写确认意见或修改意见。 | `待评审` |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议 / 用户补充建议。 | `待评审` |

说明：
- 每条风险项必须有稳定索引，便于用户在窗口中直接引用。
- 必须保留 `R-OTHER` / `其他` 行，供用户自行填写其他方面的建议。
- `备注` 用于记录用户的具体确认意见或修改意见。
- 若任一真实风险项仍为 `待评审` 或 `待修改`，架构状态必须保持 `Draft`。
- 所有真实风险项均为 `已评审` 后，才允许从 `Draft` 发布为 `Released`。

---

## 附录：架构元信息

- **架构版本**: `V1` / `V2` / `V3`
- **架构状态**: `Draft` / `Released`
- **生成时间**: `<GenerationTime>`
- **生成/修订说明**:
- **版本策略**: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。
- **发布条件**: 所有真实风险项均为 `已评审`。
- **变更点总结【简洁版】**:
  - 初版生成 / 草稿更新 / 正式版本升级。
  - 外部接口、配置、依赖、MemMap、文件结构或风险状态变化。

---

## 下一步：评审与发布引导

当前架构状态为 **V1 Draft**。请通过以下方式完成评审：

- **推荐评审方式 1**：直接修改第 10 章风险表中的 `状态` 和 `备注` 列。
- **推荐评审方式 2**：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：按 xxx 方案调整`。
- 如果所有风险项均认可，可回复：**`全部已评审，R-OTHER 无其他建议，直接发布`**。
- 如果某项需要修改，可回复：**`R5 待修改，备注：改为 MainFunction 轮询完成状态`**。
- 修改完成后仍保持 `V1 Draft`，直到所有真实风险项均为 `已评审` 后发布为 **V1 Released**。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
