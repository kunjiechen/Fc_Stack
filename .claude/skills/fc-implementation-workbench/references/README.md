# 参考资料索引

## 作用

本目录保存 `fc-implementation-workbench` 使用的实现层长期参考资料。

建议按职责和最小集合加载，不要一次性全读。

职责边界：

- `rules/*.md`
  稳定的实现设计规则与判断标准
- `grounding/`
  基于真实项目 FC 提炼出的 grounding 基线、模块事实和模式摘要
- `schemas/`
  需求、架构、详细设计的结构化输入与中间对象契约
- `templates/*.md`
  输出章节结构与文档版式
- `semantic-model.md`
  可复用的实现对象模型
- `workflow.md`
  推荐生成流程与阶段顺序
- `validation_rules.md`
  当前校验器约束
- `detailed_design_quality_contract.md`
  详细设计质量目标
- `bundle_to_dd_mapping.md`
  结构化 bundle 到详细设计章节的映射
- `chapter_generation_rules.md`
  分章节写作和渲染规则
- `../scripts/*.py`
  生成、校验、抽取和回归辅助脚本
- 本 `README.md`
  只负责索引和最小加载建议

## 核心规则

日常 FC 实现设计优先读取：

- `rules/implementation-rules.md`
- `rules/code-structure-rules.md`
- `rules/state-and-fault-rules.md`
- `rules/flowchart-rules.md`
- `rules/implementation-review-checklist.md`
- `templates/output-template.md`
- `templates/output-template-summary.md`

## Grounding 资料

在做完整详细设计生成、风格对齐或参考 FC 选型时再读取：

- `grounding/index.yaml`
- `grounding/grounding_scope.md`
- `grounding/modules/*`
- `grounding/patterns/*`

## 结构化辅助资料

只有在需要稳定中间对象时再读取：

- `semantic-model.md`
- `schemas/*.json`
- `schemas/field_dictionary.md`
- `examples/*.yaml`
- `workflow.md`
- `validation_rules.md`
- `golden_checks.md`

## 来源说明

本目录中的规则，来自当前工作区已完成的工程学习、代码设计学习和公司规范学习整理。

保留的学习笔记包括：

- `learning/aurix2g-engineering-learning.md`
- `learning/aurix2g-code-design-rules.md`
- `learning/company-code-standards-learning.md`

常规执行优先使用这里已经沉淀好的规则文件，不要直接依赖大篇幅学习笔记。

## 最小加载约定

日常实现设计建议按以下顺序加载：

1. 用户当前需求、架构或目标 FC 草稿
2. `../SKILL.md`
3. 一个输出模板
4. 当前问题真正需要的规则文件
5. 只有在需要 grounding 或流水线生成时，再加载 `grounding/`

不要默认把所有规则、模板和 grounding 一次性读入。
