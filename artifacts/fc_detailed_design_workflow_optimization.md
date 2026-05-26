# FC 详细设计生成流程优化方案

## 1. 目标

基于 `ckj/SDS` 的目标流程，评估当前详细设计 skill 的真实能力边界，并给出后续优化方向。

这里先固定边界：

- 详细设计 skill 独立存在
- 业务输入以 `需求文档 + 架构文档` 为主
- 触发时机、缺输入提示、生成后的下一步动作由外层引导承担
- 正式主产物文件名统一为 `[FC]_模块详细设计规范.md`

## 2. 先说结论

当前详细设计 skill 的底层方向是对的。

它已经具备：

1. `需求文档 + 架构文档` 驱动的详细设计思路  
2. generation bundle -> detailed design render -> validator 的对象化链路  
3. 面向 Coding 的函数、运行态、配置、Callout、MemMap 细化能力

但它现在更像：

- 实现级详细设计生成器
- 详细设计渲染器
- generation bundle 校验器

还不是完整的：

- `SDS 阶段工作流执行器`

## 3. 当前已经做到什么

### 3.1 输入边界基本合理

`fc-implementation-workbench` 当前 `SKILL.md` 已经把典型输入定义为：

- FC requirement document
- FC architecture document
- chip manual
- coding rules
- existing FC code / reference FC

其中最关键的是：

- requirement
- architecture

这和你希望的边界是一致的。

### 3.2 已有结构化中间层

当前详细设计 skill 已有：

- `build_generation_bundle.py`
- `render_detailed_design.py`
- `validate_generation_bundle.py`
- `validate_fc_docs.py`

说明它不是纯 prompt 拼文档，而是在朝对象化、可校验化演进。

### 3.3 已有可编码粒度

`render_detailed_design.py` 已经能展开：

- 外部接口详细设计
- 内部接口详细设计
- 依赖接口与 Callout
- DET
- 故障处理
- 运行态变量
- 配置设计
- MemMap
- 架构与详细设计覆盖表

这说明它在“内容深度”上比需求阶段成熟，已经接近 Coding 输入。

## 4. 当前最大问题

### 4.1 主流程还不够阶段化

当前 skill 有生成链，但没有完整实现 `ckj/SDS` 里的阶段交付逻辑。

尤其还缺少外显的：

- 输入充分性检查产物
- Gate 记录
- 评审记录
- Coding Ready 结论
- 基线结论

现在能生成详细设计正文，但还不太像一套完整的 SDS 阶段输出。

### 4.2 generation bundle 的入口仍偏“已有三件套再重建”

当前 `build_generation_bundle.py` 更像是：

- 已经有 `SRS + SDD + DD`
- 再反向构建 bundle 做校验和整理

而不是：

- 从 `SRS + SDD`
- 直接进入 SDS 首次生成

这意味着它更擅长“整理与校验现有设计”，还不够擅长“从上游直接起草第一版 SDS”。

### 4.3 输出命名没有完全统一成阶段规范

虽然正文标题可改，但当前 skill 层还没有像需求/架构那样把输出命名正式固化成：

- `[FC]_模块详细设计规范.md`

这次我已经把 `render_detailed_design.py` 的标题和文档元信息改成这套口径，但完整 workflow 级产物命名还没有像架构阶段那样系统化。

## 5. 目标流程需要什么

根据 [ckj/SDS/FC详细设计编写生成工作流.md](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/ckj/SDS/FC详细设计编写生成工作流.md)，详细设计阶段的核心不是只写一份 SDS，而是：

```text
输入收集
-> SDD 输入充分性确认
-> 文件与数据对象设计
-> 接口函数与内部函数设计
-> 状态/配置/错误/安全/资源细化
-> SDD -> SDS 追溯
-> Gate 检查
-> 问题修正
-> SDS 评审与基线
-> 进入 Coding
```

所以它至少需要同时解决三类事：

1. 正文生成  
2. 追溯与校验  
3. 评审与阶段结论

## 6. 建议的输入输出边界

### 6.1 输入

后续统一按下面边界理解：

- 必选输入：`[FC]_软件需求规范.md`
- 必选输入：`[FC]_软件架构设计.md`
- 可选输入：芯片手册、项目编码规范、参考 FC、已有代码

### 6.2 输出

最终正式主产物：

- `[FC]_模块详细设计规范.md`

建议同时生成的配套产物：

- `[FC]_架构详细设计追溯.md`
- `[FC]_Coding就绪检查清单.md`
- `[FC]_详细设计评审记录.md`
- `[FC]_详细设计基线总结.md`

注意：

- 这些配套产物是否全部归档到最终输出目录，可按项目规则决定
- 但从流程角度，它们最好存在

## 7. 最小优化顺序

### 第一阶段：先把输入输出口径固化

先做这几件事：

1. 固化输入边界为 `需求文档 + 架构文档`
2. 固化主产物命名为 `[FC]_模块详细设计规范.md`
3. 固化外层引导说法：没有架构文档不得启动 SDS

这一步我已经先补了第 1 和第 2 条。

### 第二阶段：补流程壳子

在不动核心 detailed-design 内容生成逻辑的前提下，补 workflow-layer 产物：

1. `SDD 输入充分性检查`
2. `Trace_SDD_SDS`
3. `Coding Ready 检查`
4. `Review_SDS`
5. `SDS Baseline Summary`

### 第三阶段：再补首次生成链

真正重要的升级点其实是：

- 从 `SRS + SDD`
- 直接生成第一版 SDS bundle

而不是要求先有一份 DD 文档再回头整理 bundle。

这是当前详细设计 skill 最值得补的一块。

## 8. 对当前详细设计 skill 的最终判断

一句话总结：

> 当前详细设计 skill 已经具备比较强的“实现级内容生成能力”，输入边界也基本合理，但还缺完整的 SDS 阶段流程壳子，尤其缺从 `需求文档 + 架构文档` 直接起草第一版正式 SDS 的顺滑首发链路。

所以后续最优方向不是重写，而是：

> 保留 `bundle -> render -> validate` 核心链，在外层补 `输入充分性 -> 追溯 -> Coding Ready -> 评审 -> 基线`，并统一收口为 `[FC]_模块详细设计规范.md` 这套中文产物规则。
