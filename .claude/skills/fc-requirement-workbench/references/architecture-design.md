# FC Requirement Workbench Architecture Design

本文档是 `fc-requirement-workbench` 的**唯一详细架构与方案参考**。

- `SKILL.md` 提供高层概览、输入/输出边界和最小加载策略。本文档提供完整的阶段方案、引入原因和维护要求。
- 当工程中新增、替换或升级任何阶段方案时，必须同步更新本文档。
- Pipeline 顶层步骤与 SKILL.md 的 8 步流程对齐：解析→提取→映射→剪枝→规划→验证→构建→溯源。本文档的各阶段为这 8 步的子阶段实现。

## 1. 定位

`fc-requirement-workbench` 是需求生成 skill，不是架构设计器、代码生成器或测试生成器。

目标是把芯片手册、项目需求、源码、配置、测试材料和历史 SRS 转换为：

- 可追溯的中间特征。
- 结构化需求语义对象。
- 可校验的工程需求。
- Markdown SRS。
- 需求级追溯、覆盖和验证证据。

## 2. 总体架构

```text
Input Materials
  ├─ Datasheet / Manual
  ├─ Project Requirement
  ├─ Source Code
  ├─ Configuration
  ├─ Test Material
  └─ Historical SRS
        ↓
Phase 1: Document Parsing and Semantic Infrastructure
        ↓
Phase 1A: Multi-view Feature Extraction
        ↓
Phase 1C: Feature-to-Requirement Candidate Mapping
        ↓
Phase 1C2: Candidate Pruning and Required Input Compression
        ↓
Phase 1C3: Requirement Planning and Authoring Strategy
        ↓
Phase 1D: Candidate Promotion to Draft RequirementObject
        ↓
Phase 3 Bridge: Promoted RequirementObject to SRS Draft
        ↓
Phase 1B: Requirement Semantic Object Extraction
        ↓
Phase 2: Rule Validation and Quality Infrastructure
        ↓
Phase 3: Requirement Builder and SRS Rendering
        ↓
Phase 4: Requirement Traceability and Evidence
        ↓
Outputs
  ├─ <FC>_软件需求规范.md                  (SRS)
  ├─ Review_<FC>_软件需求规范.md             (Review)
  ├─ Check_<FC>_软件需求规范.md              (Check)
  ├─ Trace_<FC>_软件需求规范.md              (Trace: Source→Req, Req→Verification, ASPICE Evidence)
  └─ ChipViews/ (条件输出，有芯片手册时)
       ├─ <FC>_芯片架构输入.md
       └─ <FC>_芯片详细设计输入.md
```

## 3. 架构原则

| 原则 | 说明 |
| --- | --- |
| 先特征，后需求 | 先理解芯片能力、项目约束和软件动作，再生成需求条目。 |
| 先证据，后结论 | 所有候选需求必须有来源证据，且保留证据强度。 |
| Datasheet 不等于项目需求 | Datasheet-only 内容默认 `Needs Review`，不得自动成为 `Ready`。 |
| 软件动作门禁 | 没有软件动作的芯片能力只能进入概述、约束或资料来源。 |
| Markdown 优先 | 当前阶段默认产物为 Markdown，不优先处理 Word/DOCX。 |
| 无中间产物 | 需求生成阶段只输出 4 个标准产物（SRS/Review/Check/Trace），不输出中间 Markdown 和过程性产物。 |

## 4. 阶段方案总览

| 阶段 | 核心问题 | 引入方案 | 主要文件 |
| --- | --- | --- | --- |
| 输入解析 | Markdown 输入结构不稳定，表格/标题/段落混合 | Markdown 结构解析、Chunk、语义索引 | `parser.py` |
| 特征提取 | 单视角提取会漏读、误读或过度摘抄 Datasheet | 多视角并行提取、特征聚合、子功能分析 | `feature_extraction.py`, `feature-extraction-design.md` |
| 正确率控制 | Datasheet-only 信息容易误判为 Ready | Evidence Level、Software Action Gate、Ready 条件 | `extraction-rules.md` |
| 候选需求映射 | 一段输入可能对应多个需求类别，直接生成会遗漏或乱配 | RequirementCandidate、映射矩阵、多类别门禁 | `candidate_mapping.py` |
| 候选需求压缩 | 多视角映射会产生父子重复、同族重复和过多候选 | Candidate Pruning、同族聚类、保留/合并决策、补料清单压缩 | `candidate_pruner.py` |
| 需求规划 | 候选压缩后仍可能又空又多，且缺少需求制定者视角 | Requirement Planning、能力域编排、需求条目规划、验证策略规划 | `requirement_planner.py` |
| 候选需求收敛 | 候选需求需要进入 SRS 链路，但不能过早 Ready 或硬塞类型 | Candidate Pruner、Requirement Planner、Draft RequirementObject | `candidate_pruner.py`, `requirement_planner.py` |
| Promoted SRS 桥接 | 新版特征/候选链路需要进入 SRS 输出，而不是继续依赖旧直接提取 | promoted-srs-markdown、复用 RuleEngine/Builder/SRS Renderer | `cli.py`, `builder.py`, `srs.py` |
| 需求语义对象 | 直接写 SRS 句子难以校验和追溯 | Requirement Semantic Object | `schema.py`, `extractor.py`, `semantic-model.md` |
| 质量校验 | 需求缺字段、冲突、缺来源、缺验证方式 | Rule Engine、Validation Report、Requirement Graph | `rules.py`, `report.py`, `graph.py`, `rule-engine.md` |
| 需求构建 | 语义对象需要稳定变成工程需求 | Requirement Builder、ID Engine、Construction Rules | `builder.py`, `construction-rules.md` |
| SRS 输出 | 输出结构需要稳定、可读、可审查 | SRS Output Template、Markdown Renderer | `srs.py`, `srs-output-template.md` |
| 写法校准 | 新 SRS 容易偏离当前约定格式和评审习惯 | Calibration Rules、Authoring Standard | `calibration-rules.md`, `authoring-standard.md` |
| 追溯验证 | 需求来源和验证覆盖需要可检查 | Traceability Pipeline、Coverage、Evidence | `traceability.py`, `rendering-templates.md` |

## 5. Phase 1 - 文档解析和语义基础设施

### 5.1 要解决的问题

输入文件主要是 Markdown，但来源可能是 Datasheet 转写、项目文档、测试材料或历史 SRS。文档中标题、表格、段落、Note、图片和 HTML 片段混杂，如果直接提取需求，会出现：

- 章节边界不清。
- 表格内容丢失。
- 页眉页脚、订购信息、封装信息误入需求。
- 后续提取无法定位来源。

### 5.2 引入的方案

引入 Markdown 结构解析方案：

- 解析 heading、paragraph、table、code block、note、warning、image、html block。
- 构建 `DocumentChunk`。
- 建立语义索引，例如 mode、timing、diagnostic、interface、configuration、state。

### 5.3 产物

- `ParsedDocument`
- `MarkdownBlock`
- `DocumentChunk`
- `semantic_index`

### 5.4 维护要求

如果新增输入格式或文档块类型，需要同步更新：

- `parser.py`
- `SKILL.md` 的输入解析说明
- 本文档的 Phase 1 说明

## 6. Phase 1A - 需求输入特征提取

### 6.1 要解决的问题

芯片手册中包含大量事实，但这些事实不天然等于软件需求。早期直接从 Datasheet 生成 SRS 会出现：

- 信息提取太少，支撑不了完整需求生成。
- 信息过散，例如每个 pin、每个寄存器行都变成独立候选。
- Datasheet 支持被误判为项目支持。
- 缺少软件动作判断，导致需求空泛。
- 缺少补料清单，用户不知道需要提供什么。

### 6.2 引入的方案：多视角并行提取

为提高芯片信息读取完整性，引入多视角并行提取方案。

提取视角包括：

- identity
- capability
- pin
- interface
- register
- bitfield
- state
- diagnostic
- timing
- electrical
- constraint
- project_mapping

这些视角可以并行读取同一份输入文件，各自产生证据，再由聚合器合并。

### 6.3 引入的方案：特征聚合

为解决“散点提取无法支撑后续组合设计”的问题，引入特征聚合。

示例：

| 散点证据 | 聚合特征 |
| --- | --- |
| P00-P17 + Input/Output/Polarity/Configuration Register | 16-bit GPIO Port Capability |
| SCL/SDA + Device Address + Read/Write Sequence | I2C Control Interface |
| INT pin + input change behavior | Interrupt and Diagnostic Signaling |
| RESET pin + POR default | Reset and Default State |

### 6.4 引入的方案：子功能分析

为支撑后续每个功能需求、接口需求、配置需求的生成，每个大特征必须继续拆成子功能。

子功能至少包含：

- Summary
- Inputs
- Outputs
- Boundary
- Related Pins
- Related Registers
- Application Scheme
- Candidate Requirement Types
- Missing Inputs
- Can Generate Requirement

### 6.5 引入的方案：应用方案输出

为避免中间特征只是“摘录事实”，每个重要特征和子功能必须输出 `Application Scheme`。

作用：

- 说明该特征在驱动需求中可能如何落地。
- 明确它是否可能对应 API、配置、状态、诊断或时序。
- 明确仍需项目确认的地方。
- 不直接承诺项目一定支持。

### 6.6 引入的方案：准确率控制规则

为提高提取信息准确率，引入三层判断：

```text
特征是否有证据
  ↓
是否有软件动作
  ↓
是否满足 Ready 条件
```

具体规则：

| 规则 | 解决的问题 | 输出字段/产物 |
| --- | --- | --- |
| Evidence Level | 防止 Datasheet-only 自动变 Ready | `Evidence Level` |
| Software Action Gate | 防止无软件动作的芯片能力进入需求 | `Software Actions`, `Software Action Gate` |
| Feature-to-Requirement Mapping | 防止特征池完整但需求生成遗漏 | `Feature-to-Requirement Mapping` |
| Required Inputs for Ready SRS | 面向补料，不只输出 Open Issue | `Required Inputs for Ready SRS` |

Evidence Level：

- L1: 项目需求明确要求。
- L2: 配置/源码已实现或已约束。
- L3: Datasheet 明确描述。
- L4: 测试材料间接覆盖。
- L5: 推断结果，需要人工确认。

Software Action Gate 允许的软件动作：

- 软件需要调用 API。
- 软件需要读寄存器。
- 软件需要写寄存器。
- 软件需要控制 Pin。
- 软件需要读取 Pin。
- 软件需要保存状态。
- 软件需要做参数校验。
- 软件需要拒绝非法输入。
- 软件需要等待时序。
- 软件需要上报/记录错误。

### 6.7 当前 NCA9539 特征组

当前 NCA9539 Datasheet 可形成：

- 16-bit GPIO Port Capability
- Input Port Function
- Output Port Function
- Polarity Inversion Function
- Direction Configuration Function
- I2C Control Interface
- Register Map
- Interrupt and Diagnostic Signaling
- Reset and Default State
- Timing Constraints
- Prohibited and Boundary Behavior

### 6.8 产物

- Feature Extraction Intermediate Markdown。
- Feature Groups。
- Subfunctions。
- Feature-to-Requirement Mapping。
- Required Inputs for Ready SRS。
- Raw Multi-view Records。

### 6.9 维护要求

当提取阶段新增方案或规则时，必须同步更新：

- `feature-extraction-design.md`
- `extraction-rules.md`
- `feature_extraction.py`
- 本文档 Phase 1A
- 必要时更新测试用例

## 7. Phase 1C - Feature-to-Requirement Candidate Mapping

### 7.1 要解决的问题

一段输入或一个特征组可能同时对应多个需求类别。例如 Direction Configuration 既可能对应配置需求，也可能对应接口需求、状态需求、诊断需求。若直接从 Feature Group 生成正式 RequirementObject，会出现：

- 多类别映射遗漏。
- 同一证据被错误归到单一类别。
- Datasheet-only 特征被过早写成正式需求。
- 缺少映射理由，人工无法判断为什么生成该候选。
- 后续设计组合无法灵活裁剪，例如只支持 port 级 API、不支持 pin 级 API。

### 7.2 引入的方案

引入 `RequirementCandidate` 中间层。

处理链路：

```text
FeatureRecord
  ↓
Subfunction
  ↓
RequirementCandidate
  ↓
Candidate Mapping Matrix
  ↓
RequirementObject
  ↓
SRS Draft
```

该阶段不直接确认需求 Ready，而是生成可审查的候选映射。

### 7.3 多类别处理规则

同一个 Feature/Subfunction 可以生成多个 RequirementCandidate，但每条候选必须独立说明：

- Candidate Type。
- Mapping Reason。
- Evidence Level。
- Software Actions。
- Required Inputs。
- Ready Conditions。
- Status。
- Target Requirement Fields。

候选映射必须满足：

```text
有证据
  ↓
有软件动作
  ↓
有映射理由
  ↓
有 Ready 条件
```

否则只能保持 `Blocked` 或 `Needs Review`。

### 7.4 防遗漏方案

为避免遗漏，采用：

- 从 Feature Group 和 Subfunction 双层映射。
- 每个 Subfunction 的 `candidate_requirement_types` 必须全部展开。
- 输出 Candidate Mapping Matrix，用于反查哪些 Feature/Subfunction 没有候选。
- 保留 Source Feature ID，支持回溯到特征中间文件和原始证据。

### 7.5 防乱配方案

为避免乱配，采用：

- 每条候选必须有 `Mapping Reason`。
- 每条候选必须通过 `Software Action Gate`。
- Datasheet-only 证据默认 `Needs Review`。
- 缺少项目输入时不得提升为正式 Ready 需求。
- Target Requirement Fields 只作为候选字段，不直接承诺最终 SRS。

### 7.6 产物字段

`RequirementCandidate` 字段包括：

| 字段 | 说明 |
| --- | --- |
| candidate_id | 候选需求 ID |
| source_feature_id | 来源 Feature ID |
| source_feature | 来源特征 |
| source_subfunction | 来源子功能 |
| candidate_type | 候选需求类别 |
| mapping_reason | 映射理由 |
| evidence_level | 证据强度 |
| software_responsibility | 软件责任 |
| software_actions | 软件动作 |
| required_inputs | 提升 Ready 所需输入 |
| ready_conditions | Ready 条件 |
| status | 当前状态 |
| can_promote_to_requirement | 是否可提升为正式需求 |
| target_requirement_fields | 候选目标字段 |

### 7.8 维护要求

当候选映射规则变化时，必须同步更新：

- `candidate_mapping.py`
- 本文档 Phase 1C
- `feature-extraction-design.md` 中的特征/子功能映射规则
- `extraction-rules.md` 中的映射门禁规则
- 必要测试用例

## 8. Phase 1C2 - Candidate Pruning and Required Input Compression

### 8.1 要解决的问题

多视角提取和多类别候选映射能降低遗漏，但会带来另一个问题：候选偏多。

典型重复包括：

- 父功能和子功能重复，例如 `GPIO Input Read` 与 `Read Input Port`、`Read Input Pin`。
- 聚合接口和具体接口重复，例如 `GPIO Input Read Interface` 与 `Read Input Port Interface`。
- 同一个配置策略被多个特征组重复引用。
- Required Inputs 分散在大量候选中，用户难以知道优先补什么。

如果不压缩，SRS 草稿会变厚、重复、不利于评审。

### 8.2 引入的方案

引入 `RequirementCandidatePruner`，在候选映射之后、候选提升之前执行。

处理链路：

```text
RequirementCandidate Mapping
  ↓
Behavior Family Clustering
  ↓
Keep / Merge Decision
  ↓
Compressed Required Inputs
  ↓
Candidate Promotion
```

该阶段在内存中完成裁解决策。所有被合并的候选仍保留 candidate_id、cluster 和 retained_by，避免证据丢失。

### 8.3 裁剪策略

| 场景 | 策略 | 原因 |
| --- | --- | --- |
| 功能需求父子重复 | 优先保留父行为候选 | 功能需求描述软件能力边界，避免同一能力被 port/pin 重复描述。 |
| 接口需求父子重复 | 优先保留具体接口候选 | 接口需求需要可落地 API 粒度，聚合接口只作为合并依据。 |
| 配置需求重复 | 保留项目策略入口候选 | 配置需求应聚焦默认值、范围、非法值处理和运行时策略。 |
| Unsupported 类型 | 不硬塞进功能需求 | 由 unsupported 清单或默认非功能模板承接。 |
| 缺失输入重复 | 按缺失项聚合 | 生成面向补料的 Required Inputs 表，而不是分散在每条候选里。 |

### 8.4 维护要求

当裁剪、合并或补料聚合规则变化时，必须同步更新：

- `candidate_pruner.py`
- 本文档 Phase 1C2
- `SKILL.md` 的候选压缩说明
- 必要测试用例

## 9. Phase 1C3 - Requirement Planning and Authoring Strategy

### 9.1 要解决的问题

候选压缩能减少重复，但仍然没有真正回答“需求制定者应该如何组织这份 SRS”。如果直接从保留候选生成正文，会出现：

- 需求条目仍然偏多。
- 同一能力域下功能、接口、配置、状态之间缺少主次关系。
- 需求描述只说“支持”，缺少条件、行为、边界、异常和验证方法。
- 读者看完 SRS 后仍然无法形成清晰芯片画像和驱动职责边界。

### 9.2 引入的方案

引入 `RequirementPlanner`，在候选压缩之后、SRS 正文生成之前执行。

处理链路：

```text
Pruned Candidates
  ↓
Capability Domain Planning
  ↓
Requirement Item Planning
  ↓
Authoring Strategy
  ↓
Verification Strategy
  ↓
Planned RequirementObject
```

该阶段的核心不是继续保留更多候选，而是站在需求制定者角度确定：

- 哪些能力域进入 SRS。
- 每个能力域生成几条需求。
- 哪些 pin/port 粒度需要合并。
- 每条需求应如何验证。
- 哪些信息必须由项目补充后才能 Ready。

### 9.3 NCA9539 能力域规划

当前 NCA9539 默认规划能力域：

- GPIO 输入采样。
- GPIO 输出控制。
- GPIO 方向与极性配置。
- I2C 寄存器访问。
- 中断、复位与异常处理。
- 时序与资源约束。

### 9.4 维护要求

当需求规划或写作策略变化时，必须同步更新：

- `requirement_planner.py`
- 本文档 Phase 1C3
- `SKILL.md` 的需求规划说明
- 必要测试用例

## 10. Phase 1D - Candidate Promotion to Draft RequirementObject

### 10.1 要解决的问题

RequirementCandidate 已经说明了 Feature/Subfunction 可以映射到哪些需求类别，但它仍然不是正式语义需求对象。若直接生成 SRS，会出现：

- 候选状态、缺失输入和证据强度无法进入需求字段。
- 诊断、安全、资源等当前 schema 不支持类型被硬塞到功能需求。
- Datasheet-only 候选被过早当作 Ready 需求。
- SRS 生成仍无法消费候选映射层。

### 10.2 引入的方案

引入 Candidate Promotion Rules 和 `RequirementCandidatePromoter`。

处理链路：

```text
RequirementCandidate
  ↓
Promotion Gate
  ↓
Draft RequirementObject
  ↓
Unsupported Candidate Type Report
  ↓
Validation / SRS Draft
```

该阶段只生成 Draft/Open Issue 语义需求对象，不生成 Ready 需求。

### 10.3 提升门禁

候选必须满足：

- Candidate status 不是 `Blocked`。
- Evidence Level 存在。
- Software Actions 非空。
- Mapping Reason 非空。
- Candidate Type 能映射到当前 schema 支持类型。

支持提升：

- 功能需求 → FunctionalRequirementObject
- 接口需求 → InterfaceRequirementObject
- 配置需求 → ConfigurationRequirementObject
- 状态需求 → StateRequirementObject
- 时序需求 → TimingRequirementObject

暂不支持独立提升：

- 诊断需求
- 安全等级需求
- 资源需求
- 编码规范需求

这些类型进入 Unsupported Candidate Type 清单，等待 schema 扩展。

### 10.4 维护要求

当提升规则变化时，必须同步更新：

- 候选进入 SRS 的限制已并入 Candidate Pruner / Requirement Planner 规则，不再单列独立文档
- 候选进入 SRS 的约束已由 `candidate_pruner.py` 和 `requirement_planner.py` 承接
- 本文档 Phase 1D
- `schema.py` / `builder.py` / `srs.py`，如果新增需求类型
- 相关测试用例

## 11. Phase 1B - 需求语义对象提取

## 12. Phase 3 Bridge - Promoted RequirementObject to SRS Draft

### 12.1 要解决的问题

Promoted RequirementObject 已经形成 Draft 语义需求对象，但如果 SRS 生成仍使用旧的直接提取结果，则前面的多视角提取、候选映射和提升规则无法真正影响最终 SRS 草稿。

需要解决：

- 新版链路如何进入 SRS 输出。
- promoted requirements 的 Draft/Needs Review 状态如何保留。
- required inputs 和 L3 Datasheet 证据如何进入需求字段。
- unsupported candidates 如何暂不进入正文。

### 12.2 引入的方案

引入 promoted SRS bridge。

执行链路：

```text
FeatureExtractor
  ↓
RequirementCandidateMapper
  ↓
RequirementCandidatePruner
  ↓
RequirementPlanner
  ↓
RequirementCandidatePromoter
  ↓
RequirementRuleEngine
  ↓
RequirementBuilder
  ↓
SrsStructureGenerator
  ↓
MarkdownSrsRenderer
```

### 12.3 规则

- promoted requirements 全部作为 Draft SRS 输入。
- Datasheet-only 需求不得自动 Ready。
- Required Inputs 保留在约束、依赖或来源证据中。
- Unsupported candidates 暂不进入正文需求。
- SRS 草稿默认消费 pruning 后的 retained candidates，避免已知同族重复直接进入正文。
- 高质量 SRS 草稿应优先消费 planning 生成的 planned requirements，避免候选痕迹进入正文。

### 12.4 维护要求

当 promoted SRS 路径变化时，必须同步更新：

- `cli.py`
- 候选进入 SRS 的约束已由 `candidate_pruner.py` 和 `requirement_planner.py` 承接
- `builder.py`
- `srs.py`
- 本文档 Phase 3 Bridge
- 相关测试用例

## 10. Phase 1B - 需求语义对象提取

### 10.1 要解决的问题

直接从文本生成 SRS 句子难以校验，且不利于后续追溯、ID 生成和章节分配。

### 10.2 引入的方案

引入 Requirement Semantic Object：

- functional
- interface
- configuration
- timing
- state

每类需求先形成结构化对象，再进入规则校验和 SRS 构建。

### 10.3 产物

- `RequirementObject`
- `FunctionalRequirementObject`
- `InterfaceRequirementObject`
- `ConfigurationRequirementObject`
- `TimingRequirementObject`
- `StateRequirementObject`

### 10.4 维护要求

如果新增需求类型，例如 diagnostic、resource、safety，需要同步更新：

- `schema.py`
- `extractor.py`
- `builder.py`
- `srs.py`
- `construction-rules.md`
- `semantic-model.md`
- 本文档 Phase 1B/Phase 3

## 11. Phase 2 - 需求质量基础设施

### 11.1 要解决的问题

候选需求可能存在：

- 字段缺失。
- 来源缺失。
- 项目约束冲突。
- Ownership 不明确。
- Dependency 不完整。
- 验证方式缺失。

### 11.2 引入的方案

引入 Rule Engine：

- Completeness check。
- Consistency check。
- Constraint check。
- Ownership check。
- Dependency check。
- Trace check。

引入 Requirement Graph：

- 需求之间的依赖关系。
- 来源关系。
- 验证关系。

引入 Validation Report：

- 汇总质量问题。
- 输出可审查的缺陷清单。

### 11.3 产物

- Validation Findings（内部校验对象，归入 Trace 追溯矩阵）。

### 11.4 维护要求

新增规则时，需要同步更新：

- `rules.py`
- `rule-engine.md`
- 相关测试
- 本文档 Phase 2

## 12. Phase 3 - 需求构建和 SRS 输出

### 12.1 要解决的问题

结构化需求对象需要转换为统一、可读、可追溯的 SRS 文档。直接自由生成会导致：

- ID 不稳定。
- 章节不一致。
- 字段缺失。
- 语言风格漂移。
- 历史 SRS 风格不一致。

### 12.2 引入的方案

引入 Requirement Builder：

- 生成稳定 SRS ID。
- 将语义对象转换为工程需求。
- 注入验证发现。

引入 SRS Output Template：

- 固定章节结构。
- 固定需求条目渲染骨架。
- 当前默认输出 Markdown。

引入 Construction Rules：

- 规定不同需求类型的必备字段。
- 判断 Ready/Draft/Open Issue。

引入 Authoring Standard：

- 规范语言、单位、粒度、模糊词处理。

引入 Calibration Rules：

- 从历史 TJA1043 SRS 中校准写法偏好、颗粒度和判断习惯。

### 12.3 产物

- Engineering Requirement。
- `<FC>_软件需求规范.md`（正式 SRS Markdown）。

### 12.4 维护要求

SRS 输出结构或字段变化时，需要同步更新：

- `srs-output-template.md`
- `authoring-standard.md`
- `construction-rules.md`
- `srs.py`
- 测试用例
- 本文档 Phase 3

## 13. Phase 4 - 需求追溯和验证证据

### 13.1 要解决的问题

SRS 不是最终闭环，需求还需要说明：

- 来源是什么。
- 如何验证。
- 哪些测试覆盖。
- 变更影响哪些测试。
- ASPICE 证据如何汇总。

### 13.2 引入的方案

引入 Traceability Pipeline：

- Source → Requirement trace。
- Requirement → Verification Intent。
- Requirement → Test coverage。
- Change impact analysis。
- ASPICE evidence summary。

### 13.3 产物

- `Trace_<FC>_软件需求规范.md`（包含 Source→Requirement、Requirement→Verification Intent、Coverage、ASPICE Evidence Summary）。

### 13.4 维护要求

追溯字段或验证策略变化时，需要同步更新：

- `traceability.py`
- `rendering-templates.md`
- `rule-engine.md`
- 测试用例
- 本文档 Phase 4

## 14. 方案维护规则

本文档是方案型文档，必须随工程演进持续更新。

当发生以下变化时，必须更新本文档：

- 新增一个阶段。
- 删除或合并一个阶段。
- 引入新的提取、校验、构建、渲染或追溯方案。
- 修改 Evidence Level、Software Action Gate、Ready 条件等核心判断规则。
- 修改 SRS 输出结构或默认产物类型。
- 新增需求类型或特征类型。
- 新增重要参考文件。

更新时至少记录：

| 字段 | 说明 |
| --- | --- |
| 变更阶段 | 例如 Phase 1A、Phase 3 |
| 原问题 | 为什么需要改 |
| 新方案 | 引入了什么 |
| 影响文件 | 哪些代码/规则/模板受影响 |
| 输出变化 | SRS 有什么变化 |
| 验证方式 | 如何确认方案生效 |

## 15. 当前方案状态

| 方案 | 状态 | 说明 |
| --- | --- | --- |
| Markdown 结构解析 | 已实现 | 支撑 md 输入。 |
| 多视角并行特征提取 | 已实现 | 支撑特征抽取。 |
| 特征聚合和子功能分析 | 已实现 | 支撑 NCA9539 特征组。 |
| Evidence Level | 已实现 | 支撑 L3 Datasheet 证据等级判定。 |
| Software Action Gate | 已实现 | 支撑软件动作和映射判定。 |
| Feature-to-Requirement Mapping | 已实现 | 支撑映射矩阵。 |
| Required Inputs for Ready SRS | 已实现 | 支撑反向补料清单。 |
| RequirementCandidate 映射中间层 | 已实现 | 支撑 Feature/Subfunction 到多类别候选需求映射。 |
| Candidate Pruning 压缩中间层 | 已实现 | 支撑同族候选保留/合并决策和补料项聚合。 |
| Requirement Planning 需求规划层 | 已实现 | 支撑按能力域规划需求条目、合并策略和验证策略。 |
| Candidate Promotion 提升中间层 | 已实现 | 支撑候选需求到 Draft RequirementObject。 |
| Planned SRS Bridge | 已实现 | 支撑新版候选/规划链路生成 SRS Markdown。 |
| Requirement Semantic Object | 已实现 | 支撑功能/接口/配置/时序/状态。 |
| Rule Engine | 已实现 | 支撑基础质量校验。 |
| SRS Markdown 输出 | 已实现 | 输出 4 个标准产物（SRS/Review/Check/Trace）。 |
| Traceability Pipeline | 已实现 | 支撑 trace/coverage/verification/evidence（归入 Trace 产物）。 |
| 芯片视图提取 | 已实现 | 有芯片手册时条件输出 3 个 ChipView 文件。 |

## 16. 下一步候选升级

| 候选升级 | 目标 |
| --- | --- |
| 增加 diagnostic/resource/safety 语义对象 | 覆盖诊断、资源、安全等级需求。 |
| 增加项目补料输入模板 | 让 Required Inputs 可直接变成用户补料表。 |
| 增加裁剪规则配置文件 | 让父子保留策略可按项目或模块调整。 |
| 增加规划规则配置文件 | 让能力域、条目数量和验证策略可按芯片类型调整。 |
| 增加特征置信度评分 | 在 Evidence Level 基础上量化多源一致性。 |
| 增加寄存器表精细解析 | 提高 register/bitfield 提取准确度。 |
