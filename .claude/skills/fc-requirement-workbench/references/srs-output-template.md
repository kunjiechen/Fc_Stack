# SRS Output Template

Use this template when generating a software requirement specification from extracted requirement inputs. It captures the preferred SRS structure for this skill and should be used as an internal output pattern, not as an external evidence source.

The generated SRS should describe software requirements only. It should not include detailed design, implementation plans, test case steps, or standalone process rules.

## Document Structure

```markdown
# 《{module_short_name} 软件需求规范》

**<FC_Name>_需求规范**

**<FC_Name>_Requirements Specification**

项目编号/Project number:<FC_Name>
保密性/Security:<Security_Level>

**Document Properties**
Status:**草稿**
版本:**<Document_Version>**
Author:<Author>
Created:<YYYY-MM-DD HH:mm>

**Approved Versions**
Current Document version **<Document_Version>** is **TBD**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| <Document_Version> | 草稿 | TBD | TBD | TBD |

## 适用说明

本文档适用于 `{project_name}` 项目中 `{module_short_name}` {module_kind}的软件需求定义。本文档仅描述软件应满足的需求，不描述详细设计方案、代码实现方案或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| {document_version} | {date} | {author} | {change_summary} | {document_status} |

---

## 目录

- [1 目的](#1-目的)
- [2 适用范围](#2-适用范围)
- [3 定义和缩写](#3-定义和缩写)
- [4 概述](#4-概述)
- [5 功能需求](#5-功能需求)
- [6 非功能需求](#6-非功能需求)
- [7 风险与待确认问题](#7-风险与待确认问题)
- [8 需求来源](#8-需求来源)
- [附录A 需求清单](#附录a-需求清单)
- [附录B 支持和相关性文件](#附录b-支持和相关性文件)
- [下一步：评审与发布引导](#下一步评审与发布引导)
```

## Section Template

```markdown
## 1 目的

本文档定义 `{module_short_name}` 模块的软件需求，明确模块在 `{project_name}` 项目中的功能边界、对外接口、状态行为、配置约束、诊断状态、时序要求、非功能约束和验证要求。

本文档作为 `{module_short_name}` 模块软件架构设计、详细设计、编码实现、单元测试、集成测试和系统测试的上游输入。所有正式需求均应具备需求 ID、来源、约束、验收准则和验证方式。

---

## 2 适用范围

本文档适用于 `{project_name}` 项目中 `{module_short_name}` 模块的软件开发、评审、集成、测试和交付活动。

### 2.1 适用对象

- 软件需求工程师
- 软件架构和详细设计工程师
- 软件开发工程师
- 软件测试工程师
- 功能安全工程师
- 项目质量和配置管理人员

### 2.2 适用范围

本文档覆盖 `{module_short_name}` 模块的软件功能、接口、配置、诊断、时序及相关非功能需求，并给出需求来源、验证方式、验证阶段和需求状态。本文档不展开详细设计方案、代码实现方案和测试用例步骤。

---

## 3 定义和缩写

### 3.1 定义

| 术语 | 定义 |
| --- | --- |
{definition_rows}

### 3.2 缩写

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
{abbreviation_rows}

---

## 4 概述

本章仅保留理解需求所需的芯片和驱动背景信息，避免展开实现细节；正式软件责任以下文需求条目为准。

### 4.1 外设芯片介绍

{peripheral_chip_summary}

芯片支持以下功能：

{peripheral_capability_items}

### 4.2 驱动功能介绍

`{module_short_name}` 驱动应实现以下软件功能：

{driver_function_items}

### 4.3 外设引脚介绍

| 引脚 | 方向 | Pin口功能 |
| --- | --- | --- |
{pin_rows}

### 4.4 状态机介绍

> 仅当芯片或模块存在复杂状态跳转时生成此章节。若不存在明确状态跳转，则不生成此章节。

{state_machine_summary}

{state_machine_diagram_optional}

| 状态 | 说明 | 进入条件 | 退出条件 |
| --- | --- | --- | --- |
{state_transition_rows}

### 4.5 通信参数

> 若该芯片不涉及 SPI、I2C 等通信要求，则不生成此章节。若涉及，仅保留与软件需求直接相关的关键通信参数。

关键通信参数：

{speed_mode_items}

- 器件寻址：{device_addressing}

{timing_param_rows}

{timing_note}
```

## Functional Requirement Sections

Sections 5.1-5.4 are mandatory and must always be emitted. When a section has no requirement items, render the heading followed by "无对应需求。" as a placeholder paragraph. Do not omit any of these four subsections.

```markdown
## 5 功能需求

本章描述模块必须实现的功能行为，包括模式与状态、接口、配置、诊断和错误处理。每条需求使用固定字段描述，以便后续生成设计、测试和追溯矩阵。

### 5.1 模式需求

{mode_and_state_requirements}

### 5.2 接口需求

{interface_requirements}

### 5.3 配置需求

{configuration_requirements}

### 5.4 诊断需求

{diagnostic_and_error_requirements}
```

## Non-Functional Requirement Sections

Sections 5.1-5.4 and 6.1-6.4 are mandatory and must always be emitted. When a section has no requirement items, render the heading followed by "无对应需求。" as a placeholder paragraph.

```markdown
## 6 非功能需求

### 6.1 时序需求

{timing_requirements}

### 6.2 安全等级需求

{safety_level_requirements}

### 6.3 编码规范需求

{coding_standard_requirements}

### 6.4 资源消耗需求

{resource_requirements}
```

## Requirement Item Template

Use this template for every requirement item. The heading carries the requirement ID and short title. The canonical rendered layout is a prose paragraph plus a requirement-type-specific bullet block. Do not render requirement fields as a Markdown table.

```markdown
#### {requirement_id} {requirement_short_title}

`{primary_category}` `{asil_or_qm}` `{verification_method} / {verification_stage}` `{status}` `来源: {upstream_sources}`

{module_short_name} 模块应{observable_required_behavior}。

**{constraint_block_title}**

- **范围边界**：{scope_boundary_and_exclusions}
- **前置条件**：{preconditions}
- **触发条件**：{triggers}
- **输入**：{inputs}
- **输出**：{outputs}
- **异常处理**：{exception_and_boundary_handling}
- **验收准则**：{acceptance_criteria}
```

If a field is not applicable, omit that bullet. Do not leave empty bullets in generated SRS output. Requirement metadata such as source, ASIL, verification method, verification stage, and status belongs in the status tag line rather than in a field table.

## Requirement Category Mapping

Use these ID type codes by default:

| Requirement Group | Default ID Code | Section |
| --- | --- | --- |
| Mode/state/function behavior | `FUNC` | 5.1 模式需求 |
| Interface/API/pin access | `INTF` | 5.2 接口需求 |
| Configuration and ownership | `CFG` | 5.3 配置需求 |
| Diagnosis, status interpretation, errors | `DIAG` | 5.4 诊断需求 |
| Timing/performance | `TIM` | 6.1 时序需求 |
| Safety level and safety boundary | `SAFE` | 6.2 安全等级需求 |
| Coding and implementation standard constraints | `CODE` | 6.3 编码规范需求 |
| ROM/RAM/Stack/CPU resources | `RES` | 6.4 资源消耗需求 |

Requirement IDs should follow:

```text
SRS-{MODULE_SHORT_NAME}-{TYPE_CODE}-{NNNN}
```

## Risk and Pending Issues Section Template

```markdown
## 7 风险与待确认问题

本章汇总当前需求版本中仍需项目确认、补料或后续评审关闭的事项，结构和评审方式与架构阶段保持一致，便于后续继承评审结论。

### 7.0 需求风险与待确认总表

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | {issue_type} | {risk_summary} | {affected_requirements} | {suggested_action} | | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议。 | 待评审 |

### 7.1 接口遗漏风险清单

| 风险项 | 风险等级 | 说明 | 建议动作 |
| --- | --- | --- | --- |
| {risk_item} | {level} | {description} | {action} |

### 7.2 待确认接口清单

| 接口名 | 来源需求 | 置信度 | 待确认原因 | 建议处理 |
| --- | --- | --- | --- | --- |
| {interface_name} | {source_req} | {confidence} | {reason} | {suggested_handling} |

### 7.3 不建议直接生成的低置信度接口

本节为空——当前所有候选接口置信度均为中或高。
```

This section should remain consistent with the same FC's architecture Draft risk table: same risk IDs, same suggested actions, same status/notes where applicable.

## Source Section Template

```markdown
## 8 需求来源

| 来源类别 | 来源名称 | 与本文档关系 | 状态 |
| --- | --- | --- | --- |
{source_rows}
```

The output document should show source inputs only. Do not include standalone trace rules, quality gate rules, or generation process rules in this section.

## Companion Review and Trace Artefacts

The formal SRS Markdown remains focused on software requirements. Each full requirement-generation run must also emit three companion artefacts in the same output directory:

| Artefact | Filename | Purpose |
| --- | --- | --- |
| Review 需求评审记录 | `Review_{module_short_name}_软件需求规范.md` | Summarize review verdict, Gate results, remaining open items, and SDD entry decision. |
| Check 需求检查清单 | `Check_{module_short_name}_软件需求规范.md` | Preserve checklist details, issue closure table, package completeness, and release verdict. |
| Trace 追溯矩阵 | `Trace_{module_short_name}_软件需求规范.md` | Preserve Source → Requirement, Requirement → Verification Intent, raw requirement coverage, and ASPICE evidence summary. |

Do not duplicate these full companion artefacts inside the SRS body; the SRS may reference them only as supporting outputs.

## Appendix Templates

```markdown
## 附录A 需求清单

| 需求ID | 类别 | 需求名称 | 验证方式 | 验证阶段 | 状态 |
| --- | --- | --- | --- | --- | --- |
{requirement_list_rows}

---

## 附录B 支持和相关性文件

| 序号 | 文件名称 | 文件编号/版本 | 来源 | 与本文档关系 |
| --- | --- | --- | --- | --- |
{supporting_file_rows}
```

Appendix A is optional when the consuming workflow already generates a separate requirement list or trace matrix. Appendix B should be retained when source material and process references are known.

## Review and Release Guidance Template

```markdown
## 下一步：评审与发布引导

当需求状态为 `Draft` 时必须执行以下评审与发布引导：

- 推荐评审方式 1：直接修改上方风险表中的`状态`和`备注`。
- 推荐评审方式 2：在当前窗口回复，例如`R1、R3 已评审；R5 待修改，备注：接口名统一为 xxx`。
- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。
- 如果某项需要修改，可回复：`R5 待修改，备注：xxx`。
- 修改完成后仍保持当前版本的`Draft`，直到所有真实风险项均为`已评审`后发布为`Released`。
- 草稿评审发布不升级版本；只有正式需求文件 + 新架构/下游交付基线发布时才升级到下一版本。
```

## Output Rules

- Do not generate per-section overview tables before requirement items.
- Do not repeat `需求ID` or `需求标题` inside the requirement body.
- Each requirement must be concrete, verifiable, and traceable to at least one source.
- Datasheet-supported capabilities must be separated from project-supported behavior.
- Project-excluded capabilities should appear as boundaries or exclusions, not as supported requirements.
- Use `Draft`, `Ready`, `needs_source`, `conflict`, or `open_issue` consistently according to evidence maturity.
- Summarize unresolved requirement-stage confirmation items in the SRS, but keep the full closure workflow in separate review artefacts.
- Keep design and implementation mechanisms out of the SRS unless they are explicit requirement constraints.
- Use `us`, `ms`, `s`, `V`, and other unit strings consistently in generated Markdown unless the source requires another notation.
- The SRS document must include the "下一步：评审与发布引导" section when status is Draft; the dialog reply after generation must also surface the review guidance block.
