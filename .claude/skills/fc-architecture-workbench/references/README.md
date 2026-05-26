# 参考资料索引

## 作用

本目录保存 `fc-architecture-workbench` 的长期参考资料。

为了控制上下文体积，建议按优先级和职责读取，而不是全量加载。

职责边界：

- `rules/*.md`
  负责稳定架构规则和判断标准
- `templates/*.md`
  负责输出结构与文档版式
- 本 `README.md`
  只负责索引和最小加载建议
- 执行逻辑仍放在 `../SKILL.md`

## 核心规则

日常 FC 架构设计优先读取：

- `rules/fc-architecture-rules.md`
- `rules/release-workflow.md`
- `rules/naming-rules.md`
- `rules/static-vs-dynamic.md`
- `rules/interface-selection.md`
- `templates/output-template.md`
- `templates/output-template-summary.md`

## 项目风格资料

- `rules/project-style-rules.md`
  记录本地项目在外部接口、头文件职责、配置粒度、多核和 Callout 上的习惯
- `source-grounding-aurix2g-live-baseline.md`
  保存基于真实工程树提炼出的文件族、配置拆分、Callout、多核、DET 与 MemMap 证据

## 深度辅助资料

只有在做 freeze 层推理、深度抽取或对象校验时再读取：

- `architecture-freeze-bundle-v1.md`
- `semantic-model.md`
- `templates/extraction-debug-template.md`
- `../scripts/build_architecture_freeze_bundle.py`
- `../scripts/check_architecture_markdown.py`
- `../scripts/validate_architecture_objects.py`
- `../scripts/validate_architecture_freeze_bundle.py`
- `../scripts/validate_architecture_source_alignment.py`
- `../scripts/extract_architecture_objects.py`

这些脚本和辅助材料是执行工具，不是规则来源。

## 来源说明

原始 PDF 已经被压缩整理进 Markdown 规则文件：

- `../archive/G-C046 软件接口命名规范.pdf`
- `../archive/G-C119 FC开发指南（C语言）.pdf`

日常架构工作优先使用已整理的 Markdown 规则；PDF 只作为追溯和审计备份。

## 最小加载约定

常规生成或评审建议按以下顺序加载：

1. 用户需求、架构草稿或目标输出文件
2. `../SKILL.md`
3. 一个输出模板
4. 当前问题真正需要的规则文件
5. 只有在需要真实工程证据时，再读取 `source-grounding-aurix2g-live-baseline.md`
6. 只有在需要 freeze 层推理时，再读取 `architecture-freeze-bundle-v1.md`

不要默认把所有规则、模板、demo 和学习笔记一起加载。

## 最小保留集

如果要保留一个最小但可用的知识集合，建议至少保留：

- `../docs/learning/AURIX2G_域控工程软件架构学习记录.md`
- `../docs/guides/AURIX2G_架构设计细节学习与后续设计指导.md`
- `rules/fc-architecture-rules.md`
- `rules/naming-rules.md`
- `rules/static-vs-dynamic.md`
- `rules/interface-selection.md`
- `rules/project-style-rules.md`
- `source-grounding-aurix2g-live-baseline.md`
- `architecture-freeze-bundle-v1.md`
- `templates/output-template.md`
