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
- for non-trivial dependency paths, are execution steps and flowcharts provided

Common failure signals:

- dependency behavior hidden inside prose
- direct hardware or MCAL assumptions leak into FC API design
- failure path is omitted for a dependency that can fail

## 6. Subfunction Decomposition Review

Check:

- does each key external API have meaningful subfunction decomposition
- do the steps reflect actual implementation order
- are internal function responsibilities aligned with those steps
- do subfunctions show where cfg, runtime, DET, fault, and callout logic occur

Common failure signals:

- only interface purpose is written
- steps are too vague to map into code
- internal helpers are listed but not connected to control flow

## 7. Single-Core / Multi-Core Review

Check:

- is the single-core or multi-core choice justified
- for multi-core, are per-core responsibilities explicit
- are per-core task entries explicit
- are shared objects identified
- are synchronization points identified
- are per-core cfg/runtime bindings clear

Common failure signals:

- multi-core claimed with no per-core partition
- shared state exists but no sync strategy is shown
- task ownership by core is missing

## 8. State Machine Review

Check:

- is a state machine present when behavior is stateful
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

## 9. Internal Function Review

Check:

- are internal functions grouped by responsibility
- is `static` vs internal-header scope reasonable
- are parameter checks, state checks, data conversion, fault helpers, and record helpers separated when needed
- are key internal control flows represented with steps or flowcharts

Common failure signals:

- one oversized internal helper is responsible for unrelated concerns
- internal decomposition follows code order instead of responsibility

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
- are detection, confirmation, response, recovery, and retention described
- are fault response categories explicit
- is reset relation explicit if present
- is fault observability exposed if needed
- is a fault flowchart present for non-trivial fault lifecycle

Common failure signals:

- only detection is described
- response says “handle fault” without concrete behavior
- recovery is missing where service return matters

## 12. Runtime-State Review

Check:

- are runtime variables or runtime state families explicitly listed
- does each runtime item have owner, read/write side, lifecycle, core affinity, and memory placement
- are shared runtime objects distinguished from per-core runtime objects
- are retained or no-clear items explicitly marked

Common failure signals:

- runtime objects are implied but not listed
- ownership is unclear
- per-core data and shared data are mixed

## 13. Config Review

Check:

- are cfg macros and cfg tables both handled where needed
- are macros used only for suitable compile-time concerns
- are tables used where mapping or repeated structured data exists
- is `Cfg.c` present when the design is table-driven

Common failure signals:

- table-driven behavior forced into macros
- `Cfg.c` omitted even though table-shaped config clearly exists
- config and runtime data are mixed

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
- can runtime state be allocated without guessing ownership
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
