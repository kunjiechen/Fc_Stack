# Calibration Rules for SRS Generation

Use these rules to calibrate writing style, judgment habits, and requirement granularity when generating new SRS items. They summarize accepted authoring preferences distilled from prior FC driver requirement work and should be treated as local writing guidance rather than source evidence.

Each rule should guide SRS generation and review. If a generated requirement violates these rules, revise the requirement, downgrade its status, or create an open issue.

Boundary of this file:

- This file captures local preference and judgment calibration.
- It does not redefine document chapter layout or rendering shape; that belongs to `authoring-standard.md` and `srs-output-template.md`.
- It does not replace per-category minimum fields or downgrade rules; those belong to `construction-rules.md`.
- Use this file to resolve ambiguous wording, granularity, capability-vs-project-support boundaries, and historical style choices.

## Rule 1: Separate Chip Capability From Project Support

Rule Name: `capability_project_support_separation`

Description: Datasheet-supported capability must not automatically become a project-supported software requirement. A capability becomes an SRS requirement only when the project assigns software responsibility, exposes an API, defines configuration, requires enforcement, or needs verification.

Example: TJA1043 supports `Listen-only` physically, but the project does not expose it as a public mode. The SRS should mention it as an excluded capability or rejection boundary, not as a supported mode requirement.

Applicability: 功能 / 状态 / 接口 / 配置 / 诊断

## Rule 2: Write Unsupported Modes As Rejection Requirements

Rule Name: `unsupported_mode_rejection`

Description: If a mode or input is explicitly unsupported by the project, generate a rejection requirement only when software receives or validates that input. The requirement must state that the request is rejected and existing state/output remains unchanged.

Example: `Listen-only` and `Go-to-Sleep` are not public API modes. `SetMode(Listen-only)` should return an error and must not change `STB_N`, `EN`, or software mode state.

Applicability: 功能 / 接口 / 状态 / 诊断

## Rule 3: Distinguish Software Request Mode From Physical Confirmed Mode

Rule Name: `software_request_vs_physical_confirmed_mode`

Description: `GetMode` or equivalent read APIs must clearly state whether they return the latest accepted software request, the physical confirmed chip state, or another status. Do not imply physical confirmation if the requirement only tracks accepted software requests.

Example: `GetMode` returns the latest accepted software request mode. After `SetMode(Sleep)` succeeds, `GetMode` may return `Sleep` even if physical Sleep is not confirmed.

Applicability: 接口 / 状态 / 诊断

## Rule 4: Treat Sleep Entry As A Controlled Software Request Plus Internal Transition

Rule Name: `sleep_request_internal_transition`

Description: Sleep mode requirements should distinguish public Sleep request semantics from internal chip transition paths such as `Go-to-Sleep`. Internal transitional states may be documented as implementation constraints or state-machine notes, but they must not be exposed as public modes unless the project requires it.

Example: `Go-to-Sleep` can be used internally to enter `Sleep`, but `Go-to-Sleep` must not be accepted by public `SetMode` or returned by public `GetMode`.

Applicability: 功能 / 状态 / 接口 / 时序

## Rule 5: Always State INH Power Impact For Sleep

Rule Name: `sleep_inh_power_impact`

Description: If Sleep mode affects `INH` or external regulator behavior, the SRS must explicitly state the system power impact and boundary of software responsibility. The module must not silently guarantee external power behavior that is controlled by system hardware.

Example: Sleep mode may cause `INH` to become floating and may turn off an external regulator. The SRS should state this as a safety/integration constraint.

Applicability: 功能 / 状态 / 安全 / 诊断 / 非功能

## Rule 6: Describe Pins By Function, Direction, Ownership, And Software Relation

Rule Name: `pin_description_ownership_relation`

Description: Pin descriptions should include chip-side direction, hardware function, and software relation. Software relation should be explicit: controlled by module, sampled by module, not used, owned by another module, or hardware-only.

Example: `STB_N` and `EN` are controlled outputs for mode selection. `INH` affects external power but is not directly controlled by the module.

Applicability: 概述 / 接口 / 配置 / 诊断

## Rule 7: Mark Unclear Pin Ownership As Open Issue

Rule Name: `unclear_pin_ownership_open_issue`

Description: Critical pins with unclear ownership must not be silently assumed. If ownership of `TXD`, `RXD`, `WAKE`, `INH`, `ERR_N`, `STB_N`, or `EN` is unknown, mark the related extraction or requirement as `Draft` or `Open Issue`.

Example: If `WAKE` appears in the datasheet but the project does not define whether software samples it, do not generate a software wake detection requirement as `Ready`.

Applicability: 接口 / 配置 / 诊断 / 状态

## Rule 8: Keep Overview For Capability Context, Requirements For Software Responsibility

Rule Name: `overview_vs_requirement_boundary`

Description: The overview may describe chip capability, pin facts, physical modes, and state machine context. Formal requirement sections should contain only software responsibilities, software-visible behavior, configuration, constraints, diagnostics, timing, or verification obligations.

Example: CAN FD fast phase support can be mentioned in the chip overview, while the SRS states that the module does not implement CAN frame handling.

Applicability: 概述 / 功能 / 接口 / 非功能

## Rule 9: Make Requirements Observable And Testable

Rule Name: `observable_testable_requirement`

Description: Requirement descriptions should state observable behavior, inputs, outputs, error handling, and acceptance criteria. Avoid vague words unless they are paired with measurable boundaries.

Example: Prefer "after mode change, wait at least 8 us before ERR_N sampling" over "wait until ERR_N is stable".

Applicability: 功能 / 接口 / 配置 / 诊断 / 时序 / 资源

## Rule 10: Use Failure Postconditions In Interface Requirements

Rule Name: `interface_failure_postcondition`

Description: Interface requirements should define what happens on invalid inputs or failed preconditions. Failure behavior should include return value and state/output preservation when applicable.

Example: If `SetMode` receives an invalid mode, it returns `E_NOT_OK` and keeps previous mode state and control outputs unchanged.

Applicability: 接口 / 功能 / 诊断

## Rule 11: Represent Configuration With Range, Default, And Validation

Rule Name: `configuration_range_default_validation`

Description: Configuration requirements should identify the configurable item, valid range or enumeration, default value when applicable, invalid-value handling, and validation phase.

Example: Core count is configurable in range `1..6`; values outside the range must fail configuration validation.

Applicability: 配置 / 资源 / 接口

## Rule 12: Separate Public State From Internal State

Rule Name: `public_state_internal_state_separation`

Description: Public states or modes exposed by API must be separated from internal helper states. Internal states may support implementation or explanation, but they should not appear as valid public API outputs unless explicitly required.

Example: `SleepPending` can exist internally after a Sleep request, but public `GetMode` should return `Sleep` if the accepted software request model is used.

Applicability: 状态 / 接口 / 诊断

## Rule 13: Preserve Source And Decision Rationale

Rule Name: `source_and_rationale_preservation`

Description: Requirements should preserve upstream source evidence and decision rationale, especially when project constraints override datasheet capability. The rationale can appear in scope boundary, source, or overview, but should not bloat the requirement statement.

Example: Source may include both `Datasheet-Operating modes` and `Project mode policy` when a datasheet mode is excluded by project policy.

Applicability: 功能 / 接口 / 配置 / 状态 / 需求来源

## Rule 14: Use Draft For Incomplete But Plausible Items

Rule Name: `draft_for_incomplete_items`

Description: If a requirement is plausible but missing source, ownership, range, default, return behavior, timing value, or verification method, keep it as `Draft`, `needs_source`, or `Open Issue`. Do not mark it `Ready`.

Example: A pin sampling requirement without a defined DIO channel or ownership should remain `Draft` or `Open Issue`.

Applicability: 全部

## Rule 15: Write Nonfunctional Requirements As Verifiable Obligations

Rule Name: `nonfunctional_verifiable_obligation`

Description: Nonfunctional requirements should still be verifiable. Resource, coding, safety level, and traceability requirements should state what artifact, analysis, review, or measurement proves compliance.

Example: ROM usage should be evaluated and recorded from link map output; MISRA compliance should be verified through static analysis and deviation records.

Applicability: 非功能 / 编码规范 / 资源 / 安全 / 过程质量

## Rule 16: Avoid Per-Section Requirement Overview Tables

Rule Name: `no_per_section_overview_tables`

Description: Do not generate large overview tables at the beginning of each requirement subsection. Use individual requirement blocks and, if needed, a single appendix requirement list.

Example: Do not place a big "功能需求总览表" before `SRS-...-FUNC-0001`. Use the requirement block directly.

Applicability: 输出模板 / 功能 / 非功能

## Rule 17: Do Not Repeat ID And Title Inside Requirement Body

Rule Name: `no_duplicate_id_title_fields`

Description: The requirement heading already carries the requirement ID and title. Do not repeat `需求ID` or `需求标题` inside the requirement body. This keeps requirement blocks compact and readable.

Example: Use heading `#### SRS-TJA1043-FUNC-0001 外设模式转换控制`, then continue with the status tags, prose description, and bullet constraint block.

Applicability: 输出模板 / 全部需求条目

## Rule 18: Prefer Boundary Language Over Hidden Assumptions

Rule Name: `boundary_language_over_hidden_assumptions`

Description: If a behavior depends on hardware, system power, configuration, ownership, or project policy, state the boundary explicitly. Do not hide assumptions inside generic requirement text.

Example: Standby entry may depend on supply and wake conditions; the SRS should state the software output behavior and the boundary of physical confirmation.

Applicability: 功能 / 状态 / 诊断 / 安全 / 配置

## Rule 19: Align Verification With Requirement Type

Rule Name: `verification_by_requirement_type`

Description: Verification method should match requirement type: behavior and interface requirements usually use Test; timing often uses Analysis/Test; configuration uses Review/Test; coding standards use Inspection/Analysis; resource constraints use Analysis.

Example: ERR_N low-active interpretation can use UT/IT; ROM usage should use Analysis from build artifacts.

Applicability: 全部

## Rule 20: Use Consistent Status Vocabulary

Rule Name: `consistent_status_vocabulary`

Description: Use a small, consistent status vocabulary. Preferred values are `Ready`, `Draft`, `needs_source`, `open_issue`, `conflict`, and `NotApplicable`. Do not invent new status terms unless the project explicitly provides them.

Example: If a requirement is missing source, use `needs_source` rather than "TBD source pending".

Applicability: 全部

## Rule 21: Avoid Head-Heavy Documents

Rule Name: `avoid_head_heavy_document`

Description: Keep front-matter, scope, and overview short. The document should place its main information weight in formal requirement sections, not in introductory explanation. Capability context belongs in overview only to the extent needed to understand later requirements.

Example: Do not use a long chip feature narrative, full register explanation, or dense communication timing dump when the real software obligations are only a few read/write, configuration, diagnostic, and timing requirements.

Applicability: 输出模板 / 概述 / 功能 / 非功能
