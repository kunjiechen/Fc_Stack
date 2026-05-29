# FC Implementation Review Checklist

## Purpose

This file provides a stable review checklist for implementation-level detailed design.

Use it when:

- reviewing a generated detailed design
- reviewing a human-written detailed design
- checking whether a design is coding-ready
- identifying omissions, ambiguity, or structure risks

The goal is not to restate all rules. The goal is to review with a practical checklist.

## 1. Review Result Categories

For each checklist area, classify the result as:

- `pass`
- `partial`
- `fail`
- `not-applicable`
- `pending-confirmation`

## 2. FC Identity And Scope

Check:

- is the FC name explicit and stable
- is the software layer explicit
- is the module purpose clear
- is the execution model clear
- is single-core or multi-core explicit

Common failure signals:

- FC purpose is vague
- layer position is missing
- execution model is implied but not stated

## 3. File Family Review

Check:

- is the file list complete enough for coding
- are `FC.c`, `FC.h`, `FC_Types.h`, `FC_Cfg.h`, `FC_CfgData.h`, `FC_Cfg.c`, and `FC_MemMap.h` handled appropriately
- is `FC_Callout.h/.c` included when real dependency variability exists
- is `FC_Internal.h` justified when used
- is `FC_Reg.h` included when register-controlled external devices exist

Common failure signals:

- cfg files missing while table-driven config is described
- callout omitted even though hardware adaptation is clearly needed
- internal helpers described but no internal exposure strategy exists

## 4. External API Review

Check:

- are all external APIs explicitly listed
- are prototypes present
- are sync/async and reentrancy defined
- are return semantics clear
- are preconditions or constraints stated
- for non-trivial APIs, are subfunctions and execution steps described
- for non-trivial APIs, is a flowchart present

Common failure signals:

- API name exists but prototype is missing
- API purpose is described but sequence is not
- `MainFunction` exists in behavior but not in the interface list

## 5. Dependency API And Callout Review

Check:

- are dependency APIs explicitly separated from external APIs
- is each dependency API tied to an implementation boundary
- are failure paths described where relevant
- are callout usage reasons explicit
- if delay/wait/timing requirements exist in external interfaces, is a delay Callout generated
- for non-trivial dependency paths, are execution steps and flowcharts provided

Common failure signals:

- dependency behavior hidden inside prose
- direct hardware or MCAL assumptions leak into FC API design
- failure path is omitted for a dependency that can fail
- delay/wait/ settling requirements exist in execution steps but no delay Callout is defined

## 6. Subfunction Decomposition Review

Check:

- does each key external API have meaningful subfunction decomposition
- do the steps reflect actual implementation order
- are internal function responsibilities aligned with those steps
- do subfunctions show where cfg, runtime, DET, fault, and callout logic occur
- are dependency/callout interfaces referenced in the internal function table for each external API
- if delay/timing requirements exist, is a corresponding delay Callout generated

Common failure signals:

- only interface purpose is written
- steps are too vague to map into code
- internal helpers are listed but not connected to control flow
- internal functions listed without their dependency interfaces
- delay/wait requirements exist in steps but no delay Callout is defined

## 7. Single-Core / Multi-Core Review

Check:

- is the single-core or multi-core choice justified
- for single-core, do flowcharts avoid core-matching, core-traversal, and `CalloutGetCoreId` nodes
- for single-core, is runtime container free of per-core indexing
- for multi-core, are per-core responsibilities explicit
- are per-core task entries explicit
- are shared objects identified
- are synchronization points identified
- are per-core cfg/runtime bindings clear

Common failure signals:

- multi-core claimed with no per-core partition
- single-core design contains core-matching or core-traversal nodes in flowcharts
- single-core design references `CalloutGetCoreId`
- shared state exists but no sync strategy is shown
- task ownership by core is missing

## 8. State Machine Review

Check:

- is a state machine present when behavior is stateful
- is the design approach explicit: chip hardware state machine vs software driver state machine
- if software driver state machine is chosen, is the mapping between software states and chip states documented
- are states explicit
- are transitions explicit
- are condition and action functions separated
- is the state-machine owner clear
- is the main state-machine flowchart present
- is state recording handled when needed

Common failure signals:

- stateful behavior exists but no explicit state model is given
- transition conditions are buried in prose
- state updates have no clear owner
- software state machine chosen without chip state mapping

## 9. Internal Function Review

Check:

- are ALL internal functions fully expanded with the same format as external APIs (prototype table + sub-function decomposition + execution steps + call relationship table + flowchart)
- are no internal functions skipped, merged, or reduced because they are "simple helpers"
- are internal functions grouped by responsibility
- is `static` vs internal-header scope reasonable
- are parameter checks, state checks, data conversion, fault helpers, and record helpers separated when needed
- does each internal function entry document its dependency/callout interfaces (or explicitly mark N/A)
- does the call relationship table's "类别" column correctly reflect whether a callee is a 依赖接口 or 内部函数

Common failure signals:

- internal functions only listed as a summary table without per-function full expansion
- "simple" internal functions skipped without sub-function decomposition or flowchart
- one oversized internal helper is responsible for unrelated concerns
- internal decomposition follows code order instead of responsibility
- internal function table missing "依赖接口" column
- internal functions listed without any indication of which callout/dependency interfaces they consume

## 10. DET Review

Check:

- are DET checks explicitly designed where external APIs need them
- are init, pointer, range, and state checks considered
- is the DET execution order clear
- is the DET return strategy clear
- is DET clearly separated from runtime fault handling

Common failure signals:

- DET exists only as a vague statement
- runtime faults are mislabeled as DET
- no return strategy is described

## 11. Fault Handling Review

Check:

- are fault objects present when runtime abnormal behavior matters
- is each fault classified as 芯片故障 or 驱动逻辑故障
- is each fault's confirmation strategy explicit (单次确认 / 连续多次 / 累计多次)
- are confirmation thresholds configurable (macros) when count > 1
- are confirmation runtime counters and statuses listed as runtime variables
- is each fault's recovery strategy explicit (不可恢复 / 单次自恢复 / 连续多次自恢复)
- are recovery thresholds configurable (macros) when count > 1, with self-recovery enable switch
- are recovery runtime counters listed as runtime variables
- are fault response categories explicit
- are fault latch semantics and clear methods explicit for each fault
- if no fault clear API exists, is the constraint documented
- is reset relation explicit if present
- is fault observability exposed if needed
- are fault confirmation and recovery flowcharts present for non-trivial fault lifecycles

Common failure signals:

- only detection is described
- faults not classified as chip fault vs driver logic fault
- response says “handle fault” without concrete behavior
- recovery is missing where service return matters
- self-recovery described but no self-recovery enable config macro
- multi-count confirmation/recovery described but no runtime counter variable
- latched faults described but no clear method specified
- no fault clear API but clear method not documented as “Init清除”

## 12. 运行参数设计 Review

运行参数设计评审必须覆盖两个独立维度：运行变量和运行参数类型。

### 12.1 运行变量 Review

Check:

- are runtime variables or runtime state families explicitly listed
- does each runtime item have owner, read/write side, lifecycle, core affinity, and memory placement
- are shared runtime objects distinguished from per-core runtime objects
- are retained or no-clear items explicitly marked

Common failure signals:

- runtime objects are implied but not listed
- ownership is unclear
- per-core data and shared data are mixed

### 12.2 运行参数类型 Review

Check:

- are runtime parameter types defined (not just variable list)
- is at least one global runtime type defined for module-level state
- are sub-structures split by semantic boundary (global / per-instance / per-core / fault / monitor)
- do key fields have field descriptions (meaning, value range)
- do key fields carry type suffixes (`_u8`/`_u16`/`_u32`/`_b` etc.) matching the 字段类型 column
- does the 字段类型 column explicitly state C standard types
- if the project has no established runtime type pattern, is the design marked `pending-confirm` with a learning item flagged

Common failure signals:

- only variables listed, no runtime parameter type definitions at all
- runtime types exist but field descriptions are missing
- field names lack type suffixes, or 字段类型 column is missing
- runtime types split by file size or arbitrary grouping instead of semantic ownership
- no global runtime type defined

## 13. 配置参数设计 Review

Configuration parameter review must cover two independent dimensions: macros and types.

### 13.1 Configuration Macro Review

Check:

- does every architecture-sourced config parameter have a corresponding macro
- are macros categorized correctly (feature / count / threshold / platform)
- are coding-standard-introduced macros explicitly listed with source marked `coding-standard`
- are macros used only for suitable compile-time concerns
- are macro default values reasonable and marked as assumption when unknown

Common failure signals:

- architecture config parameter has no corresponding macro
- coding standard macros are silently assumed but not listed
- table-driven behavior forced into macros

### 13.2 Configuration Type Review

Check:

- are configuration types defined (not just macros)
- is a top-level config container defined
- are sub-structures split by semantic boundary (hardware / timing / feature / per-instance / dependency)
- do key fields have field descriptions (meaning, value range, constraints)
- do key fields carry type suffixes (`_u8`/`_u16`/`_u32`/`_b` etc.) matching the 字段类型 column
- does the 字段类型 column explicitly state C standard types or concrete enum/struct type names
- are config type instances defined in `Cfg.c`
- if the project has no established config type pattern, is the design marked `pending-confirm` with a learning item flagged

Common failure signals:

- only macros listed, no configuration type definitions at all
- config types exist but field descriptions are missing
- field names lack type suffixes, or 字段类型 column is missing
- 字段类型 column says "枚举" or "结构体" without giving the concrete type name
- config types split by file size or arbitrary grouping instead of semantic ownership
- `Cfg.c` omitted even though config types need concrete instantiation
- config type design copied from reference module without adapting to current FC's needs

### 13.3 Config Coverage Validation

Check:

- does the design explicitly validate that architecture → config macros coverage is complete
- are all config types accompanied by field-level descriptions
- are coverage gaps recorded as blocking items, not as informational notes

### 13.4 Design-Addition Provenance Review

Check:

- are all `design-addition` macros tagged with a risk-item reference (e.g., `design-addition (R5)`)
- do all `design-addition` config type fields have a corresponding risk item in §17
- do all `design-addition` runtime variables have a corresponding risk item in §17
- do all `design-addition` runtime type fields have a corresponding risk item in §17
- does each design-addition risk item explain *why* the addition is needed and the consequence of omission
- does the risk table's "关联设计增量" column list all affected design objects
- are there any bare `design-addition` tags without a risk-item reference

Common failure signals:

- `design-addition` appears in Source/设计依据 column without `(Rx)` suffix
- risk table has no entries for design-addition items
- risk item says "待确认" but does not list the specific design objects it covers
- coding-standard macros are mislabeled as design-addition
- design-addition items have no "why" justification in the risk table

## 14. MemMap / NoClear Review

Check:

- are MemMap sections explicitly defined
- is runtime vs const vs code placement clear
- are per-core sections handled where relevant
- is NoClear justified rather than habitual
- is retained-data validation after reset addressed

Common failure signals:

- MemMap only mentioned vaguely
- NoClear is used with no reset-related reason
- per-core const or runtime sections are missing in a per-core design

## 15. Flowchart Review

Check:

- are flowcharts included in non-trivial control areas
- do they show execution order clearly
- do they align with tables and written steps
- are they readable and not oversized
- do they help coding rather than merely decorate the document
- do node labels express implementation steps instead of code fragments
- do node labels avoid variable names, array indexing, register identifiers, and direct condition expressions

Common failure signals:

- no flowchart where sequence is complex
- flowchart contradicts the steps or tables
- too much implementation trivia inside nodes
- flowchart nodes look like pseudo-code or copied C statements
- the step table says one thing while the flowchart exposes lower-level code mechanics

## 16. Coding-Readiness Review

Check:

- can a developer create files immediately from this design
- can APIs be stubbed without guessing
- can cfg objects be declared without rethinking structure
- can runtime parameters (variables and type layout) be allocated without guessing ownership
- can the state machine be implemented directly
- can fault handling be implemented without inventing missing lifecycle behavior

Common failure signals:

- multiple major sections say only “TBD”
- design still requires hidden assumptions to start coding

## 17. Review Summary Output Suggestion

When using this checklist in review mode, summarize findings in this order:

1. critical blockers
2. important omissions
3. ambiguity or pending confirmations
4. lower-risk polish items

Do not start with a broad positive summary if blockers exist.
