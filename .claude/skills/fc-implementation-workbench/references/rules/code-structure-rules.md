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

Single-core design constraints:

- no `CalloutGetCoreId` in interface flowcharts or dependency lists
- no per-core indexing in runtime containers
- no core-traversal loops in any flowchart
- no core-matching decision nodes in any flowchart
- instance/chip traversal (if multi-instance) must not be conflated with core traversal

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

Configuration design is split into two dimensions:

1. **Configuration macros** (`Cfg.h`) — what can be configured at compile time
2. **Configuration types** (`CfgData.h` / `Cfg.c`) — the structured shape of configuration data

### Configuration Macros — `FC_Cfg.h`

- feature switches (enable/disable sub-features)
- count or size macros (array dimensions, buffer sizes, instance counts)
- basic behavior-selection macros (strategy selection, mode defaults)
- compile-time platform or project selection
- thresholds expressed as scalar compile-time constants

**Coverage requirement:** Macros must cover all architecture-sourced configuration parameters. Macros introduced by coding standards during detailed design (e.g. `FC_CFG_MAX_xxx`, `FC_CFG_xxx_ENABLED`) are expected additions.

### Configuration Types — `FC_CfgData.h` / `FC_Cfg.c`

Configuration types define the structured data layout of configuration. Every FC must have configuration type definitions unless it has zero configurable parameters.

`FC_CfgData.h` owns:

- configuration type definitions (structs, enums for config domains)
- `extern` declarations of configuration objects
- public config types if needed by consumers

Configuration type splitting guidelines:

| Type Category | Contents | When Needed |
|---|---|---|
| Top-level container | Root config struct for one FC instance | Always (if FC has any config) |
| Hardware resource config | Bus addresses, channel assignments, register bases | External device or bus access exists |
| Timing / threshold config | Delays, timeouts, settling times, retry counts | Interface requires timing parameters |
| Feature enable config | Sub-feature switches, strategy selections | Multiple optional sub-features exist |
| Per-instance config | Array of per-instance structs | Multi-instance or per-core deployment |
| Dependency binding config | Callout function pointers, dependency handles | Callout interfaces exist |

**Field description rule:** Each configuration type must include field descriptions for its key fields, stating the field meaning, value range, and constraints. A configuration type table without field-level descriptions is incomplete.

**Field naming convention:** Key field names must carry type suffixes matching their C type:
- `_u8` (uint8), `_u16` (uint16), `_u32` (uint32), `_u64` (uint64)
- `_s8` (sint8), `_s16` (sint16), `_s32` (sint32), `_s64` (sint64)
- `_b` (boolean), `_f32` (float32)
- Example: `PeriodMax_u32` → field type column shows `uint32`
- The field type column must explicitly write the C standard type, not "enumeration" or "struct" without the concrete type name
- If the field is an enum type, the field type column shows the enum type name (e.g., `DeviceModeType`); the field name still follows the value-semantic suffix convention

**Type splitting principle:** Split by semantic ownership (hardware, timing, feature, instance), not by file size or arbitrary grouping.

`FC_Cfg.c` owns:

- concrete configuration object definitions
- mapping tables
- dependency-binding tables
- state-machine tables
- per-core config tables
- register or resource tables

Do not place runtime-changing values in `Cfg.c`.

Do not use config globals as a substitute for interface or runtime data flow.

### Configuration Parameter Design Validation

Before finalizing, confirm:

1. Architecture config parameters → all have corresponding macros
2. Coding-standard macros → explicitly listed as design additions
3. Type splitting → follows semantic boundaries
4. All config types have field-level descriptions (meaning, value range, constraints)
5. No experience with config types → marked `pending-confirmation`, proposed layout documented

## 运行参数设计规则

运行参数设计分为两个维度：

1. **运行变量** — 运行时变量清单
2. **运行参数类型** — 运行时数据的结构化类型定义

### 运行变量

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

### 运行参数类型

运行参数类型定义运行时数据的结构化布局。至少定义一个全局运行参数类型承载模块级状态。

类型拆分按语义边界：
- 全局运行态容器（模块级状态，如 InitStatus、DET 错误记录）
- 每实例运行态子结构（多实例时每实例独立字段）
- 每核运行态子结构（多核时每核独立字段）
- 故障运行态子结构（故障检测/确认/恢复字段聚合）
- 监控运行态子结构（周期采样/监控数据字段聚合）

每个关键字段必须包含字段描述（含义和取值范围）。

**字段命名规范：** 关键字段名必须携带类型后缀（`_u8`/`_u16`/`_u32`/`_s8`/`_s16`/`_s32`/`_b`/`_f32` 等），与 C 类型对应。字段类型列明确写出 C 标准类型。示例：`FaultConfirmCnt_u8` → 字段类型列填 `uint8`。

## Callout Rules

Use `Callout` when:

- hardware or platform differences exist
- project adaptation differences exist
- external dependency shape is unstable
- direct register or driver operations should be isolated

Do not expose raw driver dependence in external FC APIs.
Do not place core FC business logic in `Callout`; keep it in the function layer.

Standard Callout categories to consider during design:

| Category | Example Prototype | Trigger Condition |
|---|---|---|
| Core Identification | `CalloutGetCoreId` | Multi-core design with per-core routing |
| Delay / Timing | `CalloutDelayUs` / `CalloutWaitMs` | Interface requires wait, settling, or debounce periods |
| Bus Communication | `CalloutSpiTransmit` / `CalloutI2cWrite` | External device access via bus |
| Signal I/O | `CalloutDioWrite` / `CalloutPwmSet` | Direct signal output or input |
| Platform Services | `CalloutGetTimestamp` / `CalloutEnterCritical` | OS or platform service dependency |

Every delay/timing requirement found in external interface execution steps or state-machine transition conditions must produce a corresponding delay Callout entry in the dependency interface design.

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
