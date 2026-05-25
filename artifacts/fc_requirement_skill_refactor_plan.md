# FC Requirement Skill 重构方案与下一步计划

## 1. 文档目的

本文档用于沉淀 `fc-requirement-workbench` 的下一轮重构方案，明确：

- 为什么要重构需求生成 skill
- 本轮重构需要借鉴详细设计生成 skill 的哪些方法
- 当前需求 skill 已采用了哪些点、缺少哪些点
- 下一步实施计划是什么
- 如何回答“覆盖性、可落地性、合规性、下游可消费性”这 4 个关键问题

本文档聚焦对象是：

- `.claude/skills/fc-requirement-workbench`

不直接替代：

- `fc-architecture-workbench`
- `fc-implementation-workbench`

但本轮重构必须显式增强对下游架构生成、详细设计生成、测试用例生成的支撑能力。

---

## 2. 当前判断

当前 `fc-requirement-workbench` 已具备以下基础：

- 有相对完整的 SRS 写作规则
- 有 requirement semantic model
- 有 extraction / construction / calibration / authoring 分层规则
- 有 Planned SRS 单路径概念
- 有基本的格式检查脚本

但当前问题也很明确：

1. 仍然偏向“规则驱动的 SRS 生成”
2. 结构化 requirement object 已定义，但还未真正成为唯一中间真相层
3. 缺少 requirement bundle 级别的正式生成、校验和回放机制
4. 缺少对“为什么这样写、为什么这样裁剪、为什么降级为 Draft/Open Issue”的 decision 收敛机制
5. 缺少面向下游架构和测试的稳定种子输出

一句话总结：

当前需求 skill 已经有“规则体系”，但还没有完全完成“方法重构”。

---

## 2.1 当前输入现实与重构前提

当前项目的现实情况是：

- 暂时无法提供更完整、更正式的需求规范文档
- 可以提供真实工程源码
- 当前这一版生成结果是可接受的实施基线

这不是阻塞条件，反而可以形成一条更贴近工程现实的重构路径。

本轮重构的输入前提调整为：

1. 以真实工程源码作为 implemented evidence
2. 以当前可接受版本作为 acceptance baseline
3. 以现有 skill 规则文件作为 normative baseline
4. 后续再逐步补强更正式的需求规范输入

这意味着本轮不是“等待更完美输入后再做”，而是先把当前可获得的真实工程证据结构化。

---

## 3. 本轮重构总目标

本轮目标不是简单把 SRS 文档写得更像模板，而是把需求生成 skill 从：

```text
原始输入
-> 规则提取
-> 直接输出 SRS markdown
```

升级成：

```text
原始输入
-> grounding 选择
-> requirement bundle 生成
-> requirement bundle 校验
-> SRS markdown 渲染
-> coverage / architecture seed / test seed 输出
```

核心目标有五个：

1. 需求文档不再是唯一真相层，requirement bundle 才是 source of truth
2. 每条需求都能证明来源、状态、约束、验证方式和可执行性
3. 每条需求都能证明是否符合公司规范，而不是随意发挥
4. 需求输出能稳定支撑下一步架构设计和测试用例生成
5. 需求 skill 的方法与详细设计 skill 收敛为同一工程化方法族

---

## 3.1 对五个核心目标的进一步解释

### 3.1.1 requirement bundle 才是 source of truth

这句话的意思不是否定需求文档，而是改变“真相层”的位置。

旧方式：

- `SRS markdown` 是唯一主载体
- 需求状态、来源、证据、约束大量散落在 prose 中
- 一旦格式调整、章节移动、文案改写，就很难保证关键语义不漂移

新方式：

- `requirement bundle` 才是唯一真相层
- `SRS markdown` 只是 requirement bundle 的渲染结果
- 文档用于阅读和评审，bundle 用于生成、校验、回放和下游消费

因此：

- 文档格式可以变化
- 章节可以调整
- 表达可以润色

但 requirement 的核心事实不应只存在于文档文字里，而应稳定存在于结构化对象里。

### 3.1.2 每条需求都能证明来源、状态、约束、验证方式和可执行性

这句话的重点是“可证明”，不是“看起来像”。

未来一条 requirement 不再只是一句：

- 模块应支持某功能

而是至少要能同时回答：

- 这条从哪里来
- 它现在是 `Ready`、`Draft` 还是 `Open Issue`
- 它受哪些约束影响
- 它如何验证
- 它是否已具备进入架构和测试阶段的条件

### 3.1.3 每条需求都能证明符合公司规范，而不是随意发挥

这句话的重点是“规则依据可审计”。

也就是说，每条需求都应能解释：

- 为什么这么写
- 为什么这么拆粒度
- 为什么这是 formal requirement 而不是背景描述
- 为什么它不属于自由发挥

证明依据应来自：

- authoring standard
- construction rules
- calibration rules
- 平台规范
- 历史工程模式

### 3.1.4 需求输出能稳定支撑架构和测试

这句话的重点是“下游可消费”，而不是“下游可以阅读”。

也就是说，需求对象应能稳定导出：

- 架构关心的接口、配置、状态、依赖、时序、诊断边界
- 测试关心的触发条件、输入、输出、异常路径、验收准则

这要求 requirement bundle 里保留真正可供下游消费的字段，而不是只保留叙述文本。

### 3.1.5 与详细设计 skill 收敛为同一工程化方法族

这句话的重点不是三个 skill 长得一样，而是三者遵循同一方法论：

```text
grounding
-> structured bundle
-> validator
-> markdown rendering
```

只有这样，未来才能稳定形成：

- requirement bundle
- architecture bundle
- detailed design bundle

并在三层之间做一致性校验。

---

## 4. 详细设计 Skill 可借鉴的重构点

本轮需求 skill 重构，必须明确借鉴详细设计 skill 的以下方法，而不是只借鉴文风。

### 4.1 Grounding First

详细设计 skill 在生成前先做 grounding：

- 选择真实工程参考 FC
- 提炼 adopted patterns
- 记录 rejected patterns

需求 skill 也应如此。

需求层 grounding 的作用不是替代原始需求，而是回答：

- 当前模块最接近哪类已有 FC
- 哪些接口/状态/MainFunction 模式是常规模式
- 哪些芯片能力不应直接提升为项目需求
- 哪些能力应显式排除或保留为 pending_confirm

### 4.2 Structured Model First

详细设计 skill 先出 bundle，再渲染 markdown。

需求 skill 也必须从“有 semantic model 说明”升级为“所有正式 SRS 都先经过 requirement bundle”。

### 4.3 Traceable Decisions

详细设计 skill 把以下信息显式化：

- `status`
- `decision`
- `decision_reason`
- `pending_confirm`
- `reserved`
- `trace_ids`

需求 skill 也必须这样做，尤其要显式记录：

- 为什么某能力被保留为 `Draft`
- 为什么某需求被判为 `Open Issue`
- 为什么某 datasheet 能力未进入正式软件需求
- 为什么某需求只输出为架构种子而不是正式 requirement

### 4.4 Validation Gated

详细设计 skill 已经证明“规则存在”不等于“门禁存在”。

需求 skill 也必须有两层校验：

1. bundle 层校验
2. markdown 层校验

### 4.5 Document As Rendered View

SRS markdown 应是 requirement bundle 的渲染结果，而不是直接生成的唯一产物。

### 4.6 Quality Contract

详细设计 skill 有 `detailed_design_quality_contract.md`。

需求 skill 也需要一份对应的 `requirement_quality_contract.md`，定义什么叫：

- 可覆盖
- 可落地
- 可验证
- 可追踪
- 可下游消费

---

## 5. 当前需求 Skill 是否已采用这些点

### 5.1 已部分采用

- 已有 semantic model
- 已有 source / trace / verification / status 概念
- 已有 authoring / construction / calibration / extraction 分层
- 已有 rule engine 和格式检查意识

### 5.2 尚未正式落地

- 未形成正式 requirement bundle-first 流水线
- 未形成 grounding summary 正式输入层
- 未形成统一 decision object
- 未形成 bundle validator
- 未形成 markdown drift checker
- 未形成 coverage matrix 输出
- 未形成 architecture seed / test seed 输出

结论：

需求 skill 当前只采用了详细设计重构方法的一部分，主要停留在“规则体系”和“语义对象说明”层，尚未进入完整的 bundle-first、validator-first、rendering-last 阶段。

---

## 6. 本轮是否继续采用 YAML 结构化对象

答案：是，而且建议明确采用。

理由如下：

1. YAML 适合承载 requirement bundle
2. YAML 适合人工审查与版本比对
3. YAML 适合被架构 skill 和测试生成流程直接消费
4. YAML 适合导出 coverage、open issues、decision、seed 等中间产物

因此本轮建议延续详细设计 skill 的做法，把原本藏在 prose 中的关键信息抽成 requirement bundle YAML。

建议输出：

- `requirement_bundle.yaml`
- `coverage_report.yaml`
- `architecture_seed.yaml`
- `test_seed.yaml`

---

## 7. Requirement Bundle 目标结构

本轮不建议只保留单条 requirement object，而应增加 bundle 级顶层结构。

建议最小结构如下：

```yaml
module_identity:
source_inventory:
grounding_summary:
requirements:
coverage_matrix:
open_issues:
architecture_seed:
test_seed:
generation_notes:
```

### 7.1 `module_identity`

用于描述：

- module 名称
- 层级
- 芯片/平台范围
- 项目范围
- 输入版本

### 7.2 `source_inventory`

记录本次需求生成使用了哪些来源：

- datasheet
- 原始项目需求
- 参考 SRS
- 项目约束
- 平台规范
- grounding FC

### 7.3 `grounding_summary`

用于说明：

- 采用了哪些参考 FC 模式
- 排除了哪些模式
- 为什么采用 / 排除

### 7.4 `requirements`

每条 requirement 至少包含：

```yaml
- id:
  title:
  type:
  shall:
  rationale:
  source:
  constraints:
  interfaces:
  states:
  configuration:
  timing:
  diagnostics:
  ownership:
  verification:
  trace:
  status:
  decision:
  decision_reason:
  downstream_impacts:
```

### 7.5 `coverage_matrix`

至少记录：

- source chunk 是否已覆盖
- 覆盖到哪些 requirement id
- 若未覆盖，为什么未覆盖
- 若被排除，排除依据是什么

### 7.6 `open_issues`

集中记录：

- ownership 未确认
- timing 未确认
- capability 是否项目支持未确认
- interface 归属未确认

### 7.7 `architecture_seed`

用于输出可供架构 skill 消费的对象，不在需求层直接冻结架构。

### 7.8 `test_seed`

用于输出可供测试用例生成流程消费的对象。

---

## 7.9 当缺少更强需求规范文档时的输入替代策略

当前阶段允许使用三类现实输入共同构成 requirement bundle 的依据。

### A. 工程源码

源码可作为以下证据来源：

- implemented behavior evidence
- interface evidence
- config evidence
- state / fault / timing evidence
- project style evidence

但源码默认不等于“正式上游需求”，因此应在 source inventory 中显式标注：

- `source_type: codebase`
- `role: implemented_evidence`
- `confidence: medium` 或 `high`

源码的作用是：

- 证明当前工程实际落地了什么
- 证明哪些能力真实存在
- 证明项目风格和命名习惯
- 反证某些 datasheet 能力并未真正纳入工程

### B. 当前可接受版本

当前已接受的 SRS / 架构 / 详设产物，可作为：

- acceptance baseline
- rendering baseline
- calibration baseline

其作用不是证明“理论最优”，而是证明：

- 当前这个输出形态你可以接受
- 当前这个粒度边界可作为第一轮 bundle 抽取目标
- 当前这个写法可用于反推最小可接受 requirement contract

### C. 现有规则资产

当前 skill 内已有：

- `authoring-standard.md`
- `construction-rules.md`
- `calibration-rules.md`
- `rule-engine.md`

这些文件可作为本轮的规范基线，即使没有新增正式外部规范文档，也足以支撑第一轮方法重构。

因此，本轮 requirement skill 的真实输入策略应是：

```text
源码事实
+ 当前接受版本
+ 现有规则资产
-> requirement bundle 反向抽取与固化
```

---

## 8. 在需求生成中创建架构文档的建议

本轮不建议由需求 skill 直接正式生成完整架构文档。

建议做法是：

- 需求 skill 输出 `architecture_seed`
- 架构 skill 消费 `architecture_seed`
- 再由架构 skill 正式生成 architecture bundle 和 architecture markdown

原因：

1. 需求层负责“定义软件应做什么”
2. 架构层负责“冻结边界、接口、配置和依赖”
3. 若在需求层直接生成正式架构文档，容易职责越界

因此在需求生成阶段，应创建的是：

- 架构输入包
- 架构候选对象
- 架构风险与待确认项

而不是直接把需求文档扩写成正式架构设计。

---

## 9. 关键问题回答

## 9.1 如何证明当前需求能够覆盖原始需求及文档

不能只靠“文档看起来写全了”，必须建立正式覆盖机制。

本轮建议通过以下方式证明：

1. 原始输入先做 chunk 化和 source inventory
2. 每条 requirement 必须记录：
   - `document`
   - `section`
   - `chunk_id`
   - `evidence`
3. 输出 `coverage_matrix`
4. 将原始输入块划分为：
   - covered
   - partially_covered
   - excluded
   - unresolved
5. 每个 `excluded` 和 `unresolved` 项必须有 reason

这样可以明确回答：

- 原始需求中哪些内容已进入正式 requirement
- 哪些内容只作为背景信息存在
- 哪些内容因项目约束被排除
- 哪些内容因信息不足暂未确认为正式 requirement

证明方式不是人工解释，而是 bundle 和 matrix 的导出能力。

## 9.2 如何证明当前需求可落地、可执行、可验证

必须给每条 requirement 设立 `Ready Gate`。

只有满足以下条件，才允许标记为 `Ready`：

1. 行为明确，不含模糊词
2. 有明确触发条件
3. 有输入/输出定义
4. 有异常处理或边界描述
5. 有验证方式
6. 有验证阶段
7. 有验收准则
8. 有来源证据

若缺任一关键项，则只能是：

- `Draft`
- `Open Issue`
- `needs_source`
- `conflict`

因此，“可落地可执行可验证”的证明不应来自主观评价，而应来自 bundle validator 的自动判定。

## 9.3 如何证明当前需求满足公司规范要求，而不是随意发挥

本轮建议建立“规则依据可审计”机制。

每条需求至少应能追溯到以下之一：

- 项目原始输入
- datasheet
- 参考规范
- 公司 authoring standard
- construction rules
- calibration rules
- 平台规范模式

建议新增字段：

- `rule_basis`
- `normative_basis`

用于说明该需求的写法和边界判断依据。

同时通过 validator 检查：

1. 是否符合 SRS 章节与字段规范
2. 是否符合 requirement category 的最小字段要求
3. 是否违反 calibration 的边界习惯
4. 是否出现无来源且无规则依据的自由发挥内容

这样才能从“像规范文档”升级为“能证明按规范生成”。

## 9.4 如何证明当前需求能够引导下一步架构生成及测试用例生成等流程

证明方法不是主观判断，而是显式输出下游可消费对象。

### 面向架构生成

需求 bundle 至少要能稳定输出：

- external interface candidates
- dependency candidates
- config item candidates
- state concerns
- timing constraints
- diagnostic responsibilities
- ownership questions
- pending_confirm items

这些统一进入 `architecture_seed`。

### 面向测试用例生成

需求 bundle 至少要能稳定输出：

- trigger
- input
- expected output
- exception path
- acceptance criteria
- verification method / level

这些统一进入 `test_seed`。

只要 `architecture_seed` 和 `test_seed` 可稳定导出，就能证明需求对象能够实际引导下游流程，而不是只能阅读。

---

## 10. 本轮重构关键点

本轮重构最关键的不是“多写几份规则”，而是把以下 8 个点真正落地。

### 10.1 定义 Requirement Quality Contract

新增：

- `references/requirement_quality_contract.md`

作用：

- 定义什么叫合格 requirement
- 定义 `Ready` 的最低门槛
- 定义哪些内容不得进入正式 requirement

### 10.2 定义 Requirement Bundle Contract

新增：

- `references/requirement_bundle_contract.md`

作用：

- 定义 bundle 顶层结构
- 定义 requirement item 的正式字段集合
- 定义 coverage/open issue/seed 的结构

### 10.3 引入 Grounding Summary

新增：

- `references/requirement_grounding_policy.md`

作用：

- 规范如何选择参考 FC
- 规范 adopted/rejected pattern 的记录方式

### 10.4 新建 YAML Bundle 生成器

新增脚本建议：

- `scripts/build_requirement_bundle.py`

作用：

- 从 raw input / datasheet / project notes 提取 requirement bundle
- 输出 YAML

### 10.5 新建 Bundle Validator

新增脚本建议：

- `scripts/validate_requirement_bundle.py`

作用：

- 校验字段完整性
- 校验 source coverage
- 校验 duplicate/conflict
- 校验 Ready Gate
- 校验 downstream completeness

### 10.6 新建 SRS 渲染器

新增脚本建议：

- `scripts/render_srs_from_bundle.py`

作用：

- 将 requirement bundle 渲染为标准 SRS markdown

### 10.7 新建 Markdown Checker

新增脚本建议：

- `scripts/check_requirement_markdown.py`

作用：

- 检查 SRS markdown 与 requirement bundle 是否漂移
- 检查标题、状态、附录和 requirement block 一致性

### 10.8 输出下游 Seed

在需求 skill 内正式定义：

- `architecture_seed.yaml`
- `test_seed.yaml`

这一步是连接需求与架构/测试的重要桥梁。

---

## 11. 实施计划

## 11.1 Phase 0：方案冻结

目标：

- 明确重构范围和交付件

交付件：

- 本文档
- 重构任务分解表

完成标准：

- 明确本轮只重构 `fc-requirement-workbench`
- 明确不在需求层直接冻结正式架构文档

## 11.2 Phase 1：合同与结构定义

目标：

- 先定义质量合同和 bundle contract

交付件：

- `requirement_quality_contract.md`
- `requirement_bundle_contract.md`
- `requirement_grounding_policy.md`

完成标准：

- 明确 requirement 的 Ready Gate
- 明确 bundle YAML 的顶层结构
- 明确架构种子和测试种子的边界

## 11.3 Phase 2：Bundle 生成器落地

目标：

- 把当前 requirement semantic model 从说明文档升级成可执行脚本

交付件：

- `build_requirement_bundle.py`
- 首个 `requirement_bundle.yaml`

完成标准：

- 能从真实输入生成稳定 requirement bundle
- 能输出 source_inventory、requirements、coverage、open_issues

## 11.4 Phase 3：Validator 落地

目标：

- 建立 requirement 层正式门禁

交付件：

- `validate_requirement_bundle.py`
- `check_requirement_markdown.py`

完成标准：

- 能自动识别缺 source、缺 verification、状态越级、模糊词、重复项、冲突项

## 11.5 Phase 4：SRS 渲染器与 Seed 输出

目标：

- 让 markdown 成为渲染层
- 输出可供下游消费的对象

交付件：

- `render_srs_from_bundle.py`
- `architecture_seed.yaml`
- `test_seed.yaml`

完成标准：

- SRS 可由 bundle 稳定渲染
- 架构 seed 和测试 seed 可导出

## 11.6 Phase 5：样例回放与回归集

目标：

- 证明方法不是单例有效

交付件：

- `Gp_NCA95yy` 回放样例
- 至少 1 个第二 FC 家族样例
- golden artifacts

完成标准：

- 两个不同 FC 家族都能稳定产出 bundle + SRS + seed
- validator 结果稳定

---

## 12. 近期优先级建议

按优先级建议如下：

1. 先做 `requirement_quality_contract.md`
2. 再做 `requirement_bundle_contract.md`
3. 然后实现 `build_requirement_bundle.py`
4. 接着实现 `validate_requirement_bundle.py`
5. 再实现 `render_srs_from_bundle.py`
6. 最后补 `architecture_seed.yaml` 和 `test_seed.yaml`

不建议一开始就：

- 直接深改架构 skill
- 直接做完整测试用例生成器
- 直接在需求层生成正式 architecture markdown

---

## 13. 风险与注意事项

### 13.1 风险一：需求层越权

如果在需求层直接冻结正式架构接口，很容易与架构 skill 职责重叠。

控制方式：

- 需求层只输出 `architecture_seed`
- 正式 freeze 留给架构 skill

### 13.2 风险二：把芯片能力错误当成项目需求

控制方式：

- 能力和约束分离建模
- 每条需求都要求 source + decision

### 13.3 风险三：YAML 结构太重，反而影响使用

控制方式：

- 先定义最小可用字段集
- 不一次性把所有理想字段塞满

### 13.4 风险四：仅有 YAML，没有回归机制

控制方式：

- bundle、SRS、seed 都要进入 golden 回归集

---

## 13.5 风险五：过度依赖源码，导致“实现即需求”

源码是非常有价值的输入，但不能无条件上升为正式需求。

控制方式：

- 将源码标记为 `implemented_evidence`
- 对源码抽取出的需求增加 `decision` / `decision_reason`
- 区分：
  - 已在项目中实现
  - 已在项目中要求
  - 仅为某版实现习惯
- 若缺少明确上游依据，则不得直接标记为 `Ready`

这样可以避免“把已有实现合理化为必须需求”。

---

## 15. 立即执行入口

基于当前可获得输入，本轮可以直接启动，不必等待新的正式需求模板。

建议立即按以下顺序执行：

1. 选择一个试点模块
   - 首选 `Gp_NCA95yy` 或你认为更典型的已实现 FC
2. 收集该模块的现实输入
   - 当前接受版 SRS
   - 当前接受版架构文档
   - 当前接受版详细设计文档
   - 对应工程源码
3. 反向抽取首版 requirement bundle
   - 先不追求完美，只追求结构稳定
4. 用源码补 source evidence 和 implemented evidence
5. 导出首版：
   - `requirement_bundle.yaml`
   - `coverage_report.yaml`
   - `architecture_seed.yaml`
   - `test_seed.yaml`
6. 再补 validator 和渲染器

当前仓库内可直接承载执行的入口已经存在：

- `.claude/skills/fc-requirement-workbench/src/fc_requirement_workbench/`

因此本轮不是纯文档规划，后续可以直接沿当前 `src/` 结构演进，而不是重新起一个全新实现。

---

## 14. 最终结论

本轮 `fc-requirement-workbench` 的正确重构方向，不是继续堆规则或继续强化 prompt，而是借鉴详细设计 skill 已验证的方法，完成以下收敛：

```text
grounding first
-> requirement bundle first
-> validation gated
-> markdown as rendered view
-> architecture seed / test seed output
```

重构完成后，需求 skill 应能正式证明四件事：

1. 当前需求覆盖了哪些原始输入，哪些未覆盖，为什么
2. 当前需求哪些已达到可落地、可执行、可验证，哪些没有
3. 当前需求为什么符合公司规范，而不是自由发挥
4. 当前需求如何稳定引导下一步架构生成、详细设计生成和测试用例生成

这才是需求生成 skill 从“能写文档”升级到“能支撑工程链路”的关键分界点。
