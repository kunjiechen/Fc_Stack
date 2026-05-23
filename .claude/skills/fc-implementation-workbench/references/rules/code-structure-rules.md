# FC Code Structure Rules

## Purpose

This file owns stable rules for file families, framework layout, cfg organization, callout strategy, and runtime-state structure.

## Standard File Family

Default FC module file family:

- `FC.c`
- `FC.h`
- `FC_Types.h`
- `FC_Cfg.h`
- `FC_CfgData.h`
- `FC_Cfg.c`
- `FC_Callout.h`
- `FC_Callout.c`
- `FC_MemMap.h`

Optional:

- `FC_Internal.h`
- `FC_Cali.c`
- `FC_Reg.h`

Company-standard expectations:

- `FC.c/.h` own the realize-interface entry points
- `FC_Callout.c/.h` belong to the dependency-interface layer
- `FC_Types.h` owns FC-scoped macros, types, structs, and enums
- `FC_CfgData.h` is the public declaration point for config and calibration objects
- `FC_MemMap.h` is unique per FC and supports repeated include switching

## When To Add Optional Files

Add `FC_Internal.h` when:

- multiple `.c` files share internal-only APIs
- state actions or helpers must be visible across internal translation units

Add `FC_Reg.h` when:

- register-controlled external devices exist
- register addresses, bit fields, command words, or frame constants are needed

Add `FC_Cali.c` only when:

- real calibration objects are confirmed

Prefer not to add `FC_Cali.c` for ordinary BSW FCs unless the project explicitly defines true calibration data.

## File Include Relations

Default preferred include shape:

- `FC.h` includes `FC_CfgData.h`
- `FC_Types.h` includes `FC_Cfg.h`
- `FC_CfgData.h` includes `FC_Types.h`
- `FC.c` includes `FC.h` and `FC_Callout.h` when callout exists
- `FC_Callout.c` includes `FC_Callout.h`
- `FC_Cfg.c` and `FC_Cali.c` include `FC_CfgData.h`

`Std_Types.h` should be part of the FC baseline include universe.

## Layering Rules

Internal FC layering should normally be described as:

- realize interface layer
- function layer
- dependency interface layer

Use functions between layers. Do not define variable-based interfaces between FC layers.

## Complex Module Split Rules

If the FC is complex, split source files by subfeature rather than by arbitrary code size.

Typical pattern:

- `FC.c` for entry points and dispatch
- `FC_SubFeatureA.c`
- `FC_SubFeatureB.c`

When multi-file split exists:

- external entry points still belong in `FC.c/.h`
- shared internal contracts may move into `FC_Internal.h`
- each split file should keep its own local static helpers and local static data where possible

## Single-Core Framework

Use single-core structure when:

- one core owns execution
- no cross-core runtime state is needed
- no cross-core synchronization is needed

Expected design output:

- `InitMemory`
- `Init`
- `MainFunction` if periodic behavior exists
- service APIs
- one runtime container or a small set of internal runtime objects

## Multi-Core Framework

Use multi-core structure when:

- tasks are split by core
- runtime objects are core-local
- initialization has synchronization points
- monitoring is per-core

Expected design output:

- per-core init ownership
- per-core task entries
- per-core cfg containers or indexes
- per-core runtime containers
- shared-state list
- synchronization-point list

Prefer explicit per-core objects instead of large `if(core==x)` logic.

## Configuration Rules

`FC_Cfg.h`

- feature switches
- count or size macros
- basic behavior-selection macros

`FC_CfgData.h`

- `extern` config declarations
- public config types if needed by consumers

`FC_Cfg.c`

- mapping tables
- dependency-binding tables
- state-machine tables
- per-core config tables
- register or resource tables

Do not place runtime-changing values in `Cfg.c`.

Do not use config globals as a substitute for interface or runtime data flow.

## Runtime-State Rules

Classify runtime objects as:

- input state
- status state
- intermediate state
- output state
- monitor state
- fault state
- retained state

For each runtime object, define:

- owner
- reader or writer sides
- lifecycle
- core affinity
- reset behavior

## Callout Rules

Use `Callout` when:

- hardware or platform differences exist
- project adaptation differences exist
- external dependency shape is unstable
- direct register or driver operations should be isolated

Do not expose raw driver dependence in external FC APIs.
Do not place core FC business logic in `Callout`; keep it in the function layer.

## MemMap Rules

Always identify at least:

- code sections
- runtime data sections
- const sections
- no-clear sections if applicable
- per-core sections if applicable

If config constants are core-local or replicated by core, include per-core const section strategy in the design.

Prefer section naming and section planning that can map to:

- `CODE`
- `CLEAR_FAR_DATA` / `CLEAR_NEAR_DATA`
- `NO_CLEAR_FAR_DATA` / `NO_CLEAR_NEAR_DATA`
- `INIT_FAR_DATA` / `INIT_NEAR_DATA`
- `CONST_FAR_DATA` / `CONST_NEAR_DATA`

If the project is AURIX-like, allow `A0` and `A1` section variants when the platform standard requires them.
