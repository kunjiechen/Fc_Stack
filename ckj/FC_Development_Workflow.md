# FC 开发工作流

## 1 概述

本文档定义 FcStack 平台开发一个完整 FC（Function Component）的端到端工作流。工作流遵循 V 模型与 Spec-Driven 开发模式，从输入准备、需求工程、架构设计、详细设计、编码实现到 UT/IT/ST、发布交付逐级推进。

本工作流的目标不是替代各阶段的专用规范，而是提供一条可执行的总流程：每一阶段明确输入、AI 操作步骤、人工审核点、返工路径、输出产物和质量门禁。若某一阶段的专项生成工作流尚未完善，应先按本文档预留框架执行，并在后续补充对应专项工作流。

## 2 总体原则

1. **V 模型顺序执行**：阶段 0 → SRS → SDD → SDS → Coding → UT → IT → ST → Release，不得跳过阶段。
2. **基线驱动下游**：上一阶段未通过人工审核和质量门禁，不得作为下一阶段正式输入。
3. **来源驱动**：任何需求、设计、代码、测试项都必须能追溯到上游输入或已批准约束。
4. **人工审核必经**：AI 可生成、整理、修正文档和代码，但阶段出口必须保留人工审核结论。
5. **问题显性闭环**：发现输入缺失、矛盾、不可实现或不可验证时，应登记问题并回到对应上游阶段修正。
6. **持续迭代**：当前缺失的专项标准或模板先登记为待完善项，不阻断总工作流框架建立。

## 3 流程总览

```text
阶段0: 输入准备与开发策划
    ↓ 人工审核 Gate 0
阶段1: 需求工程 SRS
    ↓ 人工审核 SRS Gate
阶段2: 架构设计 SDD
    ↓ 人工审核 SDD Gate
阶段3: 详细设计 SDS
    ↓ 人工审核 SDS Gate
阶段4: 编码实现 Coding
    ↓ 人工审核 Code Gate
阶段5: 单元测试 UT
    ↓ 人工审核 UT Gate
阶段6: 集成测试 IT
    ↓ 人工审核 IT Gate
阶段7: 系统测试 ST
    ↓ 人工审核 ST Gate
阶段8: 发布与交付
    ↓ Release Gate
```

## 4 工作目录与产物约定

当前仓库推荐目录如下：

| 类别 | 推荐位置 | 说明 |
| --- | --- | --- |
| 原始输入 | `Input/<FC_SHORT_NAME>/Original/` | 未经转换的 PDF、Word、图片、压缩包等原始资料 |
| 转换输入 | `Input/<FC_SHORT_NAME>/Conversion/` | Markdown、HTML、JSON、XML 等 AI 可准确识别资料 |
| 阶段输出 | `Output/<FC_SHORT_NAME>/Doc/` | SRS、SDD、SDS、TEST、TraceMatrix 等文档 |
| 代码输出 | `Output/<FC_SHORT_NAME>/Code/` 或 `src/` | FC 源码、配置和集成代码 |
| 标准规范 | `Standard/RuleAndTemplate/`、`Standard/Conversion/` | 各阶段模板、编写规范和转换后的标准 |
| 系统流程 | `System/`、`workflow/` | V 模型流程、项目注意事项和总工作流 |

若历史文档仍使用 `Standard/Template/`、`Standard/Markdown/` 等旧路径，应在执行时映射到当前仓库实际路径，并在工作流维护时逐步统一。

---

## 5 阶段0：输入准备与开发策划

### 5.1 目的

收集并归档 FC 开发所需的原始资料，完成格式转换、原始需求整理、开发范围确认和初始追溯框架建立。

### 5.2 触发条件

- 收到新的 FC 开发任务、客户需求、芯片适配需求或模块重构任务。
- 现有 FC 需要新增功能、迁移平台或重新进入 Spec-Driven 流程。

### 5.3 输入

| 输入类型 | 示例 | 推荐位置 |
| --- | --- | --- |
| 原始开发需求 | 客户需求、Feature Request、上层模块需求 | `Input/<FC_SHORT_NAME>/Original/` |
| 芯片资料 | Datasheet、User Manual、Reference Manual、Errata | `Input/<FC_SHORT_NAME>/Original/` |
| 系统/安全输入 | System Requirement、HARA、Safety Concept、FSR/TSR | `Input/<FC_SHORT_NAME>/Original/` |
| 标准规范 | AUTOSAR、ISO 26262、MISRA、项目规范 | `Standard/Original/`、`Standard/Conversion/` |
| 项目约束 | 开发流程、目录约定、工具链、构建方式 | `System/`、`workflow/` |

### 5.4 具体操作过程

1. **录入原始资料**
   - 将用户提供的原始文档放入 `Input/<FC_SHORT_NAME>/Original/` 或对应模块输入目录。
   - 保留文件原名、版本、来源、日期和获取方式。
   - 不在原始资料上直接修改内容。

2. **转换为 AI 可读格式**
   - PDF/Word/HTML/图片等资料转换为 Markdown、HTML、JSON、XML 或可读文本。
   - 转换结果放入 `Input/<FC_SHORT_NAME>/Conversion/`。
   - 对转换质量进行抽查，确认表格、章节号、图片文字、寄存器/引脚/时序等关键信息未丢失。

3. **编写或整理原始开发需求**
   - 若用户输入零散，应使用 `Standard/RuleAndTemplate/SRS/Template-FC原始开发需求.md` 整理为原始开发需求。
   - 原始开发需求只记录已知事实、用户意图和待确认项，不把未确认内容写成确定结论。
   - 每条原始需求分配稳定 ID，例如 `RAW-[FC]-FUNC-0001`。

4. **建立输入资料清单**
   - 记录文件名称、类型、版本、章节、适用性和预期用途。
   - 对不适用资料标注 N/A 原因。
   - 初步规划来源 ID，例如 `SRC-[FC]-RAW-0001`、`SRC-[FC]-DS-0001`。

5. **明确开发策划**
   - 确认模块名称、简称、所属层级、适用平台、安全等级。
   - 确认模块做什么、不做什么。
   - 确认依赖对象：上层调用者、下层驱动/服务、硬件资源、配置工具、测试环境。
   - 确认初始验证策略：Review、Analysis、Inspection、Test 的组合。

6. **建立初始追溯框架**
   - 预留来源 → SRS → SDD → SDS → Code → Test 的追溯列。
   - 如正式 TraceMatrix 模板尚未使用，可先在 SRS 或独立 Markdown 表格中建立入口。

### 5.5 人工审核点

阶段0必须由人工确认：

- 原始资料是否齐全、版本是否可信。
- 转换文档是否能支撑后续 AI 提取。
- 原始开发需求是否忠实表达输入，没有擅自扩展。
- 模块范围、安全等级和开发边界是否明确。
- 缺失输入是否已登记为开放项或待补充资料。

### 5.6 输出产物

| 产物 | 推荐文件 | 推荐位置 |
| --- | --- | --- |
| 转换资料 | 原文件对应 `.md/.html/.json/.xml` | `Input/<FC_SHORT_NAME>/Conversion/` |
| 原始开发需求 | `[FC] 模块原始开发需求.md` | `Input/<FC_SHORT_NAME>/Conversion/OriginalRequirements/` |
| 输入资料清单 | 可内嵌 SRS 追溯章节或独立文件 | `Output/<FC_SHORT_NAME>/Doc/SRS/` 或 `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |
| 初始追溯框架 | `Trace_[FC].md/html` | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |

### 5.7 Gate 0 通过条件

- [ ] 所有已知输入资料已归档并可读取。
- [ ] 原始资料已转换为 AI 可识别格式，并完成人工抽查。
- [ ] 原始开发需求已整理，且保留待确认项。
- [ ] 模块名称、简称、层级、安全等级和职责边界已明确。
- [ ] 初始来源 ID 和追溯框架已建立。

---

## 6 阶段1：需求工程（SRS）

### 6.1 目的

按照 SRS 工作流从输入资料中提取、推导并编写软件需求规范，形成可验证、可追溯、可作为 SDD 输入的需求基线。

### 6.2 触发条件

阶段0人工审核通过，或已批准带开放项进入 SRS 编写。

### 6.3 主要依据

| 类型 | 文件 |
| --- | --- |
| SRS 生成工作流 | `Standard/RuleAndTemplate/SRS/FC需求编写生成工作流.md` |
| SRS 编写规范 | `Standard/RuleAndTemplate/SRS/FC需求编写规范.md` |
| SRS 模板 | `Standard/RuleAndTemplate/SRS/Template-FC模块软件需求规范.md` |
| 原始需求模板 | `Standard/RuleAndTemplate/SRS/Template-FC原始开发需求.md` |
| SRS Gate 检查清单 | `Standard/RuleAndTemplate/SRS/Checklist/` |

### 6.4 具体操作过程

1. **建立输入资料索引**
   - 为每个输入文件或关键章节分配唯一来源 ID。
   - 记录文件名称、类型、章节/位置、版本/日期、适用性和预期需求类别。

2. **抽取来源内容**
   - 从原始需求、芯片手册、标准规范和项目约束中抽取软件相关事实。
   - 抽取内容应覆盖功能、接口、配置、初始化、模式/状态、诊断、安全、异常、时序、资源和合规。
   - 无法确定的内容标记为待确认，不改写为确定性需求。

3. **建立需求推导矩阵**
   - 将抽取内容转化为 SRS 需求、N/A 说明或开放项。
   - 保留来源 ID、抽取 ID、推导说明和风险/待确认项。

4. **编写 SRS 文档**
   - 使用 SRS 模板建立完整章节。
   - 每条需求必须包含 ID、标题、描述、来源、ASIL、前置条件、触发条件、输入、输出、异常/边界、验证方式、验证阶段、状态。
   - 需求编号格式：`SRS-[FC_SHORT_NAME]-[CATEGORY]-[NNNN]`。

5. **登记开放项**
   - API 原型、状态语义、配置载体、错误策略、安全等级等未确认内容进入开放项。
   - 每个开放项应包含责任方、影响章节/需求、关闭条件和状态。

6. **更新追溯入口**
   - 至少完成来源 → SRS 的初始追溯。
   - 若独立 TraceMatrix 尚未完善，可在 SRS 的“需求追溯”章节保留摘要。

7. **执行 SRS Gate 自检**
   - 逐项执行 Gate1~Gate6 检查。
   - 阻断项必须修正、关闭或获得人工批准遗留。

8. **生成 SRS 实际操作步骤与 CHECK 清单**
   - 将本次输入资料、推导过程、关键判断、输出文件和问题处理记录到 `Operation_Steps_SRS_[FC].md`。
   - 将 Gate1~Gate6 的检查结果、问题、责任人、关闭状态和发布结论汇总到 `CHECK_SRS_[FC].md`。
   - 两份文件与正式 SRS 文档同目录归档，支撑后续复现与评审。

### 6.5 人工审核点

SRS 完成后必须人工审核：

- 来源是否完整，是否存在无来源需求。
- 每条需求是否单一、明确、可验证。
- 芯片能力是否被错误扩展为软件公共能力。
- 模式/状态语义是否区分软件请求、软件记录、硬件确认和不可确认。
- 高影响开放项是否已关闭或批准遗留。
- SRS 是否足以作为 SDD 输入。

### 6.6 输出产物

| 产物 | 推荐文件 | 推荐位置 |
| --- | --- | --- |
| 软件需求规范 | `SRS_[FC].md` 或 `[FC] 软件需求规范.md` | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| 输入资料索引 | 可独立或内嵌 SRS | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| 来源内容抽取表 | 可独立或内嵌 SRS | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| 需求推导矩阵 | 可独立或内嵌 SRS | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| SRS 评审记录 | `Review_SRS_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| SRS 实际操作步骤 | `Operation_Steps_SRS_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| SRS CHECK 清单 | `CHECK_SRS_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SRS/` |
| 更新后的追溯矩阵 | `Trace_[FC].md/html` | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |

### 6.7 SRS Gate 通过条件

- [ ] 每条需求具有唯一且稳定的 ID。
- [ ] 每条需求具有明确来源、ASIL、验证方式和验证阶段。
- [ ] 所有有效输入已覆盖或说明不适用。
- [ ] 所有高影响开放项已关闭或获得批准遗留。
- [ ] SRS 足以作为 SDD 输入。
- [ ] SRS 实际操作步骤和 CHECK 清单已与 SRS 同目录归档。
- [ ] 人工评审记录已归档。
- [ ] SRS 状态可更新为 `Baselined`，或明确为 `Review` 且不得进入正式 SDD。

---

## 7 阶段2：架构设计（SDD）

### 7.1 目的

基于已基线化或经批准可进入设计的 SRS，完成 FC 软件架构设计，定义模块上下文、职责边界、接口、数据流、状态机、配置模型、依赖、时序、资源、诊断、安全、多实例/多核和集成策略。

### 7.2 触发条件

SRS Gate 通过；若 SRS 仍存在开放项，必须有人工批准的遗留结论和设计约束。

### 7.3 主要依据

| 类型 | 文件 |
| --- | --- |
| SDD 生成工作流 | `Standard/RuleAndTemplate/SDD/FC架构设计编写生成工作流.md` |
| SDD 编写规范 | `Standard/RuleAndTemplate/SDD/FC架构设计编写规范.md` |
| SDD 模板 | `Standard/RuleAndTemplate/SDD/Template-FC模块架构设计规范.md` |
| SDD Gate 检查清单 | `Standard/RuleAndTemplate/SDD/Checklist/` |
| SRS 输入 | 已评审或基线化的 SRS |

### 7.4 具体操作过程

1. **确认 SRS 可设计性**
   - 列出所有 SRS 条目和开放项。
   - 对 SRS 中接口、状态、配置、错误类别、时序和安全边界进行设计输入检查。
   - 若发现 SRS 缺失或矛盾，回写 SRS 变更请求，不在 SDD 中静默补齐。

2. **建立设计输入与追溯**
   - 登记 SRS、原始需求、芯片资料、平台规范和项目约束。
   - 规划 SRS → SDD 追溯关系。

3. **定义模块上下文与职责边界**
   - 绘制上下文图，明确上层调用者、下层依赖、配置输入、硬件约束和诊断/状态交互。
   - 明确模块负责什么、不负责什么。

4. **设计软件分层与文件结构**
   - 定义 Realize/Integrated/Atomic/Dependency 等层级是否适用。
   - 规划 `.c/.h/_Types/_Cfg/_CfgData/_Callout/_MemMap` 等文件职责。

5. **设计对外接口**
   - 固定 API 名称、参数、返回值、同步/异步、可重入性和调用约束。
   - 定义成功/失败后置条件。
   - 明确空指针、无效实例、未初始化、无效模式、未使能内核等错误行为。

6. **设计数据流与状态机**
   - 定义运行时状态、配置数据、输入输出数据对象。
   - 定义状态集合、初始状态、状态转移表和状态不可确认处理。

7. **设计配置模型**
   - 定义配置项、类型、默认值、有效范围、配置时机和一致性校验。
   - 明确配置错误时模块行为。

8. **设计依赖与 Callout**
   - 明确 MCAL/BSW/IoHwAb/硬件访问边界。
   - 对跨平台差异使用配置或 Callout 承载。

9. **设计时序与资源**
   - 定义同步/异步执行语义、等待策略、有界等待、调度周期或调用方时序责任。
   - 给出 ROM/RAM/Stack/CPU Load 的估算方法或测量计划。

10. **设计诊断、安全、多实例和多核**
    - 明确 DET/DEM/DTC 是否适用及边界。
    - 按 QM/ASIL 边界设计安全机制或明确不引入安全机制。
    - 设计实例 ID、Core ID、访问权限和重入/临界区策略。

11. **建立 SRS → SDD 追溯**
    - 每个 SDD 设计项应关联 SRS ID 或明确说明 N/A。
    - 更新追溯矩阵。
    - 生成 HTML 格式追溯矩阵 `需求-架构设计追溯矩阵_[FC].html` 到 `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/`。
    - 检查 HTML 追溯矩阵：每条有效 SRS 有对应行、Open/N/A 有说明、浏览器可正常打开、与 Markdown 版本一致。

12. **执行 SDD Gate 检查**
    - 使用 `Standard/RuleAndTemplate/SDD/Checklist/` 中 Gate1~Gate7 清单执行架构输入、SRS 覆盖、架构完整性、技术正确性、通用化边界、SDS 输入充分性和基线发布检查。
    - 对无法设计的 SRS 项回写需求问题，对阻断项完成修正、开放项管理或批准遗留。

13. **生成 SDD 实际操作步骤与 CHECK 清单**
    - 将输入索引、SRS 充分性确认、架构设计、追溯生成、门禁检查、问题修正和评审准备记录到 `Operation_Steps_SDD_[FC].md`。
    - 将 Gate1~Gate7 检查结果、问题和发布结论汇总到 `CHECK_SDD_[FC].md`。
    - 两份文件与正式 SDD 文档同目录归档。

### 7.5 人工审核点

SDD 完成后必须人工审核：

- 是否覆盖所有已批准 SRS。
- 是否擅自新增 SRS 未要求的功能。
- API、状态机、配置和错误处理是否足以进入 SDS。
- 架构是否保持 FC 通用化和可移植性。
- 资源、时序、诊断、安全、多实例、多核是否有明确设计策略。
- 遗留项是否有责任人、关闭条件和下游影响说明。

### 7.6 输出产物

| 产物 | 推荐文件 | 推荐位置 |
| --- | --- | --- |
| 软件架构设计 | `SDD_[FC].md` 或 `[FC] 软件架构设计.md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| 接口规范 | `InterfaceSpec_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| 时序规格 | `TimingSpec_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| 状态机设计 | `StateMachine_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| 架构评审记录 | `Review_SDD_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| SDD 实际操作步骤 | `Operation_Steps_SDD_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| SDD CHECK 清单 | `CHECK_SDD_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDD/` |
| 需求-架构设计追溯矩阵 | `需求-架构设计追溯矩阵_[FC].html` | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |
| 更新后的追溯矩阵 | `Trace_[FC].md/html` | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |

### 7.7 SDD Gate 通过条件

- [ ] SDD 覆盖所有已基线化或批准进入设计的 SRS。
- [ ] 模块边界、文件结构、接口、数据流和状态机明确。
- [ ] 外部依赖、Callout 和配置模型明确。
- [ ] 同步/异步、可重入、多核、多实例和临界区策略明确。
- [ ] 诊断、安全、资源和时序策略与 SRS 一致。
- [ ] SRS → SDD 追溯已更新。
- [ ] SDD 实际操作步骤和 CHECK 清单已与 SDD 同目录归档。
- [ ] 人工评审通过，SDD 可基线化。

---

## 8 阶段3：详细设计（SDS）

### 8.1 目的

基于已基线化的 SDD，完成函数级详细设计和数据设计，使开发者可以不补充未定义行为即可编码，使测试工程师可以据此设计 UT。

### 8.2 触发条件

SDD Gate 通过。

### 8.3 主要依据

| 类型 | 文件 |
| --- | --- |
| SDS 生成工作流 | `Standard/RuleAndTemplate/SDS/FC详细设计编写生成工作流.md` |
| SDS 编写规范 | `Standard/RuleAndTemplate/SDS/FC详细设计编写规范.md` |
| SDS 模板 | `Standard/RuleAndTemplate/SDS/Template-FC模块详细设计规范.md` |
| SDS Gate 检查清单 | `Standard/RuleAndTemplate/SDS/Checklist/` |
| CodingReady 检查 | `Standard/RuleAndTemplate/SDS/Checklist/Checklist-Gate6-Coding输入充分性与CodingReady.md` |

### 8.4 具体操作过程

1. **建立详细设计输入索引**
   - 登记 SDD、InterfaceSpec、StateMachine、SafetyDesign、标准规范和系统输入。
   - 标记适用章节、版本、用途、N/A 和待确认项。

2. **确认 SDD 输入充分性**
   - 逐项检查职责、文件结构、接口、状态机、配置、依赖、错误、安全、资源和并发输入是否足以细化。
   - 若缺失关键信息，回写 SDD 问题，不在 SDS 中静默补齐架构决策。

3. **设计文件结构与数据对象**
   - 规划 `.c/.h/_Types/_Cfg/_CfgData/_Callout/_MemMap` 等文件职责。
   - 建立 DataDict，定义类型、枚举、结构体、宏、配置对象、运行时变量、初值、作用域和 Memory Section。

4. **编写接口函数与内部函数详细设计**
   - 每个对外 API 明确函数职责、关联 SRS/SDD、参数、返回值、前后置条件、处理步骤、分支、边界、错误处理和验证入口。
   - 对状态转换、配置校验、依赖调用、错误处理等关键内部函数进行函数级设计。

5. **细化状态、配置、错误、安全和资源设计**
   - 输出状态转移详细表、配置校验规则、错误路径、DET/DEM、安全响应、故障注入入口、多实例/多核与临界区策略。
   - 明确时序、超时、阻塞和 CPU/RAM/ROM/Stack 影响入口。

6. **建立 SDD → SDS → Code/UT 追溯**
   - 每个关键 SDS 设计项关联 SRS/SDD ID。
   - 为 Coding 和 UT 预留代码对象与测试入口。
   - 生成架构设计到详细设计追溯矩阵到 `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/`。

7. **执行 SDS Gate 检查**
   - 使用 `Standard/RuleAndTemplate/SDS/Checklist/` 中 Gate 1~Gate 7 清单执行系统性检查。
   - Gate 6 负责 Coding 输入充分性与 CodingReady 检查。

8. **修正问题并整理 SDS 交付**
   - 修正门禁发现的问题，闭环开放项。
   - 最终 SDS 输出目录只保留模块详细设计规范文档；输入索引、DataDict、CHECK、操作步骤和过程追溯等辅助材料按需要保留在过程位置，不作为最终 SDS 输出目录必需物。

### 8.5 人工审核点

SDS 完成后必须人工审核：

- 输入资料、规范和系统约束是否完整且适用。
- 每个对外接口和关键内部函数是否有可编码设计。
- 所有分支、边界、异常和错误路径是否覆盖。
- 数据对象初值、范围、生命周期和 Memory Section 是否明确。
- 通用化边界、Callout 边界、多实例/多核和安全机制是否清晰。
- 是否存在未经 SDD 批准的新设计。
- SDS 是否足以支持编码和 UT。

### 8.6 输出产物

| 产物 | 推荐文件 | 推荐位置 |
| --- | --- | --- |
| 模块详细设计规范 | `[FC] 模块详细设计规范.md` 或 `SDS_[FC].md` | `Output/<FC_SHORT_NAME>/Doc/SDS/` |
| 架构设计-详细设计追溯矩阵 | 按 TraceMatrix 模板约定命名 | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |

数据字典、详细设计输入索引、SDS-Code/SDS-UT 追溯、实际操作步骤、CHECK 清单和评审记录可按项目需要生成或维护，但不是 `Output/<FC_SHORT_NAME>/Doc/SDS/` 最终输出目录的必需产物。

### 8.7 SDS Gate 通过条件

- [ ] 每条 SRS/SDD 设计约束均追溯到 SDS 或说明不适用。
- [ ] 每个对外接口和关键内部函数均有函数级设计。
- [ ] 分支、边界、错误路径和异常路径完整。
- [ ] 数据对象定义完整。
- [ ] Gate 1~Gate 7 检查完成，Gate 6 CodingReady 通过。
- [ ] 模块详细设计规范已输出到 `Output/<FC_SHORT_NAME>/Doc/SDS/`。
- [ ] 架构设计-详细设计追溯矩阵已输出到 `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/`。
- [ ] 人工评审通过，SDS 可基线化。

---

## 9 阶段4：编码实现（Coding）

### 9.1 目的

依据已基线化 SDS 生成或编写 C 源码、头文件、配置文件和 MemMap，并完成编译、静态分析和代码评审。

### 9.2 触发条件

SDS Gate 通过。

### 9.3 主要依据

| 类型 | 文件或技能 |
| --- | --- |
| Coding 生成工作流 | `Standard/RuleAndTemplate/CODING/FC代码编写生成工作流.md` |
| 详细设计输入 | `Output/<FC_SHORT_NAME>/Doc/SDS/` 下已允许进入 Coding 的模块详细设计规范 |
| 项目规范 | `Standard/Conversion/Code/` 下的编码、命名、MemoryLayout、MISRA/HIS 规范 |
| 系统输入 | `System/` 下的 V 模型流程、项目约束和系统级边界 |
| 编码技能 | `fc-coding`，Coding 阶段必须使用 |
| 构建技能 | `fc-build`，代码完成后必须用于编译验证 |

### 9.4 具体操作过程

1. **确认编码输入**
   - 使用 `fc-coding` Skill 进入 Coding。
   - 在 `Output/<FC_SHORT_NAME>/Doc/SDS/` 定位目标 FC 的模块详细设计规范，确认 SDS 已允许进入 Coding 且 CodingReady 通过。
   - 读取 `Standard/Conversion/Code/` 下适用编码规范和 `System/` 下适用系统输入。
   - 检查接口定义、数据对象、配置模型、Callout、错误路径和 Memory Map 输入是否足够实现。

2. **确认 FC 模板与代码现状**
   - 检查 `src/FcStackBase/AURIX2G/__FcDevp` 下是否存在目标 FC 模板目录。
   - 若模板缺失，先确认 FC 名称和作者，再按 `fc-coding` 规则调用 `fc-gen` 生成模板。
   - 读取已有 `.c/.h/_Types.h/_Cfg.h/_Cfg.c/_CfgData.h/_Callout.c/.h/_MemMap.h` 等文件，再做最小必要修改。

3. **实现类型、配置和接口**
   - 按 SDS 定义类型、枚举、结构体、宏和运行时数据。
   - 按 SDS 实现配置对象和接口函数。
   - 对外接口执行未初始化、空指针、无效 ID、无效模式、权限等防御性检查。

4. **实现内部逻辑**
   - 严格依据 SDS 实现状态机、配置校验、错误处理和依赖调用。
   - 不实现未需求化、未设计化功能。

5. **通过 `fc-build` 执行编译验证**
   - 按 `fc-build` 约定运行构建，不直接绕过构建 Skill。
   - 同时检查构建退出码和 `src/FcStackBase/AURIX2G/_log/gpmake.log` 关键日志行。
   - 修正本次 Coding 引入或暴露的 error 和 warning；不能跳过编译问题。

6. **执行静态分析或准备静态分析输入**
   - 按项目可用工具执行 MISRA/HIS/编码规范检查。
   - 若工具未接入，应登记待执行项和人工检查范围。

7. **更新追溯矩阵**
   - 将 SDS ID 映射到代码文件、函数、类型、变量或配置对象。

### 9.5 人工审核点

代码完成后必须人工审核：

- 代码是否只实现已批准 SDS。
- 接口、配置、状态机和错误处理是否与 SDS 一致。
- 命名、Memory Map、注释关键字和编码规范是否符合项目要求。
- 编译和静态分析结果是否闭环。
- 是否存在临时调试代码、未需求化功能或未批准偏差。

### 9.6 输出产物

| 产物 | 推荐位置 |
| --- | --- |
| 目标 FC 源码、头文件和配置文件 | `src/FcStackBase/AURIX2G/__FcDevp/[FC]/` 或项目约定代码目录 |
| 必要集成修改 | `src/` 中项目约定位置 |
| 构建验证结果 | `src/FcStackBase/AURIX2G/_log/gpmake.log` |
| 静态分析报告 | `Output/<FC_SHORT_NAME>/Code/` 或工具报告目录 |
| 代码评审记录 | `Output/<FC_SHORT_NAME>/Doc/` 或 `Output/<FC_SHORT_NAME>/Code/` |
| 更新后的追溯矩阵 | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |

### 9.7 Code Gate 通过条件

- [ ] 代码与 SDS、DataDict、InterfaceSpec 一致。
- [ ] 编译和链接通过，无未处理 warning。
- [ ] 静态分析问题已修正或有批准偏差。
- [ ] 代码度量满足阈值或有批准说明。
- [ ] 代码评审通过。
- [ ] 已使用 `fc-coding`，且构建验证已通过 `fc-build` 完成。
- [ ] SDS → Code 追溯已更新。

---

## 10 阶段5：单元测试（UT）

### 10.1 目的

验证软件单元在 SDS 规格范围内正确运行，覆盖正常路径、边界条件、异常路径、配置裁剪和故障注入。

### 10.2 触发条件

- UT 用例编写：当前 FC 的 SRS 和 SDS 已可作为测试设计输入。
- UT 执行：Code Gate 通过，且测试环境、桩函数和观测入口已准备。

### 10.3 主要依据

| 类型 | 文件 |
| --- | --- |
| UT 用例编写工作流 | `Standard/RuleAndTemplate/TEST/FC单元测试用例编写生成工作流.md` |
| UT 编写规范 | `Standard/RuleAndTemplate/TEST/FC单元测试编写规范.md` |
| UT 静态测试用例模板 | `Standard/RuleAndTemplate/TEST/FC静态测试用例模板.html` |
| UT 动态测试用例模板 | `Standard/RuleAndTemplate/TEST/FC动态测试用例模板.html` |
| UT 功能测试用例模板 | `Standard/RuleAndTemplate/TEST/FC功能测试用例模板.html` |
| UT 执行与回归工作流 | `Standard/RuleAndTemplate/TESTING/FC单元测试执行与回归工作流.md` |
| UT 静态测试报告模板 | `Standard/RuleAndTemplate/TESTING/FC静态测试报告模板.html` |
| UT 动态测试执行与覆盖率报告模板 | `Standard/RuleAndTemplate/TESTING/FC动态测试执行与覆盖率报告模板.html` |
| UT 功能测试执行报告模板 | `Standard/RuleAndTemplate/TESTING/FC功能测试执行报告模板.html` |
| UT 全链路追溯矩阵模板 | `Standard/RuleAndTemplate/TraceMatrix/FC全链路追溯矩阵模板.html` |
| UT 用例与追溯 checklist | `Standard/RuleAndTemplate/TEST/Checklist/Checklist-单元测试用例编写与追溯检查.md` |
| 需求输入 | `Output/<FC_SHORT_NAME>/Doc/SRS/` 中当前 FC 适用需求规范 |
| 详细设计输入 | `Output/<FC_SHORT_NAME>/Doc/SDS/` 中当前 FC 适用详细设计 |
| 系统输入 | `System/` 中适用流程、追溯、评审和问题回写约束 |

### 10.4 具体操作过程

1. **确认 UT 用例编写输入**
   - 读取 `Output/<FC_SHORT_NAME>/Doc/SRS/` 下当前 FC 适用需求规范、`Output/<FC_SHORT_NAME>/Doc/SDS/` 下当前 FC 适用详细设计。
   - 读取 `Standard/RuleAndTemplate/TEST/` 下单元测试编写规范和模板，以及 `System/` 下适用流程与追溯约束。
   - 识别需求、详细设计、开放项和批准遗留是否足以定义可判定测试预期。

2. **建立测试对象与追溯基线**
   - 提取适用 SRS ID、SDS ID、函数、状态、配置、边界、错误路径和依赖入口。
   - 明确 UT 范围、不测范围、环境限制和阶段边界。

3. **编写 UT 用例文档**
   - 按测试类别使用 `FC静态测试用例模板.html`、`FC动态测试用例模板.html` 或 `FC功能测试用例模板.html` 编写用例，按规范维护 `UT-[FC]-[CATEGORY]-[NNNN]` 用例 ID。
   - 每条用例明确测试目标、前置条件、输入步骤、桩行为、观测点和可判定预期。
   - 覆盖适用正常路径、边界值、异常路径、错误返回、状态转移、配置错误、依赖失败和故障注入入口。

4. **生成需求-单元测试用例追溯矩阵**
   - 基于 `FC需求-单元测试用例追溯矩阵模板.html` 建立 SRS 到 UT 用例的正反向追溯。
   - 未由 UT 覆盖的需求必须说明 N/A、开放项或其他验证阶段原因。

5. **生成详细设计-单元测试用例追溯矩阵**
   - 基于 `FC详细设计-单元测试用例追溯矩阵模板.html` 建立 SDS 到 UT 用例的正反向追溯。
   - 关键函数、状态、配置、分支、错误和异常路径均应有用例入口或说明。

6. **生成全链路追溯矩阵**
   - 基于 `FC全链路追溯矩阵模板.html` 汇总 SRS、SDD、SDS、Code 和 UT 主链。
   - 全链路矩阵应定位三份 UT 用例文档中的 UT ID，链路断裂时在最早缺失阶段标记 Gap。

7. **执行用例编写与追溯 check**
   - 使用 `Checklist-单元测试用例编写与追溯检查.md` 检查输入充分性、用例质量、三类追溯矩阵和问题闭环。
   - 阻塞项应修正、回写上游或形成明确阻塞结论。

8. **进入 UT 执行阶段**
   - 按 `FC单元测试执行与回归工作流.md` 准备 UT 环境和桩函数，依次执行静态、动态和单元功能测试。
   - 每类报告反馈导致修码时，按 Coding 约束完成代码修正、构建验证和受影响回归。
   - 执行完成后按静态、动态覆盖和功能执行报告模板分别定版结果、覆盖率、缺陷、回归和测试结论。

### 10.5 人工审核点

- UT 用例是否覆盖 SDS 的正常、边界、异常和错误路径。
- 预期结果是否可判定。
- 桩函数是否未掩盖真实接口问题。
- 需求-单元测试用例、详细设计-单元测试用例和全链路三类追溯矩阵是否生成并一致。
- 覆盖率缺口是否有合理说明。
- 失败项是否关闭或批准遗留。

### 10.6 输出产物

| 产物 | 推荐文件 | 推荐位置 |
| --- | --- | --- |
| FC 静态测试用例 | `UTS_STA_[FC].html` 或项目约定名称 | `Output/<FC_SHORT_NAME>/Doc/TEST/` 或项目约定测试输出目录 |
| FC 动态测试用例 | `UTS_DYN_[FC].html` 或项目约定名称 | `Output/<FC_SHORT_NAME>/Doc/TEST/` 或项目约定测试输出目录 |
| FC 功能测试用例 | `UTS_FUNC_[FC].html` 或项目约定名称 | `Output/<FC_SHORT_NAME>/Doc/TEST/` 或项目约定测试输出目录 |
| 需求-单元测试用例追溯矩阵 | 按 TraceMatrix 模板约定命名 | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |
| 详细设计-单元测试用例追溯矩阵 | 按 TraceMatrix 模板约定命名 | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |
| 全链路追溯矩阵 | 按 `FC全链路追溯矩阵模板.html` 生成 | `Output/<FC_SHORT_NAME>/Doc/TraceMatrix/` |
| 用例编写与追溯检查结论 | checklist 结果或等效评审记录 | 项目约定评审位置 |
| UT 静态测试报告 | 按 `FC静态测试报告模板.html` 生成 | UT 执行完成后的项目约定位置 |
| UT 动态测试执行与覆盖率报告 | 按 `FC动态测试执行与覆盖率报告模板.html` 生成 | UT 执行完成后的项目约定位置 |
| UT 功能测试执行报告 | 按 `FC功能测试执行报告模板.html` 生成 | UT 执行完成后的项目约定位置 |
| 缺陷与回归记录 | 项目约定名称 | 项目约定缺陷或测试归档位置 |
| 最终测试结论 | 三份报告定版及评审记录 | 项目约定测试归档位置 |

### 10.7 UT Gate 通过条件

- [ ] UT 用例评审通过。
- [ ] 需求-单元测试用例、详细设计-单元测试用例和全链路追溯矩阵已生成并检查。
- [ ] UT 执行通过，无未关闭失败项。
- [ ] 覆盖率达到项目和安全等级目标，或有批准说明。
- [ ] 缺陷修复已完成回归。
- [ ] UT 报告与追溯矩阵一致。

---

## 11 阶段6：集成测试（IT）

### 11.1 目的

验证 FC 与上下层模块、配置、调度、资源、时序和依赖接口的集成行为。

### 11.2 触发条件

UT Gate 通过。

### 11.3 具体操作过程

1. **制定 IT 范围**
   - 明确接口契约、配置一致性、调度、资源、时序、多核和依赖接口测试范围。

2. **编写 IT 规格**
   - 用例关联 SRS/SDD/接口规范。
   - 明确集成环境、配置版本、依赖模块版本和观测点。

3. **准备集成环境**
   - 集成已通过 UT 的代码和配置。
   - 确认 MCAL/BSW/Callout/硬件或仿真环境可用。

4. **执行集成测试**
   - 接口契约测试。
   - 配置一致性测试。
   - 调度和时序测试。
   - 资源测试。
   - 多实例、多核和重入测试。

5. **生成 IT 报告并更新追溯**
   - 记录执行结果、缺陷、回归和遗留风险。
   - 填充 SDD/接口 → IT 追溯。

### 11.4 人工审核点

- 集成环境是否与设计输入一致。
- IT 是否覆盖关键接口、配置、时序和资源风险。
- 集成问题是否回写 SDD/SDS/Code/Test。
- 测试报告和追溯是否一致。

### 11.5 IT Gate 通过条件

- [ ] 接口、配置、资源、时序验证通过。
- [ ] 集成缺陷关闭或批准遗留。
- [ ] IT 报告完成。
- [ ] SDD/接口 → IT 追溯完整。

---

## 12 阶段7：系统测试（ST）

### 12.1 目的

在目标 ECU、SIL、HIL 或整车级环境中验证软件需求和系统级预期，确认 FC 满足已批准 SRS 和系统约束。

### 12.2 触发条件

IT Gate 通过。

### 12.3 具体操作过程

1. **制定 ST 范围**
   - 明确系统测试环境、功能测试、故障注入、边界/压力、长稳、诊断和回归范围。

2. **编写 ST 规格**
   - 用例关联 SRS、系统需求和安全输入。
   - 明确系统级输入、观测点和判定准则。

3. **执行系统测试**
   - 功能验证。
   - 故障注入和恢复验证。
   - 边界/压力验证。
   - 诊断验证。
   - 回归验证。

4. **生成 ST 报告和验证报告**
   - 记录测试环境、工具版本、软件版本、配置版本、执行结果和风险接受。

5. **更新追溯矩阵**
   - 填充 SRS → ST 追溯。

### 12.4 人工审核点

- ST 是否覆盖已基线化 SRS 和系统级风险。
- 测试环境和配置是否可复现。
- 失败项是否关闭或批准风险接受。
- 验证报告是否与追溯矩阵一致。

### 12.5 ST Gate 通过条件

- [ ] 所有已基线化需求均有验证结果或批准偏差。
- [ ] 所有测试失败项已关闭或批准遗留。
- [ ] 资源、时序和安全机制验证结论明确。
- [ ] 测试环境、工具版本、软件版本和配置可复现。
- [ ] 验证报告与追溯矩阵一致。

---

## 13 阶段8：发布与交付

### 13.1 目的

整理完整交付物，完成发布评审，形成可复现、可追溯、可归档的发布包。

### 13.2 触发条件

ST Gate 通过。

### 13.3 具体操作过程

1. **整理交付物清单**
   - SRS、SDD、SDS、测试规格、测试报告、代码、配置、构建记录、静态分析报告、评审记录、追溯矩阵。

2. **完成最终追溯矩阵**
   - 来源 → SRS → SDD → SDS → Code → UT/IT/ST 全链路闭环。
   - N/A 项必须有理由。

3. **编写 Release Note**
   - 版本、变更摘要、验证结论、已知问题、遗留风险和适用范围。

4. **执行发布评审**
   - 检查交付完整性、版本一致性、追溯一致性和遗留风险批准状态。

5. **建立发布基线**
   - 归档发布包。
   - 按项目规则打标签或记录版本。

### 13.4 Release Gate 通过条件

- [ ] 发布包包含全部必需交付物。
- [ ] 全链路追溯完整。
- [ ] 所有遗留风险已批准。
- [ ] 发布版本、配置、构建和测试结果可复现。
- [ ] 发布评审通过。

---

## 14 变更与返工控制流程

变更或返工可能发生在任一阶段，包括输入资料新增、需求变更、设计修正、代码缺陷、测试失败或标准更新。返工不是例外流程，而是 V 模型闭环的一部分。

### 14.1 人工审核后的处理结论

每个阶段人工审核后只能给出以下结论之一：

| 结论 | 含义 | 后续动作 |
| --- | --- | --- |
| 通过 | 阶段产物满足门禁 | 更新状态为 `Baselined` 或批准进入下一阶段 |
| 有条件通过 | 存在非阻断问题或已批准遗留项 | 登记遗留风险、责任人、关闭期限后进入下一阶段 |
| 不通过 | 存在阻断问题 | 回到本阶段或上游阶段修正，不得进入下一阶段 |
| 退回上游 | 当前阶段发现上游输入错误、缺失或矛盾 | 发起变更请求，回到最早受影响阶段 |

### 14.2 变更处理步骤

1. **提出变更请求**
   - 记录变更原因、影响范围、风险、回滚方案和验证方案。

2. **影响分析**
   - 分析 SRS、SDD、SDS、Code、UT、IT、ST、TraceMatrix 是否受影响。

3. **人工审批**
   - 安全等级、接口不兼容、架构重大变更必须升级评审级别。

4. **实施变更**
   - 修改所有受影响交付物，而不是只改单一文件。

5. **回归验证**
   - 执行受影响路径回归。

6. **关闭变更**
   - 更新追溯矩阵、评审记录和基线状态。

### 14.3 变更回退原则

- 若下游发现上游输入缺失，应回到最早受影响阶段修正。
- 若代码发现设计不完整，应回到 SDS/SDD，而不是在代码中隐式补设计。
- 若测试发现需求不明确，应回到 SRS，而不是修改测试预期绕过问题。

---

## 15 追溯管理流程

### 15.1 纵向追溯链

```text
原始需求 / 芯片资料 / 系统需求 / 标准 / 安全输入
    ↓
SRS / IRS / SafetyReqAlloc
    ↓
SDD / InterfaceSpec / StateMachine / TimingSpec
    ↓
SDS / DataDict
    ↓
Code / Config / MemMap / Callout
    ↓
UT / IT / ST / Verification Report
```

### 15.2 维护时机

| 阶段 | 追溯更新内容 |
| --- | --- |
| 阶段0 | 建立来源 ID 和追溯框架 |
| 阶段1 | 来源 → SRS |
| 阶段2 | SRS → SDD |
| 阶段3 | SDD → SDS，SDS → UT 入口 |
| 阶段4 | SDS → Code |
| 阶段5 | Code/SDS → UT |
| 阶段6 | SDD/接口 → IT |
| 阶段7 | SRS/系统需求 → ST |
| 阶段8 | 完成全链路追溯 |

### 15.3 相关依据

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 追溯关系总览 | `Standard/RuleAndTemplate/TraceMatrix/FC追溯关系总览表.md` | 追溯链、状态和矩阵维护约定 |
| TraceMatrix 模板 | `Standard/RuleAndTemplate/TraceMatrix/` | 阶段追溯矩阵和全链路追溯矩阵模板 |

---

## 16 专项工作流建设计划

以下专项工作流是总工作流的细化入口，可逐步完善：

| 阶段 | 专项工作流 | 当前状态 | 说明 |
| --- | --- | --- | --- |
| 阶段0 | 输入转换与原始需求整理工作流 | 待完善 | 需覆盖 PDF/Word/HTML/图片转换、原始需求模板化和人工审核 |
| 阶段1 | `FC需求编写生成工作流.md` | 已存在 | SRS 编写主流程 |
| 阶段2 | `FC架构设计编写生成工作流.md` | 已存在 | SDD 编写主流程，含 Gate 1-7 检查清单 |
| 阶段3 | `FC详细设计编写生成工作流.md` | 已存在 | 覆盖 SDD 到 SDS、DataDict、Gate 1~7 和 CodingReady 检查 |
| 阶段4 | `FC代码编写生成工作流.md` | 已存在 | 以 `fc-coding` 为入口，覆盖 SDS 输入、模板生成、代码实现、构建验证和结果说明 |
| 阶段5 | `FC单元测试用例编写生成工作流.md`、`FC单元测试执行与回归工作流.md` | 已存在 | 覆盖 UT 用例编写、追溯矩阵、静态/动态/功能执行、测试反馈修码、回归和报告定版 |
| 阶段6 | IT 工作流 | 待完善 | 需覆盖接口、配置、资源、时序和集成报告 |
| 阶段7 | ST 工作流 | 待完善 | 需覆盖系统级验证和 Verification Report |
| 阶段8 | 发布交付工作流 | 待完善 | 需覆盖发布包、Release Note、最终追溯和发布评审 |
| 全阶段 | TraceMatrix 模板与总览 | 已存在 | 通过 TraceMatrix 模板和总览维护阶段矩阵、全链路矩阵及更新规则 |

---

## 17 质量门禁总览

| 阶段 | 门禁 | 核心通过条件 |
| --- | --- | --- |
| 阶段0 | Gate 0 | 输入完整、转换可信、原始需求整理完成、追溯框架已建 |
| 阶段1 | SRS Gate | 需求可验证、可追溯、人工评审通过、无未批准高影响开放项 |
| 阶段2 | SDD Gate | 架构覆盖 SRS、接口/状态/资源/安全明确、人工评审通过 |
| 阶段3 | SDS Gate | 函数级设计完整、CodingReady 通过、人工评审通过 |
| 阶段4 | Code Gate | 编译通过、静态分析闭环、代码评审通过 |
| 阶段5 | UT Gate | UT 通过、覆盖率达标或批准偏差、追溯一致 |
| 阶段6 | IT Gate | 接口/配置/资源/时序验证通过、集成问题关闭 |
| 阶段7 | ST Gate | 需求验证完成、系统级风险接受、验证报告一致 |
| 阶段8 | Release Gate | 发布包完整、全链路追溯完整、发布评审通过 |

---

## 18 附录：当前参考文件索引

| 类别 | 当前文件 | 用途 |
| --- | --- | --- |
| V 模型流程 | `System/VModel_Development_Process.md` | 通用开发流程和阶段出口准则 |
| 项目注意事项 | `System/FcStack项目注意事项.md` | 项目级执行原则和闭环要求 |
| SRS 工作流 | `Standard/RuleAndTemplate/SRS/FC需求编写生成工作流.md` | 需求生成流程 |
| SRS 规范 | `Standard/RuleAndTemplate/SRS/FC需求编写规范.md` | 需求写法和质量约束 |
| SRS 模板 | `Standard/RuleAndTemplate/SRS/Template-FC模块软件需求规范.md` | SRS 文档骨架 |
| 原始需求模板 | `Standard/RuleAndTemplate/SRS/Template-FC原始开发需求.md` | 原始需求整理 |
| SRS Gate 检查清单 | `Standard/RuleAndTemplate/SRS/Checklist/` | 需求阶段 Gate 1-6 检查 |
| SDD 规范 | `Standard/RuleAndTemplate/SDD/FC架构设计编写规范.md` | 架构设计写法 |
| SDD 工作流 | `Standard/RuleAndTemplate/SDD/FC架构设计编写生成工作流.md` | 架构设计生成流程 |
| SDD 模板 | `Standard/RuleAndTemplate/SDD/Template-FC模块架构设计规范.md` | SDD 文档骨架 |
| SDD Gate 检查清单 | `Standard/RuleAndTemplate/SDD/Checklist/` | 架构设计 Gate 1-7 检查 |
| SDS 工作流 | `Standard/RuleAndTemplate/SDS/FC详细设计编写生成工作流.md` | 详细设计生成流程 |
| SDS 规范 | `Standard/RuleAndTemplate/SDS/FC详细设计编写规范.md` | 详细设计写法 |
| SDS 模板 | `Standard/RuleAndTemplate/SDS/Template-FC模块详细设计规范.md` | SDS 文档骨架 |
| SDS Gate 检查清单 | `Standard/RuleAndTemplate/SDS/Checklist/` | 详细设计 Gate 1-7 检查 |
| CodingReady | `Standard/RuleAndTemplate/SDS/Checklist/Checklist-Gate6-Coding输入充分性与CodingReady.md` | SDS 进入编码前检查 |
| CODING 工作流 | `Standard/RuleAndTemplate/CODING/FC代码编写生成工作流.md` | 代码编写、模板生成和构建验证流程 |
| UT 用例编写工作流 | `Standard/RuleAndTemplate/TEST/FC单元测试用例编写生成工作流.md` | 单元测试用例编写、追溯矩阵生成与检查流程 |
| UT 执行与回归工作流 | `Standard/RuleAndTemplate/TESTING/FC单元测试执行与回归工作流.md` | 静态、动态、功能执行，测试反馈修码、回归与报告定版 |
| UT 规范 | `Standard/RuleAndTemplate/TEST/FC单元测试编写规范.md` | 单元测试规格与报告约束 |
| UT 静态测试用例模板 | `Standard/RuleAndTemplate/TEST/FC静态测试用例模板.html` | 静态测试用例文档模板 |
| UT 动态测试用例模板 | `Standard/RuleAndTemplate/TEST/FC动态测试用例模板.html` | 动态测试用例文档模板 |
| UT 功能测试用例模板 | `Standard/RuleAndTemplate/TEST/FC功能测试用例模板.html` | 功能测试用例文档模板 |
| UT 静态测试报告模板 | `Standard/RuleAndTemplate/TESTING/FC静态测试报告模板.html` | 静态测试执行报告模板 |
| UT 动态测试执行与覆盖率报告模板 | `Standard/RuleAndTemplate/TESTING/FC动态测试执行与覆盖率报告模板.html` | 动态执行与覆盖率报告模板 |
| UT 功能测试执行报告模板 | `Standard/RuleAndTemplate/TESTING/FC功能测试执行报告模板.html` | 功能测试执行报告模板 |
| UT 用例与追溯 checklist | `Standard/RuleAndTemplate/TEST/Checklist/Checklist-单元测试用例编写与追溯检查.md` | 用例、SRS-UT/SDS-UT/全链路追溯和问题闭环检查 |
| SRS-UT 追溯模板 | `Standard/RuleAndTemplate/TraceMatrix/FC需求-单元测试用例追溯矩阵模板.html` | 需求到单元测试用例追溯 |
| SDS-UT 追溯模板 | `Standard/RuleAndTemplate/TraceMatrix/FC详细设计-单元测试用例追溯矩阵模板.html` | 详细设计到单元测试用例追溯 |
| 全链路追溯模板 | `Standard/RuleAndTemplate/TraceMatrix/FC全链路追溯矩阵模板.html` | SRS、SDD、SDS、Code 与 UT 主链追溯 |
| TraceMatrix | `Standard/RuleAndTemplate/TraceMatrix/FC追溯关系总览表.md` | 追溯关系维护参考 |

---

本文档为 FcStack 平台 FC 开发总工作流，后续新增或完善各阶段专项工作流时，应同步更新本文档第 16 章和相关阶段引用。
