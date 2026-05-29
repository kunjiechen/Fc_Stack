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
→ 芯片视图提取检测
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
- 当输入包含芯片手册时，自动提取芯片信息为三个下游视图，供架构生成、详细设计生成和代码生成阶段直接消费

## 3. 明确不做什么

- 不做 Requirement → Architecture 映射
- 不做 Architecture → Implementation 映射
- 不生成 C/H 代码、配置文件、接口实现或测试骨架
- 不替代人工评审，也不做自动发布
- 不凭空确认没有来源证据的需求
- 芯片视图提取只对原始信息做重组和呈现，不做代码常量的编写或命名

## 4. 核心原则

- 先抽取语义对象，再写 SRS 句子
- 每条需求都要尽量具备来源、边界、状态和验证意图
- 模糊词必须改写或标记为待澄清，例如“正常”“稳定”“快速”“多个”
- 没有证据的内容必须降级为 `needs_source` 或 `open_issue`
- SRS 只描述软件“应做什么”，不直接写实现方案

## 5. 规则分工

- `references/architecture-design.md`
  唯一的详细架构与方案参考，描述完整阶段方案、引入原因和维护要求。本文档为高层入口，具体阶段实现参见该文件。
- `references/authoring-standard.md`
  只管 SRS 的写法、章节组织、字段呈现和版式约束
- `references/construction-rules.md`
  只管需求条目的最小字段、缺失处理和构建完整性
- `references/calibration-rules.md`
  只管本地写作偏好、粒度校准和历史案例经验
- `references/srs-output-template.md`
  只管输出章节结构和渲染形态
- `references/chip-view-extraction-rules.md`
  只管芯片手册两视角提取的触发条件、提取域定义、字段 schema、递进关系和输出约束

优先级：

1. 字段完整性与缺失处理看 `construction-rules.md`
2. 文档怎么写看 `authoring-standard.md`
3. 风格与边界倾向看 `calibration-rules.md`
4. 芯片视图提取的触发、域定义和输出约束看 `chip-view-extraction-rules.md`
5. 流程边界与加载策略看本 `SKILL.md`

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

当输入包含芯片手册且 chip view 文件缺失时，额外加载：

- `references/chip-view-extraction-rules.md`

只有在需要判断 MainFunction、接口分类、多核/诊断/状态机等平台规范时，再读取：

- `references/aurix2g-normative-patterns.md`
- `references/rule-engine.md`
- `references/feature-extraction-design.md`
- `references/extraction-rules.md`

## 8. 执行步骤

**整个需求生成流水线由 `cli.py` 确定性执行，LLM 不手工实现流水线步骤。**

### 8.0 前置校验（阻断性）

在调用 CLI 之前，必须确认用户已提供以下三项工程上下文信息：

| # | 信息 | CLI 参数 | 示例 |
|---|------|---------|------|
| 1 | **FC 驱动名称** | `--module` | `Gp_NCA9539` |
| 2 | **功能安全等级** | `--safety-level` | `QM` / `ASIL-B` / `ASIL-D` |
| 3 | **单核/多核控制** | `--core-mode` | `single` / `multi` |

**校验规则**：

- 从用户消息中主动提取以上三项（格式不定，可在对话中自然描述）
- 任一项缺失 → **阻断，不允许继续向下执行**
- 向用户清晰报告缺失项并询问补充
- 三项目标都确认后，继续 §8.1

CLI 侧也会做硬校验：缺少任一项则打印错误信息并退出。

### 8.1 调用 CLI

根据输入类型组装命令并执行：

```bash
python -m fc_requirement_workbench.cli <输入文件或目录> \
  --module <FC_MODULE> \
  --safety-level <QM|ASIL-A|ASIL-B|ASIL-C|ASIL-D> \
  --core-mode <single|multi> \
  [--raw-input <原始需求文件>] \
  [--constraints <项目约束文件>] \
  [--chip-view-dir <芯片视图输出目录>] \
  [--output-dir <SRS 输出目录>]
```

**参数说明**：

| 参数 | 必填 | 说明 |
|------|------|------|
| `input` | 是 | 芯片手册文件或输入目录路径 |
| `--module` | **是** | FC 模块短名，如 `Gp_NCA9539` |
| `--safety-level` | **是** | 功能安全等级：`QM` / `ASIL-A` / `ASIL-B` / `ASIL-C` / `ASIL-D` |
| `--core-mode` | **是** | 单核/多核控制模式：`single` / `multi` |
| `--raw-input` | 否 | 原始开发需求文件 |
| `--constraints` | 否 | 项目约束/需求文档 |
| `--chip-view-dir` | 否 | 芯片视图输出目录 |
| `--output-dir` | 否 | SRS 输出目录 |
| `--skip-chip-view` | 否 | 跳过芯片视图生成 |
| `--source-root` | 否 | 项目源码根目录（用于接地增强，非必填） |

CLI 会自动完成：输入解析 → 切块索引 → 特征提取 → 候选映射 → 候选压缩 → 需求规划 → 规则校验 → SRS 构建 → 追溯覆盖。**LLM 不手工执行这些步骤。**

### 8.2 解析 CLI 输出

CLI 在 stdout 输出 JSON summary。关键字段：

| 字段 | 用途 |
|------|------|
| `output_dir` | SRS 产物目录 |
| `chip_view` | 芯片视图生成状态 |
| `requirement_count` | 需求条目数 |
| `gate_status` | 各 Gate 通过状态 |
| `open_items` | 开放项数量 |
| `files` | 生成的所有文件列表 |
| `assistant_reply` | 给用户的下步操作提示 |

### 8.3 审查与补充

CLI 执行完成后，LLM 的职责：

1. **检查 `chip_view` 状态**：
   - `chip_view.generated: true` → 打开 ChipView 文件，搜索 `<!-- LLM_SUPPLEMENT -->` 标记，根据原始芯片手册补充完善，完成后移除标记
   - `chip_view.skipped` → 两个文件已存在，无需操作
   - `chip_view.error` → 提取异常，报告错误信息

2. **检查 `gate_status`**：如有未通过的 Gate，指出具体检查项

3. **呈现 `assistant_reply`**：包含下一步操作建议

4. **无需 LLM 处理的产物**（CLI 已确定性生成）：
   - `<FC>_软件需求规范.md` — SRS 正式文档
   - `Check_<FC>_软件需求规范.md` — 检查清单
   - `Review_<FC>_软件需求规范.md` — 评审记录
   - `Trace_<FC>_软件需求规范.md` — 追溯矩阵
   - `<FC>_SRS输入资料索引.md` — 来源索引
   - `<FC>_SRS来源内容抽取表.md` — 来源抽取
   - `<FC>_SRS需求推导矩阵.md` — 推导矩阵
   - `<FC>_SRS开放项登记表.md` — 开放项
   - `<FC>_SRSGate自检报告.md` — Gate 报告
   - `<FC>_SRS操作步骤.md` — 操作步骤
   - `<FC>_SRS生成后引导.md` — 生成后引导
   - `<FC>_SRS下一步操作提示.md` — 下一步提示

## 9. 输出物

### 9.1 标准产物（CLI 确定性生成）

每次需求生成输出以下文件（均由 `cli.py` 自动生成，LLM 不需要手工编写）：

| 文件 | 内容 |
|------|------|
| `<FC>_软件需求规范.md` | 正式 SRS 文档 |
| `Review_<FC>_软件需求规范.md` | 需求评审结论、Gate 结果、遗留开放项 |
| `Check_<FC>_软件需求规范.md` | 需求检查清单、检查项明细、问题闭环表 |
| `Trace_<FC>_软件需求规范.md` | Source→Requirement、Requirement→Verification、ASPICE Evidence |
| `<FC>_SRS输入资料索引.md` | 输入资料来源索引 |
| `<FC>_SRS来源内容抽取表.md` | 从来源中抽取的内容记录 |
| `<FC>_SRS需求推导矩阵.md` | 特征→需求的推导关系 |
| `<FC>_SRS开放项登记表.md` | 待澄清/待补料项 |
| `<FC>_SRSGate自检报告.md` | Gate 1-6 自检结果 |
| `<FC>_SRS操作步骤.md` | 操作步骤记录 |
| `<FC>_SRS生成后引导.md` | 生成后下一步引导 |
| `<FC>_SRS下一步操作提示.md` | 精简的下一步操作提示 |

### 9.2 芯片视图产物（条件输出）

当输入包含芯片手册时，额外输出：

| 文件 | 服务阶段 |
|------|---------|
| `<FC>_芯片架构输入.md` | 架构生成 |
| `<FC>_芯片详细设计输入.md` | 详细设计 + 代码生成 |

视图文件与标准产物相互独立：视图缺失不影响标准产物输出，标准产物缺失不影响视图输出。

### 9.3 输出路径

- 需求生成结果不得写回 skill 目录内部
- 如果用户显式指定 `--output-dir` / `--chip-view-dir`，按用户路径输出
- 如果用户未指定，默认在输入文件所在目录下创建：

```text
<input_root>/Output/<FC>/Doc/SRS/          # 12 个标准产物
<input_root>/Output/<FC>/Doc/ChipViews/    # 2 个芯片视图产物（条件输出）
```

## 10. 使用边界提醒

- 生成结果默认是 Draft，用于评审和补料，不等于需求已 Ready
- 当外部芯片驱动是否需要 `MainFunction` 不明确时，优先查 `references/aurix2g-normative-patterns.md`
- 如果需求来源之间有冲突，优先保留显式项目输入，并把冲突记录为问题项
- 芯片视图存在时，下游阶段应优先使用对应视图而非全量芯片手册；视图缺失时下游阶段降级为从全量芯片手册自行提取
