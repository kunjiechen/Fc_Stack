---
name: fc-implementation-workbench
description: "用于设计、评审和整理 FC 实现层详细设计，包括单核或多核框架、配置布局、DET 流程、状态机、内部函数、运行时数据、故障处理以及面向编码的设计骨架。"
---

# FC 实现工作台

## 1. 定位

这是一个**实现层详细设计 skill**，负责把需求、架构与参考工程约束转成可落地的详细设计方案。

核心链路：

```text
需求 / 架构 / 参考 FC / 芯片约束
→ Grounding 选择
→ 结构化设计对象
→ 详细设计生成
→ 校验
→ 细化与评审
```

它不是代码自动驾驶，也不是需求生成器。

## 2. 适用范围

适合处理：

- FC 详细设计生成与重构
- 面向编码的框架设计
- `Cfg.h / CfgData.h / Cfg.c / Callout / MemMap` 设计
- 单核、多核、per-core 运行时容器设计
- `DET`、状态机、故障流、复位与 `NoClear` 设计
- 内部函数拆分、接口子功能分解、执行步骤设计
- 基于真实项目 FC 的实现风格归一化

## 3. 明确边界

可以产出：

1. 实现摘要
2. 正式详细设计 Markdown
3. 编码脚手架计划
4. 实现评审结论
5. 面向代码生成的设计对象

不能凭空捏造：

- 芯片时序值
- 寄存器地址
- 项目专属信号 ID
- 故障阈值
- NVM Block 绑定关系

缺失时必须显式标记为假设、待确认或待补料。

## 4. 输入优先级

```text
用户当前需求
→ 当前架构或设计草稿
→ 本地项目编码规则
→ 本 skill 的保留规则
→ 真实项目 grounding 摘要
→ AI 推断
```

冲突处理原则：

- 以当前项目显式输入为最高优先级
- 架构约束高于 demo 习惯
- grounding 只作为风格证据，不直接覆盖项目决定
- 不要悄悄改掉用户已经指定的命名、分层和接口边界

## 5. 最小加载策略

默认只加载：

1. 用户提供的需求、架构、实现草稿或目标 FC 文件
2. 本 `SKILL.md`
3. 一个输出模板
4. 当前问题真正需要的规则文件

按需加载：

- `references/workflow.md`
  任务是完整生成、流程改造或全链路排查时再读
- `references/grounding/index.yaml`
  需要选参考 FC 或模块族不清楚时再读
- `references/grounding/modules/*`
  需要接口形态、per-core、Callout、Cfg/Runtime 证据时再读
- `references/grounding/patterns/*`
  需要抽象出来的实现模式时再读
- `references/semantic-model.md` 与 `references/schemas/*`
  需要稳定结构化中间对象时再读

## 6. 规则文件分工

- `references/rules/implementation-rules.md`
  实现设计总规则、边界与冲突处理
- `references/rules/code-structure-rules.md`
  文件族、单核/多核框架、配置布局、Callout 放置、运行时容器形态
- `references/rules/state-and-fault-rules.md`
  状态机、DET、运行时错误、故障、复位和 `NoClear`
- `references/rules/flowchart-rules.md`
  何时输出流程图，以及流程图该画到什么粒度
- `references/rules/implementation-review-checklist.md`
  正式实现评审和编码就绪检查

## 7. 什么时候用这个 skill

当用户要做以下事情时使用：

- FC 详细设计
- 面向编码的实现设计
- `cfg` / `callout` / `runtime-state` 设计
- 状态机代码设计
- 内部函数拆分
- 故障处理设计
- 单核或多核实现框架设计
- 实现评审、清理和补强

以下场景不要用它：

- 纯需求抽取
- 纯软件架构生成
- 与 FC 无关的泛 C 语言教学

## 8. 输入充分度

- `L1`
  需求 + 架构，足够生成详细设计草稿
- `L2`
  需求 + 架构 + 公司规则 + 参考 FC，足够生成面向编码的详细设计
- `L3`
  需求 + 架构 + 公司规则 + 芯片手册 + 参考 FC，足够做强约束实现设计与脚手架指导

低于 `L2` 时，必须保留假设。

## 9. 推荐执行步骤

1. 确认输入边界与目标输出层级
2. 选择最接近的 grounding 模块或模式
3. 抽取结构化设计对象
4. 设计文件族、接口族、配置容器、运行时容器、状态机与故障流
5. 用规则和校验器检查设计完整性与可编码性
6. 输出详细设计、评审结论或编码脚手架计划

## 10. 输出物

标准输出文件名：

```text
<FC>_模块详细设计规范.md
```

常见输出内容：

- 模块职责与文件结构
- 外部接口与依赖接口设计
- 配置与运行时数据设计
- 状态机与故障处理
- `DET` 与防御式检查策略
- `MemMap` 与 `NoClear` 数据布局
- 编码骨架建议与评审问题清单
