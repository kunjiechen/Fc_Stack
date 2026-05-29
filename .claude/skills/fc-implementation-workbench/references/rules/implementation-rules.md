# FC Implementation Rules

## Purpose

This file owns the stable high-level rules for FC implementation-oriented detailed design.

It answers the recurring implementation questions that should not be re-invented for every FC:

- how much design detail is enough
- when to choose single-core or multi-core structure
- when `MainFunction` is needed
- when `Callout` is mandatory
- when `Cfg.c` is mandatory
- when `Internal.h` is justified
- when `NoClear` should exist

## 1. Core Position

Implementation design is the bridge from requirement and architecture to code.

It must be explicit enough that coding can start without guessing:

- file family
- API family
- cfg shape
- runtime-state ownership
- state-machine layout
- DET flow
- fault-handling path
- MemMap strategy

Implementation design is not:

- an architecture restatement
- a final full code dump
- a chip-manual replacement

## 2. Minimum Design Principle

For normal FC work, the design should be the minimum set that can constrain a main implementation, not a prose rewrite of architecture.

Use this rule:

- if developers would still need to guess file layout, API ownership, cfg placement, runtime ownership, or state transitions, the design is still too weak
- if the design contains large amounts of prose that do not affect coding choices, it is too heavy

## 3. Stable Rules

- separate configuration state from runtime state
- separate external APIs from dependency APIs from internal functions
- separate DET from runtime fault handling
- separate platform variability through `Callout` when needed
- treat multi-core ownership as a first-class design object
- treat `MemMap` and `NoClear` as design decisions, not later cleanup
- prefer explicit state-machine objects over hidden transition logic
- every runtime object must have owner, lifecycle, and read/write side
- every major design choice should be either confirmed by source or explicitly marked as assumption
- do not use variable interfaces as the normal FC boundary
- keep FC layer coupling function-based
- keep external-interface defensive checks at the interface boundary by default

## 4. Input Sufficiency

`L1`

- requirement + architecture
- output must preserve assumptions

`L2`

- requirement + architecture + company rules + reference FC
- output can be coding-oriented and relatively stable

`L3`

- requirement + architecture + company rules + chip manual + reference FC
- output may be code-generation-ready at scaffold level

Practical rule:

- below `L2`, avoid pretending to know exact cfg values, fault thresholds, or platform bindings
- at `L2` and above, structure can be strong even when some project values remain open

## 5. Framework Selection Rules

### 5.1 Single-Core vs Multi-Core

Choose `single-core` when all are true:

- one core owns the logic
- no cross-core synchronization is required
- runtime state does not need per-core partitioning
- task ownership can be expressed by one execution owner

Choose `multi-core` when any are true:

- different cores own different runtime objects
- monitoring or sampling is naturally per-core
- initialization needs cross-core synchronization
- tasks are split by core
- shared state exists and must be made explicit

Do not choose multi-core only because the platform has multiple cores. Choose it only when the FC behavior actually depends on core separation.

**Single-core purity rule:** When single-core is chosen, the design must not leak multi-core patterns into any design artifact. Specifically:

- flowcharts must not contain core matching, core traversal, `CalloutGetCoreId`, or per-core-index nodes
- runtime containers must not use per-core indexing
- init sequences must not describe per-core init paths
- task models must not reference core affinity when only one core exists

### 5.2 Event-Driven vs Periodic

Choose `periodic` ownership when any are true:

- signal polling is required
- timeout checking is required
- state transition conditions depend on elapsed time or repeated sampling
- diagnostics or monitoring need regular refresh

Choose `event-driven` ownership when all are true:

- all actions are initiated by external calls, interrupts, or explicit events
- no periodic sampling or timeout evaluation is required

Choose `hybrid` when:

- external requests exist
- but internal periodic maintenance or timeout supervision also exists

## 6. `MainFunction` Decision Rules

### 6.1 `MainFunction` Is Usually Required

Recommend `MainFunction` when any are true:

- asynchronous behavior exists
- periodic polling exists
- timeout or retry supervision exists
- state machine evolves over time rather than in one API call
- diagnostics, monitoring, or fault confirmation need periodic execution
- deferred hardware completion must be checked

### 6.2 `MainFunction` May Be Omitted

`MainFunction` may be omitted only when all are true:

- no periodic polling exists
- no deferred completion exists
- no timeout or retry logic exists
- no runtime state progression requires periodic evolution
- external APIs can complete behavior synchronously

### 6.3 Output Rule

If `MainFunction` is omitted, the detailed design should explicitly say why.

## 7. File Family Decision Rules

### 7.1 Base File Family

Normally include:

- `FC.c`
- `FC.h`
- `FC_Types.h`
- `FC_Cfg.h`
- `FC_CfgData.h`
- `FC_Cfg.c`
- `FC_MemMap.h`

### 7.2 `Callout` File Decision

Add `FC_Callout.h/.c` when any are true:

- direct hardware variation exists
- chip or board adaptation exists
- dependency implementation differs by project
- external driver interaction should be isolated from FC logic

Do not skip `Callout` only to save files if the abstraction boundary is real.

### 7.3 `Internal.h` Decision

Add `FC_Internal.h` when any are true:

- multiple internal translation units need shared helpers
- state-machine helpers are intentionally visible only inside the FC
- internal-only service contracts improve structure clarity

Do not add `Internal.h` for trivial one-file modules unless it improves real clarity.

### 7.4 `Reg.h` Decision

Add `FC_Reg.h` when any are true:

- external device access relies on register addresses
- bit masks or command words must be represented
- protocol frame constants are required

## 8. 配置参数设计规则

Configuration parameter design must answer two distinct questions:

1. **What can be configured?** → Configuration macros (`Cfg.h`)
2. **What shape does the configuration data have?** → Configuration types (`Cfg.c` / `CfgData.h`)

These two dimensions are separately designed and separately reviewed. A design that only lists macros without defining the configuration type layout is incomplete.

### 8.1 Configuration Macros — `Cfg.h`

Use `Cfg.h` for:

- feature switches (enable/disable sub-features)
- count or size macros (array dimensions, buffer sizes, instance counts)
- basic behavior-selection switches (strategy selection, mode defaults)
- compile-time platform or project selection
- thresholds expressed as scalar compile-time constants

**Coverage rule:** Every architecture-level configuration parameter must have a corresponding macro or an explicit reason why it does not need one. Macros introduced by coding standards (e.g. `FC_CFG_MAX_xxx`, `FC_CFG_xxx_ENABLED`) during detailed design are expected and must be listed alongside architecture-sourced macros.

**Design-addition accountability:** Macros introduced by the detailed design itself (not from architecture or coding standards) must be marked as `design-addition (Rx)` where `Rx` references a risk/review item in the detailed design's risk table. A bare `design-addition` tag without a review-item reference is considered incomplete.

Do not place large mapping tables or runtime-shaped data in `Cfg.h`.

### 8.2 Configuration Types — `CfgData.h` / `Cfg.c`

Configuration types define the **structured shape** of configuration data. They answer: given the macros, what concrete data layout does the FC expect at init time?

Configuration types are mandatory. Every FC detailed design must define configuration types unless the FC has zero configurable parameters (explicitly justify if so).

Configuration type design must cover:

1. **Top-level config container** — the root struct that holds all configuration for one FC instance
2. **Per-instance / per-core sub-structures** — when instances or cores have independent configuration
3. **Resource-binding sub-structures** — bus addresses, channel assignments, register bases
4. **Threshold / strategy sub-structures** — when groups of related parameters form a semantic unit
5. **Dependency-binding sub-structures** — callout function pointers or dependency handles

**Field description rule:** Each configuration type must include field descriptions for its key fields, stating the field meaning, value range, and constraints. A configuration type table without field-level descriptions is incomplete.

**Type splitting principle:** Split configuration types by semantic ownership, not by file size:

- Hardware resource config → own sub-struct
- Timing/threshold config → own sub-struct
- Feature-enable config → own sub-struct
- Per-instance replication → array of per-instance struct

**When lacking experience:** If the engineering team has no established pattern for configuration type definitions, the detailed design must:
- Propose a reasonable type layout based on the architecture and interface requirements
- Mark the type definitions as `pending-confirmation` (not as confirmed design)
- Flag this as a learning item for the engineering team

### 8.3 `CfgData.h`

Use `CfgData.h` for:

- `extern` declarations of configuration objects
- configuration type definitions that are consumed by other modules
- public config-bound types when necessary

### 8.4 `Cfg.c`

`Cfg.c` is mandatory when any are true:

- mapping tables exist
- per-core configuration exists
- register/resource binding tables exist
- dependency bindings exist
- state-machine metadata tables exist
- thresholds or strategy values are better represented as structured constants than macros
- **configuration type definitions need concrete instantiation**

`Cfg.c` contains:
- Concrete configuration object definitions (the actual data, not just types)
- Mapping and binding tables
- Per-instance or per-core config tables

### 8.5 Macro vs Table vs Type Preference

Prefer a macro when:

- the value is a simple compile-time switch or size
- the value does not belong to a larger semantic group

Prefer a config type field when:

- the parameter belongs to a semantic group (hardware, timing, feature)
- the parameter is consumed by interfaces as part of a structured config object
- the parameter differs by instance or core and benefits from structured organization

Prefer a config table when:

- entries are repeated or indexed
- values differ by core, instance, channel, or state
- mapping relationships matter more than one scalar

### 8.6 Configuration Coverage Validation

Before finalizing configuration parameter design, validate:

1. Does every architecture-sourced config parameter have a macro or type field?
2. Do coding standards require additional macros beyond what architecture specifies? If so, are they listed?
3. Is the configuration type split along semantic boundaries (hardware / timing / feature / instance)?
4. Do all configuration types have field-level descriptions (meaning, value range, constraints)?
5. If config types are proposed without established project patterns, are they marked `pending-confirmation`?

## 9. `Callout` Decision Rules

Choose `Callout` when any are true:

- hardware access policy should be replaceable
- different projects may provide different implementations
- external dependency lies below FC ownership
- portability or chip-family variation is expected

Do not expose raw MCAL driver details through external FC APIs.

When using `Callout`, define:

- who implements it
- whether it is synchronous or asynchronous
- whether it may fail
- what the FC should do on failure

### 9.1 Delay/Timing Callout Rule

When any external interface or internal flow has explicit delay, wait, or timing requirements, a corresponding delay Callout interface must be generated.

Trigger conditions:

- the requirement or architecture specifies a wait/delay period (e.g. `WaitMs`, `DelayUs`, `WaitForStable`)
- the interface execution steps include a timed wait between operations
- hardware settling time, power-up delay, or de-bounce wait is required
- a state machine transition depends on elapsed time

Required design output for each delay callout:

- prototype (e.g. `FC_CalloutDelayUs(uint32 us)` or `FC_CalloutWaitMs(uint32 ms)`)
- description of what the delay is waiting for
- who implements it (typically integration/platform layer)
- whether it is blocking or non-blocking
- minimum and typical delay values (mark as assumption if unknown)
- which external or internal interface consumes it

Do not silently embed busy-wait loops or raw timer access inside the function layer. Delay requirements must be isolated through Callout to keep the FC logic platform-independent.

## 10. Internal Function Design Rules

### 10.0 Full-Per-Function Expansion Rule

All internal functions must be fully expanded with the same format as external APIs. This is non-negotiable — every internal function, regardless of complexity, must have:

- function prototype table (prototype / description / scope / trigger point / dependency-callout)
- sub-function decomposition table
- execution steps (ordered list)
- call relationship table (callee / category / purpose / timing)
- flowchart

Do not skip or merge internal functions because they are "simple helpers." If the function exists in the design, it must be fully documented.

### 10.1 Internal Function Decomposition Rules

Prefer internal decomposition by responsibility, not by code order.

Recommended internal categories:

- parameter checking
- initialization checking
- cfg access
- runtime access
- state condition check
- state action
- data conversion
- fault detection
- fault confirmation
- fault response
- fault recovery
- record or monitor helper

Keep helpers `static` by default.

Promote helpers to `Internal.h` only when cross-file internal reuse is required.

### 10.2 Internal Function Dependency Documentation

Every internal function listed in the internal function design must document which dependency/callout interfaces it consumes.

Required documentation per internal function:

- function name, scope, and responsibility
- trigger point (which external API or internal flow triggers it)
- which dependency/callout interfaces it calls (if any)
- if it calls no dependency interfaces, explicitly mark as `N/A`

The call relationship table's "类别" column supports both `依赖接口` and `内部函数` values. An internal function may call both dependency interfaces and other internal functions.

### 10.3 Internal Function Naming Convention

All internal functions in the detailed design document must use the full module name prefix `<FC>_`. This is the same convention as external APIs and Callouts.

Rationale:

- The detailed design document is a specification, not C source code. Although internal functions are `static` and technically have file scope in C, the design document requires all identifiers to be fully qualified for unambiguous traceability.
- Grounding evidence: ALL identifiers in grounding modules (Gp_TPT1145, Gp_TLE92104, Gp_DRV8889, Gp_WkUpSrcP, Gp_06_Adc3ph, IoMcu) use the full `<FC>_` prefix across all artifact types — external APIs, Callouts, config objects, runtime objects. Internal functions are no exception.
- Without the prefix, a name like `I2cReadReg` is ambiguous — it could belong to any FC that does I2C operations. With the prefix, `Gp_NCA9539_I2cReadReg` is unambiguously traceable to Gp_NCA9539.

Violation examples (prohibited):

- `I2cReadReg` → must be `Gp_NCA9539_I2cReadReg`
- `ValidateInstance` → must be `Gp_NCA9539_ValidateInstance`
- `RecordFault` → must be `Gp_NCA9539_RecordFault`

This rule applies to:

- Function names in section §6.2 (内部接口设计)
- Function names in call relationship tables
- Function names in flowcharts
- Function names referenced in any other section of the detailed design

## 11. Realize Interface Rules

For BSW-style FC design, the realize-interface layer should normally include:

- `Init`
- `MainFunction` when periodic or deferred behavior exists
- getter-style APIs for published data when needed
- setter-style or request-style APIs for external commands when needed

Prefer function APIs over exposed global variables.

For non-trivial asynchronous interfaces, design the workflow in this order:

1. defensive checks
2. cfg or ownership lookup
3. runtime read or write
4. deferred function-layer processing or trigger placement
5. status return or result publication

### 11.1 Call Chain Flexibility Rule

External APIs may directly call dependency interfaces (Callouts) without going through internal functions. The detailed design's "调用关系" table must faithfully reflect the actual call chain:

- If an external API calls an internal function, mark the category as `内部函数`
- If an external API calls a dependency interface directly, mark the category as `依赖接口`
- An external API may have both `内部函数` and `依赖接口` entries in its call chain

Do not force every external API → dependency path through an internal function when the design does not require it.

### 11.2 Defensive-Check Rules

Apply defensive checks mainly at external interface entry points.

Typical checks:

- initialization complete
- input pointer valid
- input range valid
- state allows service execution

On defensive-check failure:

- do not execute business logic
- record DET-style information
- return `E_NOT_OK` when the API uses `Std_ReturnType`

Do not replicate the same defensive checks throughout internal helper chains unless a special safety reason exists.

### 11.3 `Std_ReturnType` Meaning Rules

For ordinary FC external service APIs, prefer `Std_ReturnType` when the call result mainly expresses interface-validity success or failure.

Do not overload `Std_ReturnType` with detailed business meaning if the project already uses:

- separate output data
- state variables
- fault objects
- diagnostic objects

## 12. 运行参数设计规则

运行参数设计必须回答两个不同的问题：

1. **运行时有那些变量？** → 运行变量清单（变量名、类别、类型、所属Core、读写方、生命周期、MemMap）
2. **运行时数据在内存中如何组织？** → 运行参数类型（结构化类型定义，体现全局/每实例/每核/故障/监控的聚合关系）

这两个维度必须分别设计、分别评审。只列变量而不定义运行参数类型布局，视为运行参数设计不完整。

### 12.1 运行变量

Every runtime variable should answer:

- who owns it
- who writes it
- who reads it
- whether it is per-core or shared
- whether it survives reset
- where it lives in MemMap

Preferred runtime classes:

- input
- status
- intermediate
- output
- monitor
- fault
- retained

If runtime ownership is unclear, the design is not ready for coding.

### 12.2 运行参数类型

运行参数类型定义运行时数据的结构化布局。每个 FC 详细设计必须定义运行参数类型。

运行参数类型设计必须覆盖：

1. **全局运行态容器** — 承载模块级状态（如 InitStatus、DET 错误记录）的顶层结构体。至少定义一个。
2. **每实例运行态子结构** — 多实例时每实例独立的状态字段
3. **每核运行态子结构** — 多核时每核独立的状态字段
4. **故障运行态子结构** — 故障检测/确认/恢复相关字段聚合
5. **监控运行态子结构** — 周期采样/监控数据字段聚合

**字段描述规则：** 每个运行参数类型的关键字段必须包含字段描述，说明字段含义和取值范围。

**类型拆分原则：** 按语义边界拆分（全局/每实例/每核/故障/监控），不得按文件大小或随意归组。

## 13. `NoClear` Decision Rules

NoClear 的使用判定和约束详见 `state-and-fault-rules.md` §17。摘要：reset continuity / last fault / safe-state continuity / retained counters 任一需要时使用 NoClear；普通临时缓冲和可重算值不应使用。

## 14. State-Machine Decision Rules

状态机的选型判定详见 `state-and-fault-rules.md` §1。摘要：存在 mode/phase progression、多条件转换、故障改变执行路径、或 startup/prerun/run/shutdown 阶段时，使用显式状态机。

## 15. DET vs Fault Rules

DET 与 Fault 的边界定义详见 `state-and-fault-rules.md` §7。摘要：DET 用于 API 滥用（参数/指针/状态/范围校验），Fault 用于硬件/通信/超时/功能异常。禁止将运行时故障描述为 DET。

### 15.1 Fault Type Classification Rule

详见 `state-and-fault-rules.md` §8。

### 15.2 Fault Confirmation Strategy Rule

详见 `state-and-fault-rules.md` §9。

### 15.3 Fault Recovery Strategy Rule

详见 `state-and-fault-rules.md` §11。

### 15.4 Fault Latch and Clear Rule

详见 `state-and-fault-rules.md` §12。

### 15.5 Fault Runtime Parameter Rule

详见 `state-and-fault-rules.md`，故障计数器/锁存标志/确认状态变量必须以 `fault` 类别列入运行变量表，变量名遵循类型后缀规范。

## 16. Coding-Readiness Rules

The design is coding-ready only if all are true:

1. file family is explicit
2. external APIs are explicit
3. dependency APIs are explicit
4. runtime ownership is explicit
5. cfg placement is explicit
6. state-machine logic is explicit when applicable
7. DET strategy is explicit when applicable
8. fault strategy is explicit when applicable
9. MemMap strategy is explicit
10. pending confirmations are isolated

## 17. Mandatory Validation Questions

Before finalizing a detailed design, check:

1. can a developer create the file skeleton directly from this output
2. can configuration parameters and runtime parameters be implemented without redesign
3. are external APIs and dependency APIs clearly separated
4. are internal function responsibilities clear enough for decomposition
5. is state-machine logic explicit enough for coding
6. are DET and fault handling intentionally different
7. if multi-core exists, are per-core ownership and sync points explicit
8. are pending confirmations isolated from confirmed facts
9. is `MainFunction` either justified or explicitly rejected
10. is every `Callout`, `Cfg`, or `NoClear` decision supported by a visible reason

## 18. Omission Handling

If any major implementation area is missing, explicitly mark one of:

- not applicable
- deferred by user
- blocked by missing input
- pending confirmation

Do not silently omit:

- state machine, if mode progression exists
- `MainFunction`, if periodic behavior exists
- `Callout`, if hardware variability exists
- `Cfg.c`, if table-driven configuration exists
- `NoClear`, if reset continuity is part of the behavior

## 19. Design-Addition Provenance Rules

When the detailed design introduces items not present in SRS or SDD (configuration macros, config type fields, runtime variables, runtime type fields, fault items), each such item must:

1. **Be tagged with source** — mark as `design-addition (Rx)` in the Source/设计依据 column, where `Rx` is the corresponding risk-item index in the detailed design's risk table (§14)
2. **Have a corresponding risk item** — create an entry in the risk table explaining *why* the addition is needed and *what happens if not adopted*
3. **Be independently reviewable** — the risk item's "关联设计增量" column lists all affected objects so reviewers can trace and close each item

A bare `design-addition` tag without a risk-item reference is a design defect.

This rule applies to:
- Configuration macros with `Source = design-addition`
- Configuration type fields with `设计依据 = design-addition`
- Runtime variables with `设计依据 = design-addition`
- Runtime parameter type fields with `设计依据 = design-addition`
- Fault items that are driver-logic faults not specified in SRS/SDD
