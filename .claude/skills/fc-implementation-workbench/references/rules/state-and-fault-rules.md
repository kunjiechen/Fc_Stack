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

## 8. Fault Type Classification

Every fault must be classified into one of two types:

- **芯片故障 (Chip Fault)** — 硬件芯片自身产生的故障（如 nFAULT 引脚拉低、过流保护、过温关断），由芯片硬件触发，驱动通过 Callout 读取并上报。
- **驱动逻辑故障 (Driver Logic Fault)** — 软件驱动逻辑检测到的异常（如 Callout 调用失败、配置不可用、时序超时、DIO/ADC/PWM 操作失败），由驱动内部检测逻辑判定。

The fault type column is mandatory in the fault design table. Do not mix chip faults and driver logic faults in a single undifferentiated list.

## 9. Fault Confirmation Strategy Rules

Every fault must specify a confirmation strategy. Choose one:

### 9.1 Single Confirmation (单次确认)

- Fault is confirmed on first detection
- Suitable for: hardware-latched faults (e.g., nFAULT pin), non-jittering one-shot anomalies
- No configurable threshold needed
- Runtime parameter: fault confirmation flag (boolean)

### 9.2 Consecutive Confirmation (连续多次)

- Fault is confirmed only after N *consecutive* detections
- Reset counter to 0 on any single non-detection
- Suitable for: de-bounced transient signals, periodically sampled faults
- Configurable threshold: consecutive confirmation count (macro in `FC_Cfg.h`)
- Runtime parameters: consecutive confirmation counter (uint8/uint16)

### 9.3 Cumulative Confirmation (累计多次)

- Fault is confirmed after N cumulative detections within a sliding window
- Suitable for: sporadic anomalies needing statistical aggregation
- Configurable thresholds: cumulative count + window size (macros in `FC_Cfg.h`)
- Runtime parameters: cumulative counter + window counter

### Decision Rule

- If the fault source is hardware-latched → prefer single confirmation
- If the fault signal may jitter or requires de-bounce → prefer consecutive confirmation
- If the fault is sporadic and statistical → prefer cumulative confirmation

## 10. Fault Lifecycle Rules

Runtime fault design must include:

1. detection — identifies abnormal evidence
2. confirmation — prevents noisy or transient false positives (strategy: single / consecutive / cumulative)
3. response — changes behavior, raises diag, blocks operation, requests reset, or enters safe mode
4. recovery — determines whether and how the fault can clear (strategy: none / single / consecutive self-recovery)
5. latch — fault remains reported after confirmation until explicitly cleared
6. retention or reporting — ensures post-event observability

## 11. Fault Recovery Strategy Rules

Every fault must specify a recovery strategy:

### 11.1 Non-Recoverable (不可恢复)

- Fault is permanently latched once confirmed; only cleared by re-initialization
- Suitable for: severe faults requiring manual intervention, permanent hardware damage
- No configurable threshold needed
- Runtime parameter: fault latch flag

### 11.2 Single Self-Recovery (单次自恢复)

- Fault recovers on first normal detection after confirmation
- Suitable for: transient self-healing faults, faults following hardware signal auto-recovery
- Configurable: self-recovery enable switch (macro in `FC_Cfg.h`)
- Runtime parameter: recovery flag

### 11.3 Consecutive Self-Recovery (连续多次自恢复)

- Fault recovers only after N *consecutive* normal detections
- Reset recovery counter on any single abnormal detection
- Suitable for: faults needing stable recovery confirmation to avoid recovery jitter
- Configurable: self-recovery enable switch + consecutive recovery count threshold (macros in `FC_Cfg.h`)
- Runtime parameter: consecutive recovery counter (uint8/uint16)

### Self-Recovery Configuration Rule

If ANY fault supports self-recovery, the following config macros must be added:

- `FC_CFG_FAULT_SELF_RECOVERY_ENABLE` (feature switch, default STD_OFF)
- Per-fault recovery count thresholds as needed

## 12. Fault Latch and Clear Rules

### Latch Semantics

Once a fault is confirmed, it enters latched state: the fault remains reported even if the fault condition disappears, until explicitly cleared.

### Clear Methods

| Method | Description | Constraint |
| --- | --- | --- |
| Init Clear | All latched faults cleared on module re-initialization | Default when no clear API exists |
| Fault Clear API | External API call clears specified or all latched faults | Must add clear API in external interface design |
| Not Clearable | Latched and cannot be cleared by any means (reset only) | Must be explicitly documented |

### Critical Rule

If the module does NOT provide a fault clear interface, latched faults, once confirmed, are permanently held and can only be cleared by re-initialization. The design must explicitly state this constraint and mark each fault's clear method as "Init清除".

## 13. Fault Design Decision Rules

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

## 14. Minimum Fault-Handling Output

When the detailed design includes fault handling, state these items explicitly for each fault:

- fault name
- fault type (芯片故障 / 驱动逻辑故障)
- detection condition
- confirmation strategy (单次确认 / 连续多次 / 累计多次)
- confirmation threshold and associated config macro
- confirmation status in runtime (未确认/确认中/已确认)
- response action
- is recoverable (是/否)
- is self-recoverable (是/否)
- recovery strategy (单次 / 连续多次 / 不适用)
- recovery threshold and associated config macro
- recovery status in runtime (恢复中/已恢复/不适用)
- triggers state transition (是/否, target state)
- latch strategy (锁存 / 不锁存)
- clear method (Init清除 / 故障清除接口 / 不可清除)

If any item is unknown, mark it as pending rather than silently omitting it.

## 15. Fault Response Categories

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

## 16. Fault Runtime Parameters

Fault confirmation and recovery counters must be documented in the runtime variable table (§13.1):

- Confirmation counters (e.g., `Fault_nFaultConfirmCnt_u8`)
- Recovery counters (e.g., `Fault_nFaultRecoveryCnt_u8`)
- Latch status flags (e.g., `Fault_nFaultLatched_b`)
- Confirmation status (e.g., `Fault_nFaultConfirmStatus_u8`)

Variable names must follow the type suffix convention. Category must be `fault`.

## 17. Reset And NoClear Rules

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

## 18. Reset Coupling Rules

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

## 19. NVM vs NoClear Guidance

Prefer `NoClear` when:

- the data is only needed across immediate reset
- startup logic needs the data before NVM restore completes

Prefer NVM-backed persistence when:

- the data must survive power loss
- historical retention beyond one reboot matters

Use both only when the design has a clear immediate-retention and long-term-retention split.

## 20. Internal Function Decomposition Rules

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

## 21. Review Checklist

Before accepting the state/fault design, check:

1. is stateful behavior represented explicitly if needed
2. are condition and action responsibilities separated
3. is there a clear owner for state mutation
4. are DET and fault semantics separated
5. are faults classified as chip fault or driver logic fault
6. does each fault specify confirmation strategy (single / consecutive / cumulative)
7. does each fault specify recovery strategy (non-recoverable / single self-recovery / consecutive self-recovery)
8. are confirmation and recovery thresholds configurable (macros) when count > 1
9. are confirmation and recovery counters listed as runtime variables
10. are fault latch semantics and clear methods explicit
11. is self-recovery enable config added when any fault supports self-recovery
12. is the absence of fault clear API explicitly documented with consequences
13. do fault objects define response and retention, not just detection
14. is reset coupling explicit when present
15. is NoClear justified, not habitual
16. are unresolved thresholds or clear conditions marked as pending
