---
name: fc-requirement-workbench
description: "用于把芯片手册、项目需求、参考 SRS 与追溯材料整理为结构化、可校验、可追溯的软件需求与 SRS 输出。该 skill 只负责需求生成，不负责后续架构、详细设计、代码骨架或测试资产生成。"
---

# FC 需求工作台

## 1. 定位

这是一个**需求生成 skill**，负责把输入资料转成工程化的软件需求与 SRS。

唯一正式生成链路：

```text
输入资料
→ 文档解析与语义切块
→ 特征提取
→ 候选需求映射
→ 候选压缩与补料分析
→ 需求规划
→ 规则校验
→ Requirement 构建
→ SRS 渲染
→ 追溯与覆盖输出
```

## 2. 能做什么

- 解析 Datasheet、项目需求、参考 SRS、Trace 表、源码片段和配置片段
- 提取功能、接口、状态、配置、时序、诊断、安全、限制条件
- 区分“芯片能力”和“项目约束”，再生成最终需求
- 输出需求对象、SRS、验证意图、追溯矩阵、覆盖矩阵
- 对需求做完整性、一致性、约束、归属、依赖、追溯校验

## 3. 明确不做什么

- 不做 Requirement → Architecture 映射
- 不做 Architecture → Implementation 映射
- 不生成 C/H 代码、配置文件、接口实现或测试骨架
- 不替代人工评审，也不做自动发布
- 不凭空确认没有来源证据的需求

## 4. 核心原则

- 先抽取语义对象，再写 SRS 句子
- 每条需求都要尽量具备来源、边界、状态和验证意图
- 模糊词必须改写或标记为待澄清，例如“正常”“稳定”“快速”“多个”
- 没有证据的内容必须降级为 `needs_source` 或 `open_issue`
- SRS 只描述软件“应做什么”，不直接写实现方案
- 方案升级时，需要同步更新 `references/architecture-design.md`

## 5. 规则分工

- `references/authoring-standard.md`
  只管 SRS 的写法、章节组织、字段呈现和版式约束
- `references/construction-rules.md`
  只管需求条目的最小字段、缺失处理和构建完整性
- `references/calibration-rules.md`
  只管本地写作偏好、粒度校准和历史案例经验
- `references/srs-output-template.md`
  只管输出章节结构和渲染形态

优先级：

1. 字段完整性与缺失处理看 `construction-rules.md`
2. 文档怎么写看 `authoring-standard.md`
3. 风格与边界倾向看 `calibration-rules.md`
4. 流程边界与加载策略看本 `SKILL.md`

## 6. 输入范围

适用输入：

- 芯片手册、寄存器说明、模块需求、项目约束
- 参考 SRS、Trace 表、测试材料、配置文件、源码片段
- CAN、LIN、SPI、PWM、GPIO、MCU 外设及 FC 模块相关资料

重点优先阅读的内容：

- Operating Modes
- State Machine
- Pin Description
- Timing
- Diagnostic / Fault
- Configuration / Register
- Wake / Sleep

输入门禁：

- 用户可以提供”需求输入文件夹”或直接提供某个需求输入文件
- 实际启动需求生成前，输入集合中至少需要包含以下三者之一：
  - 芯片资料
  - 原始开发需求
  - 需求文档
- 三者存一即可启动生成；输入越完整，生成质量越高

## 7. 最小加载策略

默认按最小集合加载：

1. 用户当前提供的输入资料
2. 本 `SKILL.md`
3. `references/srs-output-template.md`
4. 当前任务所需的规则文件
5. 只有在需要稳定结构化对象时，再读取 `references/semantic-model.md`

只有在需要判断 MainFunction、接口分类、多核/诊断/状态机等平台规范时，再读取：

- `references/aurix2g-normative-patterns.md`
- `references/rule-engine.md`
- `references/feature-extraction-design.md`
- `references/extraction-rules.md`

## 8. 执行步骤

### 8.1 输入解析

- 解析标题、表格、代码块、注记、图片标记和章节结构
- 先建立阅读地图，再抽取高价值章节

### 8.2 切块与索引

- 建立 `chapter_chunk`、`table_chunk`、`state_chunk`、`interface_chunk`、`validation_chunk`
- 为模式、时序、诊断、接口、配置、状态、安全、追溯建立索引

### 8.3 特征提取与候选映射

- 分别提取身份、能力、引脚、接口、寄存器、状态、诊断、时序、电气和项目映射
- 一个输入特征可以映射到多个候选需求，但每条候选都必须说明映射理由、证据强度、软件动作、缺失输入和 Ready 条件

### 8.4 候选压缩与需求规划

- 按行为族聚类，输出 Keep/Merge 决策与补料清单
- 按能力域规划 SRS 条目数量、合并策略、编写策略和验证策略
- 规划阶段的中间态不能直接泄露到最终 SRS 正文

### 8.5 规则校验

生成 SRS 前至少检查：

- 完整性
- 一致性
- 约束满足
- 接口/信号归属
- 依赖存在性
- 追溯与验证意图

### 8.6 SRS 构建

```text
Requirement Semantic Object
→ Requirement Pattern
→ Requirement Instance
→ SRS Section
```

默认 ID 规则：

```text
SRS-{MODULE}-{TYPE}-{NNNN}
```

## 9. 输出物

默认只输出需求层产物：

- SRS Markdown / HTML / DOCX
- Review 需求评审记录
- Check 需求检查清单
- Trace 追溯矩阵
- Source → Requirement Trace Matrix
- Requirement → Verification Intent Coverage Matrix
- ASPICE Evidence Summary

需要中间产物时，再显式启用：

- `--with-intermediates`
- `--emit features-markdown|candidates-markdown|pruning-markdown|planning-markdown`

输出路径与命名规则：

- 需求生成结果不得写回 skill 目录内部
- 如果用户显式指定输出路径，按用户路径输出
- 如果用户未指定输出路径，则默认在输入文件所在目录或输入文件夹下创建：

```text
Output/<FC_SHORT_NAME>/Doc/SRS/
```

- 正式需求文档文件名必须固定为：

```text
[FC] 软件需求规范.md
```

其中 `[FC]` 为当前模块短名或模块名，不使用下划线版本文件名作为正式输出名。

- 每次正式需求生成必须同步输出以下评审与追溯产物，`xxx` 与正式 SRS 的 `[FC]` 保持一致：

```text
Review_xxx_软件需求规范.md
Check_xxx_软件需求规范.md
Trace_xxx_软件需求规范.md
```

- `Review_xxx_软件需求规范.md` 记录需求评审结论、Gate 结果、遗留开放项和是否允许进入 SDD。
- `Check_xxx_软件需求规范.md` 记录需求检查清单、检查项明细、问题闭环表和发布包完整性。
- `Trace_xxx_软件需求规范.md` 记录 Source → Requirement、Requirement → Verification Intent、Raw Requirement Coverage 与 ASPICE Evidence Summary。

## 10. 使用边界提醒

- 生成结果默认是 Draft，用于评审和补料，不等于需求已 Ready
- 当外部芯片驱动是否需要 `MainFunction` 不明确时，优先查 `references/aurix2g-normative-patterns.md`
- 如果需求来源之间有冲突，优先保留显式项目输入，并把冲突记录为问题项
