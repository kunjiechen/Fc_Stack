---
name: fc-architecture-workbench
description: "用于设计、评审、校验和整理嵌入式汽车 FC 软件架构，包括外部接口、依赖接口、配置、标定、运行时状态、文件族与 MemMap 策略。"
---
# FC 架构工作台

## 1. 定位

这是一个**软件架构 skill**，负责把需求转成可评审、可追溯、可交接的 FC 架构方案。

它不是"无脑生成器"。开始前要先判断当前任务需要多深的验证和多重的依据。

## 2. 主要能力

- 新 FC 架构生成
- 架构评审、纠偏和收敛
- 精简版或完整版架构输出
- 外部接口、依赖接口、配置和运行时状态提取
- MemMap、Callout、文件族与配置载体规划
- 需求到架构的覆盖与缺失风险分析
- 芯片资源模型消费（当芯片架构视图可用时）

## 3. 明确边界

可以产出：

1. 架构摘要
2. 正式架构 Markdown
3. 架构评审问题清单
4. freeze bundle 相关对象与校验结果
5. 面向 SDD 阶段的架构交付件集合

明确不做：

- 不替代需求 skill 生成 SRS 或原始需求
- 不替代实现 skill 生成详细设计、代码骨架或配置源码
- 不凭空确认缺少来源证据的接口、状态、标定或寄存器结论
- 不把 demo、学习记录或历史案例直接当作当前项目事实
- 不绕过人工评审直接宣告架构 Released

缺失信息时，必须显式标记为风险项、待确认项或补料项。

## 4. 项目硬规则摘要

以下规则对后续架构生成与评审持续生效：

- 文档开头和结尾都要保留元数据，包含架构版本和生成时间
- 架构版本只用整数主版本：`V1`、`V2`、`V3`
- 外部 API、依赖 API、类型和对象名称保持显式 FC/驱动命名空间
- 外部接口较长时按函数逐个展开，不要塞进一张超宽表
- Callout 原型参数使用指针形式，不用数组声明式
- 涉及寄存器地址、位掩码、命令字或帧常量时，需要 `FC_Reg.h`
- 使用 Callout 依赖接口时，文件清单中应包含 `FC_Callout.h` 与 `FC_Callout.c`
- `FC_MemMap.h` 是所有 FC 自有头源文件共用的段切换载体
- `CONST` 段既可以全局，也可以按核划分，不能默认只有一个全局常量段

稳定细则以 `references/rules/*.md` 为准，本节只保留执行摘要。

## 5. 版本与发布规则

版本和发布流的权威来源是：

- `references/rules/release-workflow.md`

执行摘要：

- 只有需求输入时，通常从 `V1 Draft` 开始
- 草稿架构继续修订时，不自动升版
- 已发布架构遇到新需求，再升级到下一个主版本
- 只要还存在真实风险项处于"待评审"或"待修改"，状态就保持 `Draft`
- 每次更新都要附带简明变更说明

## 6. 与工作流层的关系

这个 skill 独立于需求 skill，不依赖需求 skill 的会话状态或内部文件。

当用户推进 SDD 阶段时，架构工作流应交付以下产物：

- `<FC>_软件架构设计.md`
- `Review_<FC>_软件架构设计.md`
- `Check_<FC>_软件架构设计.md`
- `Trace_<FC>_软件架构设计.md`

## 7. 设计目标

优先优化：

- 正确性
- 可追溯性
- 必要且克制的接口暴露
- 清晰的配置边界
- 安全的运行时状态治理
- 合理的执行成本

不要为了这些目标而牺牲判断：

- 文档越长越好
- 接口越多越好
- 每个请求都过度分析

## 8. 规则分工

各规则文件的主责域与补充关系：


| 主题                                     | 主责文件                                               | 补充文件                                                           |
| ---------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------ |
| 版本与发布                               | `references/rules/release-workflow.md`                 | `fc-architecture-rules.md` §2 仅保留版本号格式和输入驱动行为摘要  |
| 文件族职责与分层                         | `references/rules/fc-architecture-rules.md` §3~§7    | `project-style-rules.md` §5 仅保留 header carrier 视角            |
| MemMap 策略                              | `references/rules/project-style-rules.md` §6          | `source-grounding-aurix2g-live-baseline.md` §6 仅保留真实工程示例 |
| 接口选择（API/Callout/Macro/Binding）    | `references/rules/interface-selection.md`              | —                                                                 |
| 命名规范                                 | `references/rules/naming-rules.md`                     | —                                                                 |
| 静态/动态/标定分类                       | `references/rules/static-vs-dynamic.md`                | —                                                                 |
| 项目风格（接口骨架、参数风格、多核惯例） | `references/rules/project-style-rules.md`              | —                                                                 |
| 真实工程 grounding                       | `references/source-grounding-aurix2g-live-baseline.md` | —                                                                 |
| 语义对象模型                             | `references/semantic-model.md`                         | —                                                                 |
| 输出章节结构                             | `references/templates/output-template-summary.md`      | `output-template.md` 仅供内部脚手架使用                            |
| 架构 freeze bundle                       | `references/architecture-freeze-bundle-v1.md`          | —                                                                 |

规则冲突时优先级：

1. 架构规则含义看 `references/rules/*.md`（按上表主责文件优先）
2. 章节结构和渲染约束看 `references/templates/*.md`
3. 真实工程佐证看 `references/source-grounding-aurix2g-live-baseline.md`
4. 加载建议和索引看 `references/README.md`
5. 执行流程和升级逻辑看本 `SKILL.md`

## 9. 执行步骤

架构生成按以下步骤执行。每步有明确的输入、参考文件、操作和产出。

### 9.1 输入校验与准备

**目的**：确认输入是否满足架构生成的最低条件，识别降级场景。

**操作**：

1. 确认 FC 名称已从用户输入中提取
2. 检查 SRS 文件是否可用（用户提供路径或从 `Output/<FC>/Doc/SRS/` 自动发现）
3. 若 SRS 不可用 → 中止，提示用户先执行需求生成或提供 SRS 路径
4. 统计 SRS 中 Draft/Ready 需求比例，若 Ready 比例 < 30% 则在风险表中记录
5. 按 §11.2 规则加载芯片架构视图
6. 从 SRS 和芯片架构视图（如有）中提取 FC 名称、通信接口类型、安全等级

**产出**：输入清单（SRS 路径、芯片视图可用性、Draft/Ready 统计、关键参数摘要）

### 9.2 架构族判定与参考基线加载

**目的**：根据芯片接口类型判定架构族，加载对应的工程参考。

**操作**：

1. 从芯片架构视图 A1 或 SRS 概述中判定通信接口类型
2. 映射到架构族：


| 接口类型                    | 架构族    | 典型层级    |
| --------------------------- | --------- | ----------- |
| I2C / SPI 外设芯片          | IoExtDev  | `IoExtDev`  |
| MCU 内部外设（DIO/ADC/PWM） | IoMcu     | `IoMcu`     |
| 信号服务抽象                | IoSigSrv  | `IoSigSrv`  |
| 系统级模块                  | BswSys_Gp | `BswSys_Gp` |
| 复杂驱动/功能组件           | Cdd       | `Cdd`       |

3. 根据架构族加载参考基线：
   - **IoExtDev / IoMcu 族**：默认加载 `source-grounding-aurix2g-live-baseline.md` 中对应族章节
   - **其他族**：按需加载对应章节
4. 从 `demo-lib/MODULE_INDEX.md` 查找最近似 demo summary，加载一篇作为对照参考（不作为强制模板）

**产出**：架构族判定结论、已加载的参考基线清单

### 9.3 芯片资源模型消费（条件步骤）

**目的**：当芯片架构视图可用时，将芯片硬件资源模型结构化注入架构决策。

**触发条件**：芯片架构视图加载成功（见 §11.2），且当前架构族为 IoExtDev 或 IoMcu。

> 其他族（Cdd、BswSys_Gp、IoSigSrv、RtMon）没有芯片手册输入，无条件跳过本步骤，相关架构决策从 SRS 推导。

**操作**：按 §11.3 消费规则表，逐域消费芯片架构视图的 A1~A7：

- A1 模块身份 → §1 FC总结介绍
- A2 引脚清单 → §8 依赖接口设计（Callout 候选生成）
- A3 工作模式 → §5 全局变量与运行态策略（状态机设计）
- A4 寄存器空间概览 → §6 内存分配宏定义（FC_Reg.h 判定）、§9 文件列表
- A5 I2C/SPI 帧协议 → §8 依赖接口设计（Callout 行为约束）
- A6 中断资源 → §3 外部接口设计、§8 依赖接口设计
- A7 时钟与复位 → §3 外部接口设计、§5 运行时策略

当芯片架构视图不可用时，上述决策从 SRS 推导，并在风险表中标记不确定性。

**产出**：芯片资源消费记录（各域 → 架构章节落点）

### 9.4 语义对象构建

**目的**：在生成 Markdown 之前，先构建结构化中间对象，以便校验和追溯。

**参考文件**：`references/semantic-model.md`（必读）、`references/rules/interface-selection.md`（依赖接口选择）、`references/rules/static-vs-dynamic.md`（分类决策）

**操作**：按 semantic-model 的对象类型逐类构建。构建顺序反映对象间依赖关系（先构建外部接口和依赖接口，再基于它们派生配置、状态、文件和风险对象）。

#### 9.4.1 外部接口对象

从 SRS 接口需求中提取。若芯片架构视图可用，额外参考其 A2 引脚清单和 A6 中断资源。

每个外部接口包含：`name`、`prototype`、`description`、`sync_mode`、`reentrancy`、`return_value`、`constraints`、`evidence`、`status`。

**MainFunction 必要性判定**（参考 `project-style-rules.md` §2）：检查 SRS 是否包含以下任一场景，满足任一即需要 `MainFunction`：

- 周期采样
- 状态机推进
- 诊断处理
- 去抖
- 看门狗处理
- 恢复处理
- 缓冲请求处理

判定结果记录为 `assumptions` 中的 `MainFunction_Required: true/false`，并在 §1 的"架构设计思路"中简述理由。

#### 9.4.2 依赖接口对象

从 SRS 诊断需求 + 芯片架构视图 A2 引脚清单（如有）提取依赖需求，然后**按接口选择规则逐一判定依赖表达方式**。

**决策流程**（参考 `interface-selection.md`）：


| 条件                                   | 选择机制                   | 典型场景                         |
| -------------------------------------- | -------------------------- | -------------------------------- |
| 依赖极简、无参数/无类型转换/无实例缩放 | **Macro 替换**             | 临界区进入/退出                  |
| 平台已有标准函数签名，仅绑定函数名变化 | **Standard Binding**       | 项目级信号 getter/setter 族      |
| 项目特定适配、硬件适配、板级逻辑       | **Callout**                | DIO 控制、SPI/I2C 传输、PWM 输出 |
| 依赖选项少且稳定、效率优先             | **Fixed Integration Code** | 少量已知 MCAL 变体               |

判定后为每个依赖构建对应对象：

- Callout → `dependency_apis` 对象（`name`、`prototype`、`description`、`implemented_by`、`evidence`、`status`）
- Standard Binding → `binding_items` 对象（见 §9.4.4）
- Macro → `config_macros` 对象（见 §9.4.3）中增加 `Dependency Selection` 类型宏
- Fixed Integration → `config_macros` 中增加 `Dependency Selection` 类型宏 + 编译时分支说明

**Callout 原型规范**（参考 `interface-selection.md` §Callout）：

- I2C 写：`Std_ReturnType FC_CalloutI2cWrite(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)`
- I2C 读：`Std_ReturnType FC_CalloutI2cRead(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)`
- SPI 收发：`Std_ReturnType FC_CalloutSpiTransceive(uint16 Id_u16, uint16* TxData_pu16, uint16* RxData_pu16, uint16 Size_u16)`
- DIO 控制：`Std_ReturnType FC_CalloutDioWrite(uint16 Id_u16, uint8 Level_u8)`
- 参数使用指针形式，不用数组声明式。Size 参数用 `uint16 Size_u16`。

**Callout 文件载体判定**：存在任一 Callout → `FC_Callout.h` 和 `FC_Callout.c` 均为 Required。

#### 9.4.3 配置宏参对象

从 SRS 配置需求中提取。若芯片架构视图可用，额外参考其 A4 寄存器空间概览判定 `FC_Reg.h` 需求。

每个配置宏参包含：`name`（ALL_CAPS）、`purpose`、`macro_type`、`default_value`、`usage_location`、`evidence`、`status`。

`macro_type` 取值：`Feature Enable`、`Development Error Detect`、`Behavior Selection`、`Strategy Selection`、`Dependency Selection`、`Signal Mapping`、`Hardware Mapping`、`Count Size`、`Timing Threshold`、`Vendor Version Release`。

**DET 宏判定**：SRS 包含 DET/诊断需求或安全等级为 ASIL-B/D → 生成 `FC_CFG_DEV_ERROR_DETECT` 宏，默认 `STD_ON`。

**FC_Reg.h 判定**：芯片架构视图 A4 显示存在寄存器地址/位掩码/命令字 → `FC_Reg.h` 标记为 Required。

#### 9.4.4 绑定项对象

当 §9.4.2 中判定为 Standard Binding 时构建。

每个绑定项包含：`name`、`binding_type`、`source_side`、`target_side`、`binding_mechanism`、`description`、`status`。

若所有依赖均为 Callout/Macro/Fixed Integration，则本对象集为空。

#### 9.4.5 策略项对象

当宏参的语义复杂度超过简单的"开关/数值"时（参考 `semantic-model.md` §6A），将关键策略提升为策略项。

构建条件（满足任一）：

- 存在多个互斥行为选项（如 `SAMPLE_STRATEGY_RAW` vs `SAMPLE_STRATEGY_AVG`）
- 策略选择影响运行时行为路径（如 `FAULT_CLEAR_STRATEGY`）
- Grounding baseline 对应族中确认有同类策略宏（参考 `source-grounding-aurix2g-live-baseline.md`）

每个策略项包含：`name`、`strategy_type`、`selection_scope`、`backing_reference`、`description`、`status`。

> 大多数 IoExtDev 模块策略项为空。Cdd 和 BswSys_Gp 族更可能产生策略项。

#### 9.4.6 标定项对象

**需要标定判定门禁**（参考 `static-vs-dynamic.md` §Calibration Parameters）：

1. 检查 SRS 是否明确要求标定流程 → 有则构建
2. 检查架构族：IoExtDev/IoMcu → 默认为空；BswSys_Gp/Cdd → 检查 grounding baseline 对应族是否确有 Cali 先例
3. 检查项目输入是否要求标定工具链 → 无则默认为空

每个标定项包含：`name`、`type`、`initial_value`、`description`、`status`。可选字段：`range`、`usage_location`、`evidence`。

> IoExtDev 族（如 Gp_NCA9539）默认标定项为空。阈值和时序参数归类为编译期配置，不属于标定流程可调参数。

#### 9.4.7 运行时状态对象

从 SRS 模式需求 + 芯片架构视图 A3 工作模式（如有）提取状态机设计。

每个运行时状态包含：`name`、`owner`、`read_write_side`、`lifecycle`、`memory_section`、`concurrency_strategy`。

**DET 运行时维度检查**：若 §9.4.3 中生成了 DET 宏，检查以下场景是否需要运行时 DET bookkeeping：

- SRS 有 ASIL-B/D 安全等级 → 考虑 per-core DET buffer
- SRS 有 I2C/SPI 通信故障诊断需求 → 考虑故障计数器/状态
- Grounding baseline §7 对应族确认 DET 有运行时后果

判定为需要 → 在 runtime_states 中增加 DET 相关条目（per-core buffer、newest-error overwrite 策略、故障标志）。

**多核维度**：若 SRS 描述多实例或 grounding baseline 对应族有多核先例，增加 per-core 维度的运行时容器。

#### 9.4.8 MemMap 段对象

从 SRS 资源需求 + 芯片架构视图 A4 寄存器分类（如有）提取。

必须覆盖的段类别：CODE、RUNTIME RAM、CONST（区分 GLOBAL 和 per-core）、REG CONST（寄存器设备必须独立列出）、CALIB（条件存在）。

每个段包含：`name`、`target_content`、`start_macro`、`stop_macro`、`used_files`、`notes`。

#### 9.4.9 文件项对象

从以上对象汇总派生。每个文件项包含：`name`、`required_level`（Required/Conditional/Optional）、`responsibility`、`key_content`。

**必选文件**（始终 Required）：`FC.c`、`FC.h`、`FC_Types.h`、`FC_Cfg.h`、`FC_Cfg.c`、`FC_CfgData.h`、`FC_MemMap.h`

**条件文件**：

- `FC_Reg.h`：§9.4.3 判定需要 → Required
- `FC_Callout.h` + `FC_Callout.c`：§9.4.2 存在任一 Callout → Required
- `FC_Cali.c`：§9.4.6 存在标定项 → Required

#### 9.4.10 风险项对象

汇总以上各步产生的待确认项。每个风险项包含：`index`、`title`、`risk`、`impact`、`recommended_action`、`status`。

风险索引规则：从 R1 递增。始终包含 `R-OTHER` 行。

当存在同类 demo 的 `.arch.json` 时（如 IoExtDev 族可参考 `demo-lib/summaries/Gp_NCA95xx.arch.json`），将其作为结构对照而非内容模板。

**产出**：架构语义对象集（internal JSON，不输出为用户文件）。包含 10 类对象：external_apis、dependency_apis、config_macros、binding_items、strategy_items、calibration_items、runtime_states、memmap_sections、file_items、risk_items，以及文档信封（module、architecture_version、architecture_status、output_mode、layer、change_summary、assumptions）。

### 9.5 规则校验

**目的**：在渲染 Markdown 之前校验语义对象的完整性和一致性。

**校验项**（参考 semantic-model §11）：

- 元数据存在性（module、version、status、output_mode）
- external_apis 和 dependency_apis 未混淆
- 配置宏参使用 ALL_CAPS 标识符
- 运行时状态有 memory_section 归属
- MemMap 段有 start/stop 宏配对
- 文件项覆盖所有必选载体（`FC.c`、`FC.h`、`FC_Types.h`、`FC_Cfg.h`、`FC_Cfg.c`、`FC_CfgData.h`、`FC_MemMap.h`）
- 风险项使用有效索引和状态值
- 命名符合 `naming-rules.md`（FC 前缀保留、Callout 指针形参、配置宏 ALL_CAPS）
- 若存在 binding_items：每个绑定项有 source_side、target_side、binding_mechanism
- 若存在 strategy_items：每个策略项有 strategy_type、selection_scope、backing_reference
- 若存在 calibration_items：已通过 §9.4.6 判定门禁（非盲目为空、非盲目填充）
- MainFunction 决策已记录在 assumptions 中（`MainFunction_Required: true/false` + 理由）
- 若 DET 宏存在：检查 runtime_states 是否有对应的 DET bookkeeping 条目（per-core buffer / fault 标志）

**校验失败处理**：缺字段补全、冲突标记为风险项、无法自动修复的降级为 Draft

### 9.6 交叉校验

**目的**：用芯片架构视图反查架构输出的覆盖完整性。

**触发条件**：芯片架构视图可用时执行；不可用时跳过。

**检查项**（同 §11.3 消费后校验）：

- A2 引脚"必须连接"项 → Callout 或配置项覆盖
- A3 硬件模式全集 → SRS 状态机覆盖
- A4 R/W 寄存器 → 写路径覆盖
- A6 中断源 → Callout 或查询 API 覆盖

缺口列入 §10 风险表。

### 9.7 架构渲染

**目的**：将校验通过的语义对象渲染为正式架构 Markdown。

**参考文件**：`references/templates/output-template-summary.md`（必读，交付模板）

**操作**：按模板 10 章 + 附录结构渲染，每章从对应语义对象取值：


| 架构章节                 | 语义对象来源                                                 |
| ------------------------ | ------------------------------------------------------------ |
| §1 FC总结介绍           | 文档信封 + A1 模块身份                                       |
| §2 需求覆盖表           | SRS 需求逐条对照 external_apis/dependency_apis/config_macros |
| §3 外部接口设计         | external_apis 对象集                                         |
| §4 配置宏参设计         | config_macros + binding_items + strategy_items               |
| §5 全局变量与运行态策略 | runtime_states                                               |
| §6 内存分配宏定义       | memmap_sections                                              |
| §7 全局标定参数设计     | calibration_items                                            |
| §8 依赖接口设计         | dependency_apis                                              |
| §9 文件列表与文件关系   | file_items                                                   |
| §10 架构风险与待确认    | risk_items                                                   |

### 9.8 产物输出

**目的**：输出架构正式文档及配套评审产物。

**操作**：

1. 渲染 `<FC>_软件架构设计.md` 到输出路径（见 §12）
2. 生成配套产物：
   - `Review_<FC>_软件架构设计.md` — 评审重点、release blocker、风险关闭记录、评审结论
   - `Check_<FC>_软件架构设计.md` — 检查清单、Gate 结果、证据、问题闭环
   - `Trace_<FC>_软件架构设计.md` — SRS→Architecture 覆盖对象、覆盖状态、架构落点、设计决策
3. 若架构状态为 Draft，在对话回复中输出评审引导
4. **输出后校验**：对渲染产物做最终一致性检查：
   - 所有 10 类语义对象均已渲染到对应章节（对照 §9.7 映射表逐项核查）
   - 需求覆盖表（§2）中的 Requirement ID 与 SRS 一致，无遗漏
   - 风险表索引与语义模型 risk_items 索引一致
   - Callout 原型符合指针形参规范（无 `[]` 声明式）
   - 配置宏全部 ALL_CAPS
   - `FC_MemMap.h` 在所有 section-managed 文件的包含关系中体现
   - 校验未通过 → 标记为风险项（`R-POSTVAL`）并修正后重新渲染

---

## 10. 输入优先级

```text
用户需求
→ 芯片架构视图（条件输入，见 §11.2）
→ 项目架构约束
→ 当前项目规则
→ 本地保留学习记录
→ demo 模式
→ AI 推断
```

如果冲突：

- 优先用户显式需求和项目约束
- 芯片架构视图为芯片资源模型的权威来源，与 SRS 冲突时以 SRS 为准、差异记录为风险项
- demo 只用于比较，不直接照抄
- 当前工作区保留资料与旧学习结论冲突时，优先当前保留资料

## 11. 最小加载策略

默认加载：

1. 用户提供的需求、架构草稿或目标输出文件
2. 本 `SKILL.md`
3. `references/templates/output-template-summary.md`（正式架构交付模板）
4. `references/semantic-model.md`（语义对象模型，§9.4 必读）
5. 芯片架构视图（条件加载，见 §11.2）

按架构族加载：

- **IoExtDev / IoMcu 族**（默认）：`references/source-grounding-aurix2g-live-baseline.md` 对应族章节
- **其他族**：按需加载对应章节

按需再加载：

- `references/templates/output-template.md`（内部生成脚手架）
  仅在需要全量需求抽取、反向追踪、候选接口筛选和遗漏分析时加载，**不得作为交付模板**
- `references/rules/interface-selection.md`
  用于接口提取、接口边界和依赖选择
- `references/rules/static-vs-dynamic.md`
  用于配置、标定、运行时状态和宏/表决策
- `references/rules/naming-rules.md`
  用于命名审查和正式原型生成
- `references/rules/project-style-rules.md`
  用于文件结构、MemMap、集成方式和本地风格
- `references/rules/fc-architecture-rules.md`
  用于新模块生成、广义评审和冲突处理
- `references/rules/release-workflow.md`
  用于版本策略、风险评审和发布门禁
- `references/architecture-freeze-bundle-v1.md`
  只有需要 freeze 层推理时再读
- `demo-lib/MODULE_INDEX.md`
  需要 demo 对照时先读索引，再只读最接近的 summary
- 同类 demo 的 `.arch.json`（如 IoExtDev 族参考 `demo-lib/summaries/Gp_NCA95xx.arch.json`）
  作为语义对象结构对照，不作为内容模板

### 11.1 模板选型规则


| 场景                           | 使用模板                       | 说明                                  |
| ------------------------------ | ------------------------------ | ------------------------------------- |
| 正式架构生成（默认）           | `output-template-summary.md`   | 10 章 + 附录 + 评审引导，不含过程产物 |
| Quick Draft                    | `output-template-summary.md`   | 同上，风险表仅保留 3~5 条 + R-OTHER   |
| Formal Draft                   | `output-template-summary.md`   | 同上，风险表完整覆盖                  |
| Released                       | `output-template-summary.md`   | 同上，所有风险项已评审                |
| 内部全量抽取/反向追踪/遗漏分析 | `output-template.md`（脚手架） | 含过程章节，仅供 skill 内部推理       |

> **硬规则：正式交付文档绝不使用 `output-template.md`。** 脚手架的过程性章节属于生成中间产物，不得出现在用户可见的架构文档中。

### 11.2 芯片架构视图加载规则

**触发条件**：当架构生成任务中可从任意来源确定 FC 名称时。

**路径解析优先级**：

1. **用户显式路径** — 用户在对话中明确给出芯片架构视图文件路径时，直接使用该路径
2. **约定路径自动发现** — 按以下规则拼接路径并检测文件是否存在：

```text
Output/<FC>/Doc/ChipViews/<FC>_芯片架构输入.md
```

其中 `<FC>` 为从用户输入中提取的 FC 名称（保留原大小写和下划线，如 `Gp_NCA9539`）。

3. **降级兜底** — 以上两种方式均未找到有效文件时，架构生成降级为仅凭 SRS 工作

**加载行为**：


| 场景                       | 行为                                                       |
| -------------------------- | ---------------------------------------------------------- |
| 文件存在且内容完整         | 加载全部 7 个域（A1~A7），按 §11.3 消费规则注入架构各章节 |
| 文件存在但部分域缺失       | 加载可用域，缺失域在 §10 风险表中标记为待确认             |
| 文件不存在（降级模式）     | 架构生成不阻塞，§10 风险表自动插入`R-CHIPVIEW` 风险项     |
| 用户显式指定"不用芯片视图" | 跳过自动发现，直接降级模式，不插入`R-CHIPVIEW`             |

**降级模式下的 R-CHIPVIEW 风险项**：

```markdown
| R-CHIPVIEW | 芯片架构视图 | 缺芯片架构视图文件（路径：Output/<FC>/Doc/ChipViews/<FC>_芯片架构输入.md），以下架构决策基于 SRS 推导，待芯片资源模型确认：硬件模式全集、寄存器分类统计、burst 交替行为、中断清除机制细节。 | §1 概述 / §3 外部接口 / §6 MemMap / §8 依赖接口 | 建议先执行需求生成流程以产出芯片架构视图，或在对话中提供该文件路径后重新生成架构。 | | 待评审 |
```

### 11.3 芯片资源模型消费规则

当芯片架构视图成功加载时，其 7 个域按以下规则消费到架构输出各章节。架构 skill 内部在生成每个章节时，优先从芯片架构视图取结构化数据，芯片架构视图无覆盖的部分回退到 SRS 推导。


| 芯片架构视图域        | 消费到的架构章节                           | 消费方式                                                                                                                                                                                                                  |
| --------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A1 模块身份**       | §1 FC总结介绍                             | 芯片型号、通信接口类型(I2C/SPI)、最大速率、安全等级 → 直接填充"FC功能介绍"和"AUTOSAR架构层级"。接口类型用于判定层级（I2C/SPI 外设 → IoExtDev）                                                                          |
| **A2 引脚清单**       | §8 依赖接口设计                           | 逐引脚生成 Callout 候选：方向为 Input/Output 的非电源引脚按功能归并。SCL/SDA → I2C Callout；RESET\ → DIO Callout；INT\ → DIO Callout；A0/A1 → 配置项（非 Callout）。"内部上下拉"和"是否必须连接"写入 Callout 约束备注 |
| **A3 工作模式**       | §1 FC总结介绍, §5 全局变量与运行态策略   | 硬件模式列表写入 §1 的芯片背景描述。模式进入/退出条件直接映射到 §5 Runtime State 表的状态机设计。**重点：Standby 等 SRS 容易遗漏的硬件自动模式，芯片架构视图可补漏**                                                    |
| **A4 寄存器空间概览** | §6 内存分配宏定义, §9 文件列表           | 寄存器分类统计直接决定`FC_Reg.h` 是否需要以及结构划分。"控制/状态/配置/数据/身份"各类数量 → §6 REG CONST 段的划分依据。如有寄存器地址则标记 FC_Reg.h 为 Required                                                        |
| **A5 I2C/SPI 帧协议** | §8 依赖接口设计                           | 帧结构(命令字节、地址位宽)和 Burst 行为(交替/自增)写入对应 Callout 的 Description 和 Basic Constraints。**这是 SRS 通常不会描述的硬件协议细节，芯片架构视图是唯一来源**                                                   |
| **A6 中断资源**       | §3 外部接口设计, §8 依赖接口设计         | 中断触发条件和清除机制决定是否需要独立的中断状态查询 API。清除方式(read-clear/write-1-clear/auto-clear)影响接口的调用时序约束                                                                                             |
| **A7 时钟与复位**     | §3 外部接口设计, §5 全局变量与运行态策略 | 复位源列表和恢复时间直接写入 Init 接口的前置条件和 §5 Runtime State 的复位恢复状态转换。复位影响范围(全量/部分)决定恢复时需要重写哪些寄存器                                                                              |

**消费后的校验**（同 §9.6）：

- A2 引脚中标记"必须连接"的，架构是否都有对应的 Callout 或配置项 → 无则报遗漏风险
- A3 工作模式中列出的硬件模式，SRS 状态机是否全部覆盖 → 无则报模式遗漏
- A4 寄存器中标记"R/W"的，架构是否提供了写路径 → 无则报接口缺失
- A6 中断源，架构是否提供了中断处理 Callout 或查询 API → 无则报中断遗漏

交叉校验发现的缺口，列入 §10 架构风险与待确认。

---

## 12. 输出模式与交付物

所有输出模式均使用 `output-template-summary.md` 作为交付模板。模式差异仅体现在风险表密度和评审完整度上：

- **Quick Draft**：首轮快速讨论，风险表仅保留 3~5 条高优先级真实风险项 + R-OTHER
- **Formal Draft**（默认）：完整草稿，风险表覆盖所有待确认和待修改项
- **Released**：所有风险项已评审，文档可正式发布

输出路径与命名规则：

- 如果用户显式指定输出路径，按用户路径输出
- 如果用户未指定输出路径，则默认在项目根目录下创建：

```text
Output/<FC>/Doc/SDD/
```

- 架构文档文件名格式为 `<FC>_软件架构设计.md`
- 每次正式架构工作流交付必须同步输出以下评审与追溯产物：

```text
Review_<FC>_软件架构设计.md
Check_<FC>_软件架构设计.md
Trace_<FC>_软件架构设计.md
```

- `Review_<FC>_软件架构设计.md` 记录架构评审重点、release blocker、风险关闭记录、评审结论和是否允许进入 SDS。
- `Check_<FC>_软件架构设计.md` 记录架构检查清单、Gate 结果、证据、主要问题和下一步动作。
- `Trace_<FC>_软件架构设计.md` 记录 SRS → Architecture 的覆盖对象、覆盖状态、架构落点、设计决策和关闭条件。

## 13. 使用提醒

- 不要把 demo 摘要当成强制模板
- 不要默认所有 FC 的依赖策略都一样
- 不要在证据不足时把对象直接升为正式结论
- 常规执行中优先读 Markdown 规则，不默认加载归档 PDF
- `demo-lib/summaries/Gp_NCA95xx.arch.json` 是 NCA95xx 族芯片的语义对象参考模板，用于对照结构而非照抄内容
