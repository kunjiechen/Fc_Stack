# Extraction Rules for SRS Generation

Use these rules to extract structured information from engineering inputs before generating SRS requirement items.

The extractor must preserve source evidence, distinguish chip capability from project-supported software behavior, and mark unclear or incomplete information as `Draft` or `Open Issue`.

For chip datasheet processing, apply the multi-view parallel extraction design in `feature-extraction-design.md` first. These rules define the normalized fields and extraction record format; `feature-extraction-design.md` defines the extractor architecture, feature grouping, subfunction analysis, software responsibility judgment, and application-scheme output.

## 1. Raw Extraction Model

Raw extraction must be treated as two layers. Its job is not to decide final SRS wording, but to split raw input into stable items, remove metadata noise, preserve source references, normalize obvious fields, and prepare items for formal requirement gate classification.

### 1.1 Layer A: Structure Extraction

Responsible for:
- line splitting
- heading and metadata detection
- spreadsheet field extraction
- source reference preservation
- basic category hints

This layer answers: what raw item exists, where it came from, what fields it contains. It must not assume every extracted item is already a formal requirement.

### 1.2 Layer B: Semantic Disposition

Responsible for deciding whether the extracted item belongs to:
- `formal_requirement`
- `constraint`
- `capability`
- `metadata`
- `evidence`
- `architecture_seed_only`
- `test_seed_only`
- `open_issue`

This layer answers: should the item enter the formal requirement pool, should it stay as constraint/evidence only, should it feed only architecture/test seed.

### 1.3 Noise Filtering Rules

The following should normally be filtered before the formal requirement gate:
- module name
- module abbreviation
- document number
- chapter titles such as `原始功能需求`
- pure section labels without software behavior

These may remain in module identity or source inventory but should not become formal requirements.

### 1.4 Input Preference

When structured spreadsheet fields exist, prefer field meaning over free-text heuristics. When only plain text exists, use heuristics conservatively and preserve uncertainty.

### 1.5 Raw Item Output Requirement

Every raw extracted item should retain:
- source reference
- category hint
- normalized description
- disposition
- gate reason

Without those, later bundle validation cannot explain why an item entered or did not enter the formal pool.

## 2. Input Sources

Extract information from these source types:

| Source Type | Typical Content | Extraction Purpose |
| --- | --- | --- |
| Datasheet | Chip modes, pins, timing, electrical behavior, internal flags, wake/sleep behavior | Capture hardware capability and constraints |
| Project Requirement | Project-supported behavior, exclusions, API expectations, safety level, configuration scope | Determine final software responsibility |
| Source Code | Existing APIs, enums, structures, state variables, error handling, resource usage | Calibrate terminology and implementation-facing constraints |
| Configuration File | Instance count, core count, pin mapping, default mode, enable switches, ID ranges | Extract concrete configuration items and ranges |
| Test Material | Test cases, test reports, trace matrix, expected results | Extract verification intent and acceptance clues |

## 3. Source Priority

When the same topic appears in multiple sources, merge the evidence and assign priority:

```text
Project Requirement > Datasheet > Configuration > Source Code > Test Material
```

Priority guidance:

- Project Requirement decides project-supported behavior and exclusions.
- Datasheet defines hardware capability, mode table, pin behavior, timing values, and electrical facts.
- Configuration files define concrete project values, such as instance count, enabled cores, pin mappings, defaults, and ranges.
- Source code calibrates actual naming, enum values, API signatures, and already implemented behavior, but code alone should not invent requirements.
- Test material confirms verification intent, expected behavior, and coverage gaps, but tests alone should not create unsupported functional scope.

If sources conflict, do not silently choose one. Create a `Conflict` or `Open Issue` extraction record and preserve all conflicting evidence.

## 4. Extracted Field Types

### 4.1 Modes

Extract:

- Supported physical modes, such as `Normal`, `Standby`, `Sleep`, `Listen-only`, `Go-to-Sleep`.
- Project-supported software modes.
- Unsupported or prohibited modes.
- Mode aliases, enum values, and naming variants.
- Mode behavior and visible effects.

Extraction notes:

- A datasheet-supported mode is a hardware capability, not automatically a project-supported software mode.
- A project-prohibited mode should be extracted as an exclusion or forbidden item.
- Internal transitional states should be marked as internal unless project requirements expose them.

### 4.2 Pins

Extract:

- Pin name, such as `TXD`, `RXD`, `EN`, `STB_N`, `ERR_N`, `WAKE`, `INH`.
- Direction from chip perspective.
- Polarity, such as active-low behavior.
- Software ownership: controlled, sampled, ignored, owned by another module, or hardware-only.
- Configuration mapping to GPIO/DIO channel where available.

Extraction notes:

- If pin ownership is unclear, mark `Open Issue`.
- If a pin affects system behavior but is not controlled by software, record it as a constraint, not a software action requirement.

### 4.3 Interfaces

Extract:

- API names, such as `Init`, `SetMode`, `GetMode`, read/write APIs.
- Inputs and outputs.
- Return values.
- Preconditions and postconditions.
- Error behavior.
- Synchrony, such as synchronous/asynchronous behavior.

Extraction notes:

- API behavior must include success and failure semantics before it can become `Ready`.
- If return value mapping is missing, mark `Draft`.

### 4.4 Configuration Items

Extract:

- Core count.
- Enabled cores or core access mask.
- Instance count.
- Default mode.
- Instance ID range.
- Pin/channel mapping.
- Feature enable switches.
- Valid ranges, defaults, and invalid value handling.

Extraction notes:

- If a configurable value exists but range/default is unknown, mark `Draft` or `Open Issue`.
- Configuration must be linked to validation or review/test evidence where possible.

### 4.5 State Machine

Extract:

- States.
- Allowed transitions.
- Forbidden transitions.
- Trigger conditions.
- Guard conditions.
- Entry/exit behavior.
- Internal states and public states.

Extraction notes:

- Public API states and internal implementation states must be separated.
- If transition trigger or guard is missing, mark `Draft`.

### 4.6 Timing Values

Extract:

- Signal stabilization time.
- Mode transition delay.
- Minimum/maximum timing values.
- Timeout.
- Sampling delay.
- Hold time.
- Unit and direction, such as `>=8 us`, `<=10 ms`.

Extraction notes:

- Timing requirements must be measurable.
- If a timing statement contains words like "fast", "stable", "delay", or "wait" without a value, mark `Draft`.
- Preserve original unit and normalize to output style when generating SRS.

### 4.7 Prohibited Items

Extract:

- Unsupported modes.
- Forbidden inputs.
- Excluded chip capabilities.
- Project restrictions.
- Unsupported API values.
- Out-of-scope features.

Extraction notes:

- Prohibited items should become scope boundary, exception handling, or rejection requirements only when software has responsibility to reject or enforce them.
- If they are only project exclusions, keep them as constraints or overview notes.

### 4.8 Resource Constraints

Extract:

- Memory constraints: ROM, RAM, stack.
- CPU/load constraints.
- IO and pin usage.
- Channel allocation.
- Instance scaling.
- Buffer, interrupt, task, or polling constraints.

Extraction notes:

- If numeric budgets are unavailable, extract the requirement to evaluate and record usage, then mark budget as `Open Issue`.
- Source code may help estimate actual resource usage but should not replace project budget input.

## 5. Extraction Record Format

Use this structured Markdown format for extracted information:

```markdown
### EXT-{MODULE}-{TYPE}-{NNNN} {title}

| 字段 | 内容 |
| --- | --- |
| 类型 | {mode/pin/interface/configuration/state_machine/timing/prohibited/resource} |
| 名称 | {extracted_name} |
| 提取内容 | {normalized_extracted_content} |
| 软件责任判断 | {software_action/software_constraint/hardware_capability/project_exclusion/not_applicable/open_issue} |
| 来源 | {source_name}:{section_or_path}:{line_or_chunk} |
| 来源优先级 | {project_requirement/datasheet/configuration/source_code/test_material} |
| 证据强度等级 | {L1/L2/L3/L4/L5} |
| 合并依据 | {merged_sources_or_empty} |
| 冲突/缺口 | {conflict_or_gap_or_none} |
| 软件动作 | {api/register_read/register_write/pin_control/pin_read/state_save/parameter_check/reject_invalid/timing_wait/error_report} |
| 建议状态 | {Ready/Draft/Open Issue/Conflict/NotApplicable} |
| 可生成需求 | {Yes/No/Needs Review} |
| Ready 条件 | {conditions_required_before_ready} |
| 备注 | {notes} |
```

## 6. Aggregated Extraction Summary

For each module, also output an extraction summary:

```markdown
## Extraction Summary - {module}

### Modes

| 名称 | 类型 | 项目是否支持 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
{mode_rows}

### Pins

| Pin | 方向 | 软件关系 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
{pin_rows}

### Interfaces

| 接口 | 输入 | 输出 | 错误语义 | 来源 | 状态 |
| --- | --- | --- | --- | --- | --- |
{interface_rows}

### Configuration

| 配置项 | 范围/默认值 | 约束 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
{configuration_rows}

### State Machine

| 状态/过渡 | 触发 | 约束 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
{state_rows}

### Timing

| 时序项 | 数值 | 触发/适用条件 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
{timing_rows}

### Prohibited Items

| 禁止项 | 类型 | 软件是否需拒绝 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
{prohibited_rows}

### Resources

| 资源项 | 约束 | 来源 | 状态 |
| --- | --- | --- | --- |
{resource_rows}
```

## 7. Evidence Level

Every extraction record must include an evidence strength level. Evidence level is used to prevent Datasheet-only facts from becoming `Ready` requirements without project confirmation.

| Evidence Level | Meaning | Requirement Impact |
| --- | --- | --- |
| `L1 Project Requirement` | Project requirement explicitly states the behavior, scope, API, exclusion, safety level, or verification expectation. | May become `Ready` if software action and construction fields are complete. |
| `L2 Config/Source` | Configuration or source code already constrains or implements the behavior. | May support `Ready` after project confirmation; code alone must not invent scope. |
| `L3 Datasheet` | Datasheet explicitly describes the chip capability, register, pin, timing, or electrical behavior. | Default is `Needs Review`; can support candidate requirements only after software responsibility is confirmed. |
| `L4 Test Material` | Test material indirectly covers or expects the behavior. | Supports verification intent; tests alone must not create unsupported requirements. |
| `L5 Inference / Needs Confirmation` | The item is inferred by aggregation, naming, context, or incomplete evidence. | Must remain `Open Issue` or `Needs Review` until confirmed. |

Evidence level selection:

```text
Project Requirement -> L1
Configuration / Source Code -> L2
Datasheet -> L3
Test Material -> L4
Inference / aggregation without direct source -> L5
```

When several sources support the same feature, keep the strongest level and preserve all source evidence. If sources conflict, create `Conflict` or `Open Issue` instead of upgrading evidence.

## 8. Software Action Gate

A feature may enter candidate requirement generation only if at least one explicit software action exists.

Allowed software actions:

| Software Action | Meaning | Typical Requirement Type |
| --- | --- | --- |
| `api_call` | Software provides or calls an API. | Interface / Functional |
| `register_read` | Software reads a register. | Interface / Functional / Diagnostic |
| `register_write` | Software writes a register. | Interface / Functional / Configuration |
| `pin_control` | Software controls a pin. | Interface / Configuration / State |
| `pin_read` | Software reads or samples a pin. | Interface / Diagnostic / Functional |
| `state_save` | Software stores, caches, or reports state. | State / Functional |
| `parameter_check` | Software validates input, range, ID, enum, or configuration. | Interface / Configuration |
| `reject_invalid` | Software rejects unsupported or illegal input. | Interface / Diagnostic |
| `timing_wait` | Software waits, polls, delays, or handles timeout. | Timing / Diagnostic |
| `error_report` | Software reports, records, or returns errors. | Diagnostic / Interface |

Gate rule:

- If no software action exists, `Can Generate Requirement = No`, and the feature may only enter overview, constraints, or evidence notes.
- If a software action exists but project support or required fields are missing, `Can Generate Requirement = Needs Review`.
- If a software action exists, evidence is strong enough, and construction fields are complete, `Can Generate Requirement = Yes`.

## 9. Feature-to-Requirement Mapping

After feature aggregation, output a mapping table to connect extraction results with `construction-rules.md`.

Required format:

```markdown
## Feature-to-Requirement Mapping

| Feature | Evidence Level | Software Responsibility | Software Action Gate | Candidate Requirement Type | Ready 条件 | 当前状态 |
| --- | --- | --- | --- | --- | --- | --- |
| {feature_name} | {L1/L2/L3/L4/L5} | {software_responsibility} | {Pass/Blocked + actions} | {types} | {ready_conditions} | {Yes/Needs Review/No} |
```

Mapping rules:

- Functional requirements require a software action and verifiable behavior.
- Interface requirements require input, output, return/error semantics, and pre/post conditions.
- Configuration requirements require item, range/default, constraint, and invalid-value behavior.
- State requirements require state, trigger, guard, transition, and observable effect.
- Diagnostic requirements require observable error/status source and reporting or return behavior.
- Timing requirements require numeric value, unit, trigger, and software wait/timeout/sampling responsibility.
- Resource/nonfunctional requirements require budget, constraint, measurement method, or project acceptance criterion.

## 10. Required Inputs for Ready SRS

Extraction must output a reverse gap list focused on what must be provided before candidate requirements can become `Ready`.

Required format:

```markdown
## Required Inputs for Ready SRS

| 缺失项 | 影响需求 | 需要谁提供 | 示例 |
| --- | --- | --- | --- |
| API 命名 | 接口需求 | 软件架构 | Init / SetMode / GetMode |
| Pin 所有权 | 接口/配置需求 | 硬件/架构 | ERR_N 是否由本驱动读取 |
| 默认配置 | 配置需求 | 项目配置 | 默认模式、实例数 |
```

Typical required inputs:

| Missing Input | Owner | Example |
| --- | --- | --- |
| API naming and contract | Software architecture | `Init`, `ReadPin`, `WritePin`, return values |
| Pin ownership and wiring | Hardware / software architecture | `INT` connected to MCU, `RESET` controlled by driver |
| Default configuration | Project configuration | default direction, default output, device address |
| Runtime configuration policy | Project / software architecture | whether direction or polarity can change at runtime |
| Error handling | Software architecture / diagnostics | NACK, timeout, invalid ID return mapping |
| Timing responsibility | Software architecture / testing | wait after reset, I2C timeout, sampling delay |
| Verification method | Testing | UT, IT, HIL, review, analysis |
| Safety level | Safety / project | QM, ASIL level, diagnostic coverage expectation |

## 11. Accuracy Gate

Before SRS generation, every feature must pass this three-layer judgment:

```text
1. Feature has evidence
   ↓
2. Feature has at least one software action
   ↓
3. Feature satisfies Ready conditions from construction-rules.md
```

If any layer fails:

- No evidence -> `Open Issue`.
- Evidence exists but no software action -> `NotApplicable` or `No`, overview only.
- Software action exists but Ready fields are incomplete -> `Needs Review`.
- All layers pass -> candidate can become `Ready`.

## 12. Formal Requirement Gate

The gate between raw extracted items and the formal requirement pool enforces a key principle: **not every extracted item is a formal requirement**.

### 12.1 Disposition Meanings

| Disposition | Meaning |
|---|---|
| `formal_requirement` | Item expresses software behavior, interface, configuration, timing, or state obligations that can enter the formal requirement pool. |
| `constraint` | Item governs downstream design or verification (ASIL, MISRA, ROM/RAM budgets, DET policy) but is not itself a direct software behavior requirement. |
| `capability` | Item describes chip or project-supported capability not yet refined into implementation-ready software obligation wording. |
| `metadata` | Module names, document labels, section titles, and other non-requirement framing content. |
| `evidence` | Review, record, or assessment obligations rather than direct software behavior. |
| `architecture_seed_only` | Item primarily constrains architectural freeze decisions (multi-core ownership, memory partitioning, deployment boundary). |
| `test_seed_only` | Item is verification-oriented and should drive test design without being promoted to a formal software requirement. |
| `open_issue` | Item still depends on project confirmation, ownership clarification, or missing engineering decisions. |

### 12.2 Gate Rule

Only items with `disposition = formal_requirement` may enter the formal requirement pool automatically. All other items must stay outside the formal pool until a later explicit decision moves them in.

### 12.3 Why This Gate Exists

Without this gate, the pipeline drifts toward "extract anything → classify roughly → convert everything into requirement objects." That causes capabilities to be mistaken for requirements, nonfunctional constraints to be treated like functional behavior, and metadata to leak into downstream seeds.

### 12.4 Default Exclusions

At minimum, the gate must prevent these from entering the formal requirement pool by default:

- safety level statements
- coding-standard statements
- resource-budget statements
- module/document metadata

The machine-readable version of these gate rules is in `raw-classification-rules.yaml`.

## 13. Status Rules

- `Ready`: source is clear, meaning is unambiguous, and software responsibility is known.
- `Draft`: information is extractable but incomplete, vague, or not yet ready for SRS construction.
- `Open Issue`: source, ownership, priority, range, default, or software responsibility is unclear.
- `Conflict`: multiple sources disagree.
- `NotApplicable`: source capability exists but no software action, constraint, configuration, interface, or verification responsibility exists.

## 14. Extraction Rules

- Every extracted item must include source evidence.
- Every extracted item must include evidence level.
- Every candidate requirement feature must pass the software action gate.
- Every aggregated feature must appear in Feature-to-Requirement Mapping.
- Every missing Ready condition must appear in Required Inputs for Ready SRS.
- If multiple sources describe the same item, merge them and record source priority.
- Do not convert chip capability directly into a requirement without project software responsibility.
- Do not use source code alone to invent new project scope.
- Do not use test material alone to create unsupported functionality.
- Preserve unsupported modes and prohibited values as exclusions or rejection candidates.
- Mark unclear values, missing ranges, missing defaults, missing ownership, and missing verification intent as `Draft` or `Open Issue`.
- Output structured Markdown so the construction stage can directly consume the extraction results.
