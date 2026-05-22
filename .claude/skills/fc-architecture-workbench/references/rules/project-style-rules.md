# Project Style Rules

## Purpose

This file merges the historical local project style findings that were previously split across:

- `demo-interface-patterns.md`
- `demo-fc-header-architecture-rules.md`

Use this file when you need the local project habit layer on top of the general FC rules.

## 1. Overall Style

The historical project style is stable in two ways:

- external interfaces are semantic rather than generic
- header-file responsibilities are strongly structured before `.c` implementation details are considered

Design implication:

- define the FC at header level first
- only then derive `.c` structure and internal logic

## 2. External Interface Skeleton

The most common FC skeleton is:

- `FC_Init(void)`
- optional `FC_MainFunction(void)`
- semantic setters and getters

Do not force `MainFunction` for every FC.

Prefer `MainFunction` when the module has:

- periodic sampling
- state-machine progression
- diagnosis
- debounce
- watchdog handling
- recovery handling
- buffered request processing

## 3. Preferred Interface Naming

Namespace rule:

- Preserve the explicit FC/driver name as the C function prefix.
- If the driver name is `Gp_DRV8889`, generated APIs must use `Gp_DRV8889_...`.
- Do not convert `Gp_DRV8889` to `GpDrv8889` unless the user explicitly requests that style.
- Apply this to both external APIs and dependency/callout APIs.

Prefer project-style semantic names such as:

- `SetDevModeOutSig`
- `GetDevModeInSig`
- `SetDrvOutSig`
- `SetHbOutSig`
- `GetDevFaultSig`
- `GetCurSig`
- `Get...Diag`

Avoid generic names such as:

- `GetInput`
- `SetOutput`
- `ReadValue`
- `WriteCtrl`

## 4. Parameter Style

Prefer a single external instance selector:

- `Id_u8`
- `Id_u16`

Use internal mapping for:

- core
- chip
- channel
- signal

Prefer:

- `Std_ReturnType` for most runtime external interfaces
- output pointers for getter results
- asynchronous setter semantics when requests are buffered and later processed in `MainFunction`
- synchronous getter semantics when reading cached or directly available state

Callout parameter style:

- Do not write array declarators in function parameters, such as `uint8 TxData_au8[]`.
- Use pointer form with naming that shows pointee type, such as `uint16* TxData_pu16` or `uint8* Data_pu8`.
- Use `uint16 Size_u16` for transfer size/count parameters unless a narrower project rule is explicitly provided.
- For SPI devices whose protocol frame is 16 bit, use `uint16*` SPI data buffers so FC callers do not need casts at each call site.

## 5. Header Carrier Rules

### `FC.h`

Primary carrier for:

- external interface declarations
- interface timing and sync/async notes
- `CODE_START / CODE_STOP`

### `FC_Types.h`

Primary carrier for:

- state enums
- configuration-container types
- runtime-container types
- mapping types
- DET or interface-check types

### `FC_Cfg.h`

Primary carrier for:

- feature switches
- core enable switches
- instance counts
- behavior selection
- implementation selection

Do not overload this file with large amounts of threshold or register detail.

For SPI/I2C/register-based external devices, `FC_Cfg.h` may include `FC_Reg.h` when configuration defaults or tables reference register addresses, bit masks, command words, or frame constants.

### `FC_Reg.h`

Required when the FC controls an SPI/I2C/register-based external device and needs a stable carrier for:

- register addresses
- bit masks and bit positions
- command words
- protocol frame constants
- register reset/default values used by configuration

`FC_Reg.h` includes `Std_Types.h` and is included by `FC_Cfg.h` when configuration definitions depend on register symbols.

### `FC_CfgData.h`

Primary carrier for:

- `extern` declarations of configuration containers
- `extern` declarations of mapping tables
- optional calibration declarations

### `FC_Callout.h`

Primary carrier for:

- dependency interface declarations
- platform adaptation contracts

### `FC_Callout.c`

Primary carrier for:

- project adaptation implementation stubs
- board-specific callout binding
- platform-specific translation such as DIO inversion, SPI sequence binding, or I2C transaction binding

If an architecture defines callout dependencies, the file list must include both `FC_Callout.h` and `FC_Callout.c`.

### `FC_MemMap.h`

Primary carrier for:

- section macro mapping for all FC files

`FC_MemMap.h` should be shown as a section-boundary include for all FC-created files that place code, runtime data, const data, or calibration data into memory sections.

## 6. Configuration Granularity

Keep this split:

- `Cfg.h`
  - foundational configuration
  - feature switches
  - behavior selection
  - implementation selection
- `Cfg.c / CfgData.h`
  - mapping tables
  - resource binding
  - thresholds
  - timing parameters
  - retry counts
  - project data tables

Do not mirror every stable external interface with a feature macro unless compile-time trimming is explicitly needed.

## 7. Dependency Style

Historical project preference is:

1. reuse standard FC or standard binding when possible
2. use callout for project-specific adaptation
3. use macro replacement only for very simple hooks

Examples of simple macro cases:

- enter critical section
- exit critical section

## 8. Multi-Core and Multi-Instance Style

Prefer:

- external `Id`
- internal `cfgSigMapping`
- internal runtime containers per core
- `GetCoreId` abstraction

Avoid exposing:

- `CoreId + ChipId + ChannelId` directly as the normal external API shape

## 9. Architecture Output Guidance

When producing a new FC architecture in this project style, make sure the final result clearly defines:

- interface skeleton
- file list
- header carrier mapping
- configuration split between `Cfg.h` and `Cfg.c / CfgData.h`
- runtime-state ownership
- dependency and callout strategy
- MemMap strategy

## 10. Architecture Version And Release Style

Use integer major versions only:

- `V1`
- `V2`
- `V3`

Do not use minor or patch versions such as `V1.0`, `V1.1`, or `V1.0.1`.

Workflow:

- Requirement document only: generate initial `V1`.
- Draft architecture file with optional requirement document: update the draft without incrementing the version.
- Draft architecture with all pending confirmations resolved: promote `Vx Draft` to `Vx Released` without changing the version.
- Released architecture file plus requirement document: upgrade to the next major version, for example `V1 Released -> V2 Released`.

Risk and pending-confirmation style:

- Include a stable `索引` for every risk item, such as `R1`, `R2`, and `R-OTHER`.
- Use `状态` values exactly as `待评审`, `已评审`, and `待修改`.
- Use `备注` for user confirmation or modification comments; do not use a separate `User Expected Action` column.
- Always include an `R-OTHER` / `其他` row for user-supplied additional suggestions.
- Support both workflows: user edits the Markdown table directly, or user replies in chat using risk indexes and status decisions.
- If a row is `待修改` and `备注` is empty, execute the row's recommended action; if `备注` is present, follow the remark first.
- Keep the architecture in `Draft` while any real risk item remains `待评审` or `待修改`.
- Include a concise change summary for every draft update or released-version upgrade.
- After producing a `Draft` architecture, always guide the user to the next review step.
- The guidance should support the ideal path: `V1 Draft` -> all risks reviewed -> `V1 Released`.
- The guidance should also support the iterative path: `V1 Draft` -> one or more review/modification rounds -> all risks reviewed -> `V1 Released`.
- The guidance should provide copyable chat examples for direct release and for indexed modification requests.

Document presentation rules:

- Include architecture version and generation time near the beginning and again in a closing metadata section.
- Present long external interface definitions as one function per mini-table instead of one oversized table, especially when the result may be exported to PDF.
- Present long dependency/callout interface definitions as one function per mini-table as well; Callout constraints and evidence are often too wide for one combined PDF table.
- In file relationship output, show `FC_MemMap.h` as included by all section-managed FC files.
- In MemMap output, include per-core CONST macros such as `FC_CONST_FAR_DATA_ALIGN4_COREx_START/STOP` when const data is core-local or replicated by core.
