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

## 核心规则（架构生成必读）

日常 FC 架构设计优先读取：

- `rules/project-style-rules.md` — 接口骨架、MainFunction 判定、头文件载体职责、配置粒度、多核惯例
- `rules/interface-selection.md` — 依赖表达方式选择（Macro/Binding/Callout/Fixed）
- `rules/naming-rules.md` — 标识符命名规范（函数/变量/宏/类型）
- `rules/static-vs-dynamic.md` — 配置/标定/运行时状态分类决策
- `rules/release-workflow.md` — 版本策略、风险评审、发布门禁
- `templates/output-template-summary.md` — **唯一交付模板**（10 章 + 附录 + 评审引导）
- `semantic-model.md` — 11 类语义对象定义（架构生成的中间结构）

## 架构族与 grounding 资料

- `source-grounding-aurix2g-live-baseline.md`
  基于真实工程树提炼的文件族、配置拆分、Callout、多核、DET 与 MemMap 证据。§11A-§11D 提供按架构族的模式参考
- `../demo-lib/MODULE_INDEX.md` + `summaries/*.arch.json`
  按族组织的结构化架构参考模板。生成前根据目标架构族加载对应的 `.arch.json` 文件
- `rules/fc-architecture-rules.md`
  原始架构规则（部分章节已由上述文件取代，详见文件头部说明）。仍保有独有的分层模型和内部状态设计指导

## 脚手架与调试资料

仅在需要全量需求抽取、反向追踪或深度分析时读取：

- `templates/output-template.md` — **内部脚手架（非交付模板）**，含过程性章节供 skill 内部推理
- `templates/extraction-debug-template.md` — 需求抽取调试模板

## 深度辅助资料

只有在做 freeze 层推理或自动化校验时再读取：

- `architecture-freeze-bundle-v1.md`
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
2. `../SKILL.md`（执行流程 + 反模式清单 §14 + 预检清单 §9.0）
3. `templates/output-template-summary.md`（交付模板）
4. `semantic-model.md`（语义对象结构）
5. 根据 §9.2 判定的架构族和子类型，加载对应的 `demo-lib/summaries/*.arch.json` 参考
6. 根据架构族，加载 `source-grounding-aurix2g-live-baseline.md` 对应族章节（§11A-§11D）
7. 当前问题真正需要的规则文件（按 `SKILL.md` §8 规则分工表选择）
8. 只有在需要 freeze 层推理时，再读取 `architecture-freeze-bundle-v1.md`

不要默认把所有规则、模板、demo 和学习笔记一起加载。

## 最小保留集

如果要保留一个最小但可用的知识集合，建议至少保留：

- `../SKILL.md`（执行引擎 + 反模式 + 预检清单）
- `rules/project-style-rules.md`
- `rules/interface-selection.md`
- `rules/naming-rules.md`
- `rules/static-vs-dynamic.md`
- `rules/release-workflow.md`
- `templates/output-template-summary.md`
- `semantic-model.md`
- `source-grounding-aurix2g-live-baseline.md`
- `../demo-lib/summaries/Gp_TLE92104.arch.json`（IoExtDev Reg 参考）
- `../demo-lib/summaries/Gp_DRV887x_DIO.arch.json`（IoExtDev Pin 参考）
- `../demo-lib/summaries/Gp_IoMcuDio.arch.json`（IoMcu 参考）
- `../demo-lib/summaries/Gp_SysState.arch.json`（BswSys_Gp 参考）
