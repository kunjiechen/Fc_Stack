---
name: fc-requirement-workbench
description: "Use this skill to turn automotive technical inputs into structured, validated, traceable software requirements and SRS outputs. It is for requirement generation only: document parsing, chunking, semantic indexing, requirement semantic objects, rule validation, requirement graph/reporting, SRS rendering, and requirement-level trace/coverage/evidence. It must not generate downstream architecture, implementation artifacts, test skeletons, governance dashboards, or autonomous engineering plans."
---

# FC Requirement Workbench

##定位

这是一个**需求生成 skill**，不是架构生成器，也不是代码生成器。

唯一 SRS 生成路径（Planned SRS）：

```text
Datasheet / 项目需求 / 参考SRS / Trace输入
→ MarkdownStructureParser（文档结构解析、Chunk、语义索引）
→ FeatureExtractor（多视角并行特征提取）
→ RequirementCandidateMapper（Feature/Subfunction → Candidate）
→ RequirementCandidatePruner（候选压缩、Keep/Merge、补料清单）
→ RequirementPlanner（能力域编排、需求规划、验证策略）
→ RequirementRuleEngine（规则校验）
→ RequirementBuilder（ID 生成、工程需求构建）
→ SrsStructureGenerator + MarkdownSrsRenderer（SRS 输出）
→ TraceabilityPipeline（Trace/Coverage/Verification/ASPICE）
```

## 标准 Skill 结构

```text
.
├── pyproject.toml                            # skill Python 包配置
├── src/fc_requirement_workbench/             # Python 实现包（单一 Planned SRS 路径）
├── engineering.md                            # 工程设计文档
├── references/                               # 规则、模板、架构文档
├── scripts/
│   ├── check_srs_format.py
│   └── generate_requirement_input_templates.py
├── templates/                                # 用户可填写输入模板
└── .claude/skills/fc-requirement-workbench/
    ├── SKILL.md                              # skill 入口说明
    └── agents/openai.yaml                    # OpenAI/Codex UI 元数据
```

##范围

只做 Planned SRS 单路径，涵盖四个阶段：

1. **Phase 1 - 特征提取与候选映射** — FeatureExtractor → CandidateMapper → CandidatePruner
   文档解析、Chunk、语义索引、多视角特征提取、候选映射、候选压缩。
2. **Phase 2 - 需求规划与规则校验** — RequirementPlanner → RequirementRuleEngine
   能力域编排、需求条目规划、完整性/一致性/约束/Ownership/Dependency/Trace 校验。
3. **Phase 3 - SRS 构建** — RequirementBuilder → SrsStructureGenerator → Renderer
   语义对象 → 工程化 Requirement → ID 生成 → SRS Markdown/HTML/DOCX。
4. **Phase 4 - 可追溯性** — TraceabilityPipeline
   Source → Requirement → Verification 追溯、覆盖矩阵、ASPICE evidence。

明确不做：

- Requirement → Architecture 映射。
- Architecture → Implementation 映射。
- C/H 代码、配置文件、接口实现、外部依赖适配、测试骨架生成。
- AI Governance、Quality Gate Dashboard、Self Repair、Autonomous Workflow。
- 任何“自动发布”或绕过人工评审的流程。

##使用场景

使用本 skill 处理：

- 芯片手册、Datasheet、项目需求、参考 SRS、Trace 表。
- CAN/LIN/SPI/PWM/MCU 外设驱动、FC 模块、AUTOSAR BSW 相关需求。
- 功能、接口、状态、配置、时序、诊断、安全相关需求提取。
- 芯片能力 + 项目约束融合，例如“芯片支持 Listen-only，但项目禁止”。
- SRS、需求对象 JSON、验证报告、追溯矩阵、覆盖矩阵。

##核心原则

- 方案升级必须同步更新 [architecture-design.md](references/architecture-design.md)，记录阶段、问题、引入方案、影响文件、输出变化和验证方式。
- 先做语义对象，再写 SRS 句子。
- 先区分芯片能力和项目约束，再生成最终需求。
- 需求必须可验证、有边界、有来源、有状态。
- 模糊词必须被改写或标记为问题，例如 `正常`、`稳定`、`快速`、`多个`。
- 没有证据的需求不能直接确认，标记为 `needs_source` 或 `open_issue`。
- SRS 只描述软件应做什么，不写设计或实现方案。
- 需求提取时，判断一个外部芯片驱动是否需要 MainFunction 接口，先读取 [aurix2g-normative-patterns.md](references/aurix2g-normative-patterns.md) 的 1.2 MainFunction 规则和 1.1 接口分类法则。核心判断逻辑：存在异步（Asynchronous）Set 接口或周期轮询/SPI 诊断依赖 → 必须提供 MainFunction。纯 GPIO 直驱且无 SPI 状态读回 → 可不需要。

##规则职责

规则文件按职责分工，不要混用：

- [authoring-standard.md](references/authoring-standard.md): 只负责 SRS 文档写法、章节组织、字段呈现、语言和版式约束。
- [construction-rules.md](references/construction-rules.md): 只负责各类需求的最小必填项、缺失字段处理和构建完整性判断。
- [calibration-rules.md](references/calibration-rules.md): 只负责本地写作偏好、粒度校准和历史案例形成的判断习惯。
- [srs-output-template.md](references/srs-output-template.md): 只负责最终输出章节和渲染形态。

如果同一规则同时出现在多份文件中，应按以下优先级收口：

1. 字段是否齐全、缺失后如何降级：`construction-rules.md`
2. 文档如何写、如何排、如何避免头重脚轻：`authoring-standard.md`
3. 风格偏好、案例化判断和边界倾向：`calibration-rules.md`
4. 流程边界和何时加载哪个规则：`SKILL.md`

##工作流

开始处理工程级方案设计、阶段调整或规则升级时，先读取 [architecture-design.md](references/architecture-design.md)，确认当前整体架构、阶段边界和方案维护要求。

### 1. 输入解析

解析 Markdown 或结构化输入，提取：

- heading
- table
- fenced code block
- note / warning
- image / html block 标记
- section / subsection

大文档先建立阅读地图，优先读取：

- Operating Modes
- State Machine
- Pin Description
- Timing
- Diagnostic / Fault
- Configuration / Register
- Wake / Sleep

### 2. Chunk 与语义索引

建立工程语义 Chunk：

- `chapter_chunk`
- `table_chunk`
- `state_chunk`
- `interface_chunk`
- `validation_chunk`

建立索引：

- `mode`
- `timing`
- `diagnostic`
- `interface`
- `configuration`
- `state`
- `safety`
- `trace`

### 3. 需求语义提取

先按 [feature-extraction-design.md](references/feature-extraction-design.md) 执行多视角并行特征提取：身份、能力、Pin、接口、寄存器、bitfield、状态、诊断、时序、电气、限制和项目映射必须独立提取，再聚合、交叉校验、判断软件责任和输出缺口。每个重要特征必须进一步拆解子功能，输出功能总结和应用方案。

再按 [extraction-rules.md](references/extraction-rules.md) 从 Datasheet、项目需求、源码、配置文件和测试材料中提取模式、Pin、接口、配置项、状态机、时序值、禁止项和资源约束，并标注来源、优先级、缺口和是否可生成需求。

特征提取后必须经过 `Feature/Subfunction → RequirementCandidate` 映射，生成候选需求映射中间产物。该阶段允许一个输入特征映射到多个候选需求类别，但每条候选必须包含映射理由、证据强度、软件动作、缺失输入和 Ready 条件；不得直接把候选提升为 Ready。

候选映射后必须经过 `RequirementCandidatePruner` 压缩，生成候选需求压缩中间产物。该阶段按行为族聚类，输出 Keep/Merge 决策、保留候选矩阵和面向补料的 Required Inputs 清单；被合并候选不得丢失证据，必须保留 retained_by 关系。

候选压缩后必须经过 `RequirementPlanner` 规划，生成需求规划中间产物。该阶段按能力域规划 SRS 条目数量、合并策略、编写策略和验证策略；SRS 正文不得直接泄露候选、证据等级、映射过程等中间态内容。

Planned SRS 是唯一 SRS 生成路径：`FeatureExtractor → RequirementCandidateMapper → RequirementCandidatePruner → RequirementPlanner → RequirementRuleEngine → RequirementBuilder → SrsStructureGenerator → MarkdownSrsRenderer`。生成的 SRS 为 Draft，用于评审和补料，不代表需求已 Ready。

性能策略：默认只生成最终 SRS，不渲染、不落盘中间 Markdown。需要审查中间质量时再使用 `--with-intermediates`，或用 `--emit features-markdown|candidates-markdown|pruning-markdown|planning-markdown` 单独查看某个阶段。单阶段输出应提前返回，避免继续执行后续 SRS 构建。

需要稳定 JSON/Schema 时，读取 [semantic-model.md](references/semantic-model.md)。

### 4. 规则校验

生成 SRS 前必须检查：

- Completeness: 是否缺 Wake、GetMode、异常路径、验证方法。
- Consistency: 状态、接口、配置、时序是否冲突。
- Constraint: 项目禁止项、范围、实例数、ASIL 边界是否满足。
- Ownership: TXD/RXD/WAKE/INH/ERR_N/service interface/callback 归属是否明确。
- Dependency: 依赖接口、配置开关、诊断路径是否存在。
- Trace: 每条需求是否有来源和验证意图。

需要详细规则时，读取 [rule-engine.md](references/rule-engine.md)。

需要 AURIX 2G 平台的内置规范做比对（接口分类、MainFunction 判定、多核架构、配置容器、安全分层、状态机、诊断模式、时序约束、不同驱动类型的必须接口清单）时，读取 [aurix2g-normative-patterns.md](references/aurix2g-normative-patterns.md)。

### 5. SRS 构建

将语义对象转换为工程需求：

```text
Requirement Semantic Object
→ Requirement Pattern
→ Requirement Instance
→ SRS Section
```

默认 ID：

```text
SRS-{MODULE}-{TYPE}-{NNNN}
```

示例：

```text
SRS-CAN-FUNC-0001
SRS-CAN-IF-0001
SRS-CAN-STATE-0001
SRS-CAN-TIME-0001
```

生成 SRS 时，优先读取 [srs-output-template.md](references/srs-output-template.md)。
编写和评审 SRS 文档时，读取 [authoring-standard.md](references/authoring-standard.md)，只遵循章节、语言、字段呈现和版式规范。
构建 SRS 需求条目时，读取 [construction-rules.md](references/construction-rules.md)，并据此判断各类需求最小字段完整性和缺失处理。
校准写法、颗粒度、能力/项目支持边界和历史偏好时，读取 [calibration-rules.md](references/calibration-rules.md)。
生成 Trace/Coverage/Validation 辅助输出时，读取 [rendering-templates.md](references/rendering-templates.md)。

### 6. 输出物

默认只输出需求工程产物：

- SRS Markdown / HTML / DOCX（唯一生成路径：Planned SRS）
- Source → Requirement Trace Matrix
- Requirement → Verification Intent Coverage Matrix
- ASPICE Evidence Summary

中间产物默认关闭；调试或评审时才显式开启：

```text
--with-intermediates
--intermediate-dir artifacts/intermediate
--emit features-markdown | candidates-markdown | pruning-markdown | planning-markdown
```

SRS 渲染规则变更后，应用 `scripts/check_srs_format.py` 对生成的 Markdown 做最小格式守卫，重点检查需求条目是否误回退成字段表格。

##仓库实现入口

核心代码位于 `src/fc_requirement_workbench/`，全部服务于唯一 Planned SRS 路径：

- `parser.py`: 文档结构解析、Chunk、语义索引。
- `schema.py`: Requirement Semantic Object。
- `feature_extraction.py`: 多视角并行特征提取（身份、能力、Pin、寄存器、状态、诊断、时序）。
- `candidate_mapping.py`: Feature/Subfunction → Candidate 映射，含证据强度和 Ready 条件。
- `candidate_pruner.py`: 候选压缩，按行为族聚类 Keep/Merge，生成补料清单。
- `requirement_planner.py`: 能力域编排，规划 SRS 条目数量/合并/编写/验证策略。
- `rules.py`: 规则校验引擎（完整性、一致性、约束、Ownership、Dependency、Trace）。
- `builder.py`: Requirement Builder 和 ID Engine。
- `srs.py`: SRS 结构与 Markdown/HTML/DOCX 渲染。
- `traceability.py`: Trace/Coverage/Verification/ASPICE evidence。
- `cli.py`: 单一 Planned SRS 路径命令行入口。

不再存在多条 SRS 生成路径。不再保留旧阶段拆分实现；当前仅维护 `feature_extraction.py`、`candidate_mapping.py`、`candidate_pruner.py`、`requirement_planner.py` 等单一路径实现。
