# fc-requirement-workbench 当前设计

## 定位

`fc-requirement-workbench` 是一个需求生成 skill。

它只解决：

```text
技术输入
→ 需求语义解析
→ 需求质量校验
→ SRS 生成
→ 需求级追溯/覆盖/证据
```

它不做架构设计、不做实现设计、不生成代码、不生成 UT skeleton。

## 范围边界

当前只保留 Phase 1-4。

### Phase 1：Requirement Semantic Infrastructure

目标：把非结构化输入变成稳定的需求语义对象。

模块：

- `parser.py`：Markdown 结构解析、Chunk、语义索引。
- `schema.py`：Requirement Semantic Object。
- `extractor.py`：基础规则提取。

输出：

- Document Structure
- Semantic Chunk
- Semantic Index
- Requirement Semantic Model

### Phase 2：Requirement Quality Infrastructure

目标：让需求可校验、可约束、可解释。

模块：

- `rules.py`：完整性、一致性、约束、Ownership、Dependency、Trace 规则。
- `graph.py`：Requirement Graph。
- `report.py`：Validation Report。

输出：

- Validation Finding
- Requirement Graph
- Requirement Quality Report

### Phase 3：Requirement Builder

目标：把语义对象生成工程化 SRS 条目。

模块：

- `builder.py`：Requirement Instance、ID Engine。
- `srs.py`：SRS 章节组织与 Markdown/HTML/DOCX 渲染。

输出：

- SRS Requirement
- SRS Document
- Source → Requirement Trace Matrix
- Requirement → Verification Intent Coverage Matrix

### Phase 4：Requirement Evidence Layer

目标：建立需求级追溯、覆盖、验证意图和 ASPICE evidence summary。

模块：

- `traceability.py`：Source → Requirement → Verification/Test Evidence。

输出：

- TraceLink
- CoverageRecord
- VerificationObject
- LifecycleObject
- ImpactRecord
- ASPICE Evidence Summary

## 工作流

```text
Input Markdown / JSON
    ↓
MarkdownStructureParser
    ↓
RequirementSemanticExtractor
    ↓
RequirementRuleEngine
    ↓
RequirementGraphBuilder
    ↓
RequirementBuilder
    ↓
SrsStructureGenerator / Renderer
    ↓
TraceabilityPipeline
```

## 输入

推荐输入：

- Datasheet 摘录
- 芯片手册 Markdown
- 项目需求 Markdown
- 参考 SRS
- 需求验证计划或 Trace 文档

输入内容至少应覆盖：

- mode / state
- timing
- interface / pin / signal
- configuration
- diagnostic
- project constraints

## 输出

默认输出只包含需求工程产物：

- `structure`
- `requirements`
- `validation`
- `graph`
- `report`
- `srs-json`
- `srs-markdown`
- `srs-html`
- `srs-docx`
- `traceability`
- `coverage`
- `verification`
- `aspice`
- `impact`

## 不做什么

当前仓库不再包含：

- Requirement → Architecture 映射。
- Architecture → Implementation 映射。
- 代码结构、接口实现、配置文件、外部依赖适配生成。
- UT skeleton 生成。
- AI Governance / Quality Gate Dashboard。
- Autonomous Workflow / Self Repair / Optimization。

## 下一步开发方向

继续把 Phase 1-4 做深：

1. 提升 Markdown 表格、Note、Warning、HTML block 的解析稳定性。
2. 强化 Capability 与 Constraint 分离。
3. 去重同源/同义需求。
4. 改善 Mode/Timing/Interface/Configuration/Diagnostic 提取精度。
5. 增强完整性、一致性、约束和 Ownership 规则。
6. 优化 SRS 句式，让需求更原子、可验证、有边界。
7. 让 trace/coverage/evidence 保持需求级，不向架构和实现扩展。
