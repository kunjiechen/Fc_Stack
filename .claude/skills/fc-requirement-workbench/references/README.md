# fc-requirement-workbench Reference Files

本目录包含 `fc-requirement-workbench` skill 的所有规则、模板和参考文档。每个文件有明确的定位和加载时机。

## 文件层次

```
Layer 1: Input Processing（输入处理）
  ├── extraction-rules.md           提取规则、原始提取模型、正式需求门禁
  ├── feature-extraction-design.md  多视角并行提取器架构与设计
  └── chip-view-extraction-rules.md 芯片手册三视图提取规则

Layer 2: Requirement Construction（需求构建）
  ├── construction-rules.md         各类需求的最小必填字段与缺失处理
  ├── semantic-model.md             内部需求语义对象 schema
  └── requirement-bundle-contract.md 输出 bundle 合约（10 个 section 定义）

Layer 3: Quality & Calibration（质量与校准）
  ├── requirement-quality-contract.md 好需求包的质量定义
  ├── rule-engine.md                 完整性/一致性/约束/溯源/反幻觉规则
  ├── calibration-rules.md           历史经验沉淀的 21 条校准规则
  └── authoring-standard.md          SRS 写法、章节、字段、语言规范

Layer 4: Output & Rendering（输出与渲染）
  ├── srs-output-template.md         正式 SRS 章节结构与渲染骨架
  └── rendering-templates.md         辅助渲染模板（追溯矩阵、覆盖矩阵、验证报告）

Layer 5: Platform Reference（平台参考）
  ├── aurix2g-normative-patterns.md  AURIX 2G 平台规范经验库（接口/多核/配置/安全/状态/诊断/时序/驱动类型）
  ├── capability-promotion-policy.md 芯片能力提升为正式需求的策略
  └── requirement-grounding-policy.md 基于现有代码库的需求锚定策略

Layer 6: Machine-Readable Rules（机器可读规则）
  └── raw-classification-rules.yaml  原始项门禁分类规则（YAML，由 raw_classification.py 加载）

Layer 7: Architecture（架构设计）
  └── architecture-design.md         完整阶段方案、引入原因、维护要求（详细版 pipeline 参考）
```

## 按文件

| 文件 | 定位 | 何时加载 |
|---|---|---|
| `architecture-design.md` | 唯一详细架构与方案参考，描述所有阶段的方案、引入原因和维护要求 | 需要理解阶段实现细节时 |
| `extraction-rules.md` | 提取规则、两层原始提取模型、正式需求门禁、证据等级、软件动作门 | 需要判断如何从输入提取结构化信息时 |
| `feature-extraction-design.md` | extraction-rules.md 的配套详细设计：12 视角提取器、6 后处理器、聚合规则 | 需要理解多视角提取架构时 |
| `chip-view-extraction-rules.md` | 芯片手册三视图提取的触发条件、提取域、字段 schema、递进关系 | 输入包含芯片手册且 chip view 文件缺失时 |
| `construction-rules.md` | 每类需求的最小必需字段、缺失降级处理、Ready/Draft/Open Issue 判定 | 构建需求条目时 |
| `semantic-model.md` | 内部需求语义对象 JSON schema、关系类型、状态模型 | 需要稳定结构化对象时 |
| `requirement-bundle-contract.md` | 输出 bundle 的 10 个 section 契约、下游消费接口 | 生成 bundle 或下游消费 bundle 时 |
| `requirement-quality-contract.md` | 好需求包的 7 个质量维度定义 | 评审需求包质量时 |
| `rule-engine.md` | 完整性/一致性/约束/归属/追溯/反幻觉校验规则 | 校验需求质量时 |
| `calibration-rules.md` | 21 条经验校准规则（写法偏好、粒度、边界判断） | 校准 SRS 写法和解决歧义时 |
| `authoring-standard.md` | SRS 文档写法、章节结构、字段呈现、语言/单位/粒度规范 | 生成或评审 SRS 文档时 |
| `srs-output-template.md` | 正式 SRS 默认章节结构和渲染骨架 | 生成 SRS Markdown 时（默认加载） |
| `rendering-templates.md` | 辅助渲染模板（追溯矩阵、覆盖矩阵、验证报告） | 生成追溯/覆盖矩阵时 |
| `aurix2g-normative-patterns.md` | AURIX 2G 平台规范经验库（接口/多核/配置/安全/诊断/时序/驱动类型） | 需要判断 MainFunction、接口分类、多核/诊断/状态机等平台规范时 |
| `capability-promotion-policy.md` | 芯片能力提升为正式需求的 4 个前置条件和门禁问题 | 判断能力是否可提升为需求时 |
| `requirement-grounding-policy.md` | 基于现有代码库的锚定策略（参考模块发现、模式采纳/拒绝） | 有代码库可锚定时 |
| `raw-classification-rules.yaml` | 原始项门禁分类规则（机器可读，由 raw_classification.py 加载） | 分类原始提取项时（代码自动加载） |

## 优先级

当规则冲突时，优先级从高到低：

1. 字段完整性与缺失处理 → `construction-rules.md`
2. 文档写法与呈现 → `authoring-standard.md`
3. 风格与边界倾向 → `calibration-rules.md`
4. 芯片视图提取 → `chip-view-extraction-rules.md`
5. 流程边界与加载策略 → `SKILL.md`
6. 阶段方案细节 → `architecture-design.md`
