# FC Detailed Design Skill 设计文档

## 1. 文档目的

本文档用于沉淀当前“详细设计生成 skill”的重构结果，明确：

- 这个 skill 要解决什么问题
- 当前采用了什么设计思路
- skill 内部的核心组成是什么
- 生成流程如何工作
- 当前达到什么状态
- 后续如何继续演进

本文档面向后续 skill 优化、方法复用和能力迁移。

## 2. 背景与目标

在本轮重构前，详细设计生成主要存在以下问题：

- 过度依赖 prompt 直接出 markdown
- 缺少真实工程 grounding
- 缺少结构化中间模型
- 缺少自动校验门禁
- 文档容易“看起来完整”，但实际存在接口漂移、漏项、关系错误

本轮重构的目标不是单纯“把文档写长”，而是把详细设计生成升级成一条更稳定的流水线：

```text
真实工程 grounding
-> 结构化中间模型
-> trace / decision / pattern 收敛
-> 自动校验
-> 正文渲染
```

核心目标可以概括为四点：

1. 生成前有真实工程依据
2. 生成中有结构化对象承载设计信息
3. 生成后有自动校验拦截明显错误
4. 输出正文更贴近工程详细设计，而不是生成过程说明

## 3. Skill 载体

当前详细设计生成能力承载在：

- `.claude/skills/fc-implementation-workbench`

说明：

- 这个目录当前实际承担“详细设计生成 skill”角色
- 后续如果需要命名收敛，可演进为 `fc-detailed-design`
- 当前设计方法已与需求/架构 skill 解耦，可后续逐步上游迁移

## 4. 总体设计思路

### 4.1 核心原则

当前 skill 采用以下原则：

1. `Grounding First`
先基于真实工程样本和配置资产建立参考基线。

2. `Structured Model First`
先生成 bundle / schema 对象，再渲染 markdown。

3. `Traceable Decisions`
对 reserved、pending、降级能力进行 decision / reason 记录。

4. `Validation Gated`
在 bundle 层和 markdown 层都设置自动校验。

5. `Document As Rendered View`
正文是渲染结果，不是唯一真相层。

### 4.2 正文设计原则

当前正文渲染不再追求“暴露 skill 内部过程”，而是强调：

- 面向实现
- 面向功能方案
- 面向接口、内部接口、配置、故障、运行态
- 少暴露内部机制
- 问题可以暴露，但不应伪装为已确认结论

## 5. Skill 内部结构

当前核心结构如下：

```text
.claude/skills/fc-implementation-workbench/
├── SKILL.md
├── scripts/
│   ├── build_generation_bundle.py
│   ├── render_detailed_design.py
│   ├── validate_fc_docs.py
│   └── validate_generation_bundle.py
└── references/
    ├── grounding/
    ├── schemas/
    ├── examples/
    ├── templates/
    ├── detailed_design_quality_contract.md
    ├── bundle_to_dd_mapping.md
    ├── chapter_generation_rules.md
    ├── workflow.md
    └── README.md
```

### 5.1 `grounding/`

职责：

- 存放真实工程基线模块
- 提供 pattern、module facts、selection rules
- 支撑设计风格和结构选择

当前 grounding 基线来源已固定为：

- `Gp_WkUpSrcP`
- `Gp_06_Adc3ph`
- `Gp_TPT1145`
- `Gp_TLE92104`
- `Gp_DRV8889`
- `IoMcu`

以及对应的 `conf` 资产。

### 5.2 `schemas/`

职责：

- 定义 requirement / architecture / detailed design 的结构化对象
- 作为 bundle 中间层的契约

### 5.3 `scripts/build_generation_bundle.py`

职责：

- 从现有输入文档抽取结构化 bundle
- 收敛：
  - trace_ids
  - decision / decision_reason
  - pending_confirm
  - grounding_patterns

### 5.4 `scripts/validate_generation_bundle.py`

职责：

- 校验 bundle 层的结构和关系
- 检查：
  - formal interface coverage
  - trace completeness
  - relationship_links 合法性
  - grounding/module 一致性

### 5.5 `scripts/validate_fc_docs.py`

职责：

- 校验 markdown 正文层
- 检查：
  - external/dependency interface 与 architecture 一致性
  - `关联接口` 字段存在性
  - 未定义引用
  - 明显漂移

### 5.6 `scripts/render_detailed_design.py`

职责：

- 从 detailed design bundle 渲染详细设计正文
- 当前已支持：
  - FC概述
  - 设计输入
  - 功能设计
  - 文件列表设计
  - 单核/多核框架设计
  - 外部接口设计
  - 内部接口设计
  - 依赖接口与Callout设计
  - 状态机设计
  - DET设计
  - 故障处理设计
  - 运行时变量设计
  - 配置宏参设计
  - MemMap设计
  - 代码编写限制要求
  - 架构与详细设计覆盖表

## 6. 正文生成规则体系

为了让正文不再只是“字段平铺”，当前建立了 3 份核心规则文档。

### 6.1 `detailed_design_quality_contract.md`

作用：

- 定义什么叫一份好的 FC 详细设计
- 明确正文定位、粒度边界、禁止事项

强调：

- 面向实现
- 面向编码起步
- 不暴露内部生成痕迹
- 内部接口要规范化
- 功能框图要表达模块调用关系

### 6.2 `bundle_to_dd_mapping.md`

作用：

- 定义 bundle 字段落到正文哪些章节
- 区分：
  - 直接呈现型字段
  - 控制生成型字段

特别强调：

- grounding / conf evidence 用于控制生成，不直接写进正文
- 配置点可由 config 类 requirement 抽出
- 待确认内容不再单独作为主章节

### 6.3 `chapter_generation_rules.md`

作用：

- 逐章定义“怎么写”
- 控制结构、粒度、图示、章节保留与删除

本轮重构后，已根据评审意见调整了：

- 删除 `待确认项` 主章节
- `功能框图` 改为模块调用链视角
- `配置参数` 改为面向 `Cfg.c` 需要配置的点
- `内部控制流摘要` 删除
- `代码编写限制要求` 替代 `编码起步建议`
- 新增 `架构与详细设计覆盖表`

## 7. 当前正文结构

当前渲染器输出的正文主结构为：

1. `FC概述`
2. `设计输入`
3. `功能设计`
4. `文件列表设计`
5. `单核/多核框架设计`
6. `外部接口设计`
7. `内部接口设计`
8. `依赖接口与Callout设计`
9. `状态机设计`
10. `DET设计`
11. `故障处理设计`
12. `运行时变量设计`
13. `配置宏参设计`
14. `MemMap设计`
15. `代码编写限制要求`
16. `架构与详细设计覆盖表`

说明：

- 这套结构已明显偏向“工程详细设计交付文档”
- 不再偏向“生成过程说明文档”

## 8. 功能框图设计策略

本轮针对功能框图做了专门收敛。

当前规则要求：

- 前后都以模块为主视角
- 中间在当前模块内展开调用链
- 调用链最多 5 层：

```text
外部模块
-> 外部接口
-> 内部接口
-> 依赖接口
-> 外部依赖模块
```

- 相同 external / internal / dependency 节点应合并
- 不再重复画多个同名接口节点

这套策略比早期“模块总览图”更接近真实实现关系，也更符合详细设计文档用途。

## 9. 配置参数设计策略

当前配置章节分成两部分：

### 9.1 配置宏参

来源：

- `architecture.config_items`

用于表达：

- formal 配置宏
- reserved 配置开关

### 9.2 配置参数

来源：

- 优先来自 grounding 模块真实 `Cfg.c` 抽取结果
- 无法抽到真实 `Cfg.c` 时，退化使用 `requirements` 中 `category == config` 的条目

当前能力边界：

- 已能稳定抽取 grounding 模块中的真实配置对象
- 已能识别：
  - 顶层配置容器
  - per-core / per-chip 配置数组
  - 关键字段
  - 配置对象维度
- 当前已支持的真实样本包括：
  - `Gp_TPT1145_Cfg.c`
  - `Gp_TLE92104_Cfg.c`
  - `Gp_DRV8889_Cfg.c`
- 当前仍属于 V1：
  - 主要基于 `Cfg.c` 结构做对象级抽取
  - 还没有深入到“字段业务含义完全自动解释”
  - 也还没有把目标模块自身 `Cfg.c` 与新生成 DD 做一一回填

所以当前正文已从“纯配置点清单”升级为“参考模块真实配置对象 + 关键配置点”表达，例如：

- `Gp_TPT1145_PnRegCfg_lcatst`
- `Gp_TPT1145_SpiCfg_lcatst`
- `Gp_TLE92104_cfgChipCore0_lcatst`
- `Gp_DRV8889_cfgChipCore0_lcatst`
- `Gp_DRV8889_cfgCont_vcatst`

这让 `15.2 配置参数` 已经能体现“真实 `Cfg.c` 里到底有哪些对象和字段需要配置”，不再只停留在需求侧口径。

## 10. 校验策略

当前 skill 的校验分两层：

### 10.1 Bundle 层

目标：

- 防止结构不完整
- 防止 formal interface 漏项
- 防止 trace / relationship 不闭合

### 10.2 Markdown 层

目标：

- 防止 architecture 与正文漂移
- 防止 `关联接口` 缺失
- 防止未定义对象引用

当前策略不是“自动修复所有问题”，而是：

- 问题要暴露
- 问题不能被隐藏
- 满足基本门禁后，可以继续进入 coding

## 11. 当前达成状态

如果严格按成熟度判断，当前详细设计 skill 已达到：

- `可稳定生成第一版工程风格详细设计`
- `可通过结构化 bundle 和 markdown 校验`
- `可支持继续 coding`

当前可以给出的工程判断是：

- grounding 已可用
- structured bundle 已可用
- validator 已可用
- renderer 已可用
- 正文规则体系已建立

仍未完全成熟的部分主要是：

- 多模块 regression 覆盖还不够
- `Cfg.c` 对象抽取已可用，但语义标签和目标模块回填还不够深
- 某些复杂模块上的状态机 / 故障分型还需更多样例验证

## 12. 后续建议

下一步建议按以下顺序推进：

1. 稳定当前 detailed design renderer
2. 增加多个真实模块回归样例
3. 补深 `Cfg.c` 配置对象语义抽取与目标模块映射能力
4. 复用这套方法到 requirement / architecture skill

其中迁移时应优先保留的方法，不是某个章节模板，而是这套方法论：

- grounding first
- structured model first
- validation gated
- document as rendered view

## 13. 结论

本轮重构之后，详细设计生成 skill 已经从“会生成文档”升级成“具备工程方法和门禁的生成系统”。

更准确地说：

- 它已经不再只是 prompt 技巧集合
- 它已经具备结构化建模、真实工程参考、自动校验和正文渲染能力
- 它已经能产出可用于继续 coding 的详细设计初稿

这意味着后续对需求生成和架构生成的优化，也不应再走“直接写文档”的老路，而应逐步复用这套设计方法。
