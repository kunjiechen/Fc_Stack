---
name: fc-architecture-workbench
description: Use when the user wants to design, review, validate, refine, or quickly draft an embedded automotive FC software architecture, including interfaces, configuration, calibration, runtime-state, dependency, and MemMap strategy.
---

# FC Architecture Workbench

## 1. Purpose

This skill supports embedded automotive FC software architecture work.

The skill is not a pure generator. It must first determine how much validation is actually necessary before running expensive architecture reasoning.

Core principle:

```text
Requirement
  -> Architecture Understanding
  -> Risk Evaluation
  -> Execution-Level Selection
  -> Output-Mode Selection
  -> Architecture Generation
  -> Validation & Refinement
```

This skill supports:

- new FC architecture generation
- architecture review and refinement
- concise architecture summary generation
- interface extraction
- configuration and calibration planning
- runtime-state governance
- dependency/callout strategy
- MemMap strategy
- omission-risk analysis
- requirement-to-architecture validation

## 1.1 Recent Project Corrections

These corrections are hard rules for all future FC architecture generation and review. Stable file-structure, naming, and release-process details live in `references/rules/*.md`; use this section as the compact execution summary.

- Architecture documents must include document metadata near the beginning and a closing metadata section at the end, including architecture version and generation time.
- Architecture versioning uses integer major versions only: `V1`, `V2`, `V3`, and so on. Do not use `V1.0`, `V1.1`, or patch/minor versions.
- Preserve the explicit FC/driver name as the C namespace for external APIs, dependency APIs, types, and objects. For example, `Gp_DRV8889` must generate `Gp_DRV8889_Init` and `Gp_DRV8889_CalloutSpiTransceive`, not `GpDrv8889_Init` or `GpDrv8889_CalloutSpiTransceive`.
- External FC API design should be presented one function at a time when prototypes or constraints are long. Avoid one oversized table that becomes unreadable after PDF generation.
- Callout prototypes must not use array declarators in parameters. Use pointer form such as `uint16* TxData_pu16`, `uint16* RxData_pu16`, and `uint16 Size_u16`.
- SPI/I2C external-device communication requires an `FC_Reg.h` carrier when register addresses, bit masks, command words, or frame constants are needed. `FC_Reg.h` includes `Std_Types.h`; `FC_Cfg.h` includes `FC_Reg.h` when configuration macros or tables depend on register definitions.
- If an FC uses Callout dependency interfaces, include both `FC_Callout.h` and `FC_Callout.c` in the file list. The `.h` declares the adaptation contract; the `.c` owns the project adaptation implementation or integration stub description.
- `FC_MemMap.h` is the MemMap carrier used by all FC-created source/header files at section boundaries, not only implementation files.
- CONST memory sections may be global or per-core. If configuration constants are core-local or replicated per core, include `FC_CONST_FAR_DATA_ALIGN4_COREx_START/STOP`; do not assume one global CONST section is sufficient.

## 1.2 Architecture Version And Release Workflow

Use `references/rules/release-workflow.md` as the source of truth for versioning, draft/release classification, risk-row handling, and release gate checks.

Compact execution summary:

- Requirement only -> initial `V1`, usually `V1 Draft` unless no real pending items exist.
- Draft architecture input -> update draft without bumping version.
- Released architecture + new requirement -> upgrade to next major version.
- Keep `Draft` while any real risk row remains `待评审` or `待修改`.
- Every update must carry a concise change summary.

## 2. Design Philosophy

Optimize for:

```text
correctness
traceability
minimum necessary interface exposure
clear configuration boundary
safe runtime-state governance
reasonable execution cost
```

Do not optimize for:

```text
maximum document size
maximum interface count
over-analysis on every request
```

The skill should dynamically scale reasoning depth while keeping final output mode stable and explicit.

## 2.1 Rule Responsibilities

Keep architecture guidance split by responsibility. Do not let `SKILL.md` grow into the long-term rule store.

- `SKILL.md`
  - execution entry
  - when to use the skill
  - input classification
  - execution-level selection
  - output-mode selection
  - minimal source-loading strategy
- `references/rules/*.md`
  - stable architecture rules
  - naming, file-carrier, dependency, release, and classification rules
- `references/templates/*.md`
  - output shape only
  - concise vs full architecture document structure
  - debug extraction layout
- `references/README.md`
  - retained reference index
  - minimal loading guidance

If a rule appears in multiple places, use this priority:

1. stable architecture rule meaning -> `references/rules/*.md`
2. output chapter shape and rendering contract -> `references/templates/*.md`
3. loading guidance and retained index -> `references/README.md`
4. execution flow and escalation logic -> `SKILL.md`

## 3. Source Priority

Priority order:

```text
User requirement
-> Project architecture constraint
-> Current project rules
-> Retained learning records
-> Demo patterns
-> AI inference
```

If sources conflict:

- prefer explicit user requirements and project constraints
- use demo only as comparison reference
- never blindly copy demo patterns
- if current local retained documents conflict with older study conclusions, prefer the current local retained documents for this workspace

## 4. Primary Sources

Main knowledge base:

- `docs/learning/AURIX2G_域控工程软件架构学习记录.md`
- `docs/guides/AURIX2G_架构设计细节学习与后续设计指导.md`

Rule layer:

- `references/rules/fc-architecture-rules.md`
- `references/rules/release-workflow.md`
- `references/rules/project-style-rules.md`
- `references/rules/naming-rules.md`
- `references/rules/static-vs-dynamic.md`
- `references/rules/interface-selection.md`

Templates:

- `references/templates/output-template.md`
- `references/templates/output-template-summary.md`
- `references/templates/extraction-debug-template.md`

Demo reference:

- `demo-lib/README.md`
- `demo-lib/MODULE_INDEX.md`
- `demo-lib/summaries/`

Demo summaries are reference only. If historical source-code paths are mentioned in the learning records, treat them as old study objects, not required live paths.

Use only the minimum source set needed for the current task. Stable rules should be read from `references/rules/*.md`; final output shape should be read from `references/templates/*.md`. Do not repeat full rule content in this `SKILL.md`.

## 4.1 Source Loading Strategy

Do not load all primary sources by default. Source loading must be staged to control execution time and context size.

Default minimal loading:

1. Read the user-provided requirement, architecture draft, or target output file.
2. Read this `SKILL.md` for execution rules.
3. Read only the selected output template:
   - `output-template-summary.md` for default validated concise output
   - `output-template.md` only for explicit full debug/trace output

Load rule files only when the task needs that rule area:

- `interface-selection.md`: interface extraction, interface omission, or API boundary questions
- `static-vs-dynamic.md`: configuration, calibration, runtime-state, global-variable, or macro-vs-table questions
- `naming-rules.md`: naming review or formal prototype/name generation
- `project-style-rules.md`: file structure, project style, MemMap style, or integration style questions
- `fc-architecture-rules.md`: broad architecture review, new module generation, or conflict resolution

Load retained learning records only when:

- the requirement is ambiguous and local architecture precedent is needed
- the task asks for AURIX2G-derived guidance
- the selected rule files do not provide enough basis
- a prior output quality issue requires deeper comparison

Load demo reference only when:

- the task needs implementation-style comparison
- dependency/callout or file-structure decisions are unclear
- the user explicitly asks to compare against demo patterns

When demo reference is needed, read `demo-lib/MODULE_INDEX.md` first, then read only the closest `demo-lib/summaries/<FC>.md` file. Do not expect retained source/config demo directories to exist.

Do not load archived PDFs during normal execution. Use retained Markdown rules instead unless the user explicitly asks for PDF-based verification.

Parallel file reads are allowed to reduce wall-clock time only after selecting the minimal file set. Parallelism improves speed but does not reduce context usage, so do not use it as a substitute for staged loading.

Prefer targeted reads over full-file reads:

- use headings, `rg`, and small line ranges to locate relevant sections
- summarize large source sections internally instead of carrying full text forward
- stop loading more sources once the decision has enough evidence

## 4.2 Progress Communication Rules

During execution, do not expose internal learning records, rule files, template paths, demo files, or retained source paths in user-facing progress updates.

Internal references may be read and used silently. Mention them only if the user explicitly asks what internal sources were used or asks for debug/trace details.

Progress updates should describe only the current work stage, for example:

- requirement understanding
- risk trigger evaluation
- execution-level selection
- output-mode selection
- interface classification
- configuration/dependency boundary check
- MemMap and runtime-state validation
- coverage and risk consolidation
- architecture output generation

Avoid progress text such as:

- reading `docs/...`
- checking `references/...`
- comparing with `demo-lib/...`
- loading internal templates

Final deliverables should list only user-facing business input documents. Internal retained learning records, rule files, templates, and demo comparison files must not appear as final input documents unless the user explicitly requests debug/source disclosure.

## 5. Inputs

Typical inputs:

- FC requirement document
- project architecture description
- AUTOSAR layer position
- platform/chip constraints
- MCAL dependency constraints
- multi-core requirements
- existing architecture draft
- interface draft
- file structure draft

If project facts are missing:

- do not invent them
- continue with explicit assumptions
- mark uncertain items as `Conditional`
- output pending confirmation items when the selected output mode allows them

## 6. Execution Level System

The skill uses dynamic execution levels. Execution level controls reasoning depth. It does not decide whether the final document is full or concise.

Default execution level:

```text
L2 Standard Mode
```

### L1 Fast Mode

Purpose:

```text
Quick architecture draft generation.
```

Use when:

- user requests a quick draft
- the FC is simple
- there is strong demo similarity
- no multi-core complexity exists
- no diagnosis complexity exists
- no interrupt/callback complexity exists
- no complex MemMap requirement exists

Execution flow:

```text
Requirement Extraction
-> Quick Interface Extraction
-> Lightweight Classification
-> Template Generation
```

Checks:

- basic interface completeness
- obvious configuration conflict
- global-variable exposure check

Do not run by default:

- full reverse trace
- deep omission analysis
- full conflict matrix

### L2 Standard Mode

Purpose:

```text
Balanced architecture generation and validation.
```

Use when:

- standard architecture work
- normal FC generation
- interface/config/runtime-state planning
- moderate complexity

Execution flow:

```text
Feature Extraction
-> Interface Classification
-> Implicit Interface Completion
-> Config/Calibration Separation
-> Basic Traceability
-> Generation
```

Checks:

- interface coverage
- configuration classification
- dependency separation
- runtime-state governance
- MemMap sanity

### L3 Deep Review Mode

Purpose:

```text
Formal architecture review and validation.
```

Use when:

- safety-related module
- multi-core/multi-instance
- interrupt-heavy behavior
- callback-heavy behavior
- diagnosis-heavy behavior
- complex MemMap
- ASIL
- requirement ambiguity
- architecture review request
- prior output quality issue

Execution flow:

```text
Explicit Extraction
-> Implicit Completion
-> Requirement Traceability
-> Reverse Architecture Support Check
-> Omission Analysis
-> Conflict Analysis
-> Validation Gate
-> Final Generation
```

Checks:

- bidirectional traceability
- omission risk
- false interface generation
- dependency leakage
- MemMap justification
- runtime-state correctness
- configuration/calibration correctness

## 7. Risk Trigger System

Upgrade execution level automatically if input contains:

- multi-core
- multi-instance
- interrupt
- callback
- diagnosis
- timeout
- fault handling
- calibration
- MemMap
- `NO_CLEAR`
- `NEAR`
- ASIL
- shared global state
- cross-core
- dependency callout
- retained data
- high-frequency control loop

Triggers force analysis. They do not guarantee final interface generation.

## 8. Output Mode System

Output mode controls the final artifact shape. It is independent from execution level.

Default output mode:

```text
Validated Concise Architecture Output
```

Default draft depth:

```text
Formal Draft
```

Use this output-mode decision rule before writing any deliverable:

- **Validated Concise Architecture Output**: use by default for new architecture generation, architecture rewrite, architecture completion, architecture definition, architecture design, architecture review with requested corrections, and any request that does not explicitly ask for debug/trace details.
- **Full Debug Architecture Output**: use only when the user explicitly asks for `debug`, `调试`, `完整版`, `完整模板`, `完整追踪`, `抽取过程`, `候选接口`, `反向追踪`, `遗漏矩阵`, `coverage matrix`, `full trace`, or equivalent process-level validation details.
- **Both outputs**: use only when the user explicitly asks for both a validated concise architecture document and a full debug/trace document. Keep them as separate artifacts.
- Updating or refining this skill based on prior architecture output deficiencies is not, by itself, a reason to generate a full debug output. First determine whether the requested deliverable is a skill update, a validated concise architecture document, or a debug/trace document.

### 8.1 Draft Depth

Draft depth controls how heavy the pending-risk section should be for draft architecture outputs.

- **Quick Draft**
  - use when the user asks for a quick draft, the FC is simple, or the goal is first-round discussion
  - generate the architecture body first
  - keep only the top `3..5` highest-value risk/pending-confirmation rows plus `R-OTHER`
  - skip exhaustive omission matrices, full candidate rejection logic, and long risk backlogs
- **Formal Draft**
  - use by default
  - generate the architecture body plus the full architecture risk and pending-confirmation table
  - include all meaningful pending confirmations needed for release review

Selection guidance:

- `L1` + concise output -> prefer `Quick Draft`
- `L2/L3` + concise output -> prefer `Formal Draft`
- if the user explicitly asks for fast first version, discussion draft, or skeleton architecture, use `Quick Draft`
- if the architecture is intended for review handoff or release preparation, use `Formal Draft`

## 9. Architecture Workflow

All execution levels follow:

```text
Understand
-> Extract
-> Classify
-> Validate
-> Generate
```

The difference is reasoning depth and how many validation artifacts are produced.

## 10. Architecture Object Classification

Classify into:

- external interfaces
- dependency interfaces
- configuration macros
- configuration tables
- calibration parameters
- runtime state
- internal static state
- memory macros
- file carriers
- assumptions
- pending confirmation items
- low-confidence items

When the task benefits from a structured intermediate layer, use `references/semantic-model.md` as the object contract before writing final Markdown. Prefer object-level validation first, then render into the selected output template.

Final output must distinguish:

```text
Formal
Conditional
Pending Confirmation
Not Recommended
```

## 11. Interface Extraction Rules

Always perform explicit extraction:

- extract directly stated interfaces
- extract directly stated dependency points
- extract directly stated configuration, calibration, and MemMap requirements

Perform implicit completion at the depth required by the selected execution level. Infer from:

- behavior
- data flow
- scheduling
- interrupts
- diagnosis
- configuration access
- calibration access
- dependency adaptation

### External Capability vs Internal Mechanism

When extracting interfaces, distinguish whether the requirement asks for a capability visible to external callers or an internal mechanism used by the FC.

Generate a formal external interface only when the requirement indicates that an external caller must request, read, set, or observe the result.

Do not generate a formal external interface when the requirement explicitly says the behavior is internal, such as:

- used for internal verification
- used for internal consistency check
- used internally to confirm a write
- used internally to diagnose communication reliability
- not exposed to external users

For internal mechanisms, classify the item as internal runtime behavior, dependency action, configuration macro, configuration table, or pending confirmation.

Example:

- `FC shall provide register readback through I2C to read chip register values for checking whether configuration or output values were written.` This is an external capability if callers are expected to request/read register values; extract an external API such as `GetReg...` or `ReadReg...` according to project naming rules.
- `FC shall provide register readback through I2C for internal verification that configuration or output values were written.` This is an internal consistency-check feature; do not create an external readback API by default. Extract a feature-level configuration macro such as `FC_CFG_REG_READBACK_VERIFY_ENABLE`, internal runtime/check logic, and the required I2C dependency interface.

## 12. Mandatory Interface Categories

Always scan:

1. Init
2. DeInit
3. MainFunction
4. External API
5. Internal API
6. Callback
7. Interrupt-related
8. Read interface
9. Write interface
10. Config access
11. Calibration access
12. Diagnosis interface
13. Status query
14. OS/scheduling
15. MCAL/dependency
16. MemMap-related integration items

If not applicable, mark as `Not Applicable` in internal analysis. Print that mark only in Full Debug Architecture Output or when the user asks for extraction/debug details.

## 13. Trigger-Word Scan

Force review when detecting:

- init/start/stop/reset
- periodic/task/schedule
- receive/send/report/notify
- read/write/update
- config/enable/disable
- timeout/error/fault
- calibration/threshold
- interrupt/callback/event
- memory section/MemMap
- retained data
- multi-core/core-id

Triggers force analysis. They do not guarantee final interface generation.

## 14. Traceability Rules

Each final or candidate interface should carry:

- module
- category
- parameters
- return value
- source requirement
- derivation basis
- confidence
- manual confirmation flag

Bidirectional traceability:

```text
Requirement -> Architecture
Architecture -> Requirement/Rule/Pattern
```

Low-confidence items must not directly enter formal generation. Keep them in `Pending Confirmation`, `Conditional`, or `Not Recommended` status.

## 15. Validation, Gate, and Failure Handling

Validation depth follows the selected execution level:

- `L1`: obvious interface omission, global-variable exposure, and basic configuration conflict.
- `L2`: interface completeness, config/calibration separation, dependency separation, runtime-state governance, and MemMap sanity.
- `L3`: bidirectional traceability, reverse support, omission risk, conflict analysis, dependency leakage, MemMap correctness, low-confidence isolation, and false interface generation.

Formal architecture output is allowed only when validation is complete to the selected level, blocking issues are identified, low-confidence items are isolated, and dependency/MemMap strategies are complete.

Acceptable architecture must satisfy:

- requirements map to architecture objects or are explicitly marked as non-interface/config/runtime only
- external interfaces have full attributes
- dependency interfaces are separated from external FC APIs
- config, calibration, runtime-state, dependency, and MemMap objects have evidence and ownership
- fake calibration, unnecessary external globals, and unexplained low-confidence items are excluded

If the gate fails or requirements are weak, output an assumption-based draft with pending confirmations, blocking issues, and a suggested fix plan. Do not invent interfaces, calibration, MemMap sections, or configuration macros to fill tables.

## 16. External Interface Rules

Prefer:

```text
Semantic API
```

Avoid:

```text
Generic Read/Write Naming
```

Default interface skeleton:

- `Init`
- optional `MainFunction`
- semantic `Get...` and `Set...` APIs

Use `Std_ReturnType` for most external runtime interfaces other than `Init` and `MainFunction`.

Getter-style interfaces use output pointers.

Function namespace rule:

- Use the explicit FC/driver name as the function prefix exactly as provided by the user or input document.
- Preserve underscores and capitalization in the module prefix.
- Example: `Gp_DRV8889` -> `Gp_DRV8889_Init`, `Gp_DRV8889_MainFunction`, `Gp_DRV8889_Set...`.
- Do not normalize `Gp_DRV8889` to `GpDrv8889` unless the user explicitly requests that namespace style.

When outputting external interface design, prefer a separate mini-table per function for readable PDF generation if any prototype, description, or constraint is long. A compact single table is allowed only for very short APIs.

Do not expose global variables directly. Prefer function-based access such as:

- `GetStatus`
- `GetFault`
- `GetValue`
- `SetRequest`
- `UpdateRequest`

If the requirement includes fault detection, diagnostic classification, interrupt anomaly tracking, or communication error reporting, prefer adding a readable fault/diagnostic query interface such as `GetFaultStatus` or `GetDiag` unless the source explicitly limits the behavior to internal-only handling.

## 17. Configuration Rules

Configuration macro-parameters must not be freely expanded. A macro may enter formal output only after passing a necessity check.

Configuration macro identifier naming is a hard rule:

- macro identifiers must be ALL_CAPS C preprocessor identifiers
- allowed characters are `A-Z`, `0-9`, and `_`
- the FC/module name portion must also be converted to uppercase
- valid examples: `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`, `DRV8876_CFG_DEV_ERROR_DETECT`
- forbidden examples: `Gp_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`, `Drv8876_CFG_DEV_ERROR_DETECT`, `DRV8876_Cfg_DEV_ERROR_DETECT`
- this rule applies only to macro identifiers, not file names such as `Drv8876_Cfg.h`, function names, type names, or configuration object names

Allowed formal configuration macro types:

1. Feature enable macro: controls whether an FC-level feature is compiled or enabled.
2. Development error detect macro: controls development-time parameter checking, DET checking, or error detection.
3. Behavior selection macro: selects implementation strategy at compile time.
4. Count / size macro: defines device count, channel count, instance count, table length, or buffer size.
5. Timeout / retry / timing macro: allowed only when the value is confirmed as a compile-time fixed strategy.
6. Vendor / version / release macro: used for vendor ID, module ID, software version, release version, or standard metadata.

Use configuration tables or const parameters, not macros, for normal mapping data, hardware binding, threshold tables, timing tables, and project data unless compile-time selection is proven.

Carrier mapping:

```text
FC_Cfg.h
FC_Cfg.c
FC_CfgData.h
```

Default priority:

```text
External Interface
-> Configuration Table
-> Const Parameter
-> Macro
```

Use a macro only when behavior truly needs compile-time trimming, conditional compilation, or a standard module switch.

Do not generate:

- macro for runtime variable state
- macro for calibration parameter
- macro for every hardware mapping item
- enable macro for every external interface
- feature switch for every minor subfunction
- duplicate macro for behavior already controlled by an external interface
- macro for internal helper function
- macro without clear usage location
- macro without clear default value source
- macro only for making the table look complete

If a subfunction is already expressed through a formal external interface, do not generate a one-to-one corresponding subfunction enable macro by default.

External interface means the architecture provides the capability. Configuration macro means the project can compile-time select, cut, or replace the capability. Interface existence does not imply an interface-level macro is required.

Subfunction macros are allowed only for key subfunctions with project trimming value, such as:

- project-trimmable feature
- optional hardware feature
- optional diagnosis feature
- optional communication feature
- optional safety/protection feature
- optional filter/limit/protection strategy
- internal consistency-check feature, such as register readback verification after write/configuration
- project-differentiated feature
- feature with meaningful compile-time replacement or exclusion

If a requirement explicitly states that a subfunction is for internal verification rather than external caller access, prefer a feature-level configuration macro over an external interface when the feature has compile-time/project trimming value.

Configuration macro necessity check:

| Check Item | Required Result |
| --- | --- |
| Does it control a key subfunction? | Yes |
| Does it have project trimming or compile-time selection value? | Yes |
| Is it not a one-to-one duplicate switch of an external interface? | Yes |
| Does it affect compile-time behavior or integration-time fixed behavior? | Yes |
| Does it have a clear usage location? | Yes |
| Does it have a clear default value? | Yes |
| Does it have requirement, rule, or demo evidence? | Yes |

If the check is not satisfied, downgrade the item to `Conditional`, `Pending Confirmation`, or `Not Recommended`.

Configuration macro-parameters must use this fixed output format:

```text
Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status
```

The `Macro or Parameter` value must obey the ALL_CAPS macro identifier rule.

Allowed status values:

```text
Formal
Conditional
Pending Confirmation
Not Recommended
```

## 18. Calibration Rules

Only create calibration parameters when real evidence exists.

Calibration must include:

- name
- type
- initial value
- description
- status

If no calibration exists:

```text
Empty
```

is valid and preferred over invented parameters.

## 19. Runtime-State Rules

Default external global-variable status:

```text
Empty
架构不允许对外提供全局变量输出。
```

Internal runtime state should define:

- owner
- read/write side
- lifecycle
- memory section
- concurrency strategy

Prefer structured runtime containers over scattered globals.

## 20. Dependency Strategy

Dependency interfaces must not be freely generated or freely omitted.

Core principle:

```text
FC does not directly implement low-level hardware control.
```

When FC needs to operate external hardware, external signal, or platform resource, it must use dependency interface / callout abstraction.

The concrete implementation may be provided by:

- MCAL
- IoMcu
- IoExtDev
- Service Layer
- Project Adaptation Layer

The FC architecture must not assume the concrete implementation layer unless the project explicitly specifies it.

Dependency priority:

```text
Standard Layer
-> Project Abstraction
-> Callout
-> Macro Replacement
-> Direct Dependency
```

Mandatory callout scenarios normally include:

1. IO / DIO operation: read DIO input, set DIO output, get IO state, control external chip pin.
2. SPI/I2C communication: transmit/write, receive/read, transceive, sequence trigger, error/status query.
3. PWM control: set PWM output, get PWM duty cycle, start PWM, stop PWM, get PWM status.
4. ADC / sensor acquisition: read ADC raw value, read converted sensor value, get sampling status, trigger acquisition.
5. External chip control: read/write external chip register, control external chip pin, get external chip fault/status.
6. Platform capability: get core ID, get system tick, enter/exit critical section, report diagnosis/error, get platform state.

Recommended naming:

- `FC_CalloutReadDio(...)`
- `FC_CalloutWriteDio(...)`
- `FC_CalloutSpiTransmit(...)`
- `FC_CalloutSpiReceive(...)`
- `FC_CalloutSpiTransceive(...)`
- `FC_CalloutI2cWrite(...)`
- `FC_CalloutI2cRead(...)`
- `FC_CalloutI2cTransceive(...)`
- `FC_CalloutSetPwmDuty(...)`
- `FC_CalloutGetPwmDuty(...)`
- `FC_CalloutReadAdc(...)`
- `FC_CalloutReportError(...)`
- `FC_CalloutGetCoreId(...)`

Replace `FC` with the exact FC/driver namespace from the input. For `Gp_DRV8889`, use `Gp_DRV8889_CalloutGetCoreId`, not `GpDrv8889_CalloutGetCoreId`.

Callout parameter rules:

- Do not use array declarators such as `uint8 Data_au8[]` in any callout prototype.
- Use pointer parameters with explicit pointee width, for example `uint16* TxData_pu16` and `uint16* RxData_pu16`.
- Use `uint16 Size_u16` for transfer size/count parameters unless a narrower size is explicitly required by a project rule.
- For 16-bit SPI frame devices, the SPI callout data pointer type should be `uint16*` so callers do not need local casts between byte buffers and SPI frame buffers.
- If byte-oriented I2C payloads are required, use `uint8*` pointer form and still use `uint16 Size_u16` for length.

Project naming rules may override the prefix. However, the name must reflect FC intent, operation, and hardware/resource type.

Dependency interface decision rule:

```text
FC-required hardware action
-> abstract as callout
-> implemented by another layer
```

Do not assume the implementation owner inside FC unless explicitly specified.

Allowed implementation description:

```text
Implemented by MCAL / IoMcu / IoExtDev / Service Layer / Project Adaptation Layer.
```

Use callout for:

- project adaptation
- core selection
- platform-specific behavior
- hardware/platform actions outside FC ownership

Do not leak low-level APIs upward.

Forbidden direct dependency:

- FC directly calls raw MCAL API
- FC directly operates registers
- FC directly binds to a concrete IoMcu implementation
- FC directly binds to a concrete SPI/PWM/DIO/ADC driver
- FC exposes low-level driver details in external interfaces
- callout prototype leaks excessive MCAL-specific parameters
- dependency interface is generated without a call scenario
- dependency interface is generated without clear owner/implementation layer
- dependency interface is generated without return value semantics

Dependency necessity check:

| Check Item | Required Result |
| --- | --- |
| Does FC need a hardware/platform action? | Yes |
| Is the action outside FC ownership? | Yes |
| Should the implementation be provided by another layer? | Yes |
| Is there a clear call timing? | Yes |
| Are input/output semantics clear? | Yes |
| Is return value/error handling clear? | Yes |
| Is there requirement, rule, or hardware-action evidence? | Yes |

If the check is not satisfied, downgrade the item to `Conditional`, `Pending Confirmation`, or `Not Recommended`.

Dependency interfaces must use this fixed output format:

```text
Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status
```

Rules:

- Prefer one mini-table per dependency function when prototypes, descriptions, constraints, evidence, or implementation notes are long. A compact combined table is allowed only for very short dependency lists.
- `Description` must be a complete English sentence.
- `Implemented By` may be `MCAL`, `IoMcu`, `IoExtDev`, `Service Layer`, or `Project Adaptation`.
- Dependency interfaces must not be mixed into the external FC API section.
- Dependency interfaces must have clear call scenario and ownership boundary.
- Allowed status values are `Formal`, `Conditional`, `Pending Confirmation`, and `Not Recommended`.

When presenting callout, show both:

- whether callout is required, optional, or not recommended
- the recommended callout prototypes when callout is needed

Dependency interfaces such as `CalloutGetCoreId` must be listed as dependency interfaces, not mixed into the external FC API section.

Macro and dependency anti-divergence rule:

- Configuration macro-parameters should be conservative.
- If a key subfunction has project trimming value, generate a feature-level configuration macro.
- Dependency interfaces should be generated according to hardware/platform actions.
- If FC needs to operate IO, SPI, PWM, ADC, an external chip, or a platform resource, abstract the action as a callout.
- Internal register readback verification still requires I2C/SPI dependency abstraction; internal use only changes external API extraction, not the dependency-interface requirement.
- Feature-level macro is preferred over interface-level macro.
- Hardware-action callout is preferred over direct MCAL dependency.
- Project adaptation is preferred over FC internal hard binding.

Only objects satisfying all of the following may enter formal output:

- has requirement/rule/evidence
- has usage location
- has default value or return value semantics
- has clear owner or implementation boundary
- does not duplicate an external interface or configuration table
- does not expose unnecessary implementation detail

Otherwise downgrade to `Conditional`, `Pending Confirmation`, or `Not Recommended`.

## 21. MemMap Rules

Always consider:

- `CODE`
- `CONST`
- runtime RAM
- optional calibration

CONST section selection:

- Use `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_START/STOP` for truly shared configuration constants.
- Use `FC_CONST_FAR_DATA_ALIGN4_COREx_START/STOP` when const data is core-local, replicated per core, or selected by core ownership.
- If both shared and per-core const objects exist, list both macro pairs.

Default runtime RAM:

```text
CLEAR_FAR_DATA
```

Do not default to:

```text
NO_CLEAR
NEAR
```

Use `NO_CLEAR` only when there is an explicit lifecycle need such as warm-reset retention or equivalent retained-data requirement.

Use `NEAR` only when the requirement explicitly implies high-frequency interrupt execution with strict timing constraints, such as fast control-loop or FOC-style access paths.

Items such as `NO_CLEAR` or `NEAR` should appear in the final architecture only as conditional items unless the input explicitly requires them.

When presenting MemMap, explain the selection rule, not just the macro names.

## 22. File Carrier Rules

Default carriers:

- `Std_Types.h` (external standard header, referenced but not created by this FC)
- `FC.c`
- `FC.h`
- `FC_Types.h`
- `FC_Cfg.h`
- `FC_Cfg.c`
- `FC_CfgData.h`
- `FC_Reg.h` when the FC controls an SPI/I2C/register-based external device
- `FC_Callout.h`
- `FC_Callout.c` when callout implementation or project adaptation stubs belong to the FC integration package
- `FC_MemMap.h`

Include:

- file responsibility
- dependency relationship
- ownership boundary
- header carrier mapping
- external standard header relationship

The `Input Documents` section of final architecture output should list only user-facing business input documents. Do not list retained learning records, rule files, or demo comparison files as final input documents.

The default include relationship should follow the FC project-style pattern below unless the project explicitly defines a different one:

- `FC_Cfg.h` includes `Std_Types.h`.
- `FC_Reg.h`, when present, includes `Std_Types.h` and carries register addresses, bit masks, command words, frame constants, and protocol data constants.
- `FC_Cfg.h` includes `FC_Reg.h` when configuration macros, register default values, or configuration tables use register symbols.
- `FC_Types.h` includes `FC_Cfg.h`.
- `FC_Callout.h` includes `FC_Types.h`.
- `FC.h` includes `FC_CfgData.h`.
- `FC_CfgData.h` includes `FC_Types.h`.
- `FC.c` includes `FC.h`, `FC_Callout.h` when callout is used, and `FC_MemMap.h`.
- `FC_Cfg.c` includes `FC_CfgData.h` and `FC_MemMap.h`.
- `FC_Callout.c`, when present, includes `FC_Callout.h` and `FC_MemMap.h`.
- `FC_Cali.c`, when present, includes `FC_CfgData.h` and `FC_MemMap.h`.
- `FC_MemMap.h` is included by all FC-created files that place code, const data, calibration data, or runtime data into sections. Treat it as a section-boundary include relationship, not a normal type dependency.

`Std_Types.h` and other platform standard headers are external dependencies. They should appear in file relationship tables, but must not be listed as files to create for the FC.

## 23. Full Debug Architecture Output

Use `references/templates/output-template.md` as the primary shape for the full architecture deliverable.

Full Debug Architecture Output is not the default architecture deliverable. Use it only when the user explicitly requests debug/trace/process-level validation details.

Full Debug Architecture Output should include:

- architecture summary
- external interface design
- dependency interface design
- file list
- file-to-file dependency relationship
- header carrier mapping
- configuration macro-parameter strategy
- configuration tables and mapping tables
- calibration parameter strategy
- runtime-state strategy
- MemMap strategy
- validation summary
- omission risk
- pending confirmation

For architecture extraction work in Full Debug Architecture Output mode, the final result should not stop at a plain interface list.

Include according to execution level:

- interface list with confidence
- requirement coverage table
- omission risk list
- pending confirmation items
- low-confidence interfaces that are not recommended for direct code generation

## 24. Validated Concise Architecture Output

Use `references/templates/output-template-summary.md` as the primary shape for the concise summary deliverable.

The validated concise architecture output is the default architecture deliverable. It is not a shortened dump of the full debug architecture. It is a formally shaped architecture result with selected validation evidence and without debug/process tables.

Include these 10 high-level sections by default:

1. FC summary introduction
2. requirement coverage table
3. external interface design
4. configuration macro-parameter design
5. global variable and runtime-state strategy
6. full MemMap macro design
7. global calibration parameter design
8. dependency interface design
9. file list and file relationship
10. architecture risk and pending confirmation

Do not include unless explicitly requested:

- requirement extraction tables
- reverse trace tables
- full validation matrix
- low-confidence interface analysis
- detailed dependency inventory
- raw omission-risk list
- interface candidate list

The validated concise output must include selected validation evidence:

- a requirement coverage table, compressed to requirement ID, architecture coverage object, coverage status, and notes
- the full MemMap macro table from the full architecture template
- a file list and file-to-file relationship table
- an "architecture risk and pending confirmation" section that compresses omission risks, assumptions, and open questions into reviewable action items

Use internal validation checks to avoid omissions, but fold confirmed conclusions into the 10 concise sections instead of printing the analysis tables.

Do not print debug/process details such as extraction rounds, discarded candidate interfaces, reverse trace matrices, raw omission matrices, or low-confidence interface analysis unless the user explicitly asks for Full Debug Architecture Output.

### Concise FC Summary Introduction

Must explicitly cover:

- architecture version
- architecture status: `Draft` or `Released`
- generation time
- concise change summary when this is an architecture update or upgrade
- FC functional introduction
- application scenario
- architecture design idea
- AUTOSAR architecture layer
- current software layer position such as `IoExtDev` when applicable

Layer names and architecture terms may use English. All other descriptive content in this section must be in Chinese.

### Concise External Interface Design

Present as a table with exactly these columns:

- `Interface Prototype`: full C function prototype, e.g. `Std_ReturnType Gp_BTS7x_DIO_GetDevFaultSig(uint16 Id_u16, uint32* DevFault_pu32)`
- `Description`: complete English sentence describing what the interface does
- `Sync/Async`: `Synchronous` or `Asynchronous`
- `Reentrancy`: `Reentrant` or `Non-reentrant`
- `Return Value`: `E_OK` / `E_NOT_OK` or `void`
- `Basic Constraints`: initialization dependency, parameter validity, core ownership, pointer non-null, call timing, etc.

Each external interface must appear as a separate row. `Init` and `MainFunction`, if present, must also appear in this section with their Sync/Async and Reentrancy attributes.

For PDF-friendly concise output, prefer one mini-table per function using the same columns when the combined table would be too wide. Do not compress important constraints merely to fit a single table.

### Concise Configuration Macro-Parameter Design

Present as a table with exactly these columns:

- `Macro or Parameter`: full ALL_CAPS macro name, e.g. `DRV8876_CFG_DEV_ERROR_DETECT`
- `Purpose`: short description of what the macro controls
- `Type`: `Macro` or specify the type if a const parameter
- `Default Value`: recommended default
- `Evidence`: requirement ID, project rule, retained rule, or demo pattern that justifies the macro
- `Usage Location`: expected file/function/compile condition where the macro is used
- `Status`: `Formal`, `Conditional`, `Pending Confirmation`, or `Not Recommended`

Show only macro-parameters that pass the configuration macro necessity check.

Do not show per-core macro-parameters, per-core instance counts, core-local mapping items, project data tables, hardware binding tables, thresholds, retry counts, or timing values unless the user explicitly asks for them.

If a subfunction is already controlled through a formal external interface, do not also present a duplicate subfunction feature-switch macro.

Do not add macros just to make the table look complete. If a potential macro lacks evidence, usage location, or default value source, downgrade it to `Conditional`, `Pending Confirmation`, or `Not Recommended`.

### Concise Global Variable Design

Default status must be:

```text
Empty
架构不允许对外提供全局变量输出。
```

Do not list internal static variables or internal runtime containers in this section.

### Concise Requirement Coverage Table

Present as a table with exactly these columns:

- `Requirement ID`: requirement identifier or grouped requirement identifier
- `Requirement Summary`: short Chinese summary
- `Architecture Coverage`: interface, configuration, runtime state, dependency, MemMap, or file carrier that covers it
- `Coverage Status`: `Covered`, `Partially Covered`, or `Pending Confirmation`
- `Notes`: concise explanation or remaining condition

This table is validation evidence, not a debug extraction table. Do not include extraction rationale, candidate history, reverse trace details, or low-confidence analysis here.

### Concise Memory Macro Design

Use the full MemMap output shape from the full architecture template. Present as a table with exactly these columns:

- `Memory Section`: code, const, runtime RAM, calibration, or conditional section name
- `Target Content`: content covered by the section
- `Start Macro`: entry macro
- `Stop Macro`: exit macro
- `Used Files`: files expected to use the macro pair
- `Notes`: selection rationale, per-core applicability, or conditional status

Include the full recommended MemMap macro set needed for architecture review. If per-core sections exist, it is acceptable to summarize repeated core variants with `COREx` notation when the pattern is identical, but do not omit section categories needed to judge correctness.

If const data is per-core or may be core-local, include `FC_CONST_FAR_DATA_ALIGN4_COREx_START/STOP` in addition to or instead of the global CONST macro. Do not collapse all const data into one global section when the runtime architecture is core-partitioned.

### Concise Global Calibration Parameter Design

Present as a table with exactly these columns:

- `Parameter Name`: full name
- `Type`: C type
- `Initial Value`: numeric or macro literal
- `Description`: Chinese sentence describing the parameter
- `Status`: `Formal`, `Conditional`, or `Empty`

May be `Empty` when no validated calibration need exists.

When empty, write a single row:

```text
Empty | N/A | N/A | 当前无确认的全局标定参数 | Empty
```

Do not invent calibration parameters just to fill the section.

### Concise Dependency Interface Design

Prefer one mini-table per dependency interface for PDF-friendly output. Use this exact table format for each dependency function:

- `Interface Prototype`
- `Description`
- `Sync/Async`
- `Reentrancy`
- `Return Value`
- `Basic Constraints`
- `Implemented By`
- `Evidence`
- `Status`

List dependency interfaces, callout prototypes, and macro-replaced hooks here, not mixed into the external FC API section.

Each dependency interface must show:

- full C prototype, e.g. `uint32 DRV8876_CalloutGetCoreId(void)`
- description in English
- `Synchronous` or `Asynchronous`
- `Reentrant` or `Non-reentrant`
- return value semantics
- basic constraints, including platform adaptation contract and expected behavior
- implementation owner boundary, such as `MCAL`, `IoMcu`, `IoExtDev`, `Service Layer`, or `Project Adaptation`
- requirement, rule, or hardware-action evidence
- status: `Formal`, `Conditional`, `Pending Confirmation`, or `Not Recommended`

SPI/I2C callout prototypes must use pointer parameters, not array declarators. For 16-bit SPI frame protocols, use `uint16*` data pointers and `uint16 Size_u16`.

A compact combined dependency-interface table is allowed only when all dependency prototypes and constraints are short. Do not drop implementation boundary, evidence, or constraints just to fit one wide table.

### Concise File List and File Relationship

Include a file list table with exactly these columns:

- `File`
- `Required/Optional`
- `Responsibility`
- `Key Content`

Include a file relationship table with exactly these columns:

- `File`
- `Direct Dependency`
- `Relationship Description`

Keep this section architecture-facing. Do not include internal study references, retained rule files, or demo files as final input documents or file dependencies.

The file relationship table must include external standard header dependencies such as `Std_Types.h` when they are required for `Std_ReturnType`, `uint8`, `uint16`, `uint32`, `boolean`, or AUTOSAR standard macros. Mark them as external headers and do not list them as FC-created files.

For SPI/I2C/register-controlled external devices, include `FC_Reg.h` in the file list and file relationship table. For any FC with callout dependencies, include `FC_Callout.c` together with `FC_Callout.h`.

The file relationship table must show `FC_MemMap.h` as included by all FC-created files that place code or data into memory sections.

### Concise Architecture Risk and Pending Confirmation

Compress omission risks, assumptions, weak evidence, and open questions into one table with exactly these columns:

- `索引`
- `问题项`
- `问题/风险`
- `影响`
- `建议动作`
- `备注`
- `状态`

Allowed `状态` values for this risk review table:

- `待评审`: user has not decided this item yet
- `已评审`: user has reviewed and accepts the current architecture handling, or the requested change has already been incorporated
- `待修改`: user expects the architecture to be modified based on this item

Always include an `R-OTHER` / `其他` row for user-supplied additional suggestions or concerns.

`备注` records the user's specific opinion or modification instruction. If `状态` is `待修改` and `备注` is empty, execute the row's `建议动作`. If `备注` is present, follow the remark first.

Draft-to-release rule:

- If any real row remains `待评审` or `待修改`, keep architecture status as `Draft`.
- Promote to `Released` only when every real risk item is `已评审`.
- A released architecture plus a requirement document triggers the next major version (`V1 -> V2`, `V2 -> V3`).

Chat-friendly review examples:

- `R1、R2、R3 已评审。`
- `R4 待修改，备注：恢复策略改为先 nSLEEP 复位，再 CLR_FLT。`
- `其他：无其他建议，已评审。`
- `全部已评审，直接发布。`

This section replaces the raw omission-risk list in the default output. Do not include debug-style omission matrices, candidate-interface rejection details, or full low-confidence analysis unless explicitly requested.

## 25. Review and Skill Validation

When reviewing architecture, focus on:

- interface omission
- overexposed interfaces
- weak runtime-state governance
- dependency leakage
- MemMap gaps
- configuration abuse
- calibration abuse
- unclear ownership
- traceability weakness

Output findings as:

```text
Issue
Impact
Recommendation
Priority
```

For review requests, default to L3 Deep Review Mode unless the user explicitly asks for a lightweight review.

When validating this skill itself, use representative cases for basic driver, interrupt/callback, config/calibration, multicore, and fault diagnosis. Judge by requirement coverage, interface recall, false interface count, MemMap correctness, config classification accuracy, calibration invention count, and dependency separation correctness.

Final optimization rule: prefer correctness, reasonable complexity, traceability, maintainability, and architecture closure over more files, more tables, or more interfaces. Every formal interface, configuration item, runtime-state item, dependency, and MemMap strategy must be explained by requirements, rules, or architecture constraints.
