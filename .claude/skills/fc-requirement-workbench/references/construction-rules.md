# Construction Rules for SRS Generation

Use these rules when converting extracted requirement semantics into SRS requirement items. These rules define the minimum construction elements for each requirement category and the status handling when evidence or required fields are missing.

Generated requirements must be concrete, executable by software, verifiable, and traceable. If a source describes only a chip capability and no software action, interface, configuration, constraint, or verification responsibility exists, the capability should remain in the overview or source notes. Do not generate a formal SRS requirement for it unless the project scope assigns software responsibility.

Boundary of this file:

- This file owns per-category minimum required elements.
- This file owns missing-field downgrade handling and category-level `Ready/Draft/open_issue/needs_source` judgment.
- It does not define chapter layout or document prose style; those belong to `authoring-standard.md`.
- It does not define local historical writing preferences; those belong to `calibration-rules.md`.

## 1. 功能需求 Functional Requirements

Functional requirements describe observable software behavior, mode behavior, state behavior, data/control behavior, or user-visible module behavior.

Required elements:

- Title
- Description
- Source, such as Datasheet or Project Requirement
- ASIL/Level
- Verification Method
- Status

Recommended elements:

- Scope boundary
- Preconditions
- Trigger conditions
- Inputs
- Outputs
- Exception handling
- Acceptance criteria

Missing handling:

- If any required element is missing, set `Status` to `Draft`.
- If the source is missing but the behavior is engineering-plausible, set `Status` to `needs_source` or `open_issue`.
- If `Description` is empty, vague, or not observable, set `Status` to `Draft`.
- If the behavior is only a chip capability without software action, mark `NotApplicable` in intermediate analysis or omit it from SRS output.

Example:

- Title: 外设模式切换
- Description: 支持实例在 Normal/Standby/Sleep 切换
- Source: Datasheet
- ASIL: QM
- Verification Method: UT/IT
- Status: Ready

## 2. 接口需求 Interface Requirements

Interface requirements describe API behavior, input/output behavior, pin access, return value semantics, preconditions, and ownership of external interaction points.

Required elements:

- Title
- Description, including Input/Output behavior and Pre/Post conditions
- Interface function name (matching `aurix2g-normative-patterns.md` 1.1 classification rules for the module's AUTOSAR layer)
- Source
- ASIL/Level
- Verification Method
- Status

Recommended elements:

- Valid input range
- Return value mapping
- Failure postcondition
- Ownership or responsible layer
- Acceptance criteria

Missing handling:

- If any required element is missing, set `Status` to `Draft`.
- If ownership is unclear for a critical interface, set `Status` to `open_issue`.
- If return value or failure postcondition is undefined, set `Status` to `Draft`.
- If interface function name does not match the naming classification for the module's AUTOSAR layer (e.g., IoExtDev chip-level fault must use `GetDevFaultSig`, not `GetDiag`; IoMcu signal-level diagnostic uses `GetXxxSigDiag`), set `Status` to `Draft`.

Example:

- Title: SetMode 接口
- Description: 设置模式接口，仅接受 Normal/Standby/Sleep，返回 E_OK/E_NOT_OK
- Source: Project Requirement
- ASIL: QM
- Verification Method: UT/IT
- Status: Ready

## 3. 配置需求 Configuration Requirements

Configuration requirements describe configurable items, ranges, default values, ownership, consistency constraints, and invalid-configuration handling.

Required elements:

- Title
- Description, including configuration item, default value if applicable, and constraints
- Source
- Verification Method
- Status

Recommended elements:

- Valid range or enumeration
- Default value
- Configuration dependency
- Invalid value handling
- Configuration validation phase
- Acceptance criteria

Missing handling:

- If any required element is missing, set `Status` to `Draft`.
- If range or enumeration is implied but not explicitly known, set `Status` to `Draft` or `needs_source`.
- If ownership of configuration generation or validation is unclear, set `Status` to `open_issue`.

Example:

- Title: 内核数量配置
- Description: 支持配置 1~6 个内核
- Source: Project Requirement
- Verification Method: Review/Test
- Status: Ready

## 4. 诊断需求 Diagnostic Requirements

Diagnostic requirements describe status interpretation, diagnostic signals, internal flags, wake-related behavior, uninitialized access, parameter errors, controlled failure semantics, and readable fault/diagnostic status behavior when such faults exist.

Required elements:

- Title
- Description, covering ERR_N/Wake/internal flags/uninitialized/parameter error as applicable
- Source
- Verification Method
- Status

Recommended elements:

- Signal polarity or interpretation rule
- Applicable mode or state
- Fault or invalid-condition trigger
- Error return or unavailable-state behavior
- Readable fault/diagnostic status interface or equivalent observable mechanism
- Boundary where complete DEM/DTC design is outside scope
- Acceptance criteria

Missing handling:

- If any required element is missing, set `Status` to `Draft`.
- If diagnostic meaning cannot be supported by source evidence, set `Status` to `needs_source`.
- If software responsibility is unclear, set `Status` to `open_issue`.
- `DET` or equivalent development error detection is mandatory for externally callable modules and should be rendered as a formal requirement.
- If the module has fault detection or diagnostic behavior, include an interface requirement for fault/diagnostic readout such as `GetDevFault`, `GetDiag`, or a project-equivalent status interface.

Example:

- Title: ERR_N 低有效语义
- Description: LOW=置位, HIGH=清除, 保证诊断一致性
- Source: Datasheet
- Verification Method: UT/IT
- Status: Ready

## 5. 时序需求 Timing Requirements

Timing requirements describe mode transition timing, signal stabilization time, sampling delay, timeout, bounded wait, and timing responsibility.

Required elements:

- Title
- Description, including mode transition time or signal stabilization time
- Source
- Verification Method
- Status

Recommended elements:

- Numeric timing value and unit
- Minimum/maximum direction
- Trigger event that starts timing
- Action that is constrained by timing
- Responsibility, such as module-enforced or caller-guaranteed
- Acceptance criteria

Missing handling:

- If any required element is missing, set `Status` to `Draft`.
- If a timing statement has no numeric value or measurable boundary, set `Status` to `Draft`.
- If timing responsibility is unclear, set `Status` to `open_issue`.

Example:

- Title: ERR_N 稳定时间
- Description: 模式切换后读取 ERR_N 前需等待 >=8 us
- Source: Datasheet
- Verification Method: Analysis/Test
- Status: Ready

## 6. 资源需求 Resource Requirements

Resource requirements describe memory, CPU, stack, IO, pin, channel, instance, buffer, and resource conflict constraints.

Required elements:

- Title
- Description, including Memory/CPU/IO/pin usage constraints
- Source
- Verification Method
- Status

Recommended elements:

- Resource type
- Budget, limit, or measurement expectation
- Scaling rule, such as per-instance growth
- Conflict handling
- Measurement or analysis artifact
- Acceptance criteria

Missing handling:

- If any required element is missing, set `Status` to `Draft`.
- If the project budget is unknown, keep the requirement measurable by requiring recording/analysis and set the exact threshold as `open_issue`.
- If IO/pin ownership or conflict handling is unclear, set `Status` to `open_issue`.

Example:

- Title: IO 资源限制
- Description: 每实例分配固定 TXD/RXD 引脚，不得冲突
- Source: Project Requirement
- Verification Method: Review/Test
- Status: Ready

## 7. 状态判断规则 Status Rules

Status should be assigned by evidence maturity. This section is the source of truth for construction-time downgrade logic:

- `Ready`: all required elements are present, source evidence exists, behavior is software-actionable, and verification is defined.
- `Draft`: required fields are missing, description is vague, acceptance criteria are incomplete, or construction is still being refined.
- `needs_source`: behavior is plausible but lacks upstream evidence.
- `open_issue`: source, ownership, responsibility, or project decision is unresolved.
- `conflict`: sources or constraints disagree and require resolution.
- `NotApplicable`: source capability exists but does not map to a software action, interface, configuration, constraint, or verification responsibility.

Any missing required element must prevent `Ready`.

## 8. 前提条件

- Requirement items must be practical, executable, verifiable, and traceable.
- A formal SRS requirement must correspond to a software action, software responsibility, software-visible state, configuration item, diagnostic behavior, timing constraint, resource constraint, or process-quality requirement.
- If a feature is only provided by the chip but software has no action interface or responsibility, describe it in the overview or source context only.
- Before generating an item, determine whether the function maps to software responsibility. If not, mark it as `NotApplicable` in intermediate analysis or omit it from SRS output.
- All generated Ready items must follow the SRS output template field style and provide enough information for downstream design and verification.

Document-level writing balance, language compactness, and overview-vs-requirement placement are defined in `authoring-standard.md`.
