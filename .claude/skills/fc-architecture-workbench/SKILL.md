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

### 4.0 最高频出错规则（TOP 5，生成前后必查）

以下 5 条是实践中出错率最高的规则，生成前和生成后必须逐条核对。任何一条违反即为硬错误，必须修正后重新渲染。

| # | 规则 | 正例 | 反例（禁止） |
|---|------|------|-------------|
| 1 | **Callout 命名前缀**：必须包含 `<FC>_Callout`，禁止通用 `FC_Callout` | `Gp_TJA1043_CalloutDioWrite` | `FC_CalloutDioWrite` |
| 2 | **配置宏前缀**：必须使用 `<FC>_CFG_`（ALL_CAPS），禁止通用 `FC_CFG_` | `GP_TJA1043_CFG_DEV_ERROR_DETECT` | `FC_CFG_DEV_ERROR_DETECT` |
| 3 | **引脚 ID**：CfgType 结构体成员（如 `StbN_DioId_u16`），禁止 Cfg.h 逐引脚 `#define` | `Cfg_st.StbN_DioId_u16` | `#define GP_TJA1043_CFG_DIO_ID_STB_N 0` |
| 4 | **禁止版本宏**：不生成 `CFG_SW_MAJOR_VERSION` / `CFG_SW_MINOR_VERSION` | （不存在） | `#define GP_TJA1043_CFG_SW_MAJOR_VERSION 1` |
| 5 | **禁止 `Hardware Mapping` / `Signal Mapping` / `Vendor Version Release` 宏类型**：这些是 config_params（Cfg.c），不是 config_macros（Cfg.h） | `macro_type: "Development Error Detect"` | `macro_type: "Hardware Mapping"` |

### 4.1 完整摘要

以下规则对后续架构生成与评审持续生效：

- 文档开头和结尾都要保留元数据，包含架构版本和生成时间
- 架构版本只用整数主版本：`V1`、`V2`、`V3`
- 外部 API、依赖 API、类型和对象名称保持显式 FC/驱动命名空间
- **依赖接口（Callout）命名必须固化**：每个 Callout 函数名必须包含 `<FC>_Callout` 前缀（如 `Gp_TJA1043_CalloutDioWrite`），不得使用不绑定 FC 的通用名（如 `FC_CalloutDioWrite`）
- 外部接口和依赖接口按函数逐个展开，使用结构化列表格式而非超宽表格——架构文档不是详细设计，不需要逐字段罗列实现细节
- Callout 原型参数使用指针形式，不用数组声明式
- 涉及寄存器地址、位掩码、命令字或帧常量时，需要 `FC_Reg.h`
- 使用 Callout 依赖接口时，文件清单中应包含 `<FC>_Callout.h` 与 `<FC>_Callout.c`
- `<FC>_MemMap.h` 是所有 FC 自有头源文件共用的段切换载体
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
| 架构族判定与子类型区分                   | `SKILL.md` §9.2                                       | `source-grounding-aurix2g-live-baseline.md` §11A-§11D 按族参考    |
| 文件族职责与分层                         | `references/rules/fc-architecture-rules.md` §3~§7    | `project-style-rules.md` §5 仅保留 header carrier 视角            |
| MemMap 策略                              | `references/rules/project-style-rules.md` §6          | `source-grounding-aurix2g-live-baseline.md` §6 仅保留真实工程示例 |
| 接口选择（API/Callout/Macro/Binding）    | `references/rules/interface-selection.md`              | `SKILL.md` §9.4.2 Callout 归并决策树                               |
| MainFunction 必要性判定                  | `references/rules/project-style-rules.md` §2          | `SKILL.md` §9.4.1 按族判定表                                       |
| 命名规范                                 | `references/rules/naming-rules.md`                     | —                                                                 |
| 静态/动态/标定分类                       | `references/rules/static-vs-dynamic.md`                | —                                                                 |
| 项目风格（接口骨架、参数风格、多核惯例） | `references/rules/project-style-rules.md`              | —                                                                 |
| 真实工程 grounding                       | `references/source-grounding-aurix2g-live-baseline.md` | `demo-lib/MODULE_INDEX.md` 按族选择对照 demo                      |
| 语义对象模型                             | `references/semantic-model.md`                         | `demo-lib/summaries/*.arch.json` 结构化参考模板                    |
| 输出章节结构                             | `references/templates/output-template-summary.md`      | `output-template.md` 仅供内部脚手架使用                            |
| 反模式与禁止项                           | `SKILL.md` §14                                        | §9.8 产物输出后校验第一轮（硬错误）                                |
| 架构 freeze bundle                       | `references/architecture-freeze-bundle-v1.md`          | —                                                                 |

规则冲突时优先级：

1. 架构规则含义看 `references/rules/*.md`（按上表主责文件优先）
2. 章节结构和渲染约束看 `references/templates/*.md`
3. 真实工程佐证看 `references/source-grounding-aurix2g-live-baseline.md`
4. 加载建议和索引看 `references/README.md`
5. 执行流程和升级逻辑看本 `SKILL.md`

## 9. 执行步骤

架构生成按以下步骤执行。每步有明确的输入、参考文件、操作和产出。

### 9.0 生成前预检（Pre-Flight Checklist）

在开始 §9.1 之前，确认以下 8 项已明确。任一项不明确 → 阻断，向用户确认后再继续。

| # | 检查项 | 来源 | 阻断？ |
|---|--------|------|--------|
| 1 | FC 名称已提取（保留原始大小写和下划线） | 用户输入 / SRS | **是** |
| 2 | SRS 文件路径已确认 | 用户输入 / 自动发现 | **是** |
| 3 | 芯片架构视图是否可用？路径？ | §11.2 自动发现 | 否（降级模式） |
| 4 | 架构族 + 子类型已判定 | §9.2 映射表 | **是** |
| 5 | 已判定子类型的关键影响（FC_Reg.h / REG CONST / Callout 类型） | §9.2 影响矩阵 | **是** |
| 6 | MainFunction 必要性已初步判定（按族默认 + SRS 场景） | §9.4.1 判定表 | **是** |
| 7 | 已加载对应的 .arch.json 参考（如有） | demo-lib/MODULE_INDEX.md | 否 |
| 8 | 已加载对应族的 grounding baseline 章节 | source-grounding-aurix2g-live-baseline.md §11A-§11D | 否 |

检查通过后，在架构元信息中记录：架构族、子类型、MainFunction_Required、已加载的参考文件清单。

### 9.1 输入校验与准备

**目的**：确认输入是否满足架构生成的最低条件，识别降级场景。

**操作**：

1. **（新增）旧产物检测与覆写判定**：在开始生成前，检查输出路径（`Output/<FC>/Doc/SDD/`）是否已存在架构产物。
   - 若 `<FC>_软件架构设计.md` 已存在 → 先读取其 §3（依赖接口）和 §4.1（配置宏参），扫描是否使用旧规则命名：
     - `FC_Callout` 前缀 → 旧版，必须全量覆写
     - `FC_CFG_` 前缀 → 旧版，必须全量覆写
     - 逐引脚 `#define <FC>_CFG_DIO_ID_xxx` → 旧版，必须全量覆写
     - 存在 `CFG_SW_MAJOR_VERSION` → 旧版，必须全量覆写
   - 判定为旧版后：**全量覆写**（Write 整文件），不得在原文件上增量修补。旧内容仅用于版本判定，不作为新架构的任何参考。
   - 若判定为新版（已使用 `<FC>_Callout` 和 `<FC>_CFG_` 前缀且无版本宏）→ 进入修订模式（用户可能在做增量修改）。
2. 确认 FC 名称已从用户输入中提取
3. 检查 SRS 文件是否可用（用户提供路径或从 `Output/<FC>/Doc/SRS/` 自动发现）
4. 若 SRS 不可用 → 中止，提示用户先执行需求生成或提供 SRS 路径
5. 统计 SRS 中 Draft/Ready 需求比例，若 Ready 比例 < 30% 则在风险表中记录
6. 按 §11.2 规则加载芯片架构视图
7. 从 SRS 和芯片架构视图（如有）中提取 FC 名称、通信接口类型、安全等级

**产出**：输入清单（SRS 路径、芯片视图可用性、Draft/Ready 统计、关键参数摘要、旧产物判定结果）

### 9.1A SRS 需求到架构的消费规则

**目的**：定义 SRS 的每条需求类别如何消费到架构各章节。这是需求 skill 与架构 skill 的正式接口。

**操作**：对 SRS 中的每条需求，按以下映射表确定其在架构中的落点：

| SRS 需求类别 | ID 前缀 | 架构消费章节 | 消费方式 |
|-------------|---------|-------------|---------|
| 接口需求 | `IF` | §2 外部接口设计 | 每条 IF 需求映射为 1 个 `external_apis` 对象。函数名、参数、返回值、约束从 SRS 描述中提取。 |
| 配置需求 | `CFG` | §3 配置参数设计 | 配置项按类型拆分：编译期开关/行为选择 → §3.1 `config_macros`；硬件映射/查找表 → §3.2 `config_params` |
| 诊断需求 | `DIAG` | §2 外部接口（GetDevFaultSig）、§5 故障设计（逐故障检测/去抖/恢复链路）、§9 依赖接口（ERR_N/INT Callout） | DIAG-0001 故障枚举表 → §5.2 每项故障独立 fault_handler 对象（含检测机制、去抖策略、确认后动作、恢复路径、影响范围）；DIAG-9001 DET → `config_macros` 中的 DEV_ERROR_DETECT 宏 + 运行时 DET buffer |
| 时序需求 | `TIME` | §4.2 配置参数（时序阈值 const）、§2 外部接口（时序约束） | 时序数值 → `config_params` 中的阈值常量（Cfg.c const）；时序责任（调用方保证 vs 模块保证）→ 外部接口的 Basic Constraints |
| 安全需求 | `SAFE` | §3 DEV_ERROR_DETECT 宏、§2 各 API 参数校验、§6 DET bookkeeping | ASIL 等级决定：DET 默认值（QM→STD_OFF, ASIL→STD_ON）、参数校验完整性、故障去抖策略。ASIL-D：强制 DET buffer + newest-error overwrite |
| 编码需求 | `CODE` | §10 文件列表、§1 命名规范 | 编码规范版本 → §1 设计思路中的符合性声明；MISRA/静态检查 → 不产生架构对象，在 Check 产物中记录 |
| 资源需求 | `RES` | §7 MemMap 段 | ROM/RAM 预算 → 各 MemMap 段的规模估算依据；IO/引脚资源 → `CfgType` 中的 DioId 成员规模 |
| 核心控制需求 | `CORE` | §6 运行时状态（per-core vs global）、§7 MemMap（COREx vs GLOBAL）、§3 配置宏参（core enable 宏）、§9 CalloutGetCoreId | **单核**：运行时状态和配置数据归属 global，不暴露 CoreId，无 core enable 宏，MemMap 使用 global 段不标注具体核号；**多核**：每核独立运行时容器，per-core MemMap 段（COREx），需要 CalloutGetCoreId，Cfg.h 中定义 core enable 宏 |

**消费判定流程**（逐条需求过一遍）：

```
对于 SRS 中的每条需求：
├── 接口需求 (IF) → 是否已有对应 external_api？
│   ├── 是 → 补充 constraints/evidence
│   └── 否 → 新建 external_api 对象
│
├── 配置需求 (CFG) → 该项是编译期开关还是硬件映射数据？
│   ├── 开关/行为选择/容量/阈值 → config_macros
│   └── 引脚映射/查找表/器件地址 → config_params
│
├── 诊断需求 (DIAG) → 是故障枚举还是 DET？
│   ├── DIAG-0001 故障枚举 → fault_handlers 逐故障构建 + runtime_states 故障标志
│   ├── DIAG-xxxx 具体故障 → 同上，合并到 §5.2 故障全链路表
│   └── DIAG-9001 DET → config_macros 增加 DEV_ERROR_DETECT
│
├── 接口需求 (IF-0001 Init) → external_api + 内部函数分解（≥4 个）
│
│
├── 安全需求 (SAFE) → 提取 ASIL 等级
│   └── 影响: DET 默认值、参数校验策略、DET buffer 需求
│
├── 资源需求 (RES) → 提取预算值
│   └── 影响: MemMap 段规模估算
│
└── 核心控制需求 (CORE) → 单核 or 多核？
    ├── single → 所有 runtime_states 归属单核，MemMap 无 COREx
    └── multi → 所有 runtime_states per-core，MemMap COREx 段，CalloutGetCoreId Required
```

**遗漏检查**：消费完成后，统计未被任何架构对象覆盖的 SRS 需求，列入 §11 风险表中标记 `Pending Confirmation`。SRS→架构的完整覆盖追溯由 `Trace_<FC>_软件架构设计.md` 独立承载，不在架构主文档中渲染需求覆盖表。

### 9.2 架构族判定与参考基线加载

**目的**：根据芯片接口类型判定架构族，加载对应的工程参考。

**操作**：

1. 从芯片架构视图 A1 或 SRS 概述中判定通信接口类型
2. 映射到架构族和子类型：


| 接口类型 | 架构族 | 子类型 | 寄存器型 | FC_Reg.h | REG CONST | 典型层级 |
|----------|--------|--------|---------|----------|-----------|----------|
| I2C / SPI 外设芯片（有寄存器） | IoExtDev | **寄存器型 (Reg)** | 是 | Required | Required | `IoExtDev` |
| 引脚直连外设芯片（无寄存器） | IoExtDev | **引脚型 (Pin)** | 否 | 不渲染 | 不渲染 | `IoExtDev` |
| MCU 内部外设（DIO/ADC/PWM） | IoMcu | — | 否 | 不需要 | 不需要 | `IoMcu` |
| 信号服务抽象 | IoSigSrv | — | 否 | 不需要 | 不需要 | `IoSigSrv` |
| 系统级模块 | BswSys_Gp | — | 否 | 不需要 | 不需要 | `BswSys_Gp` |
| 复杂驱动/功能组件 | Cdd | — | 否 | 不需要 | 不需要 | `Cdd` |

**子类型判定规则**：
- 芯片架构视图 A4 标记为"无寄存器"/"引脚直连"/"pin-control" 或 A1 通信接口类型为"引脚直连(Pin-Control)" → **引脚型 (Pin)**
- 芯片架构视图 A4 有寄存器地址/位掩码/命令字 或 A1 通信接口为 I2C/SPI → **寄存器型 (Reg)**
- 若芯片架构视图不可用，从 SRS 概述中的通信接口类型推导

**子类型对生成的关键影响**：

| 影响项 | 寄存器型 (Reg) | 引脚型 (Pin) |
|--------|---------------|-------------|
| FC_Reg.h | Required | 不渲染 |
| §6 REG CONST 段 | 渲染 | 不渲染 |
| 依赖接口 Callout | I2C/SPI + DIO | 仅 DIO |
| A4 寄存器消费 | 执行 | 跳过 |
| A5 帧协议消费 | 执行 | 跳过 |
| 配置参数（Cfg.c） | 含寄存器默认值/地址表 | 仅 IO 引脚 DioId 成员 |

3. 根据架构族和子类型加载参考基线：
   - **IoExtDev 寄存器型**：加载 `source-grounding-aurix2g-live-baseline.md` §1-§10（TLE92104 SPI 参考）
   - **IoExtDev 引脚型**：加载 `source-grounding-aurix2g-live-baseline.md` §4（DIO Callout 参考），**不加载寄存器相关章节**
   - **IoMcu 族**：加载 `source-grounding-aurix2g-live-baseline.md` §11A
   - **其他族**：按需加载对应章节
4. 从 `demo-lib/MODULE_INDEX.md` 查找最近似 demo summary，加载一篇作为对照参考（不作为强制模板）

**产出**：架构族判定结论、已加载的参考基线清单

### 9.3 芯片资源模型消费（条件步骤）

**目的**：当芯片架构视图可用时，将芯片硬件资源模型结构化注入架构决策。

**触发条件**：芯片架构视图加载成功（见 §11.2），且当前架构族为 IoExtDev 或 IoMcu。

> 其他族（Cdd、BswSys_Gp、IoSigSrv、RtMon）没有芯片手册输入，无条件跳过本步骤，相关架构决策从 SRS 推导。

**操作**：按 §11.3 消费规则表，逐域消费芯片架构视图。消费行为取决于 §9.2 判定的子类型：

**所有 IoExtDev/IoMcu（通用）**：
- A1 模块身份 → §1 FC总结介绍
- A2 引脚清单 → §9 依赖接口设计（Callout 候选生成）
- A3 工作模式 → §4 状态机设计
- A7 时钟与复位 → §2 外部接口设计、§6 运行时策略

**仅 IoExtDev 寄存器型（Reg）**：
- A4 寄存器空间概览 → §7 内存分段设计（REG CONST 段）、§10 文件列表（FC_Reg.h Required）
- A5 I2C/SPI 帧协议 → §9 依赖接口设计（Callout 行为约束：帧结构、Burst 行为）
- A6 中断资源 → §2 外部接口设计、§9 依赖接口设计

**IoExtDev 引脚型（Pin）和 IoMcu**：
- A4 跳过（无寄存器，不渲染 REG CONST 和 FC_Reg.h）
- A5 跳过（无通信帧协议）
- A6 按需消费（引脚型通常无独立中断引脚；若有 ERR_N/INT 等多功能状态引脚，作为 DIO 输入 Callout 处理而非中断资源）

当芯片架构视图不可用时，上述决策从 SRS 推导，并在风险表中标记不确定性。

**产出**：芯片资源消费记录（各域 → 架构章节落点）

### 9.4 语义对象构建

**目的**：在生成 Markdown 之前，先构建结构化中间对象，以便校验和追溯。

**参考文件**：`references/semantic-model.md`（必读）、`references/rules/interface-selection.md`（依赖接口选择）、`references/rules/static-vs-dynamic.md`（分类决策）

**操作**：按 semantic-model 的对象类型逐类构建。构建顺序反映对象间依赖关系（先构建外部接口和依赖接口，再基于它们派生配置、状态、文件和风险对象）。

#### 9.4.1 外部接口对象

从 SRS 接口需求中提取。若芯片架构视图可用，额外参考其 A2 引脚清单和 A6 中断资源。

每个外部接口包含：`name`、`prototype`、`description`、`sync_mode`、`reentrancy`、`return_value`、`constraints`、`evidence`、`status`。

**MainFunction 必要性判定**（参考 `project-style-rules.md` §2）：判定分两步——先看架构族默认策略，再看 SRS 是否覆盖特殊场景。

**第一步：架构族默认策略**

| 架构族 | 子类型 | MainFunction 默认 | 理由 |
|--------|--------|------------------|------|
| IoExtDev | Reg (寄存器型) | **Required** | 需要周期轮询寄存器获取芯片状态、诊断和故障 |
| IoExtDev | Pin (引脚型) | **Conditional** | 仅当需要周期轮询 ERR_N/INT 等状态引脚或故障去抖时需要 |
| IoMcu | — | **Not Default** | API 同步读取 MCU 外设状态，通常不需要周期轮询 |
| Cdd | — | **Not Default** | 转换驱动，按需触发，无通用周期任务 |
| BswSys_Gp | — | **Not Default** | 系统状态导向，查询式接口 |
| IoSigSrv | — | **Conditional** | 取决于是否需要周期采样/转换 |

**第二步：SRS 场景覆盖检查**。无论架构族默认策略如何，若 SRS 包含以下任一场景，MainFunction 必须为 Required：

- 周期采样（如周期读取 ERR_N 引脚状态）
- 状态机推进（如 Go-to-Sleep → Sleep 自动转换等待）
- 诊断处理（如故障去抖确认、故障计数器）
- 去抖（如 ERR_N 稳定等待 ≥8μs 后的多次确认读取）
- 恢复处理（如欠压恢复后自动重新初始化）
- 缓冲请求处理（如异步模式切换请求队列）

若架构族默认策略为 Not Default 且 SRS 无上述场景 → MainFunction 不生成。若默认策略为 Required 或 Conditional 但 SRS 有上述场景 → MainFunction Required。

判定结果记录为 `assumptions` 中的 `MainFunction_Required: true/false`，并在 §1 的"架构设计思路"中简述理由。判定为 false 时，不得在外部接口列表中渲染 `MainFunction`。

#### 9.4.2 依赖接口对象

从 SRS 诊断需求 + 芯片架构视图 A2 引脚清单（如有）提取依赖需求，然后**按接口选择规则逐一判定依赖表达方式**。

**决策流程**（参考 `interface-selection.md`）：


| 条件                                   | 选择机制                   | 典型场景                         |
| -------------------------------------- | -------------------------- | -------------------------------- |
| 依赖极简、无参数/无类型转换/无实例缩放 | **Macro 替换**             | 临界区进入/退出                  |
| 平台已有标准函数签名，仅绑定函数名变化 | **Standard Binding**       | 项目级信号 getter/setter 族      |
| 项目特定适配、硬件适配、板级逻辑       | **Callout**                | DIO 控制、SPI/I2C 传输、PWM 输出 |
| 依赖选项少且稳定、效率优先             | **Fixed Integration Code** | 少量已知 MCAL 变体               |

**依赖接口设计原则（硬规则）**：

依赖接口的抽取不是按功能 pin 逐个生成，而是**按依赖的模块类别归并**。同一个模块（如 DIO 控制器）提供的同类能力（如 GPIO 输出），无论控制多少个 pin，都应归并为**一个**参数化 Callout。此外需主动推导隐藏依赖点：

**隐藏依赖推导**：

| 场景条件 | 推导结果 | 函数签名 | 说明 |
|---------|---------|---------|------|
| 系统为多核架构 | **1 个** `GetCoreId` Callout | `uint8 <FC>_CalloutGetCoreId(void)` | 多核架构下运行时状态需区分核归属，必须能获取当前核 ID |
| 模块有延时等待需求（如模式切换后需等待芯片稳定） | **1 个** `Delay` Callout | `void <FC>_CalloutDelayUs(uint32 Delay_us)` | 微秒级延时。架构只判定是否需要，不展开实现方式（硬件定时器/软件循环） |
| 模块有模拟量采集需求（如电流检测、电压采样） | **1 个** `AdcRead` Callout | `Std_ReturnType <FC>_CalloutAdcRead(uint16 Id_u16, uint16* Value_pu16)` | ADC 采样值读取。`Id` 区分不同采样通道，通道映射表在 `Cfg.c` 中 |
| 模块有通信需求（I2C/SPI） | 通信 Callout（见下表） | — | 通信接口独立一个 Callout bucket，不按 pin 拆分 |

**显式 Callout 归并规则**：

判定为 Callout 后，**严禁逐引脚生成独立 Callout**。必须按硬件访问方式归并：

| 硬件访问方式 | 归并结果 | 函数签名 | Pin 身份区分方式 |
|-------------|---------|---------|----------------|
| DIO 输出控制（所有需要 FC 拉高/拉低的 GPIO） | **1 个** `<FC>_CalloutDioWrite` | `Std_ReturnType <FC>_CalloutDioWrite(uint16 Id_u16, uint8 Level_u8)` | `Id` 参数，传入 `CfgType` 结构体中对应引脚的 `DioId` 成员（如 `Cfg_st.StbN_DioId_u16`） |
| DIO 输入读取（所有需要 FC 读取电平的 GPIO） | **1 个** `<FC>_CalloutDioRead` | `Std_ReturnType <FC>_CalloutDioRead(uint16 Id_u16, uint8* Level_pu8)` | `Id` 参数，传入 `CfgType` 结构体中对应引脚的 `DioId` 成员（同上） |
| I2C 写 | **1 个** `<FC>_CalloutI2cWrite` | `Std_ReturnType <FC>_CalloutI2cWrite(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` | `Id` 参数（I2C 器件地址，在 `Cfg.c` 中作为 const 常量） |
| I2C 读 | **1 个** `<FC>_CalloutI2cRead` | `Std_ReturnType <FC>_CalloutI2cRead(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` | `Id` 参数（I2C 器件地址，同上） |
| SPI 收发 | **1 个** `<FC>_CalloutSpiTransceive` | `Std_ReturnType <FC>_CalloutSpiTransceive(uint16 Id_u16, uint16* TxData_pu16, uint16* RxData_pu16, uint16 Size_u16)` | `Id` 参数（SPI 器件 ID，在 `Cfg.c` 中作为 const 常量） |
| PWM 输出 | **1 个** `<FC>_CalloutPwmSetDuty` | `Std_ReturnType <FC>_CalloutPwmSetDuty(uint16 Id_u16, uint16 Duty_u16)` | `Id` 参数 + `Cfg.c` 中的 PWM 通道映射表 |

**归并判定流程**：

1. 从 A2 引脚清单中提取所有非电源引脚
2. 将每个引脚按硬件访问方式分到上表的类型桶中（DIO_OUT / DIO_IN / I2C / SPI / PWM）
3. 每个类型桶生成**恰好 1 个** Callout 依赖接口对象
4. 桶中所有引脚各自对应 `CfgType` 结构体中的一个 `DioId` 成员（如 `StbN_DioId_u16`）。Callout 调用时直接传入对应成员的值为 `Id` 参数。**不在 `Cfg.h` 中为每个引脚生成独立宏。**
5. A0/A1 等地址/strap/配置引脚 → `Cfg.c` 中的 const 常量，不生成 Callout

**示例**：NCA9539 的 RESET\ 和 INT\ 都是 DIO 引脚，但方向不同：
- RESET\ → DIO 输出控制 → `Gp_NCA9539_CalloutDioWrite(Cfg_st.Reset_DioId_u16, level)`
- INT\ → DIO 输入读取 → `Gp_NCA9539_CalloutDioRead(Cfg_st.Int_DioId_u16, &level)`
- 只生成 2 个 Callout（1 个 DIO Write + 1 个 DIO Read），不是 2 个 RESET/INT 专用接口

**反例（不允许）**：
- `<FC>_CalloutResetDioWrite(Level)` — 引脚身份进入了函数名，无法复用
- `<FC>_CalloutIntDioRead()` — 同上
- 每新增一个 DIO 引脚就新增一个 Callout 函数
- `#define FC_CFG_DIO_ID_RESET 0` / `#define FC_CFG_DIO_ID_INT 1` — 引脚身份作为独立宏写入 `Cfg.h`，引脚多了宏泛滥
- 使用不绑定 FC 的通用 Callout 名（如 `FC_CalloutDioWrite`）— 缺少命名空间隔离，跨 FC 模块产生符号冲突风险

判定后为每个依赖构建对应对象：

- Callout → `dependency_apis` 对象（`name`、`prototype`、`description`、`implemented_by`、`evidence`、`status`）；对应的引脚 ID 作为 `CfgType` 结构体成员归入 §9.4.3 配置参数
- Standard Binding → `binding_items` 对象（见 §9.4.4）
- Macro → `config_macros` 对象（见 §9.4.3 配置宏参）中增加 `Dependency Selection` 类型宏
- Fixed Integration → `config_macros` 中增加 `Dependency Selection` 类型宏 + 编译时分支说明

**Callout 原型规范**（参考 `interface-selection.md` §Callout）：

- DIO 控制：`Std_ReturnType <FC>_CalloutDioWrite(uint16 Id_u16, uint8 Level_u8)`
- DIO 读取：`Std_ReturnType <FC>_CalloutDioRead(uint16 Id_u16, uint8* Level_pu8)`
- I2C 写：`Std_ReturnType <FC>_CalloutI2cWrite(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)`
- I2C 读：`Std_ReturnType <FC>_CalloutI2cRead(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)`
- SPI 收发：`Std_ReturnType <FC>_CalloutSpiTransceive(uint16 Id_u16, uint16* TxData_pu16, uint16* RxData_pu16, uint16 Size_u16)`
- PWM 输出：`Std_ReturnType <FC>_CalloutPwmSetDuty(uint16 Id_u16, uint16 Duty_u16)`
- 多核 GetCoreId：`uint8 <FC>_CalloutGetCoreId(void)`
- 微秒延时：`void <FC>_CalloutDelayUs(uint32 Delay_us)`
- ADC 采样：`Std_ReturnType <FC>_CalloutAdcRead(uint16 Id_u16, uint16* Value_pu16)`
- 参数使用指针形式，不用数组声明式。Size 参数用 `uint16 Size_u16`。

**Callout 归并决策树（机械执行，逐引脚过一遍）**：

以下决策树将每个非电源引脚映射到确定的 Callout 函数和配置参数条目。按顺序执行，每个引脚落入且仅落入一个分支。

```
输入：芯片架构视图 A2 中的所有非电源引脚

对于每个引脚：
├── 引脚方向是 MCU→Chip（输出控制）？
│   ├── 控制方式 = DIO 电平写入？
│   │   └── → CalloutDioWrite bucket
│   │       配置：CfgType 结构体中增加 1 个 DioId 成员（如 `StbN_DioId_u16`）
│   │
│   ├── 控制方式 = PWM 输出？
│   │   └── → CalloutPwmSetDuty bucket
│   │       配置：CfgType 结构体中增加 1 个 PWM 通道 ID 成员
│   │
│   └── 控制方式 = 通信总线（I2C/SPI）？
│       └── → CalloutI2cWrite/CalloutSpiTransceive bucket
│           （通信总线 Callout 不逐引脚拆分，整个总线 = 1 个 Callout）
│
├── 引脚方向是 Chip→MCU（输入读取）？
│   ├── 读取方式 = DIO 电平读取（GPIO）？
│   │   └── → CalloutDioRead bucket
│   │       配置：CfgType 结构体中增加 1 个 DioId 成员（如 `ErrN_DioId_u16`）
│   │
│   ├── 读取方式 = 通信总线（I2C/SPI）？
│   │   └── → CalloutI2cRead/CalloutSpiTransceive bucket
│   │
│   └── 读取方式 = 中断信号？
│       └── → 评估是否需独立中断 Callout 或复用 CalloutDioRead
│           （多数引脚型设备的状态引脚复用 CalloutDioRead 轮询）
│
└── 引脚是地址/strap 配置引脚（A0/A1/ADDR）？
    └── → 不生成 Callout
        配置：Cfg.c 中增加 1 个 const 常量（如 I2C 器件地址）
```

**硬约束**：
- 每个 bucket 即使有 N 个引脚，也只生成 **1 个** Callout 函数，不随引脚数量增长。
- I2C 和 SPI bucket 的器件地址/ID 在 Cfg.c 中作为 const 常量，不进入 Callout 函数名。
- 空 bucket（0 个引脚）不生成 Callout。
- 一个引脚只能落入一个 bucket。若不确定归属，以芯片手册功能描述为准。

**Callout 文件载体判定**：存在任一 Callout → `<FC>_Callout.h` 和 `<FC>_Callout.c` 均为 Required（`<FC>` 替换为实际模块名，如 `Gp_TJA1043_Callout.h`）。

#### 9.4.3 配置参数对象

从 SRS 配置需求和芯片手册中提取。**配置宏参体现功能开关，配置参数体现功能的参数**。

提取前过滤：芯片自主行为的时间参数不提取（软件只观测结果，不参与过程）。只有软件主动使用、且不同项目可能取不同值的参数才进入配置。

通过过滤后按以下规则归属：

| 载体 | 放入条件 | 典型内容 |
|------|---------|---------|
| `Cfg.h` `#define`（宏参） | 功能开关——`#if`/`#ifdef`/数组维度 | DET 开关、默认模式、去抖次数、实例数 |
| `Cfg.c` `const` 结构体（配置参数） | 功能参数——运行时值，不改变编译路径 | IO 引脚 ID、寄存器默认值、SPI 通道号、超时时间 |

---

**配置宏参**（`Cfg.h` `#define`）：

- `macro_type` 取值：`Feature Enable`、`Development Error Detect`、`Behavior Selection`、`Strategy Selection`、`Dependency Selection`、`Count Size`。
- 不做 `Timing Threshold`、`Hardware Mapping`、`Signal Mapping`、`Vendor Version Release`。
- 每个宏参对象含：`name`、`purpose`、`macro_type`、`default_value`、`evidence`、`status`。

DET 宏判定：SRS 含 DET/诊断需求或安全等级为 ASIL-B/D → 生成 `<FC>_CFG_DEV_ERROR_DETECT`，默认 `STD_ON`。

---

**配置参数**（`Cfg.c` / `CfgData.h` `const` 结构体）：

以 `<FC>_CfgType` 为索引入口结构体，按资源类别组织成员。四类成员：

| 类别 | 内容 | 组织方式 |
|------|------|---------|
| **IO资源配置** | DIO 引脚 ID、PWM 通道 ID、ADC 通道 ID | **直接展开为独立成员**（`uint16 StbN_DioId_u16`），不用数组 |
| **寄存器配置** | 寄存器默认值 | 建子结构体 `RegCfgType`。位域多的寄存器**整寄存器配置，不拆 bit**。多个寄存器合并到一起 |
| **通信配置** | SPI/I2C 通道号、序列号、器件地址 | 建子结构体 `SpiCfgType` / `I2cCfgType` |
| **功能参数** | 采样次数、去抖次数（不用宏时）、软件等待超时 | 标量成员 |

构建规则：
- 引脚型设备通常只有 1 个 `CfgType`（无寄存器/通信子结构体）。
- 寄存器型设备嵌套子结构体。
- 每个成员或子结构体需记录：`name`、`type`、`category`、`description`、`evidence`、`status`。

**展现形式**（不允许出现代码段，用表格逐结构体描述）：

每个结构体类型一个表：表头为"结构体类型 | 类别 | 描述"，紧跟其成员表（成员名 | 类型 | 说明）。

示例——引脚型（Gp_TJA1043）：

**结构体类型**：`Gp_TJA1043_CfgType` | **类别**：IO资源配置 + 功能参数 | **描述**：引脚型设备的配置容器。

| 成员 | 类型 | 说明 |
|------|------|------|
| `StbN_DioId_u16` | `uint16` | STB_N 引脚的 DIO 通道 ID |
| `En_DioId_u16` | `uint16` | EN 引脚的 DIO 通道 ID |
| `ErrN_DioId_u16` | `uint16` | ERR_N 引脚的 DIO 通道 ID |
| `Inh_DioId_u16` | `uint16` | INH 引脚的 DIO 通道 ID |
| `ModeSwitchTimeoutMs_u16` | `uint16` | 模式切换后等待芯片就绪的超时时间（ms） |

示例——寄存器型 + SPI（Gp_TLE92104）：

**结构体类型**：`Gp_TLE92104_SpiCfgType` | **类别**：通信配置 | **描述**：SPI 通信参数。

| 成员 | 类型 | 说明 |
|------|------|------|
| `SpiChannel_u8` | `uint8` | SPI 硬件通道号 |
| `SpiSequence_u8` | `uint8` | SPI 序列器 ID |

**结构体类型**：`Gp_TLE92104_RegCfgType` | **类别**：寄存器配置 | **描述**：芯片寄存器默认值，整寄存器配置不拆 bit。

| 成员 | 类型 | 说明 |
|------|------|------|
| `Ctrl1_u16` | `uint16` | 控制寄存器 1 默认值 |
| `Ctrl2_u16` | `uint16` | 控制寄存器 2 默认值 |
| `Ctrl3_u16` | `uint16` | 控制寄存器 3 默认值 |

**结构体类型**：`Gp_TLE92104_CfgType` | **类别**：顶级配置容器 | **描述**：嵌套子结构体 + IO 直接展开。

| 成员 | 类型 | 说明 |
|------|------|------|
| `SpiCfg_st` | `Gp_TLE92104_SpiCfgType` | SPI 通信配置 |
| `RegCfg_st` | `Gp_TLE92104_RegCfgType` | 寄存器默认值 |
| `Reset_DioId_u16` | `uint16` | RESET 引脚的 DIO 通道 ID（IO 直接展开，不嵌套子结构体） |

**FC_Reg.h 判定**（与 A4 联动）：芯片架构视图 A4 有寄存器地址/位掩码/命令字 → `FC_Reg.h` Required。引脚型 → 不渲染。

版本宏：不生成。

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

#### 9.4.7A 状态转换详表对象

从芯片架构视图 A3 工作模式 + SRS 模式需求中提取。**每个可能的状态转换生成一行**，不遗漏硬件触发的转换。

每个转换包含：`current_state`、`trigger_event`、`target_state`、`trigger_source`（software/hardware）、`entry_action`、`exit_action`、`timing_constraint`。

构建规则：
- A3 模式列表中每个模式的进入/退出方式 → 至少 1 条转换
- Table 4/Figure 4 中的模式转换表 → 逐行映射
- 芯片硬件触发的转换（UVNOM→Sleep, UVBAT→Standby, Wake→Standby）不可遗漏
- 触发源区分：API 调用 = software，芯片自主行为 = hardware

#### 9.4.7B 故障处理架构对象

从 SRS 诊断需求（DIAG-0001）+ 芯片架构视图 A6 中断/状态资源中提取。**每条故障独立构建一个 fault_handler 对象**，覆盖检测→确认→响应→快照→恢复→清除全生命周期。

每个故障包含 9 个字段：`fault_name`、`classification`、`detection_mechanism`、`confirmation_strategy`、`fault_response`、`snapshot_strategy`、`recovery_strategy`、`clear_strategy`、`impact_scope`。

构建规则（逐维度决策）：

**确认策略**（`confirmation_strategy`）：
- 芯片硬件自判定故障（如过温、TXD 超时、总线短路）→ `chip_self_determined`（单次触发即确认，无需软件去抖）
- 外部引脚电平读取（如 INH 判断欠压、ERR_N 判断故障）→ `consecutive_N`，N 默认 2~3，由 `CFG_FAULT_DEBOUNCE_CNT` 控制
- 软件状态/参数检查 → 单次触发即确认（调用路径明确，无瞬态干扰）

**故障响应**（`fault_response`）：
- 仅记录 → `LogOnly`
- DET 上报 + 返回错误 → `DET+ReturnError`（软件故障默认）
- 禁用发送器 → `DisableTx`（芯片已执行，软件记录）
- 强制切换模式 → `ForceModeSwitch`（如 UVNOM→Sleep，软件等待恢复）
- 通知上层 → `NotifyUpperLayer`（如总线故障需上层仲裁）

**快照策略**（`snapshot_strategy`）：
- `None`：芯片行为确定，快照无额外诊断价值（如 TXD 超时）
- `ModeSnapshot`：锁存故障时刻的当前模式，用于恢复后校验
- `FullContext`：锁存模式+引脚电平+供电状态+故障计数，用于根因分析（具体锁存字段待项目诊断需求确认）
- ASIL-D：安全相关故障建议至少 `ModeSnapshot`

**恢复策略**（`recovery_strategy`）：
- `Auto`：芯片自动恢复，软件仅检测恢复完成
- `Manual`：需软件主动执行恢复动作（如重新初始化、切换模式）
- `Reset`：需芯片硬件复位
- `Fatal`：不可恢复，需系统级处理

**清除策略**（`clear_strategy`）：
- `EnterNormal`：进入 Normal 模式是天然清除点（芯片侧约定）
- `PowerOnReset`：故障标志只在完全重新上电时清除
- `ApiClear`：需软件调用特定 API 显式清除
- `Auto`：故障条件消失后自动清除（如过温降温后、非法参数仅当次调用拒绝）

通用规则：
- hardware_chip 故障从数据手册提取；software_state/software_param 故障为必选基线
- ASIL-D 要求硬件故障 + 软件故障全覆盖，安全相关故障的快照策略需满足诊断覆盖

#### 9.4.8 MemMap 段对象

从 SRS 资源需求 + 芯片架构视图 A4 寄存器分类（如有）提取。

必须覆盖的段类别：CODE、RUNTIME RAM、CONST（区分 GLOBAL 和 per-core）。

条件段（仅当芯片/需求满足条件时渲染）：
- REG CONST：仅当 FC 控制 SPI/I2C/寄存器型外设时渲染。引脚直连型设备不渲染此段。
- CALIB：仅当存在确认的标定参数时渲染。

每个段包含：`name`、`target_content`、`start_macro`、`stop_macro`、`used_files`、`notes`。

#### 9.4.9 文件项与内部函数对象

从以上对象汇总派生。每个文件项包含：`name`、`required_level`（Required/Conditional/Optional）、`responsibility`、`key_content`。

**必选文件**（始终 Required）：`<FC>.c`、`<FC>.h`、`<FC>_Types.h`、`<FC>_Cfg.h`、`<FC>_Cfg.c`、`<FC>_CfgData.h`、`<FC>_MemMap.h`

**条件文件**（满足条件时渲染文件行，不满足时不渲染）：

- `<FC>_Reg.h`：仅当芯片为寄存器型外设（SPI/I2C 寄存器器件）→ Required。引脚直连型设备不渲染。
- `<FC>_Callout.h` + `<FC>_Callout.c`：§9.4.2 存在任一 Callout → Required（`<FC>` 替换为实际模块名）
- `<FC>_Cali.c`：§9.4.6 存在标定项 → Required

**内部函数分解**（与文件项同步构建）：

从外部接口的执行流程和依赖接口的调用关系中，提取影响架构结构的关键内部函数。不是所有 helper 都需要列出——仅列出承担独立职责、影响函数拆分或调用层次的内部函数。

每个内部函数包含：`name`（C 函数名）、`responsibility`（一句话职责）、`called_by`（哪个外部 API 调用它）、`operates_on`（操作哪些运行时数据/配置表/引脚）、`calls`（调用哪些 Callout 或其他内部函数）。

构建规则：
- Init 的步骤分解 → 至少提取：配置校验、Callout 验证、引脚设置、运行时初始化（在内部函数中体现，不在外部接口章节逐步骤展开）
- MainFunction 的周期处理 → 至少提取：状态轮询、故障去抖、模式检测、故障标志更新
- 调用层次图用 ASCII art 表达，标注 Callout 调用点
- 简单的 getter/setter（纯读缓存/写缓存）不单独列为内部函数

#### 9.4.10 风险项对象

汇总以上各步产生的待确认项。每个风险项包含：`index`、`title`、`risk`、`impact`、`recommended_action`、`status`。

风险索引规则：从 R1 递增。始终包含 `R-OTHER` 行。

当存在同类 demo 的 `.arch.json` 时（如 IoExtDev 族可参考 `demo-lib/summaries/Gp_NCA95xx.arch.json`），将其作为结构对照而非内容模板。

**产出**：架构语义对象集（internal JSON，不输出为用户文件）。包含 13 类对象：external_apis、dependency_apis、config_macros、config_params、binding_items、strategy_items、calibration_items、runtime_states、state_transitions、fault_handlers、memmap_sections、file_items、risk_items，以及文档信封（module、architecture_version、architecture_status、output_mode、layer、sub_type、change_summary、assumptions）。

### 9.5 规则校验

**目的**：在渲染 Markdown 之前校验语义对象的完整性和一致性。

**校验项**（参考 semantic-model §11）：

- 元数据存在性（module、version、status、output_mode）
- external_apis 和 dependency_apis 未混淆
- 配置宏参使用 ALL_CAPS 标识符；配置参数使用 C 标识符（非 ALL_CAPS）
- 配置宏参中无 `Hardware Mapping`、`Signal Mapping`、`Vendor Version Release` 类型（应分别在 config_params 或不存在）
- 运行时状态有 memory_section 归属
- MemMap 段有 start/stop 宏配对
- 文件项覆盖所有必选载体（`<FC>.c`、`<FC>.h`、`<FC>_Types.h`、`<FC>_Cfg.h`、`<FC>_Cfg.c`、`<FC>_CfgData.h`、`<FC>_MemMap.h`）
- 风险项使用有效索引和状态值
- 命名符合 `naming-rules.md`（FC 前缀保留、Callout 指针形参、配置宏 ALL_CAPS）
- 若存在 binding_items：每个绑定项有 source_side、target_side、binding_mechanism
- 若存在 strategy_items：每个策略项有 strategy_type、selection_scope、backing_reference
- 若存在 calibration_items：已通过 §9.4.6 判定门禁（非盲目为空、非盲目填充）
- MainFunction 决策已记录在 assumptions 中（`MainFunction_Required: true/false` + 理由）
- 若 DET 宏存在：检查 runtime_states 是否有对应的 DET bookkeeping 条目（per-core buffer / fault 标志）
- state_transitions 覆盖 A3 所有硬件模式（含硬件触发转换：UV 欠压、Wake 唤醒）
- fault_handlers 覆盖 DIAG-0001 所有故障条目（硬件故障 + 软件故障），每个 handler 有 classification/debounce/recovery

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

**操作**：按模板 10 章 + 附录结构渲染，每章从对应语义对象取值。各章渲染规则如下：

| 架构章节 | 语义对象来源 | 渲染规则 |
|----------|-------------|---------|
| §1 FC总结介绍 | 文档信封 + A1 模块身份 | 从 semantic-model 信封取 module/architecture_version/architecture_status/output_mode/layer/sub_type。芯片型号、通信接口类型从 A1 直接填充。架构设计思路段落包含：MainFunction 决策及理由、Callout 归并策略、DET 策略、单核/多核执行模型。 |
| §2 外部接口设计 | external_apis | 每个 external_api 渲染为结构化列表项（非表格），所有接口统一格式。格式：**原型**、**概述**（一句话职责）、**同步/异步 | 可重入 | 返回值**（紧凑行）、**前置条件**、**异常处理**。Init 用前置条件/异常处理描述初始化契约（不逐步骤展开）；MainFunction_Required=true 则 MainFunction 必须列入。架构只描述接口契约，不展开实现细节。 |
| §3 依赖接口设计 | dependency_apis | 每个 dependency_api 渲染为结构化列表项（非表格）。格式：**原型**、**目标**（此 Callout 统一了哪些硬件依赖）、**实现方**、**约束**。紧接外部接口之后——两者都是"接口"。隐藏依赖推导结果（GetCoreId/DelayUs）若产生也列入本节。Callout 原型必须使用指针形参（无 `[]` 声明式），函数名包含 `<FC>_Callout` 前缀。 |
| §4 配置参数设计 | config_macros + config_params | **分两子节**：§4.1 配置宏参——功能开关，每条独立展开（类型/默认值/说明/来源）；§4.2 配置参数——`<FC>_CfgType` 结构体（IO 直接展开成员、寄存器建 `RegCfgType` 子结构体、通信建 `SpiCfgType`/`I2cCfgType`、功能参数标量），配成员表。binding_items / strategy_items 非空时归入 §4.1。 |
| §5 状态机设计 | state_transitions + runtime_states（状态相关变量） | **分三部分**：(1) §5.1 芯片工作模式（硬件）；(2) §5.2 软件状态机（状态枚举、转换图、变量设计——含 ModeState 等状态变量，本章直接声明）；(3) §5.3 状态转换详表（增加"软件动作"列体现驱动代码操作）。硬件触发转换不可遗漏。 |
| §6 故障设计 | fault_handlers + runtime_states（故障相关变量） | **分三部分**：(1) §6.1 故障分类；(2) §6.2 策略维度定义（6 维度）；(3) §6.3 全链路表（9 列）。故障运行时变量（FaultFlags、去抖计数器、快照存储）在本章直接声明。 |
| §7 全局变量设计 | calibration_items | **分两子节**：(1) §7.1 全局变量（固定 Empty，架构不允许对外暴露全局变量）；(2) §7.2 标定变量（空或条件填充）。运行时状态变量（ModeState、FaultFlags 等）已在 §5、§6 中定义，不在此处重复汇总。 |
| §8 内存分段设计 | memmap_sections | 每段一行。RUNTIME RAM 段承载 §5/§6 中的运行时状态变量（ModeState、FaultFlags 等）。仅 Reg 子类型渲染 REG CONST 行。仅 §7.2 非空时渲染 CALIB 行。 |
| §9 驱动文件设计 | file_items | **分两部分**：§9.1 文件列表；§9.2 文件关系。仅 Reg 子类型渲染 `<FC>_Reg.h`。 |
| §10 架构风险与待确认 | risk_items | 每风险项一行。索引 R1 递增，始终含 R-OTHER。Quick Draft 仅 3~5 条 + R-OTHER。 |

### 9.8 产物输出

**目的**：输出架构正式文档及配套评审产物。

**操作**：

1. 渲染 `<FC>_软件架构设计.md` 到输出路径（见 §12）
2. 生成配套产物：
   - `Review_<FC>_软件架构设计.md` — 评审重点、release blocker、风险关闭记录、评审结论
   - `Check_<FC>_软件架构设计.md` — 检查清单、Gate 结果、证据、问题闭环
   - `Trace_<FC>_软件架构设计.md` — SRS→Architecture 覆盖对象、覆盖状态、架构落点、设计决策
3. 若架构状态为 Draft，在对话回复中输出评审引导
4. **输出后校验（Gate Check）**：对渲染产物逐项检查，分两轮执行：

**第一轮：反模式扫描（硬错误，必须修正）**。逐条对照 §14 的 26 条反模式，检查渲染产物。任何命中 → 修正后重新渲染，不降级为风险项。

**第二轮：完整性校验（Conditional → 标记风险项）**：
   - 所有语义对象均已渲染到对应章节（对照 §9.7 映射表逐项核查）
   - 风险表索引与语义模型 risk_items 索引一致
   - Callout 原型符合指针形参规范（无 `[]` 声明式）
   - 配置宏参（§4.1）全部 ALL_CAPS，且使用 `<FC>_CFG_` 模块前缀（非通用 `FC_CFG_`）；配置参数（§4.2）使用 C 标识符并保留 FC 原大小写
   - 无独立引脚 ID 宏出现在 `Cfg.h` 中
   - 引脚直连型设备不渲染 `FC_Reg.h` 和 `REG CONST` 段
   - §5.3 状态转换详表覆盖全部硬件模式（含 UV/Wake 硬件触发），"软件动作"列非空
   - §6.3 故障全链路表覆盖全部故障条目，硬件+软件故障均有，6 个策略维度完整
   - §2 外部接口全量列出，格式统一（无 Ini t特殊表）
   - `<FC>_MemMap.h` 在所有 section-managed 文件的包含关系中体现
   - 校验未通过 → 标记为风险项（`R-POSTVAL`）并修正后重新渲染

5. **强制 Shell 命名校验（必执行，不可跳过）**：产物渲染完成后，立即用以下 grep 命令逐项检查。任何命中 → 硬错误，修正后重新渲染。

   ```bash
   # 校验 1: Callout 命名前缀（必须包含 <FC>_Callout，不得使用通用 FC_Callout）
   # 期望输出: 空（无命中）
   grep -n 'FC_Callout' <FC>_软件架构设计.md

   # 校验 2: 配置宏前缀（必须包含 <FC>_CFG_，不得使用通用 FC_CFG_）
   # 期望输出: 空（无命中）。注意：MemMap 段的宏不属此类。
   grep -n 'FC_CFG_' <FC>_软件架构设计.md

   # 校验 3: DIO 引脚拆分宏（不得在 Cfg.h 中逐引脚定义）
   # 期望输出: 空（无命中）
   grep -n 'CFG_DIO_ID_' <FC>_软件架构设计.md

   # 校验 4: 版本宏（禁止生成）
   # 期望输出: 空（无命中）
   grep -n 'CFG_SW_MAJOR_VERSION\|CFG_SW_MINOR_VERSION' <FC>_软件架构设计.md

   # 校验 5: Hardware Mapping / Signal Mapping / Vendor Version Release 宏类型（禁止）
   # 期望输出: 空（无命中）
   grep -n 'Hardware Mapping\|Signal Mapping\|Vendor Version Release' <FC>_软件架构设计.md

   # 校验 6: 命名规范——类型后缀检查（常见遗漏：enum 缺 _e、struct 缺 _st、boolean 缺 _b）
   # 列出 §5/§6 中变量声明行，人工核对后缀是否符合 naming-rules.md
   grep -nE '\| *[A-Za-z_]+ *\| *(enum|struct|boolean|uint8|uint16|uint32|sint8|sint16|sint32) *\|' <FC>_软件架构设计.md
   ```
   > 校验 6 使用宽松匹配（列出 §5/§6 中变量名与类型在同一行的条目），命中行需人工核对命名是否符合命名规范。常见遗漏：enum 变量未用 `_e` 后缀、boolean 未用 `_b` 后缀、struct 变量未用 `_st` 后缀、uint32 未用 `_u32` 后缀。参考 `references/rules/naming-rules.md`。

   以上 6 条 grep 校验必须全部通过（校验 1-5 输出为空；校验 6 需人工核对无违规）。若任一命中 → 定位到具体行号，修正后重新渲染，再跑 grep 校验直至全部通过。校验结果记录在 `Check_<FC>_软件架构设计.md` 的 Gate 1 章节中。

6. **可选的 Python 脚本校验**：若语义对象已序列化为 JSON（如 freeze bundle 场景），可额外运行：
   ```bash
   python scripts/validate_architecture_objects.py <objects.json>
   python scripts/validate_architecture_source_alignment.py <objects.json> --baseline references/source-grounding-aurix2g-live-baseline.md
   python scripts/check_architecture_markdown.py <FC>_软件架构设计.md
   ```
   LLM 生成流程中通常不序列化语义对象，此步为可选。若未序列化，跳过 Python 脚本校验，但强制 Shell 校验（第 5 步）必须执行。

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
| R-CHIPVIEW | 芯片架构视图 | 缺芯片架构视图文件（路径：Output/<FC>/Doc/ChipViews/<FC>_芯片架构输入.md），以下架构决策基于 SRS 推导，待芯片资源模型确认：硬件模式全集、寄存器分类统计、burst 交替行为、中断清除机制细节。 | §1 概述 / §2 外部接口 / §7 MemMap / §9 依赖接口 | 建议先执行需求生成流程以产出芯片架构视图，或在对话中提供该文件路径后重新生成架构。 | | 待评审 |
```

### 11.3 芯片资源模型消费规则

当芯片架构视图成功加载时，其 7 个域按以下规则消费到架构输出各章节。架构 skill 内部在生成每个章节时，优先从芯片架构视图取结构化数据，芯片架构视图无覆盖的部分回退到 SRS 推导。


| 芯片架构视图域        | 消费到的架构章节                           | 消费方式                                                                                                                                                                                                                  |
| --------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A1 模块身份**       | §1 FC总结介绍                             | 芯片型号、通信接口类型(I2C/SPI)、最大速率、安全等级 → 直接填充"FC功能介绍"和"AUTOSAR架构层级"。接口类型用于判定层级（I2C/SPI 外设 → IoExtDev）                                                                          |
| **A2 引脚清单**       | §9 依赖接口设计, §3.2 配置参数           | **按依赖类型归并，不是逐引脚生成独立接口。** 从 A2 中提取所有非电源引脚，按硬件访问方式分为以下依赖类型，每类只生成一个参数化 Callout：<br><br>**DIO 输出控制类**：所有需要 FC 主动拉高/拉低的引脚（如 RESET\、EN、STB、nSLEEP）→ **一个** `<FC>_CalloutDioWrite(Id_u16, Level_u8)`，引脚身份通过 `CfgType` 结构体中对应引脚的 `DioId` 成员区分<br><br>**DIO 输入读取类**：所有需要 FC 读取电平的引脚（如 INT\、nFAULT、RDY）→ **一个** `<FC>_CalloutDioRead(Id_u16, Level_pu8)`，引脚身份同上<br><br>**I2C 通信类**：SCL/SDA → `<FC>_CalloutI2cWrite` + `<FC>_CalloutI2cRead`（协议级，已参数化），器件地址在 `Cfg.c` 中作为 const 常量<br><br>**SPI 通信类**：SCK/MOSI/MISO/CS → `<FC>_CalloutSpiTransceive`（协议级，已参数化），器件 ID 在 `Cfg.c` 中作为 const 常量<br><br>**地址/strap 引脚**：A0/A1 等 → `Cfg.c` 中的 const 常量，不生成 Callout<br><br>**归并判定原则**：同类硬件访问方式 → 同一个参数化 Callout；引脚身份通过 `Id` 参数 + `CfgType` 成员区分，不进入函数名。不在 `Cfg.h` 中为每个引脚生成独立 `#define` 宏。 |
| **A3 工作模式**       | §1 FC总结介绍, §4 状态机设计             | 硬件模式列表写入 §1 的芯片背景描述。模式进入/退出条件直接映射到 §4.3 状态转换详表。**重点：Standby 等 SRS 容易遗漏的硬件自动模式，芯片架构视图可补漏** |
| **A4 寄存器空间概览** | §7 内存分段设计, §10 文件列表          | **仅 IoExtDev 寄存器型消费。** 寄存器分类统计决定`FC_Reg.h` 是否需要以及 §7 是否渲染 REG CONST 段。引脚型（Pin）和 IoMcu 跳过此域——不渲染 `FC_Reg.h`，§7 不渲染 REG CONST 行。 |
| **A5 I2C/SPI 帧协议** | §9 依赖接口设计                           | **仅 IoExtDev 寄存器型消费。** 帧结构(命令字节、地址位宽)和 Burst 行为(交替/自增)写入对应 Callout 的 Description 和 Basic Constraints。引脚型（Pin）跳过此域——无通信帧协议。 |
| **A6 中断资源**       | §2 外部接口设计, §9 依赖接口设计         | 中断触发条件和清除机制决定是否需要独立的中断状态查询 API。清除方式(read-clear/write-1-clear/auto-clear)影响接口的调用时序约束                                                                                             |
| **A7 时钟与复位**     | §2 外部接口设计, §6 全局变量与运行态策略 | 复位源列表和恢复时间直接写入 Init 接口的前置条件和 §6 Runtime State 的复位恢复状态转换。复位影响范围(全量/部分)决定恢复时需要重写哪些寄存器                                                                              |

**消费后的校验**（同 §9.6）：

- A2 引脚"必须连接"项 → 对应的 Callout 类型是否已覆盖（DIO_OUT / DIO_IN / I2C / SPI）+ 是否在 `CfgType` 结构体中配置了对应的 `DioId` 成员 → 缺 Callout 类型覆盖则报遗漏，缺 DioId 成员则报配置缺失
- A3 工作模式中列出的硬件模式，§4 状态机是否全部覆盖 → 无则报模式遗漏
- A4 寄存器中标记"R/W"的，架构是否提供了写路径 → 无则报接口缺失
- A6 中断源，架构是否提供了中断处理 Callout 或查询 API → 无则报中断遗漏

交叉校验发现的缺口，列入 §11 架构风险与待确认。

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

---

## 14. 禁止生成的模式（Anti-Patterns）

本节是**集中式反模式清单**。在架构渲染前（§9.7）和产物输出后校验（§9.8）两个节点，必须逐项检查以下条目。任何命中均为错误，必须修正后重新渲染。

### 14.1 配置宏参反模式（Cfg.h）

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| A1 | `#define CFG_SW_MAJOR_VERSION 1` | 版本管理由项目构建系统负责，不属于 FC 配置项 | 不生成任何版本宏 |
| A2 | `#define CFG_SW_MINOR_VERSION 0` | 同上 | 不生成任何版本宏 |
| A3 | `#define <FC>_CFG_DIO_ID_STB_N 0` | 引脚身份被拆成独立宏写入 Cfg.h，引脚多了宏泛滥 | 引脚 ID 作为 `CfgType` 结构体成员（如 `StbN_DioId_u16`）放入 Cfg.c |
| A4 | `#define <FC>_CFG_DIO_ID_ERR_N 2` | 同上——逐引脚宏 | 同上——CfgType 成员 |
| A5 | `#define <FC>_CFG_I2C_DEV_ADDR 0x74` | I2C 器件地址是数据查表（不改变编译路径），应在 Cfg.c 中作为 const 常量 | 归入 Cfg.c 配置参数 |
| A6 | 为每个外部接口生成 `#define <FC>_CFG_<API>_ENABLE` | 编译期裁剪仅在需求明确要求时保留 | 不为无明确编译期分支需求的 API 生成 enable 宏 |
| A7 | `#define FC_CFG_DEV_ERROR_DETECT`（使用通用 `FC_` 前缀） | 缺少模块命名空间隔离 | 必须使用 `<FC>_CFG_DEV_ERROR_DETECT`（如 `GP_TJA1043_CFG_DEV_ERROR_DETECT`） |

### 14.2 依赖接口反模式（Callout）

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| B1 | `<FC>_CalloutResetDioWrite(Level)` | 引脚身份进入函数名，无法复用 | 归并为 `<FC>_CalloutDioWrite(Id_u16, Level_u8)`，引脚身份通过 Id 参数 + 查表区分 |
| B2 | `<FC>_CalloutIntDioRead()` | 同上 | 归并为 `<FC>_CalloutDioRead(Id_u16, Level_pu8)` |
| B3 | 每新增一个 DIO 引脚就新增一个 Callout 函数 | 违反归并原则，Callout 数量膨胀 | 同类硬件访问方式 → 恰好 1 个参数化 Callout |
| B4 | `<FC>_CalloutStbDioWrite(Level)` + `<FC>_CalloutEnDioWrite(Level)` | 两个 DIO 输出引脚生成了两个 Callout | 合并为 1 个 `<FC>_CalloutDioWrite(Id_u16, Level_u8)` |
| B5 | 对引脚直连型设备生成 `<FC>_CalloutSpiTransceive` 或 `<FC>_CalloutI2cWrite/Read` | 芯片无 SPI/I2C 接口 | 仅生成 DIO Callout |
| B6 | Callout 原型中使用数组声明式 `uint8 TxData_au8[]` | 违反指针形参规范 | 使用指针形式 `uint8* TxData_pu8` |
| B7 | DIO Read Callout 缺少输出参数 | 无法获取读取结果 | 必须包含 `uint8* Level_pu8` 输出指针 |
| B8 | 使用不绑定 FC 的通用 Callout 名（如 `FC_CalloutDioWrite`） | 缺少 FC 命名空间隔离，跨模块符号冲突风险 | 必须包含 `<FC>_Callout` 前缀，如 `Gp_TJA1043_CalloutDioWrite` |
| B9 | 遗漏隐藏依赖推导 | 多核场景缺 GetCoreId，延时场景缺 DelayUs；架构交付不完整 | 按 §9.4.2 隐藏依赖推导表逐项检查 |

### 14.3 文件与 MemMap 反模式

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| C1 | 引脚直连型设备渲染 `FC_Reg.h` | 无寄存器，不需要寄存器定义文件 | 引脚型不渲染 FC_Reg.h 行 |
| C2 | 引脚直连型设备 §6 渲染 `REG CONST` 段 | 无寄存器常量 | 引脚型不渲染 REG CONST 行 |
| C3 | IoExtDev 族默认渲染 `FC_Cali.c` | IoExtDev 默认无标定参数 | 仅在 §9.4.6 判定有标定项时才渲染 Cali.c；否则保持 Empty |
| C4 | CONST 段只给 GLOBAL，遗漏 per-core | 单核也有对应段，架构完整性缺失 | 始终包含 CONST GLOBAL + CONST per-core |
| C5 | `FC_Cfg.h` 中包含 `FC_Reg.h` 但设备为引脚型 | 无 Reg.h 却写了 include 关系 | 引脚型设备：Cfg.h 不包含 Reg.h，文件关系表中不出现 Reg.h 相关行 |

### 14.4 接口与命名反模式

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| D1 | FC 名称 `Gp_TJA1043` 被自动 CamelCase 为 `Gp_Tja1043_Init` | 违反命名空间保留原则 | 保留原始命名：`Gp_TJA1043_Init` |
| D2 | IoExtDev 芯片故障查询命名为 `GetDiag` | AUTOSAR 层级错误——IoExtDev 用 `GetDevFaultSig` | 外部芯片级诊断用 `GetDevFaultSig`，IoMcu 信号级诊断用 `GetXxxSigDiag` |
| D3 | 对外接口使用全局变量而非函数 | 违反架构规则 | 全部对外接口为函数形式 |
| D4 | MainFunction 判定为不需要但仍强制生成 | 违反 MainFunction 必要性判定规则 | CAN/LIN 收发器等设备按判定规则决定；无周期采样/去抖/状态机推进/诊断的场景不生成 MainFunction |
| D5 | 变量名缺失类型后缀（如 `ModeState` 而非 `ModeState_e`） | 违反 naming-rules.md 的 `<xx><dt>` 规则 | enum 变量用 `_e` 后缀（`ModeState_e`），boolean 用 `_b`（`InitFlag_b`），uint32 用 `_u32`（`FaultFlags_u32`），struct 用 `_st`（`FaultSnapshot_st`），数组用 `_a`（`Counters_au8`） |
| D6 | 配置结构体成员缺失类型后缀（如 `StbN_DioId` 而非 `StbN_DioId_u16`） | 同上，所有变量标识符必须带类型后缀 | `StbN_DioId_u16`、`ModeSwitchTimeoutMs_u16` |
| D7 | typedef/enum/struct 名称缺失 `Type` 后缀 | 违反 naming-rules.md 类型命名规则 | `Gp_TJA1043_ModeStateType`、`Gp_TJA1043_FaultSnapshotType` |

### 14.5 标定与策略反模式

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| E1 | IoExtDev 族生成标定参数 | IoExtDev 默认无标定流程 | 标定项保持 Empty，阈值和时序参数归类为编译期配置 |
| E2 | 策略项可以表达为简单宏开关但仍拆成独立 strategy_item | 过度设计 | 简单行为选择保留为 config_macros 中的 `Behavior Selection` 类型宏 |

### 14.6 校验时机

- **§9.7 架构渲染前**：对照本清单逐项检查语义对象（config_macros、dependency_apis、file_items、memmap_sections、calibration_items），发现问题立即修正。
- **§9.8 产物输出后**：对照渲染后的 Markdown 再次检查——确认引脚型设备未出现 `FC_Reg.h`/`REG CONST`，确认无版本宏，确认无逐引脚 DIO 宏。
- 任何命中反模式的条目 → 修正后重新渲染，不降级为风险项（这些是硬错误，不是待确认项）。
