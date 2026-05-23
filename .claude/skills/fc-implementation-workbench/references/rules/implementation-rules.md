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

## 8. `Cfg` Decision Rules

### 8.1 `Cfg.h`

Use `Cfg.h` for:

- feature switches
- count or size macros
- basic behavior-selection switches
- compile-time platform or project selection

Do not place large mapping tables or runtime-shaped data in `Cfg.h`.

### 8.2 `CfgData.h`

Use `CfgData.h` for:

- exported configuration object declarations
- configuration table visibility
- public config-bound types when necessary

### 8.3 `Cfg.c`

`Cfg.c` is mandatory when any are true:

- mapping tables exist
- per-core configuration exists
- register/resource binding tables exist
- dependency bindings exist
- state-machine metadata tables exist
- thresholds or strategy values are better represented as structured constants than macros

Do not force everything into macros if the real shape is table-driven.

### 8.4 Macro vs Table Preference

Prefer a macro when:

- the value is a simple compile-time switch or size

Prefer a config table when:

- entries are repeated or indexed
- values differ by core, instance, channel, or state
- mapping relationships matter more than one scalar

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

## 10. Internal Function Decomposition Rules

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
- fault response
- record or monitor helper

Keep helpers `static` by default.

Promote helpers to `Internal.h` only when cross-file internal reuse is required.

## 10.1 Realize Interface Rules

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

## 10.2 Defensive-Check Rules

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

## 10.3 `Std_ReturnType` Meaning Rules

For ordinary FC external service APIs, prefer `Std_ReturnType` when the call result mainly expresses interface-validity success or failure.

Do not overload `Std_ReturnType` with detailed business meaning if the project already uses:

- separate output data
- state variables
- fault objects
- diagnostic objects

## 11. Runtime-State Rules

Every runtime object should answer:

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

## 12. `NoClear` Decision Rules

Use `NoClear` when any are true:

- reset continuity matters
- last fault or reset cause must survive reset
- safe-state continuity matters
- state trace or retained counters are required across reset

Do not use `NoClear` for:

- ordinary temporary buffers
- values that can be recomputed cheaply
- routine per-cycle scratch data

If `NoClear` is used, define:

- what survives reset
- why it survives reset
- who validates retained data after reset

## 13. State-Machine Decision Rules

Use an explicit state machine when any are true:

- mode or phase progression exists
- transitions depend on multiple conditions
- fault handling can change behavior path
- startup, prerun, run, or shutdown phases exist

Avoid implicit state machines hidden inside unrelated helpers if the module behavior is mode-driven.

## 14. DET vs Fault Rules

Use DET for:

- API misuse
- initialization misuse
- invalid pointer
- invalid range
- invalid state for the call

Use fault handling for:

- hardware failure
- sampling failure
- communication failure
- timeout
- functional abnormal behavior
- monitored violation

Never describe runtime faults purely as DET.

## 15. Coding-Readiness Rules

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

## 16. Mandatory Validation Questions

Before finalizing a detailed design, check:

1. can a developer create the file skeleton directly from this output
2. can cfg and runtime state be implemented without redesign
3. are external APIs and dependency APIs clearly separated
4. are internal function responsibilities clear enough for decomposition
5. is state-machine logic explicit enough for coding
6. are DET and fault handling intentionally different
7. if multi-core exists, are per-core ownership and sync points explicit
8. are pending confirmations isolated from confirmed facts
9. is `MainFunction` either justified or explicitly rejected
10. is every `Callout`, `Cfg`, or `NoClear` decision supported by a visible reason

## 17. Omission Handling

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
