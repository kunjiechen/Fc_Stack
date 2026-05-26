# FC 架构生成流程优化方案

## 1. 目标

基于 `ckj/SDD` 中的目标流程，评估当前 `fc-architecture-workbench` 的真实能力边界，并给出“下一步架构生成流程怎么优化”的方案。

这里的重点不是单纯让架构文档“写得更长”或“多出几张表”，而是让架构生成真正具备：

- 明确的阶段入口
- 稳定的对象化中间层
- 可解释的设计决策
- 可执行的评审闭环
- 可进入 SDS 的正式交接能力

这里先明确边界：

- `需求 skill` 和 `架构 skill` 是独立 skill
- `架构 skill` 的业务输入就是需求文档
- “什么时候启动架构阶段、用户下一步怎么做、缺输入时怎么提示” 统一由外层引导承担
- 不在架构 skill 内部假定需求 skill 的 session、状态文件或内部数据结构

---

## 2. 先说结论

当前架构 skill 的底层能力已经具备三块比较扎实的基础：

1. **对象化基础**  
   有 `architecture seed -> freeze bundle -> render -> validate -> release gate` 这一条真实链路。

2. **架构规则基础**  
   有较成熟的接口、配置、依赖、MemMap、风险、发布状态规则。

3. **发布判定基础**  
   有 `Draft / Released`、`Quick Draft / Formal Draft / Released`、风险表、release gate 评估。

真正不足的不是“不会生成”，而是“不会作为 SDD 阶段流程来运行”。

也就是说，现在它更像：

- 架构对象生成器
- 架构文档渲染器
- 架构对象校验器
- 架构发布判断器

但还不是：

- 完整的 `SDD 阶段工作流执行器`

---

## 3. 目标流程要求什么

根据 [ckj/SDD/FC架构设计编写生成工作流.md](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/ckj/SDD/FC架构设计编写生成工作流.md)，架构阶段需要的不是一份文档，而是一整套阶段交付。

至少要有：

1. 架构输入索引
2. SRS 输入充分性确认
3. 模块职责与边界设计
4. 接口、数据流、状态机、配置、依赖设计
5. 时序、资源、诊断、安全、多核与集成设计
6. SRS -> SDD 追溯
7. Gate1 ~ Gate7 检查
8. 问题修正与开放项闭环
9. 实际操作步骤
10. CHECK 清单
11. SDD 评审记录
12. 基线发布与进入 SDS 的结论

所以架构阶段本质上是：

```text
输入审查
-> 架构设计
-> 追溯验证
-> 质量门禁
-> 人工评审
-> 基线交接
```

---

## 4. 当前 skill 真正已经做到什么

## 4.1 做到的部分

### 4.1.1 执行深度控制

当前 skill 已经有：

- `L1 Fast`
- `L2 Standard`
- `L3 Deep Review`

这意味着它已经具备“不同复杂度下做不同分析深度”的基础。

这很重要，因为架构阶段最怕两件事：

- 简单模块过度分析
- 复杂模块分析不够

### 4.1.2 输出模式控制

当前 skill 已经区分：

- `Validated Concise Architecture Output`
- `Full Debug Architecture Output`
- `Quick Draft`
- `Formal Draft`
- `Released`

这比需求阶段成熟，因为它已经开始区分：

- 给评审人看的正式架构输出
- 给调试/优化 skill 本身用的 debug 输出

### 4.1.3 架构对象冻结能力

从脚本链路看：

- `build_architecture_freeze_bundle.py`
- `render_architecture_objects.py`
- `validate_architecture_objects.py`
- `evaluate_architecture_release_gate.py`

当前已经不是简单从 prompt 直接拼 Markdown，而是开始围绕对象做冻结、校验和发布判断。

这说明架构 skill 的正确演进方向已经定了：

- **对象优先，不是 Markdown 优先**

### 4.1.4 发布 Gate 雏形已具备

当前 release gate 脚本已经会检查：

- 是否还有 `pending_confirm`
- 是否还有 `reserved`
- 风险项是否仍是 `待评审/待修改`
- formal 对象是否缺少 rule evidence
- module grounding 是否齐

这已经很接近 `Gate7-SDD基线发布` 的底层判据了。

---

## 4.2 没做到的部分

### 4.2.1 缺少真正的“架构阶段入口”

现在架构 skill 可以从 requirement 或 architecture draft 开始推理，但它没有严格实现：

- `SRS 输入充分性确认`
- `架构输入索引`
- 基于需求文档的 `输入不充分时阻断/条件进入规则`

结果就是：

- skill 能生成架构
- 但不能仅凭需求文档明确告诉外层“现在该不该开始架构阶段”

这部分不应该继续塞回架构 skill 内部，而应该由外层流程引导解决。

### 4.2.2 缺少 SRS -> SDD 的正式追溯交付

当前 skill 很强调 coverage，但更偏对象级或摘要级。

而 `ckj/SDD` 期望的是明确产物：

- `Trace_SRS_SDD_[FC].md`
- `需求-架构设计追溯矩阵_[FC].html`

也就是说：

- 当前有“验证思想”
- 但缺“流程交付件”

### 4.2.3 缺少阶段化三件套

当前架构阶段还缺明显的：

- `Operation_Steps_SDD_[FC].md`
- `CHECK_SDD_[FC].md`
- `Review_SDD_[FC].md`

没有这三件套，评审和交接永远像“某次 AI 生成结果”，而不是“正式阶段输出”。

### 4.2.4 缺少多轮评审状态持久化

架构 skill 现在有风险表和 Draft/Released 逻辑，但还没有形成面向 SDD 阶段的独立评审记录闭环。

所以现在它可以：

- 生成 draft
- 生成风险表
- 根据风险判断是否 released

但它还不擅长：

- 记录第 1 轮评审改了什么
- 第 2 轮关闭了哪些风险
- 哪些风险被接受遗留
- 哪一轮达到了架构基线

### 4.2.5 缺少进入 SDS 的交接摘要

当前 skill 可以导出 freeze bundle，但从流程视角还缺一个人可读的交接件，比如：

- `SDD_Baseline_Summary_[FC].md`

内容应该明确：

- 哪些 SRS 已被架构覆盖
- 哪些风险保留
- 哪些对象已冻结为正式输入
- SDS 设计必须继承哪些约束

---

## 5. 当前最大结构问题

如果只挑一个最大问题，我会认为是：

### 当前架构 skill 是“对象与规则导向”，不是“阶段导向”

它的强项是：

- 想清楚应该有什么外部接口
- Callout 怎么抽象
- 配置宏怎么分层
- MemMap 怎么判
- 风险怎么挂出来

但 `ckj/SDD` 需要的还包括：

- 当前这次架构工作基于哪份需求文档开始
- 从需求文档中哪些输入仍然缺
- 为什么外层流程允许现在开始架构
- 这次架构输出是否足以进入 SDS
- 本轮评审如何闭环

所以优化方向不该是“继续往 SKILL.md 加更多规则”，也不该是“让架构 skill 直接依赖需求 skill”，而该是：

- **在现有对象链外面补一层阶段编排层**

---

## 6. 下一步优化的总原则

## 6.1 不重写核心对象链

不要推翻：

- architecture seed
- freeze bundle
- render
- validate
- release gate

这些已经是架构 skill 最值钱的部分。

## 6.2 先补阶段包装，再补推理细节

优先级应该是：

1. 阶段入口和输出统一
2. 评审和 Gate 统一
3. 追溯交付件补齐
4. 最后再优化对象抽取质量

原因很简单：

- 没有阶段包装，抽取得再漂亮也只是“生成器”

## 6.3 让冻结包成为阶段中枢

建议后续把 freeze bundle 定位成：

- 架构阶段的结构化中枢产物

而不是仅仅一个脚本中间文件。

它应该成为：

- SDD 正文的来源
- Release Gate 的输入
- SDS 阶段的正式结构化输入
- Trace 和 Review 的证据载体

---

## 7. 下一步优化方案

## 7.1 Phase A：补齐架构阶段流程外壳

这是最优先的。

建议新增一个 `architecture workflow wrapper`，不碰核心对象推理，只负责阶段运行。

### 应新增能力

1. `Architecture_Input_Index_[FC].md`
2. `SRS_Input_Readiness_[FC].md`
3. `Trace_SRS_SDD_[FC].md`
4. `需求-架构设计追溯矩阵_[FC].html`
5. `Operation_Steps_SDD_[FC].md`
6. `CHECK_SDD_[FC].md`
7. `Review_SDD_[FC].md`
8. `SDD_Baseline_Summary_[FC].md`

### 预期收益

- 先把“能生成”升级成“能交付阶段产物”

---

## 7.2 Phase B：建立架构阶段状态机

建议新增外层状态，不替代当前 `Draft/Released`，而是并行存在。

### 建议状态

| 状态 | 含义 |
| --- | --- |
| `SddInputChecking` | 正在检查 SRS 输入是否足够 |
| `SddDrafting` | 正在生成/修订架构 |
| `SddInReview` | 已提交架构评审 |
| `SddConditionallyAccepted` | 条件通过，可进入 SDS |
| `SddBaselined` | 架构基线发布 |
| `SddRework` | 退回返工 |

### 与现有 `Draft/Released` 的关系

- `Draft/Released` 保留作为文档/对象层状态
- `SddInReview/SddBaselined` 作为流程层状态

这样可以避免：

- `Draft` 既表示“文档未发布”，又表示“流程还没评审”的混乱

---

## 7.3 Phase C：补多轮评审 session

但这个 session 如果存在，也应视为架构 skill 自己的评审记录，不应依赖需求 skill。

架构阶段建议也加：

- `.fc-sessions/<module>/architecture-session.json`

### 至少记录

- 当前架构版本
- 当前 round
- 输入摘要
- 风险项状态变化
- 本轮修改内容
- 发布结论

### 这样做的价值

架构评审往往比需求评审更容易多轮拉扯，因为：

- 风险项多
- 设计折中更多
- “接受遗留”比需求更常见

没有 session，很难把“为什么这版可以过”说清楚。

---

## 7.4 Phase D：把风险表升级成正式评审驱动器

现在风险表已经存在，但它更像输出内容的一部分。

下一步应把它变成：

- **架构评审驱动器**

### 建议加强

1. 风险项自动映射到：
   - release blocker
   - implementation blocker
   - incremental follow-up

2. 风险项自动映射到：
   - 影响章节
   - 影响对象
   - 影响的 SRS ID

3. 风险项关闭时自动更新：
   - review record
   - release gate
   - baseline summary

这样风险不只是“表里一行字”，而是整个阶段推进的主控器。

---

## 7.5 Phase E：把 SRS -> SDD trace 从“验证”升级成“正式交付”

这是架构阶段最需要补的硬交付。

### 建议输出双形态

1. `Trace_SRS_SDD_[FC].md`
   - 给评审、版本管理、diff 看

2. `需求-架构设计追溯矩阵_[FC].html`
   - 给浏览、筛选、评审会议看

### 字段建议统一

- SRS ID
- SRS 标题
- 覆盖的架构对象
- 覆盖状态
- 是否进入 SDS
- 风险/备注

### 核心目标

后续任何人都能回答：

- 这条 SRS 在架构里到底落哪了

---

## 7.6 Phase F：把 freeze bundle 真正作为 SDS 入口

当前 freeze bundle 已经具备很强的潜力。

建议下一步正式规定：

- SDS 阶段默认只接受 released 或 conditionally accepted 的 architecture freeze bundle

### 这样做的好处

1. SDS 不再直接从 Markdown 猜设计
2. 正式对象边界更稳定
3. 架构规则和 SDS 规则能更好串起来

### 需要补的内容

- 在 baseline summary 里明确 freeze bundle 路径
- 在 release gate 里输出“是否可进入 SDS”

---

## 8. 推荐的实施顺序

## 第一优先级

先做外壳，不动核心推理：

1. `Architecture_Input_Index`
2. `Trace_SRS_SDD`
3. `CHECK_SDD`
4. `Review_SDD`
5. `Operation_Steps_SDD`

## 第二优先级

再做流程状态和评审 session：

1. `SddDrafting / SddInReview / SddConditionallyAccepted / SddBaselined`
2. `architecture-session.json`

## 第三优先级

最后做对象链深化：

1. freeze bundle 字段收敛
2. HTML trace matrix
3. 风险项自动闭环
4. SDS 入口固化

---

## 9. 对当前架构 skill 的最终判断

如果从“下一步值不值得继续优化”这个问题来看，答案是很值得，而且方向已经比较明确。

当前它不是从 0 到 1 的阶段，而是处在：

- **对象能力已经到位，流程化还没补完**

这其实是一个好位置，因为说明：

- 不需要推翻重来
- 也不需要再去做一个纯 prompt 的架构生成器

真正应该做的是：

- 把 `fc-architecture-workbench` 从“强生成器”升级成“强阶段执行器”

一句话总结下一步：

> 保留现有 `seed -> freeze -> render -> validate -> release gate` 核心链路，在其外层补 `基于需求文档的输入检查 -> 追溯交付 -> Gate 记录 -> 评审记录 -> 基线交接`，并把“何时触发、如何提示用户下一步”交给外层引导，让架构 skill 在独立边界内承担 `ckj/SDD` 定义的 SDD 设计职责。
## 6.3 输入边界固定为“需求文档”

后续架构阶段统一按下面的输入边界执行：

- 必选输入：`SRS_[FC]` 或 `[FC]_软件需求规范.md`
- 可选输入：用户额外提供的架构约束说明、既有架构草稿
- 非架构 skill 输入：需求 skill 的内部 session、内部状态文件、内部命令

也就是说，架构 skill 不负责理解“需求阶段内部怎么跑出来的”，它只负责：

- 读取需求文档
- 基于需求文档做 SRS 输入充分性判断
- 生成 SDD 与配套追溯/评审产物
- 明确告诉外层当前是 `Draft / Conditional / Baseline Ready`

## 6.4 引导责任在外层

外层引导至少要承担三件事：

1. 判断是否允许启动架构 skill  
   核心依据是：是否已经有需求文档。

2. 在触发前明确提示用户输入情况  
   例如：
   - 已有需求文档，可启动架构生成
   - 无需求文档，不允许启动架构生成
   - 需求文档存在但开放项较多，只能生成 Draft/Conditional 架构

3. 在生成后明确提示用户下一步  
   例如：
   - 需要补需求，返回需求阶段
   - 需要继续评审架构，进入 Review_SDD
   - 可条件进入 SDS
   - 可正式基线
