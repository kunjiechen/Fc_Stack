---
name: fc-implementation-workbench
description: "用于设计、评审和整理 FC 实现层详细设计，包括单核或多核框架、配置布局、DET 流程、状态机、内部函数、运行参数设计、故障处理以及面向编码的设计骨架。"
---

# FC 实现工作台

## 1. 定位

这是一个**实现层详细设计 skill**，负责把需求、架构与参考工程约束转成可落地的详细设计方案。

核心链路：

```text
需求 / 架构 / 参考 FC / 芯片约束
→ Grounding 选择
→ 结构化设计对象
→ 详细设计生成
→ 校验
→ 细化与评审
```

它不是代码自动驾驶，也不是需求生成器。

## 2. 适用范围

适合处理：

- FC 详细设计生成与重构
- 面向编码的框架设计
- `Cfg.h`（配置宏参）/ `CfgData.h`（配置类型定义）/ `Cfg.c`（配置类型实例化）/ `Callout` / `MemMap` 设计
- 单核、多核、per-core 运行参数设计
- `DET`、状态机、故障流、复位与 `NoClear` 设计
- 内部函数拆分、接口子功能分解、执行步骤设计
- 基于真实项目 FC 的实现风格归一化

## 3. 明确边界

可以产出：

1. 实现摘要
2. 正式详细设计 Markdown
3. 编码脚手架计划
4. 实现评审结论
5. 面向代码生成的设计对象

不能凭空捏造：

- 芯片时序值
- 寄存器地址
- 项目专属信号 ID
- 故障阈值
- NVM Block 绑定关系

缺失时必须显式标记为假设、待确认或待补料。

## 4. 输入优先级

```text
用户当前需求
→ 当前架构或设计草稿
→ 芯片详细设计输入（条件加载）
→ 本地项目编码规则
→ 本 skill 的保留规则
→ 真实项目 grounding 摘要
→ AI 推断
```

冲突处理原则：

- 以当前项目显式输入为最高优先级
- 架构约束高于 demo 习惯
- grounding 只作为风格证据，不直接覆盖项目决定
- 不要悄悄改掉用户已经指定的命名、分层和接口边界
- D1-D8 芯片详细设计输入与 SRS/架构冲突时，以 SRS/架构为准，差异记录为详细设计风险项

## 5. 最小加载策略

默认只加载：

1. 用户提供的需求、架构、实现草稿或目标 FC 文件
2. 本 `SKILL.md`
3. 芯片详细设计输入（条件加载，见 §8.1；消费映射表见 §8.1.3，交叉校验见 §8.1.4）
4. `references/templates/output-template.md`（唯一正式交付模板，覆盖所有输出模式）
5. 当前问题真正需要的规则文件

按需加载：

- `references/workflow.md`
  任务是完整生成、流程改造或全链路排查时再读
- `references/grounding/index.yaml`
  需要选参考 FC 或模块族不清楚时再读
- `references/grounding/modules/*`
  需要接口形态、per-core、Callout、Cfg/Runtime 证据时再读
- `references/grounding/patterns/*`
  需要抽象出来的实现模式时再读
- `references/semantic-model.md` 与 `references/schemas/*`
  需要稳定结构化中间对象时再读

## 6. 规则文件分工

- `references/rules/implementation-rules.md`
  实现设计总规则、边界与冲突处理
- `references/rules/code-structure-rules.md`
  文件族、单核/多核框架、配置布局、Callout 放置、运行参数类型形态
- `references/rules/state-and-fault-rules.md`
  状态机、DET、运行时错误、故障、复位和 `NoClear`
- `references/rules/flowchart-rules.md`
  何时输出流程图，以及流程图该画到什么粒度
- `references/rules/implementation-review-checklist.md`
  正式实现评审和编码就绪检查

加载建议和索引看 `references/README.md`。

## 7. 什么时候用这个 skill

当用户要做以下事情时使用：

- FC 详细设计
- 面向编码的实现设计
- `cfg` / `callout` / 运行参数设计
- 状态机代码设计
- 内部函数拆分
- 故障处理设计
- 单核或多核实现框架设计
- 实现评审、清理和补强

以下场景不要用它：

- 纯需求抽取
- 纯软件架构生成
- 与 FC 无关的泛 C 语言教学

## 8. 输入充分度

- `L1`
  需求 + 架构，足够生成详细设计草稿
- `L2`
  需求 + 架构 + 公司规则 + 参考 FC，足够生成面向编码的详细设计
- `L3`
  需求 + 架构 + 公司规则 + 芯片详细设计输入 + 参考 FC，足够做强约束实现设计与脚手架指导

低于 `L2` 时，必须保留假设。

### 8.1 芯片详细设计输入加载规则

**触发条件**：当详细设计生成任务中可从任意来源确定 FC 名称时。

#### 8.1.1 路径解析与加载判定

**路径解析优先级**：

1. **用户显式路径** — 用户在对话中明确给出芯片详细设计输入文件路径时，直接使用
2. **约定路径自动发现** — 按以下规则拼接路径并检测文件是否存在：

```text
Output/<FC>/Doc/ChipViews/<FC>_芯片详细设计输入.md
```

3. **降级兜底** — 以上两种方式均未找到有效文件时，降级为仅凭 SRS + 架构工作

**加载行为表**：

| 场景 | 行为 |
|------|------|
| 文件存在且 D1~D8 全部有内容 | 加载全部 8 个域，按 §8.1.3 消费规则注入详细设计各章节 |
| 文件存在但部分域缺失 | 加载可用域，缺失域在详细设计风险表中标记为 `D域缺失-待确认`，对应设计对象标记 `source=D1-D8缺失`，常量值标记为假设 |
| 文件不存在（降级模式） | 详细设计生成不阻塞，降级为仅凭 SRS + 架构工作，缺失的芯片行为常量标记为假设，自动插入 R-CHIPVIEW-DESIGN 风险项 |
| 用户显式指定"不用芯片详细设计输入" | 跳过自动发现，直接降级模式，不插入 R-CHIPVIEW-DESIGN |

#### 8.1.2 降级模式下的风险项

文件不存在时，自动插入以下风险项到详细设计风险表：

```markdown
| R-CHIPVIEW-DESIGN | 芯片详细设计输入缺失 |
  缺芯片详细设计输入文件（路径：Output/<FC>/Doc/ChipViews/<FC>_芯片详细设计输入.md），
  以下详细设计决策基于 SRS + 架构推导，待芯片行为确认：
  寄存器位掩码/移位量/读写副作用/RMW约束(D1)、状态转换精确条件(D2)、
  故障源触发条件和清除方式(D3)、操作时序min/max值(D4)、初始化验证读回值(D5)、
  数据组装规则(D6)、I2C命令编码(D7)、跨寄存器访问顺序约束(D8)。 |
  §6.1 执行步骤 / §7 状态机 / §11 配置常量 / §9 Fault |
  建议先执行需求生成流程以产出芯片详细设计输入，或在对话中提供该文件路径后重新生成详细设计。 |
  待评审 |
```

#### 8.1.3 D1~D8 消费映射表

芯片详细设计输入提供 8 个域的数据，按以下规则消费到详细设计各章节：

<style>
table { font-size: 0.92em; }
th:first-child { width: 9%; }
th:nth-child(2) { width: 18%; }
th:nth-child(3) { width: 73%; }
</style>

| D域 | 消费到的详细设计章节 | 消费方式 |
|-----|-------------------|---------|
| **D1** 寄存器完整行为与常量表 | §6.1 外部接口执行步骤 | 读写副作用（如读 Input Port 清除 INT\）→ 读写 API 执行步骤中增加中断状态处理；RMW 约束 → 写操作步骤中明确 RMW 流程；模式访问限制 → 执行步骤中的状态前置检查 |
| | §6.2 内部函数 | 每寄存器行为约束 → 拆分为独立内部函数（如 `ReadInputPort`、`WriteOutputPort`、`ReadConfig`）；保留位写策略 → 内部函数中的位掩码操作；读回锁存值 vs 引脚实际电平 → 读操作语义区分 |
| | §11 配置参数 | 位段掩码(hex)+移位量 → `FC_Reg.h` 常量定义；访问属性+复位值(hex) → 配置类型字段的默认值依据；写后等待时间 → `FC_Cfg.h` 时序宏 |
| | §10 运行参数 | 读副作用（如读 Input Port 可能清除中断标志）→ 运行态标志变量（如 `IntStatusChanged_b`）；模式访问限制 → 运行态模式检查变量 |
| **D2** 状态转换条件 | §7 状态机 | 完整映射：当前状态/下一状态/触发条件/判定方式/转换延迟 → 状态机转换表的条件函数+动作函数；转换延迟值（如 t_rec(rst) ≥ 200ns）→ `FC_Cfg.h` 中状态转换超时宏 |
| **D3** 故障源行为 | §9 Fault | 每个故障源的完整映射：故障名 → 故障项名称；故障类型（芯片故障/驱动逻辑故障）→ 故障类型列；硬件触发条件 → 检测条件列；可观测标志位 → 检测方式列；芯片硬件自动响应动作 → 响应动作参考；清除方式 → 确认策略列；是否自恢复 → 恢复策略列；清除前置条件 → 恢复条件列 |
| | §7 状态机 | 故障发生是否触发状态转换 → 故障状态节点+转换路径；上电复位/欠压复位 → 复位恢复状态转换 |
| **D4** 操作时序参数 | §11 配置参数 | 每个参数的符号+含义+min/max值 → `FC_Cfg.h` 时序阈值宏（如 `FC_CFG_T_V_Q_MAX_NS`、`FC_CFG_T_REC_RST_MIN_NS`）；单位 → 宏注释 |
| | §6.1 外部接口执行步骤 | t_v(Q) max 300ns → 写 Output 后的等待步骤；t_rec(rst) → Init 中的复位恢复等待步骤；t_rst(INT_N) → 中断清除等待步骤 |
| | §6.3 Callout 约束 | I2C 时序参数组（f_SCL、t_BUF、t_HD;STA、t_SU;STO 等）→ I2C Callout 的 Basic Constraints 中写入时序要求；t_w(rst) → DIO Callout 的 RESET\ 控制约束 |
| **D5** 初始化约束 | §6.1 Init() 步骤拆分 | 操作序号+前置条件+判定成功标准 → Init 执行步骤顺序；精确等待时间 → 步骤间延迟量；失败重试次数上限+失败行为 → 错误返回点和重试循环边界 |
| | §6.2 内部函数 | 期望读回值(hex)（如 Config0=0xFF, Config1=0xFF）→ 内部验证函数（如 `VerifyConfigDefaults`）的判定常量 |
| | §8 DET | 失败行为（如"上报初始化验证失败"）→ DET 检查点；重试次数上限 → DET 错误类型区分（重试耗尽 vs 单次失败） |
| **D6** 读回数据组装规则 | §6.1 ReadInput/ReadOutput 执行步骤 | 源寄存器+各寄存器取值 bit 段+组装后总位宽+有无符号 → 多字节读取后的移位拼接步骤；组装顺序约束 → 读取顺序 |
| | §6.2 内部函数 | 组装逻辑 → 独立内部函数（如 `Assemble16BitInput`）；每个逻辑值的寄存器对映射 → 函数输入/输出定义 |
| **D7** 命令/响应编码 | §6.3 Callout 行为约束 | 器件地址表（A1/A0 四种组合的 7 位地址+写地址+读地址）→ I2C Callout 的地址参数说明；命令字节表（8个寄存器地址）→ Callout 的命令参数说明；I2C 读写帧序列（START→地址→命令字节→数据→STOP 完整步骤）→ Callout 行为描述的权威来源，这是 SRS 和架构不会描述的硬件协议细节 |
| | §11 配置参数 | 器件地址 + 命令字节 → `FC_Reg.h` 或 `FC_Cfg.h` 中的地址/命令常量宏 |
| | §6.1 读写接口执行步骤 | 读写帧序列的 ACK/NACK/重复 START 步骤 → 读写 API 中 Callout 调用前后的帧校验步骤 |
| **D8** 跨寄存器关系 | §6.1 执行步骤顺序约束 | Burst 交替行为（port 0↔port 1 交替，无地址递增/回绕）→ 多字节读写时的地址切换策略（Burst 连续 vs 单寄存器分别访问）；输出端口生效依赖方向配置 → 写 Output 前必须先写 Configuration 的步骤顺序硬约束 |
| | §6.2 内部函数 | 跨寄存器访问顺序约束 → 内部顺序控制函数；寄存器对交替边界（0x00↔0x01, 0x02↔0x03, 0x04↔0x05, 0x06↔0x07）→ 地址切换逻辑 |

**部分域可用时的处理**：

| 条件 | 行为 |
|------|------|
| D1~D8 完整可用 | 上述全部消费，详细设计各章节有芯片权威数据支撑 |
| D1~D8 部分可用 | 可用域正常消费；缺失域在设计对象中标记 `source=D1-D8缺失`，对应常量值标记为假设；在风险表中逐域记录缺失影响 |
| D1~D8 不可用（降级） | 消费规则不执行，所有设计对象从 SRS+架构推导，芯片行为常量标记为假设，自动插入 R-CHIPVIEW-DESIGN |

#### 8.1.4 消费后交叉校验

D1~D8 消费完成后，反查详细设计输出的覆盖完整性：

| 检查项 | 校验逻辑 | 缺口处理 |
|--------|---------|---------|
| D1 R/W 寄存器 → 写路径覆盖 | 每个标记为 R/W 的寄存器是否在 §6.1 中有对应的写 API 或步骤 | 缺则列入风险表，报接口遗漏 |
| D1 读副作用 → 运行态处理 | 有读副作用的寄存器（如 Input Port 读可能清除 INT\）是否有对应的运行态标志/计数器 | 缺则列入风险表，报运行态缺失 |
| D2 状态转换全集 → 状态机覆盖 | D2 的每行转换是否在 §7 中有对应转换条目（当前状态+下一状态+条件函数+动作函数） | 缺则列入风险表，报状态转换遗漏 |
| D3 故障全集 → Fault 表覆盖 | D3 的每个故障源是否在 §9 Fault 表中有对应条目，且故障类型、清除方式、自恢复标记与 D3 一致 | 缺则列入风险表，报故障遗漏 |
| D4 带 min/max 的时序参数 → 配置宏 | 每个有 min 或 max 约束的时序参数是否生成了对应 `FC_Cfg.h` 宏 | 缺则列入风险表，报配置缺失 |
| D5 初始化步骤 → Init() 步骤覆盖 | D5 的每个初始化操作是否在 Init 步骤拆分中体现（包括等待时间和重试上限） | 缺则列入风险表，报初始化步骤遗漏 |
| D7 器件地址/命令字节 → 配置常量 | 地址表和命令字节是否有对应的 `FC_Reg.h` 常量或 `FC_Cfg.h` 宏 | 缺则列入风险表，报配置缺失 |

交叉校验发现的缺口，列入详细设计风险表，索引从 R1 递增（R-CHIPVIEW-DESIGN 已占一个索引）。

## 9. 推荐执行步骤

详细设计生成按以下步骤执行。每步有明确的输入、参考文件、操作和产出。

### 9.0 生成前预检（Pre-Flight Checklist）

在开始 §9.1 之前，确认以下 7 项已明确。硬阻断项不明确 → 阻断，向用户确认后再继续。

| # | 检查项 | 来源 | 阻断？ |
|---|--------|------|--------|
| 1 | FC 名称已提取（保留原始大小写和下划线） | 用户输入 / 架构文档 | **是** |
| 2 | 架构设计文件路径已确认 | 用户输入 / 自动发现 | **是** |
| 3 | 芯片详细设计输入是否可用？路径？ | §8.1.1 自动发现 | 否（支持降级） |
| 4 | Grounding 模块已选定（IoExtDev / IoMcu / BswSys） | §9.3 选择规则 | **是** |
| 5 | 架构族 / 子类型已从架构文档中提取 | 架构文档 §1 | 否（可从通信接口推导） |
| 6 | MainFunction 必要性已从架构文档中确认 | 架构文档 §2 | 否（可从 SRS 场景推导） |
| 7 | 输出模式已判定（Quick / Formal / Released） | 用户指定 | 否（默认 Formal） |

检查通过后，在详细设计元信息中记录：架构族、子类型、MainFunction_Required、已加载的参考文件清单。

### 9.1 输入校验与准备

**目的**：确认输入是否满足详细设计生成的最低条件，识别降级场景。

**参考文件**：架构设计文档、芯片详细设计输入（§8.1）

**操作**：

1. 确认 FC 名称已从用户输入或架构文档中提取
2. 检查架构设计文件是否可用（用户提供路径或从 `Output/<FC>/Doc/SDD/` 自动发现）
3. 若架构设计不可用 → 中止，提示用户先执行架构生成或提供架构文件路径
4. 按 §8.1.1 规则加载芯片详细设计输入
5. 从架构文档中提取架构族、子类型、MainFunction 必要性（若架构文档未明确，从通信接口类型和 SRS 场景推导）

**产出**：输入清单（架构文件路径、芯片设计输入可用性、关键参数摘要）

### 9.2 架构到详细设计消费映射表

**目的**：定义架构文档中的每个语义对象如何消费到详细设计各章节。这是架构 skill 与实现 skill 的正式接口。

**操作**：对架构文档中的每个语义对象，按以下映射表确定其在详细设计中的落点：

| 架构对象 | 消费到的详细设计章节 | 消费方式 |
|---------|-------------------|---------|
| `external_apis` | §6.1 外部接口设计 | 原样展开为完整子功能拆分 + 执行步骤 + 流程图 |
| `dependency_apis` | §6.3 依赖接口设计 | 展开为 Callout 行为约束 + 关联接口 + 时序要求 |
| `config_macros` | §11.1 配置宏参 | 展开为 7 列表格，增加设计依据和状态列 |
| `config_params` | §11.2 配置类型 | 展开为结构体定义 + 每个成员的 Id 取值表 |
| `runtime_states` | §10 运行参数 | 展开为运行变量表 + 运行参数类型（标注 global/per-core 归属） |
| `state_transitions` | §7 状态机 | 展开为状态定义表 + 转换详表 + 流程图 |
| `fault_handlers` | §9 故障处理 | 展开为故障项表（≥15 列）+ 确认/恢复/清除策略 |
| `memmap_sections` | §12 MemMap | 展开为段表 + 起止宏 + 所用文件 |
| `file_items` | §4 文件列表 | 展开为文件名 + 必需/可选 + 职责 + 关键内容 |
| `risk_items` | §14 风险与待确认项 | 展开 + 新增详细设计独有的风险项 |
| 未消费对象 | §14 | 自动归入 R-OTHER 风险项 |

**遗漏检查**：消费完成后，统计未被任何详细设计章节消费的架构对象，列入 §14 风险表中标记为待确认。

### 9.3 Grounding 选择

**目的**：从架构设计文档和芯片详细设计输入中选定最接近的 grounding 模块或模式。

**参考文件**：`references/grounding/selection_rules.md`、`references/grounding/index.yaml`

**操作**：

1. 从架构文档判定架构族（IoExtDev / IoMcu / BswSys / Cdd）
2. 按 selection_rules.md 的算法选择 grounding 模块
3. 记录采纳和拒绝的模块及模式，每个决策附理由

**产出**：grounding 选择结论、已加载的 grounding 模块清单

### 9.4 语义对象构建

**目的**：在生成 Markdown 之前，先构建结构化中间对象，以便校验和追溯。

**参考文件**：`references/semantic-model.md`（必读）

**操作**：按以下顺序逐类构建语义对象，每步引用 semantic-model.md 的 schema 定义做字段级校验：

```
module_identity → source_input → file_item → external_api →
dependency_api → internal_function → state_machine → core_model →
task_model → cfg_macro → cfg_table → runtime_state →
det_object → fault_object → memmap_section → pending_item
```

每构建一个对象，对照 schema 做字段级校验。

**产出**：详细设计语义对象集（内部 JSON，不输出为用户文件）

### 9.5 设计展开

**目的**：基于 §9.4 构建的语义对象，展开各章节的详细设计内容。

**操作**：

1. **文件族设计**：按 code-structure-rules.md 确定文件清单（Required/Conditional/Optional），包括 `<FC>.c`、`<FC>.h`、`<FC>_Cfg.h`、`<FC>_CfgData.h`、`<FC>_Cfg.c`、`<FC>_Types.h`、`<FC>_Reg.h`（仅寄存器型）、`<FC>_Callout.h`、`<FC>_Callout.c`（如有 Callout）、`<FC>_MemMap.h`
2. **配置设计**：
   - config_macros 展开为 7 列表格
   - config_params 展开为 CfgType 结构体定义 + 每个成员的 Id 取值表
   - runtime_states 展开为运行变量表
3. **语义对象逐类构建**：按 `references/semantic-model.md` 的 16 类对象逐类构建，每步引用 schema 定义

### 9.6 规则校验

**目的**：在渲染 Markdown 之前校验语义对象的完整性和一致性。

**参考文件**：`references/validation_rules.md`、`references/golden_checks.md`

**校验项**：

1. validation_rules.md 的 8 条规则
2. golden_checks.md 的 P0/P1 检查项
3. **反模式扫描**（对照 §14 清单逐项检查）：
   - 配置宏前缀（使用 `Gp_<FC>_` 而非 `FC_`）
   - Callout 归并（无逐引脚拆分）
   - 命名后缀（`_e` / `_b` / `_u32` / `_st` / `Type`）
   - 文件族完整性（引脚型不渲染 FC_Reg.h）
4. **硬错误**阻断，**风险项**列入风险表

**校验失败处理**：缺字段补全、冲突标记为风险项、无法自动修复的降级为 Draft

### 9.7 交叉校验

**目的**：用 D1-D8 芯片设计输入反查详细设计覆盖完整性。

**触发条件**：芯片设计输入可用时执行；不可用时跳过。

**检查项**（同 §8.1.4）：

- D1 R/W 寄存器 → 写路径覆盖
- D1 读副作用 → 运行态处理
- D2 状态转换全集 → 状态机覆盖
- D3 故障全集 → Fault 表覆盖
- D4 时序参数 → 配置宏覆盖
- D5 初始化步骤 → Init() 步骤覆盖
- D7 器件地址/命令字节 → 配置常量覆盖

缺口列入 §14 风险表。

### 9.8 渲染与输出

**目的**：将校验通过的语义对象渲染为正式详细设计 Markdown 并输出。

**参考文件**：`references/templates/output-template.md`、`references/chapter_generation_rules.md`

**操作**：

1. 按 output-template.md 的 15 章模板渲染，每章从对应语义对象取值
2. 确保渲染完整性：
   - §1.1 必须有 ASCII art 架构框图
   - 流程图按 flowchart-rules.md 渲染
   - 故障表不使用超宽表格，使用逐故障 key-value 格式
3. 输出详细设计到输出路径（见 §10）
4. 生成配套产物：`Review_<FC>_详细设计规范.md`、`Check_<FC>_详细设计规范.md`、`Trace_<FC>_详细设计规范.md`
5. **输出后校验（Gate Check）**：对渲染产物执行反模式扫描和 grep 门控检查。任何硬错误 → 修正后重新渲染。

#### 强制 Grep 门控（必执行，不可跳过）

产物渲染完成后，立即用以下 grep 命令逐项检查。任何命中 → 硬错误，修正后重新渲染。

```bash
# 检查 1: 确认无 FC_ Cfg.h 前缀（应使用 Gp_<FC>_）
grep -n 'FC_CFG_' <FC>_模块详细设计规范.md  # 期望: 空

# 检查 2: 确认无版本宏
grep -n 'CFG_SW_MAJOR_VERSION\|CFG_SW_MINOR_VERSION' <FC>_模块详细设计规范.md  # 期望: 空

# 检查 3: 确认逐引脚 Callout 未出现（DIO Write/Read 必须使用 Id_u16 参数）
grep -n 'Callout.*DioWrite\|Callout.*DioRead' <FC>_模块详细设计规范.md | grep -v 'Id_u16'  # 期望: 空

# 检查 4: 确认所有 Callout 有 FC 前缀
grep -n 'Callout' <FC>_模块详细设计规范.md | grep -v '<FC>_Callout\|FC_Callout'  # 期望: 空

# 检查 5: 确认引脚型设备未渲染 FC_Reg.h
grep -n 'FC_Reg\.h' <FC>_模块详细设计规范.md  # 引脚型设备期望: 空

# 检查 6: 确认 _Callout.h 和 _Callout.c 存在（如有 Callout）
grep -n '_Callout\.h\|_Callout\.c' <FC>_模块详细设计规范.md  # 有 Callout 时期望: 找到

# 检查 7: 确认架构框图存在
grep -n '架构框图\|调用层次' <FC>_模块详细设计规范.md  # 期望: 找到

# 检查 8: 确认流程图存在
grep -n '流程图\|flowchart' <FC>_模块详细设计规范.md  # 期望: 找到

# 检查 9: 确认无 9 列超宽故障表
grep -n '^| 故障名称 | 分类 | 检测机制 | 确认策略 | 故障响应 | 快照策略 | 恢复策略 | 清除策略 | 影响范围 |$' <FC>_模块详细设计规范.md  # 期望: 空

# 检查 10: 确认状态转换表无超宽列
grep -n '^| .*| .*| .*| .*| .*| .*| .*| .*|' <FC>_模块详细设计规范.md | wc -l  # 人工核对是否有超宽表格
```

以上 grep 校验必须全部通过。若任一命中 → 定位到具体行号，修正后重新渲染，再跑 grep 校验直至全部通过。校验结果记录在 `Check_<FC>_详细设计规范.md` 的 Gate 章节中。

#### 依赖接口设计硬规则（Callout 归并规则）

继承架构 skill 的设计决策，在详细设计中展开为可编码设计。

架构阶段已经将引脚按硬件访问方式归并为参数化 Callout（如 `FC_CalloutDioWrite(Id, Level)`），详细设计阶段**严禁将参数化 Callout 重新拆分为逐引脚专用函数**。

详细设计中的 Callout 展开方式：

| 架构 Callout | 详细设计 §6.3 展开内容 | 引脚区分方式 |
|-------------|---------------------|-------------|
| `FC_CalloutDioWrite` | 写入调用约束、Id 参数取值表、时序要求 | `FC_CFG_DIO_ID_<PIN>` 配置宏 |
| `FC_CalloutDioRead` | 读取调用约束、Id 参数取值表、电平判断逻辑 | `FC_CFG_DIO_ID_<PIN>` 配置宏 |
| `FC_CalloutI2cWrite` | 器件地址参数、命令字节序列、Burst 行为约束 | `FC_CFG_I2C_DEV_ADDR` 配置宏 |
| `FC_CalloutI2cRead` | 器件地址参数、读帧序列、ACK/NACK 处理 | `FC_CFG_I2C_DEV_ADDR` 配置宏 |
| `FC_CalloutSpiTransceive` | SPI 模式、帧位宽、CS 控制时序 | `FC_CFG_SPI_DEV_ID` 配置宏 |

**反例（详细设计中不允许）**：
- 对外部接口的执行步骤中写"调用 `FC_CalloutNResetDioWrite(LOW)`"——RESET 的身份不应进入函数名
- 正确写法："调用 `FC_CalloutDioWrite(FC_CFG_DIO_ID_RESET, STD_LOW)`"——引脚身份在宏中，函数保持通用

**新增引脚的处理**：
- 同类型新引脚 → 只需新增 `FC_CFG_DIO_ID_<NEW_PIN>` 宏 + 在配置类型 `DioChannelIdType` 中增加枚举成员
- 不需要新增 Callout 函数、不需要修改 Callout.h/c

## 10. 输出物

### 10.0 模板与输出模式

所有输出模式均使用 `references/templates/output-template.md` 作为唯一正式交付模板。模式差异仅体现在风险表密度和评审完整度上：

- **Quick Draft**：首轮快速讨论，风险表仅保留 3~5 条高优先级真实风险项 + R-OTHER
- **Formal Draft**（默认）：完整草稿，风险表覆盖所有待确认和待修改项
- **Released**：所有风险项已评审，文档可正式发布

### 10.1 输出路径与命名规则

**输出路径解析优先级**（按顺序判定，命中即停止）：

1. **用户显式路径** — 用户在对话中明确给出输出目录时，直接使用
2. **输入文件同级推断** — 当用户提供的输入文件（SRS/架构/芯片设计输入）均位于同一 `Output/<FC>/Doc/` 目录树下时，输出到该目录下的 `SDS/` 子目录。判定规则：扫描用户提供的所有输入文件路径，若它们共享 `Output/<FC>/Doc/` 前缀，则输出路径为 `<共同前缀>/SDS/`。此规则优先于默认路径
3. **默认路径降级** — 以上规则均不匹配时，使用项目根目录下的默认路径：

```text
Output/<FC_SHORT_NAME>/Doc/SDS/
```

- 详细设计生成结果不得写回 skill 目录内部
- **路径判定必须在生成前执行，不得跳过**

**标准输出文件名：**

```text
<FC>_模块详细设计规范.md
```

**伴生文档硬性要求（每次生成必须全部产出，不得遗漏）：**

每次正式详细设计生成**必须同步输出**以下 4 个文件，缺一不可：

```text
<FC>_模块详细设计规范.md           ← 主文档
Review_<FC>_详细设计规范.md         ← 评审记录（必产）
Check_<FC>_详细设计规范.md          ← 检查清单（必产）
Trace_<FC>_详细设计规范.md          ← 追溯矩阵（必产）
```

- `Review_<FC>_详细设计规范.md` 记录详细设计评审重点、阻断项、风险关闭记录、评审结论和是否允许进入编码。
- `Check_<FC>_详细设计规范.md` 记录详细设计检查清单、检查结果、证据、主要问题和下一步动作。
- `Trace_<FC>_详细设计规范.md` 记录 Requirement / Architecture → Detailed Design 的覆盖对象、覆盖状态、详细设计落点和关闭条件。
- **输出后校验**：生成完成后，必须验证输出目录下存在全部 4 个文件。若伴生文档缺失，视为产出不完整，必须立即补齐。

常见输出内容：

- 模块职责与文件结构
- 外部接口与依赖接口设计
- 配置宏参、配置类型、运行变量与运行参数类型设计
- 状态机与故障处理
- `DET` 与防御式检查策略
- `MemMap` 与 `NoClear` 数据布局
- 编码骨架建议与评审问题清单

---

## 14. 禁止生成的模式（Anti-Patterns）

本节是**集中式反模式清单**。在语义对象构建（§9.4）和产物输出后校验（§9.8）两个节点，必须逐项检查以下条目。任何命中均为错误，必须修正后重新渲染。

### 14.1 配置宏参反模式（Cfg.h）

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| A1 | `#define CFG_SW_MAJOR_VERSION 1` | 版本管理由项目构建系统负责，不属于 FC 配置项 | 不生成任何版本宏 |
| A2 | `#define CFG_SW_MINOR_VERSION 0` | 同上 | 不生成任何版本宏 |
| A3 | `#define FC_CFG_DIO_ID_STB_N 0` | 引脚身份被拆成独立宏写入 Cfg.h，引脚多了宏泛滥 | 引脚 ID 作为 `CfgType` 结构体成员（如 `StbN_DioId_u16`）放入 Cfg.c |
| A4 | `#define FC_CFG_DIO_ID_ERR_N 2` | 同上——逐引脚宏 | 同上——CfgType 成员 |
| A5 | `#define FC_CFG_I2C_DEV_ADDR 0x74` | I2C 器件地址是数据查表（不改变编译路径），应在 Cfg.c 中作为 const 常量 | 归入 Cfg.c 配置参数 |
| A6 | 为每个外部接口生成 `#define FC_CFG_<API>_ENABLE` | 编译期裁剪仅在需求明确要求时保留 | 不为无明确编译期分支需求的 API 生成 enable 宏 |
| A7 | `#define FC_CFG_DEV_ERROR_DETECT`（使用通用 `FC_` 前缀） | 缺少模块命名空间隔离 | 必须使用 `<FC>_CFG_DEV_ERROR_DETECT`（如 `Gp_NCA9539_CFG_DEV_ERROR_DETECT`） |

### 14.2 依赖接口反模式（Callout）

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| B1 | `<FC>_CalloutResetDioWrite(Level)` | 引脚身份进入函数名，无法复用 | 归并为 `<FC>_CalloutDioWrite(Id_u16, Level_u8)`，引脚身份通过 Id 参数区分 |
| B2 | `<FC>_CalloutIntDioRead()` | 同上 | 归并为 `<FC>_CalloutDioRead(Id_u16, Level_pu8)` |
| B3 | 每新增一个 DIO 引脚就新增一个 Callout 函数 | 违反归并原则，Callout 数量膨胀 | 同类硬件访问方式 → 恰好 1 个参数化 Callout |
| B4 | `<FC>_CalloutStbDioWrite(Level)` + `<FC>_CalloutEnDioWrite(Level)` | 两个 DIO 输出引脚生成了两个 Callout | 合并为 1 个 `<FC>_CalloutDioWrite(Id_u16, Level_u8)` |
| B5 | 对引脚直连型设备生成 `<FC>_CalloutSpiTransceive` 或 `<FC>_CalloutI2cWrite/Read` | 芯片无 SPI/I2C 接口 | 仅生成 DIO Callout |
| B6 | Callout 原型中使用数组声明式 `uint8 TxData_au8[]` | 违反指针形参规范 | 使用指针形式 `uint8* TxData_pu8` |
| B7 | DIO Read Callout 缺少输出参数 `uint8* Level_pu8` | 无法获取读取结果 | 必须包含 `uint8* Level_pu8` 输出指针 |
| B8 | 使用不绑定 FC 的通用 Callout 名（如 `FC_CalloutDioWrite`） | 缺少 FC 命名空间隔离，跨模块符号冲突风险 | 必须包含 `<FC>_Callout` 前缀，如 `Gp_NCA9539_CalloutDioWrite` |

### 14.3 文件族反模式

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| C1 | 引脚直连型设备渲染 `FC_Reg.h` | 无寄存器，不需要寄存器定义文件 | 引脚型不渲染 FC_Reg.h 行 |
| C2 | 存在 Callout 但文件列表遗漏 `<FC>_Callout.h` 或 `<FC>_Callout.c` | Callout 没有文件载体 | 存在任一 Callout → `_Callout.h` 和 `_Callout.c` 均为 Required |
| C3 | CONST 段只给 GLOBAL，遗漏 per-core | 单核也有对应段，架构完整性缺失 | 始终包含 CONST GLOBAL + CONST per-core |
| C4 | `FC_Cfg.h` 中包含 `FC_Reg.h` 但设备为引脚型 | 无 Reg.h 却写了 include 关系 | 引脚型设备：Cfg.h 不包含 Reg.h |

### 14.4 接口命名反模式

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| D1 | FC 名称 `Gp_TJA1043` 被自动 CamelCase 为 `Gp_Tja1043_Init` | 违反命名空间保留原则 | 保留原始命名：`Gp_TJA1043_Init` |
| D2 | 变量名缺失类型后缀（如 `ModeState` 而非 `ModeState_e`） | 违反 naming-rules.md 的 `<xx><dt>` 规则 | enum 变量用 `_e` 后缀，boolean 用 `_b`，uint32 用 `_u32`，struct 用 `_st` |
| D3 | 配置结构体成员缺失类型后缀（如 `StbN_DioId` 而非 `StbN_DioId_u16`） | 所有变量标识符必须带类型后缀 | `StbN_DioId_u16`、`ModeSwitchTimeoutMs_u16` |
| D4 | typedef/enum/struct 名称缺失 `Type` 后缀 | 违反 naming-rules.md 类型命名规则 | `Gp_TJA1043_ModeStateType`、`Gp_TJA1043_FaultSnapshotType` |

### 14.5 文档渲染反模式

| # | 反模式 | 错误原因 | 正确做法 |
|---|--------|---------|---------|
| E1 | 缺少 ASCII art 架构框图 | 详细设计缺少直观的分层调用结构图 | 必须生成调用层次图，至少 3 层（外部 API → 内部函数 → Callout），附图例说明 |
| E2 | 使用超宽 9 列故障全链路表 | 单元格内容过长导致 Markdown 渲染器解析失败 | 使用逐故障小节 + 2 列 key-value 表（维度/决策） |
| E3 | 缺少流程图 | 关键操作无执行路径可视化 | 按 flowchart-rules.md 生成 Init/MainFunction/故障处理流程图 |
| E4 | 状态转换表超宽（≥9 列） | 同 E2 | 使用合理列数或拆分为多个子表 |

### 14.6 校验时机

- **§9.4 语义对象构建时**：逐项检查以上反模式，发现问题立即修正
- **§9.8 产物输出后**：对渲染后的 Markdown 再次扫描——确认引脚型设备未出现 `FC_Reg.h`、无版本宏、无逐引脚 DIO 宏、无通用 `FC_` 前缀、Callout 文件清单完整、架构框图存在、无超宽故障表
- 任何命中 → 修正后重新渲染，不降级为风险项（这些是硬错误，不是待确认项）
