# SRS Authoring Standard

Use this standard when writing, reviewing, or validating SRS documents and SRS requirement items.

This file defines the authoring rules for structure, requirement fields, status, language, units, and granularity. The concrete output layout must follow `srs-output-template.md` by default. If this authoring standard describes a full-process section that the calibrated output template omits or merges, the section intent must still be covered by requirement fields, source tables, appendix content, or internal validation rules.

Boundary of this file:

- This file defines document writing and rendering expectations.
- It does not own per-category minimum required fields; that belongs to `construction-rules.md`.
- It does not own local case-by-case writing preferences; that belongs to `calibration-rules.md`.
- It may reference status vocabulary and field presence, but category-specific completeness and downgrade rules must be maintained in `construction-rules.md`.

## 0. Relationship To Output Template

`srs-output-template.md` is the default rendering contract. This authoring standard is the quality and review contract.

Use them together as follows:

| Concern | Source Of Truth |
| --- | --- |
| Final chapter order and heading names | `srs-output-template.md` |
| Cover page, approval table, revision table, and source appendix shape | `srs-output-template.md` |
| Requirement item rendered shape and omission of empty optional bullets | `srs-output-template.md` |
| Writing quality, field completeness, status judgment, units, and granularity | `authoring-standard.md` |
| Extraction source priority and structured extraction output | `extraction-rules.md` |
| Requirement construction completeness by category | `construction-rules.md` |
| Historical style and judgment calibration | `calibration-rules.md` |

Default generated SRS documents must not add standalone `约束与假设`, `需求追溯`, or `验证策略` chapters unless the user explicitly asks for the full-process layout. Their intent is handled as follows:

| Full-Process Intent | Default Output Location |
| --- | --- |
| Constraints and assumptions | Requirement `范围边界`, `异常处理`, nonfunctional requirements, or `Open Issue` status |
| Traceability rules | Internal rules; output only `需求来源` and requirement-level `来源` |
| Verification strategy | Requirement-level `验证方式`, `验证阶段`, and `验收准则` |

## 1. Chapter Structure

The full SRS authoring structure contains these chapters:

| Chapter | Purpose | Output Guidance |
| --- | --- | --- |
| 目的 | Define why the SRS exists and what downstream activities consume it. | Required |
| 适用范围 | Define the applicable software scope and exclusions in concise prose. | Required |
| 定义和缩写 | Define domain terms, abbreviations, and semantic distinctions. | Required |
| 概述 | Summarize chip/module context, supported capability, driver responsibility, pins, and state machine only when complex state transitions exist. | Required |
| 软件需求 / 功能需求 | Define functional software requirements. | Required; default output heading is `功能需求`. |
| 非功能需求 | Define timing, safety level, coding standard, resource, and process-quality requirements. | Required |
| 约束与假设 | Capture explicit constraints and unresolved assumptions. | Optional as standalone section; may be folded into requirement scope boundaries, nonfunctional requirements, or open issues. |
| 需求追溯 | Capture source and trace intent. | Optional as standalone section; calibrated template uses `需求来源` and keeps trace rules internal. |
| 验证策略 | Explain verification methods and stages. | Optional as standalone section; each requirement must still include verification method and stage. |
| 附录 | Provide requirement list, supporting files, terms, or generated matrices. | Optional, depending on output workflow. |

Document balance rule:

- Avoid `头重脚轻`: front-matter, scope, and overview should stay concise and serve only as context.
- The main document weight should be in `5 功能需求` and `6 非功能需求`.
- Do not use long overview prose, oversized capability lists, or communication parameter dumps to replace formal requirements.
- If a statement defines software responsibility, move it to a requirement item instead of expanding the overview.

For the calibrated FC output template, use this generated chapter layout unless the user asks for the full-process structure:

```text
1 目的
2 适用范围
3 定义和缩写
4 概述
5 功能需求
6 非功能需求
7 需求来源
附录A 需求清单
附录B 支持和相关性文件
```

## 2. Requirement Item Fields

Each formal requirement item should render with the following common fields:

| Field | Meaning | Required |
| --- | --- | --- |
| Title | Short requirement title in the heading. | Yes |
| Description / 需求陈述 | Observable required behavior. | Yes |
| Source / 来源 | Upstream evidence such as datasheet, project requirement, configuration, code, or test material. | Yes |
| ASIL/Level | Safety level or quality level, such as `QM` or `ASIL-B`. | Yes when applicable; otherwise state project level. |
| Verification Method / 验证方式 | Review, Analysis, Test, Inspection, or a project-approved equivalent. | Yes |
| Verification Stage / 验证阶段 | Review, UT, IT, ST, or project-approved equivalent. | Yes |
| Status / 状态 | Requirement maturity. | Yes |

Default output fields:

| Field | Meaning |
| --- | --- |
| 类别 | Requirement category and subcategory. |
| 范围边界 | Explicit inclusion/exclusion boundary. |
| 前置条件 | Required state before the behavior applies. |
| 触发条件 | Event, call, condition, or transition that triggers the behavior. |
| 输入 | Inputs, parameters, signals, configuration values, or states. |
| 输出 | Outputs, return values, state changes, signals, or records. |
| 异常处理 | Invalid input, failed precondition, boundary, and error behavior. |
| 验收准则 | Concrete evidence needed to accept the requirement. |

Requirement block style:

```markdown
#### {requirement_id} {requirement_title}

`{primary_category}` `{level}` `{verification_method} / {verification_stage}` `{status}` `来源: {sources}`

{observable_behavior}

**{constraint_block_title}**

- **范围边界**：{scope_boundary}
- **前置条件**：{preconditions}
- **触发条件**：{triggers}
- **输入**：{inputs}
- **输出**：{outputs}
- **异常处理**：{exception_handling}
- **验收准则**：{acceptance_criteria}
```

Field rules:

- Do not repeat `需求ID` or `需求标题` inside the body when the heading already contains them.
- Omit optional bullets that are not applicable.
- Do not render Markdown field tables for requirement items.
- Keep `来源`, `验证方式`, `验证阶段`, and `状态` present for every formal requirement in the status tag line.
- Use `范围边界` to carry project exclusions, unsupported modes, scope limits, and source-derived caveats.
- `DET` or equivalent development error detection is a mandatory requirement topic for externally callable software modules.
- If the module detects, latches, reports, or evaluates faults/diagnostic status, the SRS should include a readable fault/diagnostic status interface or an equivalent observable mechanism.
- Whether a specific category has enough fields to be `Ready` is decided in `construction-rules.md`, not here.

## 3. Status Standard

Use these status values in human-facing SRS output:

| Status | Meaning | Use When |
| --- | --- | --- |
| Ready | Requirement is complete enough for downstream design and verification. | Required fields exist, source is clear, behavior is actionable, verification is defined. |
| Draft | Requirement is incomplete or still being shaped. | Required fields are missing, wording is vague, acceptance criteria are incomplete, or evidence is not mature. |
| Open Issue | Requirement needs a project decision. | Ownership, source priority, range, default, mode support, timing responsibility, or behavior boundary is unresolved. |

Additional internal or generated statuses may be used in extraction, validation, or intermediate artifacts:

| Status | Meaning |
| --- | --- |
| needs_source | Engineering-plausible item lacks source evidence. |
| conflict | Sources or constraints disagree. |
| NotApplicable | Source capability exists but does not map to software responsibility. |

Rendering rules:

- Missing required field prevents `Ready`.
- Vague description prevents `Ready`.
- Unclear ownership prevents `Ready`.
- Conflicting source evidence prevents `Ready`.
- A requirement with no source must be `Draft`, `needs_source`, or `Open Issue`.
- In final SRS output, prefer `Ready`, `Draft`, and `Open Issue`. Use `needs_source`, `conflict`, or `NotApplicable` in intermediate reports unless the user requests diagnostic statuses in the SRS.

Detailed category-specific downgrade conditions belong to `construction-rules.md`.

## 4. Language Style

SRS language must be:

- Concise.
- Standardized.
- Non-ambiguous.
- Actionable by software.
- Verifiable by review, analysis, inspection, or test.
- Traceable to source material.

Preferred sentence style:

```text
{module} 模块应在 {condition} 时 {observable_action}，并 {observable_result}。
```

Examples:

- Good: `当上层请求 Normal 模式且请求被接受时，模块应控制 STB_N=HIGH 且 EN=HIGH。`
- Good: `当目标模式不属于 Normal、Standby、Sleep 时，模块应返回 E_NOT_OK 并保持原控制输出不变。`
- Avoid: `模块应正常切换模式。`

## 5. Vague Language Ban

Do not use vague words unless a measurable condition, boundary, or acceptance rule is provided.

Vague words include:

- 正常
- 合理
- 稳定
- 快速
- 可靠
- 及时
- 适当
- 多个
- 若干
- 尽量
- 必要时
- 支持相关功能

Replacement guidance:

| Vague Expression | Preferred Form |
| --- | --- |
| 正常工作 | Define specific state, output, return value, or accepted behavior. |
| 合理范围 | Provide numeric range, enum set, or project-defined boundary. |
| 稳定后 | Provide timing value, sampling rule, or caller/module responsibility. |
| 快速返回 | Provide maximum execution time or state that interface is synchronous. |
| 多个实例 | Provide allowed range, such as `1..256`. |

## 6. Unit Standard

All numeric values must include explicit units where applicable.

Preferred unit style:

| Quantity | Preferred Unit Examples |
| --- | --- |
| Time | `us`, `ms`, `s` |
| Frequency | `Hz`, `kHz`, `MHz` |
| Voltage | `V`, `mV` |
| Memory | `B`, `KB`, `MB` |
| Data rate | `bit/s`, `kbit/s`, `Mbit/s` |
| Count/range | `1..6`, `0..255`, enum names |

Rules:

- Use explicit comparison direction: `>=8 us`, `<=10 ms`, `1..6`.
- Do not write timing constraints without a value.
- Preserve source units during extraction, then normalize consistently in generated SRS.
- Avoid mixing `μs` and `us` in the same generated document. The calibrated Markdown output prefers `us` for ASCII stability.

## 7. Requirement Granularity

Each requirement item must describe one behavior, one interface contract, one configuration item, one diagnostic rule, one timing constraint, or one resource obligation.

Avoid mixed requirements:

- Do not combine mode setting, mode reading, and error handling in one requirement if they can be verified separately.
- Do not combine multiple unrelated configuration parameters in one requirement.
- Do not combine chip capability summary and software action in one requirement.
- Do not combine implementation detail and requirement unless the implementation constraint is explicitly required.

Split when:

- Different verification methods are needed.
- Different sources justify different behavior.
- One part is Ready and another part is Draft/Open Issue.
- One behavior is functional and another is nonfunctional.
- One behavior is public API and another is internal state.

Concrete category patterns and minimum construction elements belong to `construction-rules.md`.

## 8. Source And Traceability Authoring

Each requirement must include upstream source evidence.

Source examples:

- `Project Requirement - Mode Policy`
- `Datasheet - Operating Modes`
- `Configuration - InstanceCount`
- `Source Code - Tja1043_SetMode`
- `Test Material - UT mode transition cases`

Rules:

- Datasheet capability is not automatically project-supported behavior.
- Project requirement overrides datasheet capability for supported/excluded behavior.
- Source code calibrates naming and behavior but should not invent project scope.
- Test material provides verification intent but should not create unsupported functional scope.
- If multiple sources are merged, preserve the dominant source and note supporting sources.

## 9. Example Requirement Item

```markdown
#### SRS-TJA1043-FUNC-0001 外设模式转换控制

`功能需求` `QM` `Test / UT/IT` `Ready` `来源: 原始需求-功能需求1；Datasheet-Operating modes`

`TJA1043` 模块应支持每个已配置实例在 `Normal`、`Standby`、`Sleep` 三种对外支持模式之间进行受控转换。

**功能约束**

- **范围边界**：仅支持公共 API 暴露的三种软件模式；`Listen-only` 和 `Go-to-Sleep` 不属于对外支持模式。
- **前置条件**：模块已初始化；目标实例已配置并启用；当前内核具备访问权限。
- **触发条件**：上层调用模式设置接口并传入有效目标模式。
- **输入**：实例 ID、目标模式。
- **输出**：`STB_N`/`EN` 控制输出、实例软件模式状态、接口返回值。
- **异常处理**：未初始化、实例无效、目标模式无效、当前内核未使能或配置无效时，应拒绝切换并保持原控制输出和原软件模式状态。
- **验收准则**：对每个有效实例，`Normal`、`Standby`、`Sleep` 请求均产生对应控制路径；非法请求不改变实例状态；不同实例互不影响。
```

## 10. Review Checklist

Before accepting an SRS item:

- Does it describe software responsibility?
- Does it have a clear source?
- Does it have one primary behavior?
- Is the wording observable and testable?
- Are inputs, outputs, preconditions, and exceptions clear when applicable?
- Are units and ranges explicit?
- Is status consistent with evidence maturity?
- Is verification method appropriate for the requirement type?
- Are chip capability and project support separated?
- Are unsupported or excluded functions handled as boundaries or rejection requirements?
