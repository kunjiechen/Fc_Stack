# FC软件架构校验精简版

说明：
- 本模板用于默认“校验精简版”FC 软件架构输出。
- 本模板强调对外可读性、架构结果表达和必要校验结论，不展开需求抽取过程、反向追踪表、候选接口清单、遗漏矩阵和低置信度接口分析。
- 外部接口和依赖接口的描述应优先使用英文。
- 本模板默认包含以下 10 个章节。

## 1. FC总结介绍

- 架构版本: `V1` / `V2` / `V3`
- 架构状态: `Draft` / `Released`
- 生成时间:
- 变更点总结: (初版写“初版生成”；升级/更新时用一句话概括主要变化)
- FC名称:
- FC功能介绍: (中文完整句子；层级名、接口名、架构术语可保留英文)
- 应用场景: (中文完整句子；层级名、接口名、架构术语可保留英文)
- 架构设计思路: (中文完整句子；层级名、接口名、架构术语可保留英文)
- AUTOSAR架构层级:
- 当前软件架构所处层级: (e.g. `IoExtDev`, `IoHwAb`, `Cdd`, `Srv`)

说明：
- 当前软件架构所处层级填写项目的正式层级名，如 `IoExtDev`、`IoHwAb`、`Srv`、`Cdd` 等。
- 若项目已有固定层级归属，直接落正式结论，不展开过程性讨论。
- 版本号仅使用 `V1`、`V2`、`V3` 这种整数大版本，不使用 `V1.0`、`V1.1`。
- 仅需求文档输入时生成 `V1`；正式架构文件 + 需求文档输入时升级到下一大版本；草稿架构更新不升级版本。

## 2. 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| `FC-FR-001` | 中文需求摘要。 | `FC_Init` / configuration / runtime state / dependency / MemMap / file carrier. | Covered | 简要说明覆盖结论。 |

说明：
- 本表是校验结论，不是需求抽取调试表。
- 不展示候选接口、反向追踪过程、低置信度推理过程或遗漏矩阵。
- `Coverage Status` 取值：`Covered`、`Partially Covered`、`Pending Confirmation`。

## 3. 外部接口设计

每个函数优先单独描述，避免 PDF 生成时因超宽表格影响可读性。

### 3.x `FC_FunctionName`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType FC_GetXxx(uint16 Id_u16, uint32* Xxx_pu32)` | English description here. | Synchronous | Reentrant | `E_OK` / `E_NOT_OK` | Initialization dependency, parameter validity, core ownership, pointer non-null. |

说明：
- 接口原型按项目正式风格展示，写出完整 C 函数原型。
- 函数名前缀必须保留输入中的 FC/驱动名称，不得自动 CamelCase 化。例如驱动名称为 `Gp_DRV8889` 时，应使用 `Gp_DRV8889_Init`，不得使用 `GpDrv8889_Init`。
- `Description` 使用英文完整句子。
- `Basic Constraints` 简述初始化前置条件、参数范围、输出指针非空、当前核归属、调用时序等。
- `Init` 和 `MainFunction`（如存在）也必须列入本节。
- 所有对外接口在此列出，不做接口遗漏。
- 若接口很短，可合并为一个总表；若接口描述、约束或原型较长，必须使用单函数小表。

## 4. 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `FC_CFG_DEV_ERROR_DETECT` | Global feature switch for development error detection. | Macro | `STD_ON` | Requirement/rule evidence for parameter checking or DET. | `FC_Cfg.h`, external API parameter checks. | `Formal` |

说明：
- 仅体现通过必要性检查的正式配置宏参。
- `Macro or Parameter` 必须是全大写 C 宏标识符，只允许 `A-Z`、`0-9`、`_`；FC 名称部分也必须转为大写，例如 `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`，不得写成 `Gp_NCA9539_CFG_...`。
- 不体现各核内配置宏参（如 `CORE0_ENABLE` ~ `CORE5_ENABLE`）、各核实例数（如 `MULTI_CHIP_NUM_IN_COREx`）、核内映射表、硬件绑定明细。
- 如果某子功能已存在正式外部接口控制，则不再重复体现该子功能配置宏开关，除非需求明确要求编译期开关。
- 行为选择宏不是强制项；只有确实存在编译期实现分支时才保留。
- 不为运行态变量、标定参数、每个外部接口、内部 helper 或硬件映射项生成宏。
- 缺少证据、使用位置或默认值来源的宏应降级为 `Conditional`、`Pending Confirmation` 或 `Not Recommended`。

## 5. 全局变量与运行态策略

状态：`Empty`

说明：
- 架构不允许对外提供全局变量输出。
- 若无用户明确指令，本节保持 `Empty`。
- 可补充内部运行态策略摘要，但不得列出对外全局变量。

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Init state / request cache / status cache / fault state | Internal runtime container. | Internal API and `MainFunction`. | Initialized in `Init`, updated during runtime. | Runtime RAM. | Per-core ownership or protected access. |

## 6. 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | 外部接口函数实现和内部静态函数代码段。 | `FC_CODE_START` | `FC_CODE_STOP` | `FC.h`, `FC.c` | 正式推荐。 |
| RUNTIME RAM | 运行态变量、请求缓存、状态缓存、故障状态。 | `FC_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `FC_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `FC.c` | 默认使用 `CLEAR_FAR_DATA`；多核可用 `COREx` 代表同构段。 |
| CONST | 配置常量、映射表、阈值表和项目数据。 | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `FC_Cfg.c`, `FC_CfgData.h` | 正式推荐。 |
| CONST PER-CORE | 按核隔离或按核复制的 static const 配置常量。 | `FC_CONST_FAR_DATA_ALIGN4_COREx_START` | `FC_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `FC_Cfg.c`, `FC_CfgData.h` | 多核 const 数据存在核内归属时必须体现；可用 `COREx` 代表同构段。 |
| CALIB | 标定常量段。 | `FC_CONST_FAR_DATA_ALIGN4_CALI_START` | `FC_CONST_FAR_DATA_ALIGN4_CALI_STOP` | `FC_Cali.c` / `FC_CfgData.h` | 仅在存在确认标定参数时产生实际内容。 |

说明：
- 本节采用完整版 MemMap 输出形态。
- 若存在多核按核分段，可使用 `COREx` 总结同构规律，但不得遗漏判断架构正确性所需的段类别。
- `CONST` 不能默认只给 GLOBAL；若存在按核 const 对象、每核配置表或每核 static const 数据，必须增加 `CONST PER-CORE`。
- 不将 `NO_CLEAR`、`NEAR` 等条件段作为默认正式推荐；仅在需求明确要求时才体现，并在 Notes 中说明依据。

## 7. 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。 | `Empty` |

说明：
- 若存在正式标定参数，应体现参数名、类型、初始值和描述。
- 若无明确标定需求，不得为填表而虚构标定项；使用上方的 `Empty` 行即可。
- `Status` 取值：`Formal`（需求明确确认）、`Conditional`（待确认）、`Empty`（无标定项）。

## 8. 依赖接口设计

每个依赖接口优先单独描述，避免 Callout 原型、约束、证据和实现边界导致表格过宽。

### 8.x `FC_CalloutFunctionName`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType FC_CalloutSpiTransceive(uint16 Id_u16, uint16* TxData_pu16, uint16* RxData_pu16, uint16 Size_u16)` | Performs a full-duplex SPI transceive operation using 16-bit protocol frames. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on communication failure. | Pointer parameters must be non-null. `Size_u16` is the number of 16-bit frames. | IoMcu / Project Adaptation | SPI external device register access. | `Formal` |

说明：
- 本节仅体现依赖接口（Callout 原型、宏替换钩子），不与 FC 对外接口混排。
- `Description` 使用英文完整句子。
- 当 FC 需要操作 DIO、PWM、ADC、SPI、外部芯片引脚/寄存器或平台资源时，应抽象为依赖接口/Callout。
- 每个依赖接口必须展示完整 C 原型、英文描述、同步/异步、可重入性、返回值语义、基本约束、实现边界、证据和状态。
- 依赖接口/Callout 函数名前缀必须保留输入中的 FC/驱动名称。例如驱动名称为 `Gp_DRV8889` 时，应使用 `Gp_DRV8889_CalloutSpiTransceive`，不得使用 `GpDrv8889_CalloutSpiTransceive`。
- 若依赖接口较多或内容较长，必须使用单函数小表；只有依赖接口很短时才允许合并为一个总表。
- Callout 原型中不允许使用数组形参写法（如 `TxData_au8[]`），必须使用指针形参。
- SPI/I2C transfer size 默认使用 `uint16 Size_u16`；16bit SPI 帧使用 `uint16*` 数据指针，byte-oriented I2C 使用 `uint8*` 数据指针。
- `Implemented By` 可为 `MCAL`、`IoMcu`、`IoExtDev`、`Service Layer` 或 `Project Adaptation`。
- 不允许 FC 直接调用裸 MCAL API、直接操作寄存器、直接绑定具体 DIO/PWM/ADC/SPI driver，或在外部 FC API 中泄漏底层驱动细节。

## 9. 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `FC.c` | Required | 模块实现文件。 | 外部接口实现、内部静态函数、运行态容器访问。 |
| `FC.h` | Required | 对外接口头文件。 | 外部 API 原型、对外类型引用。 |
| `FC_Types.h` | Required | 类型定义头文件。 | 枚举、结构体、位定义、公开类型。 |
| `FC_Cfg.h` | Required | 配置宏头文件。 | 全局开关、基础宏、编译期行为选择。 |
| `FC_Cfg.c` | Required | 配置数据实现文件。 | 配置常量、映射表、项目数据。 |
| `FC_CfgData.h` | Required | 配置数据声明头文件。 | 配置表类型、外部配置数据声明。 |
| `FC_Reg.h` | Conditional | 外设寄存器定义头文件。 | SPI/I2C 外设寄存器地址、位定义、命令字、协议帧常量；涉及寄存器通信的外设必须增加。 |
| `FC_Callout.h` | Conditional | 平台适配接口头文件。 | Callout 原型、项目适配契约。 |
| `FC_Callout.c` | Conditional | 平台适配实现文件。 | Callout 适配实现或集成 stub；存在 Callout 依赖时必须列出。 |
| `FC_MemMap.h` | Required | 内存段映射头文件。 | 模块 MemMap 宏与集成映射入口。 |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `FC_Cfg.h` | `Std_Types.h` (external) | 引用 `Std_ReturnType`、`uint8/uint16/uint32`、`boolean`、`STD_ON/STD_OFF` 等平台标准类型和宏；`Std_Types.h` 不由本 FC 创建。 |
| `FC_Reg.h` | `Std_Types.h` (external) | 外设寄存器地址、位定义、命令字和协议帧常量依赖标准整数类型；`Std_Types.h` 不由本 FC 创建。 |
| `FC_Cfg.h` | `FC_Reg.h` | 当配置宏、寄存器默认值或配置表使用寄存器符号时，`Cfg.h` 包含 `Reg.h`。 |
| `FC_Types.h` | `FC_Cfg.h` | 类型定义依赖配置宏、标准类型和基础开关。 |
| `FC_Callout.h` | `FC_Types.h` | Callout 原型引用 FC 公开类型和标准类型。 |
| `FC.h` | `FC_CfgData.h` | 暴露正式外部 API，并通过 `CfgData` 间接获得公开类型和配置数据声明。 |
| `FC.c` | `FC.h`, `FC_Callout.h`, `FC_MemMap.h` | 实现对外接口，通过 `FC.h` 获取 API/类型，通过 Callout 访问平台依赖，通过 MemMap 放置代码和运行态数据。 |
| `FC_Cfg.c` | `FC_CfgData.h`, `FC_MemMap.h` | 定义配置表和项目数据，受 MemMap 管理。 |
| `FC_CfgData.h` | `FC_Types.h` | 声明配置数据类型和外部配置对象。 |
| `FC_Callout.c` | `FC_Callout.h`, `FC_MemMap.h` | 实现或承载项目适配层 Callout stub，通过 MemMap 放置适配代码。 |
| `FC_Cali.c` | `FC_CfgData.h`, `FC_MemMap.h` | 可选；仅在存在正式标定参数时定义标定数据。 |
| `FC_MemMap.h` | 所有 FC-created section-managed files | 被所有需要放置代码、运行态数据、const 数据或标定数据的 FC 文件在段边界处包含。 |

说明：
- 文件名和 C 标识符中的 `FC` 应替换为实际模块名前缀，并保留输入中的下划线和大小写。
- 不在本节列出内部学习记录、规则文件或 demo 文件。
- `Std_Types.h` 等平台标准头文件应体现在文件关系中，但不列入本 FC 的待创建文件列表。
- 若 FC 涉及 SPI/I2C 寄存器通信，必须增加 `FC_Reg.h`。
- 若 FC 存在 Callout 依赖，必须同时列出 `FC_Callout.h` 与 `FC_Callout.c`。
- `_MemMap.h` 应作为所有 section-managed FC 文件的包含关系体现。

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
- 本节压缩呈现遗漏风险、假设、弱证据和待确认项。
- 不输出候选接口清单、反向追踪矩阵、遗漏矩阵或低置信度接口调试过程。
- 每条风险项必须有稳定索引，便于用户在窗口中直接引用。
- 必须保留 `R-OTHER` / `其他` 行，供用户自行填写其他方面的建议。
- `备注` 用于记录用户的具体确认意见或修改意见。
- 若任一真实风险项仍为 `待评审` 或 `待修改`，架构状态必须保持 `Draft`。
- 所有真实风险项均为 `已评审` 后，才允许从 `Draft` 升级为 `Released`，且草稿发布不升级版本号。

## 附录：架构元信息

- 架构版本: `V1` / `V2` / `V3`
- 架构状态: `Draft` / `Released`
- 生成时间:
- 生成/修订说明:
- 版本策略: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。
- 发布条件: 所有真实风险项均为 `已评审`。
- 变更点总结【简洁版】:
  - 初版生成 / 草稿更新 / 正式版本升级。
  - 主要接口、配置、依赖、MemMap、文件结构或风险状态变化。

## 下一步：评审与发布引导

当架构状态为 `Draft` 时必须输出本节：

- 推荐评审方式 1：直接修改第 10 章风险表中的 `状态` 和 `备注`。
- 推荐评审方式 2：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：按 xxx 方案调整`。
- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。
- 如果某项需要修改，可回复：`R5 待修改，备注：改为 MainFunction 轮询完成状态`。
- 修改完成后仍保持当前版本的 `Draft`，直到所有真实风险项均为 `已评审` 后发布为 `Released`。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
