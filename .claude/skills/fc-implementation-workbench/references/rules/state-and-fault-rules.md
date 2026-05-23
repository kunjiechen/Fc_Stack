# FC State And Fault Rules

## Purpose

This file owns stable rules for state-machine design, DET handling, runtime error handling, fault strategy, reset coupling, and NoClear usage.

It should answer these recurring design questions:

- when an explicit state machine is required
- how state transitions should be organized
- how DET should be separated from runtime fault handling
- how runtime fault lifecycle should be expressed
- when reset and NoClear must be part of the design

## 1. State Machine Decision Rules

Use an explicit state machine when any are true:

- the FC has phase, mode, or lifecycle progression
- startup, prerun, run, postrun, shutdown, or recovery phases exist
- behavior differs materially by operating state
- transitions depend on multiple conditions
- fault behavior can change execution flow
- the module must remember previous execution mode to determine next behavior

A state machine may be omitted only when all are true:

- behavior is stateless or nearly stateless
- every API completes synchronously without deferred progression
- there is no meaningful mode memory between cycles

If a state machine is omitted, the detailed design should explicitly say why.

## 2. State Machine Structure Rules

Prefer explicit state-machine objects:

- state enums
- switch-path enums when useful
- condition-check functions
- action functions
- transition metadata or tables
- one main transition entry

Avoid hiding transition policy inside a large mixed `switch` body unless the module is truly trivial.

Recommended state-machine shape:

1. state definition
2. transition condition set
3. transition action set
4. transition table or bounded transition scan
5. optional record or trace mechanism

## 3. State Transition Discipline

- scan only the transitions allowed by the current state
- allow at most one state transition per main cycle unless strong evidence says otherwise
- record state change when traceability matters
- separate transition condition from transition action
- keep condition checks side-effect free whenever possible
- let transition actions own state mutation or request mutation explicitly

Recommended decision rule:

- condition functions answer whether the transition is allowed
- action functions perform the transition work
- one centralized helper updates the current state if the design benefits from traceability or auditability

## 4. State Recording Rules

Use explicit state recording when any are true:

- startup or shutdown timing matters
- reset continuity matters
- faults can force state change
- project debugging depends on mode history
- system-level review needs phase traceability

Recording options:

- none
- current-state only
- current-state + timestamp
- current-state + transition history buffer
- no-clear retained recorder

If recording is chosen, the design should define:

- what gets recorded
- when it gets recorded
- whether it survives reset
- who reads it

## 5. DET Rules

DET is for development-use protection, not full fault handling.

Typical DET checks:

- module not initialized
- null pointer
- parameter out of range
- invalid state for the API
- invalid address or alignment if applicable

Recommended DET design objects:

- `InitStatusType`
- `DevErrMaskType`
- `CheckInit`
- `CheckPtr`
- `CheckRange`
- optional `CheckState`
- optional `LogDevErr`

## 6. DET Execution Flow

Recommended DET execution order for an external API:

1. check module initialization state
2. check pointer validity
3. check parameter range
4. check API-call state legality
5. record DET result
6. exit by the defined return strategy

Recommended return strategy:

- for `void` APIs: log and return early
- for status-return APIs: log and return `E_NOT_OK` or equivalent failure

DET should be visible in the design for every relevant external API, even if the implementation later shares helpers.

## 7. Runtime Error vs Fault Rules

Use DET for:

- API misuse
- caller misuse
- initialization misuse

Use runtime fault handling for:

- hardware failure
- communication failure
- timeout
- retry exhaustion
- invalid sampled data
- protocol failure
- safety-monitor violation
- algorithmic abnormal behavior

Do not describe runtime faults purely as DET, and do not over-promote ordinary API misuse into fault strategy.

## 8. Fault Lifecycle Rules

Runtime fault design should normally include:

1. detection
2. confirmation or debounce
3. response
4. recovery
5. retention or reporting

Recommended interpretation:

- detection
  - identifies abnormal evidence
- confirmation
  - prevents noisy or transient false positives when needed
- response
  - changes behavior, raises diag, blocks operation, requests reset, or enters safe mode
- recovery
  - determines whether and how the fault can clear
- retention or reporting
  - ensures post-event observability

## 9. Fault Design Decision Rules

A formal fault object should exist when any are true:

- the FC can fail due to hardware or dependency behavior
- invalid runtime behavior must trigger degraded or blocked operation
- diagnostic exposure is required
- state-machine behavior depends on abnormal runtime conditions
- reset or retained information is part of the expected response

A lightweight runtime error path may be enough when all are true:

- abnormal behavior only causes a local API failure
- no state memory is needed
- no degradation, reporting, or recovery policy exists

## 10. Minimum Fault-Handling Output

When the detailed design includes fault handling, state these items explicitly:

- fault source
- detection condition
- confirmation rule
- response action
- recovery condition
- retention strategy
- reset relation
- observable interface if any

If any item is unknown, mark it as pending rather than silently omitting it.

## 11. Fault Response Categories

Typical response categories:

- ignore and continue
- reject current operation
- retry
- degrade function
- latch fault until clear condition
- request state transition
- request safe state
- request reset

The detailed design should choose one or more explicitly, not just say "handle fault."

## 12. Fault Recovery Rules

Recovery should be defined when any are true:

- the fault is intended to self-clear
- recovery impacts service availability
- recovery affects state-machine return path
- user or higher layer can request clear

Recovery rules may include:

- immediate clear after valid sample
- clear after N valid cycles
- manual clear only
- clear after reset only

## 13. Reset And NoClear Rules

Consider `NoClear` when the data is needed across reset for:

- reset cause analysis
- persistent fault state
- safe-state continuity
- state transition trace
- retained counters
- recovery discrimination after reboot

Do not use `NoClear` for ordinary transient buffers that can be recomputed.

If `NoClear` is used, define:

- what survives reset
- why it survives reset
- who validates retained data after reset
- whether data is single-save, double-save, or mirrored

## 14. Reset Coupling Rules

Reset coupling should be explicit when any are true:

- a fault may trigger reset
- reset is part of the recovery policy
- retained data changes post-reset behavior
- restart phase depends on previously stored fault or state information

If reset is part of the design, define:

- which faults can request reset
- what data must be preserved
- what modules re-interpret preserved data
- whether startup path changes after retained fault evidence

## 15. NVM vs NoClear Guidance

Prefer `NoClear` when:

- the data is only needed across immediate reset
- startup logic needs the data before NVM restore completes

Prefer NVM-backed persistence when:

- the data must survive power loss
- historical retention beyond one reboot matters

Use both only when the design has a clear immediate-retention and long-term-retention split.

## 16. Internal Function Decomposition Rules

Prefer these internal function categories:

- parameter check
- init check
- config access
- runtime access
- state condition check
- state action
- data conversion
- fault detect
- fault confirm
- fault response
- fault recovery
- record or monitor helper

Keep helpers `static` by default unless they must be shared across internal translation units.

Promote to internal-header scope only when cross-file internal reuse is real.

## 17. Review Checklist

Before accepting the state/fault design, check:

1. is stateful behavior represented explicitly if needed
2. are condition and action responsibilities separated
3. is there a clear owner for state mutation
4. are DET and fault semantics separated
5. do fault objects define response and retention, not just detection
6. is reset coupling explicit when present
7. is NoClear justified, not habitual
8. are unresolved thresholds or clear conditions marked as pending
