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
- [7 需求来源](#7-需求来源)
- [附录A 需求清单](#附录a-需求清单)
- [附录B 支持和相关性文件](#附录b-支持和相关性文件)
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

### 2.2 范围内

本文档覆盖：

{in_scope_items}

### 2.3 范围外

本文档不覆盖：

{out_of_scope_items}

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

### 4.1 外设芯片介绍

{peripheral_chip_summary}

芯片具备以下与软件需求相关的能力：

{peripheral_capability_items}

### 4.2 驱动功能介绍

`{module_short_name}` 驱动应实现以下软件功能：

{driver_function_items}

**边界约束**：

{driver_boundary_constraint_items}

**待定项**：

{driver_pending_items}

### 4.3 外设引脚介绍

| 引脚 | 方向 | Pin口功能 |
| --- | --- | --- |
{pin_rows}

### 4.4 状态机介绍

> 若该外设芯片没有状态机跳转，则不生成此章节。若存在状态跳转，需给出状态机框图、状态介绍和跳转条件。

{state_machine_summary}

{state_machine_diagram_optional}

| 状态 | 说明 | 进入条件 | 退出条件 |
| --- | --- | --- | --- |
{state_transition_rows}

### 4.5 通信参数

> 若该芯片不涉及 SPI、I2C 等通信要求，则不生成此章节。若涉及，需提取通信参数和通信时序图。

{bus_type} 总线支持以下速率模式：

{speed_mode_items}

**器件寻址**：

{device_addressing}

{timing_diagram_optional}

| 参数 | 符号 | 条件 | 最小值 | 最大值 | 单位 |
| --- | --- | --- | --- | --- | --- |
{timing_param_rows}

{register_map_summary}

{timing_note}
```

## Functional Requirement Sections

Use the following section layout for functional requirements. Omit a subsection only when it is not applicable and the scope section clearly excludes it.

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

### 6.5 可追溯性需求

{traceability_requirements}
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
| Timing/performance | `TIM` | 6.1 |
| Safety level and safety boundary | `SAFE` | 6.2 |
| Coding and implementation standard constraints | `CODE` | 6.3 |
| ROM/RAM/Stack/CPU resources | `RES` | 6.4 |
| Traceability/process quality | `COMP` | 6.5 |

Requirement IDs should follow:

```text
SRS-{MODULE_SHORT_NAME}-{TYPE_CODE}-{NNNN}
```

## Source Section Template

```markdown
## 7 需求来源

| 来源类别 | 来源名称 | 与本文档关系 | 状态 |
| --- | --- | --- | --- |
{source_rows}
```

The output document should show source inputs only. Do not include standalone trace rules, quality gate rules, or generation process rules in this section.

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

## Output Rules

- Do not generate per-section overview tables before requirement items.
- Do not repeat `需求ID` or `需求标题` inside the requirement body.
- Each requirement must be concrete, verifiable, and traceable to at least one source.
- Datasheet-supported capabilities must be separated from project-supported behavior.
- Project-excluded capabilities should appear as boundaries or exclusions, not as supported requirements.
- Use `Draft`, `Ready`, `needs_source`, `conflict`, or `open_issue` consistently according to evidence maturity.
- Keep design and implementation mechanisms out of the SRS unless they are explicit requirement constraints.
- Use `us`, `ms`, `s`, `V`, and other unit strings consistently in generated Markdown unless the source requires another notation.
