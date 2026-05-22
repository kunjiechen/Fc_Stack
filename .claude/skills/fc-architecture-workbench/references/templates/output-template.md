# FC软件架构定义

说明：
- 本模板用于“完整版本”FC 软件架构定义。
- 若用户要求“精简版本 / 总结版本 / 对外展示版本 / 规则受限版本”，应改用 `output-template-summary.md`，不要直接删减本模板后混用。

## 文档元信息

- 架构版本: `V1` / `V2` / `V3`
- 架构状态: `Draft` / `Released`
- 生成时间:
- 生成/修订说明:
- 变更点总结【简洁版】:

说明：
- 版本号仅使用整数大版本：`V1`、`V2`、`V3`。
- 只有需求文档输入时生成 `V1`。
- 草稿架构文件更新不升级版本。
- 草稿中全部真实风险项均为 `已评审` 后，可从 `Vx Draft` 发布为 `Vx Released`，版本号不变。
- 正式架构文件 + 需求文档输入时升级到下一大版本，例如 `V1 Released -> V2 Released`。

## 0. 抽取与判定总览

### 0.1 需求抽取与分类表

| 需求条目 | 抽取点 | 是否外部接口 | 分类 | 暂定落点 | 判定依据 | 备注/待确认 |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

### 0.2 外部接口候选清单

| 候选接口 | 所属模块 | 来源需求 | 接口类型 | 输入参数 | 输出参数 | 置信度 | 是否保留 | 是否人工确认 | 保留原因/不保留原因 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | 初始化/周期/外部调用/内部接口/回调通知/中断/读/写/配置/标定/诊断/状态查询/OS/MCAL |  |  | 高/中/低 |  | 是/否 |  |  |

### 0.3 配置宏参清单

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | Feature Enable / Development Error Detect / Behavior Selection / Count Size / Timeout Retry Timing / Vendor Version Release |  |  |  | Formal / Conditional / Pending Confirmation / Not Recommended |

说明：
- `Cfg.h` 优先体现基础配置、功能开关、行为选择、实现方式选择。
- `Macro or Parameter` 必须是全大写 C 宏标识符，只允许 `A-Z`、`0-9`、`_`；FC 名称部分也必须转为大写，例如 `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`，不得写成 `Gp_NCA9539_CFG_...`。
- 寄存器初始化、时序、阈值、重试次数等项目参数，优先收敛成 `Cfg.c/CfgData.h` 中的配置表项，不在 `Cfg.h` 逐项展开。
- 已有稳定对外接口承载的基本功能，默认不重复抽成功能开关宏；仅当需求明确要求项目裁剪、编译期切换或变体选择时，才保留对应配置宏参。

## 1. FC概述
- FC名称:
- 核心职责:
- 功能摘要:
- 运行模型:
- 目标场景:

## 2. 设计输入
### 2.1 输入文档
- FC需求:

说明：
- 最终产物中，这里只列用户侧正式输入文档。
- 不在最终产物中列出内部学习记录、规则文件、demo 对照文件等内部参考资料。
- 内部参考仅用于推理，不作为最终输入文档显示。

### 2.2 场景约束
- 平台/芯片:
- MCAL/BSW假设:
- OS假设:
- 多核:
- 多实例:
- 其他约束:

## 3. 假设与缺失信息
- 假设1:
- 假设2:
- 缺失信息1:
- 缺失信息2:

### 3.1 需求中的占位项与未决项
- `TBD`项:
- 缺失附件:
- 未定义信号列表:
- 暂定接口区域:

## 4. 需求到架构映射

| 需求条目 | 抽取含义 | 分类 | 架构落点 | 判定依据 | 待确认问题 |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

### 4.1 接口覆盖率表

| 需求ID | 功能描述 | 对应接口/配置/运行态 | 覆盖状态 | 备注 |
| --- | --- | --- | --- | --- |
|  |  |  | 已覆盖/部分覆盖/待补充 |  |

### 4.2 反向追踪表

| 接口名 | 来源需求ID | 来源类型 | 置信度 | 备注 |
| --- | --- | --- | --- | --- |
|  |  | 需求/项目风格/规则推导 | 高/中/低 |  |

## 5. 文件列表定义

| 文件名 | 必需/可选 | 职责 | 关键内容 |
| --- | --- | --- | --- |
| `FC.c` | Required |  |  |
| `FC.h` | Required |  |  |
| `FC_Cfg.c` | Required |  |  |
| `FC_Cfg.h` | Required |  |  |
| `FC_CfgData.h` | Required |  |  |
| `FC_Types.h` | Required |  |  |
| `FC_Reg.h` | Conditional | SPI/I2C/register-based external-device register carrier. | Register addresses, bit masks, command words, protocol frame constants; required for register-controlled external devices. |
| `FC_Callout.h` | Conditional |  |  |
| `FC_Callout.c` | Conditional |  |  |
| `FC_MemMap.h` | Required |  |  |

### 5.1 文件之间的链接关系

| 文件 | 直接依赖 | 关系说明 |
| --- | --- | --- |
|  |  |  |

### 5.2 五大类头文件承载关系

| 类别 | 主承载头文件 | 次承载头文件 | 承载说明 |
| --- | --- | --- | --- |
| 对外接口 | `FC.h` | `FC_Types.h` |  |
| 配置宏参 | `FC_Cfg.h` | `FC_CfgData.h`、`FC_Types.h` | `Cfg.h` 优先保留基础配置、功能开关、行为选择；寄存器和项目参数表优先下沉到 `Cfg.c/CfgData.h` |
| 寄存器定义 | `FC_Reg.h` | `FC_Cfg.h` | 涉及 SPI/I2C/register 外设时，`Reg.h` 承载寄存器地址、位定义、命令字和协议帧常量；`FC_Reg.h` 引用 `Std_Types.h`，`FC_Cfg.h` 在需要寄存器符号时包含 `FC_Reg.h` |
| 标定参数 | `FC_CfgData.h` | `FC_Types.h` |  |
| 全局参数 | `FC_Types.h` | `FC_Internal.h` 或 `FC.h` |  |
| 内存分配宏 | `FC_MemMap.h` | 各头文件中的段宏入口 |  |

### 5.3 可选文件

| 文件名 | 触发条件 | 职责 |
| --- | --- | --- |
| `FC_Cali.c` |  |  |
| `FC_Reg.h` | FC 涉及 SPI/I2C/register 外设通信。 | 承载外设寄存器地址、位定义、命令字、协议帧常量。 |
| `FC_Callout.c` | 存在 Callout 依赖。 | 承载项目适配实现或集成 stub。 |
| `FC_Callout.h` | 存在 Callout 依赖。 | 承载 Callout 原型和项目适配契约。 |

## 6. 外部接口定义

优先按函数单独描述，避免完整文档导出 PDF 时出现超宽表格。接口很短时可合并为一个总表。

### 6.x `FC_FunctionName`

| 接口名 | 类型 | 用途 | 输入 | 输出 | 返回值 | 时序/模式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

### 6.1 接口设计规则应用说明
- 对外接口采用函数形式。
- 函数名前缀必须保留输入中的 FC/驱动名称，不得自动 CamelCase 化。例如驱动名称为 `Gp_DRV8889` 时，应使用 `Gp_DRV8889_Init`，不得使用 `GpDrv8889_Init`。
- 不定义对外全局变量接口。
- 在需要处增加防御性检查。
- 当需求细节缺失时，明确标记为暂定接口形态。

## 7. 外部依赖与Callout定义

| 依赖项 | 依赖用途 | 选用方式 | 暂定接口 | 原因 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### 7.1 接口统一性判定
- 已统一依赖:
- 未统一依赖:
- 需要Callout的依赖:
- 判定理由:

### 7.2 Callout接口定义

优先按依赖函数单独描述，避免完整文档导出 PDF 时出现超宽表格。依赖接口很短时可合并为一个总表。

#### 7.2.x `FC_CalloutFunctionName`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | English complete sentence. | Synchronous / Asynchronous | Reentrant / Non-reentrant |  |  | MCAL / IoMcu / IoExtDev / Service Layer / Project Adaptation |  | Formal / Conditional / Pending Confirmation / Not Recommended |

说明：
- 每个依赖接口必须展示完整 C 原型、英文描述、同步/异步、可重入性、返回值语义、基本约束、实现边界、证据和状态。
- 依赖接口/Callout 函数名前缀必须保留输入中的 FC/驱动名称。例如驱动名称为 `Gp_DRV8889` 时，应使用 `Gp_DRV8889_CalloutSpiTransceive`，不得使用 `GpDrv8889_CalloutSpiTransceive`。
- 若依赖接口原型、约束或证据较长，必须使用单函数小表，不要压缩信息以适配一个总表。
- Callout 原型参数不得使用数组形参写法，例如 `uint8 Data_au8[]`。
- SPI/I2C 传输接口使用指针形参，例如 `uint16* TxData_pu16`、`uint16* RxData_pu16` 或 `uint8* Data_pu8`。
- 传输长度/帧数默认使用 `uint16 Size_u16`。
- 16bit SPI 帧协议应使用 `uint16*` 数据指针，避免调用处反复强转。

## 8. 全局参数定义

| 参数名 | 作用域 | 角色 | 分类 | 类型 | 存储/内存段 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

说明：
- 默认不定义对外全局变量。
- 如果无对外全局变量，应显式写明本节为空。

### 8.1 内部运行态说明
- 内部状态策略:
- DET/故障状态策略:
- 输入/输出缓存策略:

## 9. 配置宏参定义

### 9.1 基础配置

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | Formal / Conditional / Pending Confirmation / Not Recommended |

### 9.2 功能相关配置

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | Formal / Conditional / Pending Confirmation / Not Recommended |

### 9.3 功能开关与行为选择

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | Feature Enable / Behavior Selection |  |  |  | Formal / Conditional / Pending Confirmation / Not Recommended |

### 9.4 配置原则说明
- 不同项目的配置宏参值可以不同。
- `Cfg.h` 优先保留基础配置、功能开关、行为选择、实现方式选择。
- `Macro or Parameter` 必须是全大写 C 宏标识符，只允许 `A-Z`、`0-9`、`_`；FC 名称部分也必须转为大写，例如 `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`，不得写成 `Gp_NCA9539_CFG_...`。
- 常规寄存器配置、时序、阈值、重试次数等项目参数通常在 `Cfg.c/CfgData.h` 中以配置表方式组织，架构阶段不必在 `Cfg.h` 中逐项展开。
- 已有稳定对外接口承载的基本功能，默认不再重复生成对应功能开关宏；只有需求明确提出可裁剪、可关闭或可编译期选择时，才生成对应配置宏参。
- 除非需求明确指出某功能需要标定，否则默认无标定项。
- 各核使能、各核实例数、硬件绑定表、阈值和重试次数，默认不放入最终“全局配置宏参”清单。
- 行为选择宏不是强制项；只有确实存在编译期实现分支时才保留。

## 10. 内存分配宏定义

| 内存段 | 目标内容 | 进入宏 | 退出宏 | 使用文件 | 备注 |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

### 10.1 MemMap策略
- 代码段规则:
- RAM变量段规则:
- ROM/配置/标定段规则:
- 集成重定义预期:

### 10.2 段宏使用边界

- 默认运行态优先使用 `CLEAR_FAR_DATA`。
- 若 static const 或配置常量存在按核归属、按核复制、按核实例配置，必须增加 `FC_CONST_FAR_DATA_ALIGN4_COREx_START/STOP`；不能默认只使用 `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_START/STOP`。
- `NO_CLEAR` 段仅在存在暖复位保留数据等明确生命周期要求时引入。
- `NEAR` 段仅在明确存在快速中断执行且时间要求严格的场景下引入。
- 若 `NO_CLEAR` 或 `NEAR` 不是正式推荐项，应放入“条件触发项”而不是默认段宏总表。

### 10.3 MemMap包含关系

- `FC_MemMap.h` 应被所有需要放置代码、运行态数据、const 数据或标定数据的 FC-created 文件在段边界处包含。
- 文件关系表中应体现 `_MemMap.h` 与所有 section-managed 文件的关系，而不仅是 `FC.c` 或 `FC_Cfg.c`。

## 11. 全局标定参数定义

| 参数名 | 类型 | 初始值 | 描述 | 状态 |
| --- | --- | --- | --- | --- |
|  |  |  |  | 正式/Empty/条件项 |

说明：
- 若无明确标定需求，应显式标记为 `Empty`。

## 12. 命名与符合性检查

### 11.1 命名规则应用
- 文件/模块命名规则:
- C标识符命名空间规则:
- FC标识符规则:
- 函数命名规则:
- 全局参数命名规则:
- 类型命名规则:

### 11.2 符合性观察
- 观察1:
- 观察2:

## 13. 风险与待确认问题
- 风险1:
- 风险2:
- 待确认问题1:
- 待确认问题2:

### 13.0 架构风险与待确认总表

填写说明：
- 用户可以直接修改下表的 `状态` 和 `备注`，也可以在当前窗口直接回复，例如：`R1、R3 已评审；R4 待修改，备注：按 xxx 方案调整`。
- `状态` 只允许填写：`待评审`、`已评审`、`待修改`。
- 若某条为 `待修改` 且 `备注` 为空，则默认按 `Recommended Action` 执行修改；若 `备注` 不为空，则优先按备注执行。
- 若希望直接发布，请将所有真实风险项标为 `已评审`，并将 `R-OTHER` 填为 `已评审` / `备注：无其他建议`。

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Pending item |  |  |  | 用户填写确认意见或修改意见。 | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议 / 用户补充建议。 | 待评审 |

说明：
- 每条风险项必须有稳定索引，便于用户在窗口中直接引用。
- 必须保留 `R-OTHER` / `其他` 行，供用户自行填写其他方面的建议。
- `备注` 用于记录用户的具体确认意见或修改意见。
- 若任一真实风险项仍为 `待评审` 或 `待修改`，架构状态必须保持 `Draft`。
- 所有真实风险项均为 `已评审` 后，才允许从 `Draft` 发布为 `Released`。

### 12.1 接口遗漏风险清单

| 风险项 | 风险等级 | 说明 | 建议动作 |
| --- | --- | --- | --- |
|  | 高/中/低 |  |  |

### 12.2 待确认接口清单

| 接口名 | 来源需求 | 置信度 | 待确认原因 | 建议处理 |
| --- | --- | --- | --- | --- |
|  |  | 高/中/低 |  |  |

### 12.3 不建议直接生成的低置信度接口

| 接口名 | 推导依据 | 低置信度原因 | 建议 |
| --- | --- | --- | --- |
|  |  |  | 先人工确认，不直接落代码 |

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

- 推荐评审方式 1：直接修改风险表中的 `状态` 和 `备注`。
- 推荐评审方式 2：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：按 xxx 方案调整`。
- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。
- 如果某项需要修改，可回复：`R5 待修改，备注：改为 MainFunction 轮询完成状态`。
- 修改完成后仍保持当前版本的 `Draft`，直到所有真实风险项均为 `已评审` 后发布为 `Released`。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
