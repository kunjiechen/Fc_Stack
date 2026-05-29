# FC Architecture Rules

This reference condenses the architecture guidance from:
- `../../archive/G-C119 FC开发指南（C语言）.pdf`

Routine use note:
- the main guidance needed for later FC architecture work has already been extracted into this Markdown file
- the original PDF is useful mainly as provenance or audit backup

Use this file when deciding FC file structure, layering, interface placement, and MemMap strategy.

## Core Principles

- FC architecture design comes before FC code writing.
- The architecture should decouple FC evolution from software integration work.
- FC external interface definition includes more than functions. It also includes:
  - integration-visible information that the FC must provide
  - special integration constraints imposed by FC functional needs
- The architecture definition must cover:
  - file structure definition
  - interface definition
  - memory section definition
- The architecture definition must carry version and release state.

## Version And Release Rules

Use only integer major versions:

- `V1`
- `V2`
- `V3`

Do not use minor or patch versions.

Input-driven behavior:

- Requirement document only: generate initial `V1`.
- Draft architecture file with optional requirement document: update the draft and keep the same version.
- Draft architecture with all pending confirmations resolved: promote to `Released` without changing version.
- Released architecture file plus requirement document: increment to the next major version.

Release gate:

- Do not mark an architecture as `Released` while any real risk item remains `待评审` or `待修改`.
- Risk tables should include a stable `索引` for each item so users can answer in chat by index.
- Risk tables should use `状态` values exactly as `待评审`, `已评审`, and `待修改`.
- Risk tables should include a `备注` column for user confirmation or modification comments.
- Risk tables should include an `R-OTHER` / `其他` row for user-provided suggestions.
- If the user replies in chat, parse indexed decisions such as `R1、R3 已评审；R4 待修改，备注：...` and update the table before applying changes.
- Architecture updates and upgrades should include a concise change summary.

## Default FC File Set

Default required files:
- `FC.c`
- `FC.h`
- `FC_Cfg.c`
- `FC_Cfg.h`
- `FC_CfgData.h`
- `FC_Types.h`
- `FC_MemMap.h`

Optional files:
- `FC_Cali.c`
- `FC_Callout.c`
- `FC_Callout.h`
- `FC_Reg.h` for SPI/I2C/register-based external-device register definitions
- `FC_Desc.c`
- `FC_Desc.h`
- `FC_Desc_Cfg.c`
- `FC_Desc_Cfg.h`
- `FC_Desc_CfgData.h`
- `FC_Desc_Types.h`

> **Desc 文件组说明**：Desc 文件组仅用于非常复杂的多层 FC（多函数层、通信与寄存器抽象层分离、多核/多实例分解、配置簇独立拆分等场景）。常规架构生成管道（SKILL.md §9）默认不生成 Desc 文件组。仅当人工评审判定 FC 确实需要 Descriptor 层抽象时才手动启用。

## File Responsibilities

### `FC.c` and `FC.h`

Contain:
- FC implementation code
- internal static variables
- external interface function definitions and declarations

Rules:
- when multiple code file groups exist, the main FC external interface must remain in `FC.c` and `FC.h`
- do not define global variables as the FC external interface

### `FC_Cfg.c`, `FC_Cfg.h`, `FC_CfgData.h`

Contain:
- configuration parameter definitions as const variables in `FC_Cfg.c`
- configuration macro switches or macro values in `FC_Cfg.h`
- declarations for configuration parameters and calibration parameters in `FC_CfgData.h`

Use these files for compile-time and integration-time configuration.

### `FC_Cali.c`

Contains calibration parameter definitions as const variables.

For BSW FCs, calibration is optional and should be used conservatively. Many threshold-like items belong in `Cfg` unless there is a real calibration workflow.

### `FC_Types.h`

Contains:
- common FC macros
- special basic type declarations
- structure declarations
- enum declarations

If the FC becomes complex and multiple type files exist, consider a shared general type file such as `FC_Gen_Types.h` for definitions referenced by several groups.

### `FC_Callout.c` and `FC_Callout.h`

Contain dependency interface implementation and declaration.

Use when the dependency cannot be represented as a simple macro replacement or standard platform signal binding.

If callout dependencies are defined, include both files in architecture file lists:
- `FC_Callout.h` declares the adaptation contract.
- `FC_Callout.c` owns the project adaptation implementation or integration stub.

Callout prototypes must use pointer parameters instead of array declarators. For example, use `uint16* TxData_pu16`, `uint16* RxData_pu16`, and `uint16 Size_u16` for a 16-bit SPI transceive callout.

### `FC_Reg.h`

Contains register and protocol constants for SPI/I2C/register-based external devices:
- register addresses
- bit masks and bit positions
- command words
- frame constants
- register reset/default constants

`FC_Reg.h` includes `Std_Types.h`. `FC_Cfg.h` includes `FC_Reg.h` when configuration macros or configuration tables reference register symbols.

### `FC_MemMap.h`

Contains memory section macro mapping or integration override mapping for all FC files.

Each FC has one and only one `FC_MemMap.h`.

Show `FC_MemMap.h` as a section-boundary include for all FC-created files that place code, runtime data, const data, or calibration data into sections.

## Layering

### Realize Interface Layer

Contains FC external interface functions for user calls, such as:
- init
- mainfunction
- getter and setter style signal interfaces

Default behavior for asynchronous interfaces:
- save user-provided output values into internal variables
- expose user-readable values from internal variables written by the previous mainfunction cycle

Defensive checks belong here, not in deeper internal functions. Typical checks:
- init called or not
- input range validity
- output pointer null check

When a defensive check fails:
- do not execute the functional behavior
- record the issue in DET-related internal variables
- return `E_NOT_OK` for external interfaces other than mainfunction

### Function Layer

Contains internal static functions implementing FC behavior.

Rules:
- focus on functional decomposition
- improve reuse
- reduce cyclomatic complexity
- internal functions do not need external defensive checks

### Dependency Interface Layer

Contains dependency-facing integration logic.

Possible styles:
- fixed dependency code with compile-time selection
- macro replacement
- standard interface binding
- callout

## Dependency Strategy

### Fixed Dependency Code

Use when dependency options are limited and stable, such as a small family of MCAL variants selected by compile-time macros.

If used, provide an `UNDEFINED` style option so builds can still compile when the dependency is not present.

### Macro Replacement

Use for very simple dependencies with no complex parameters or instance scaling, such as entering or leaving a critical section.

The macro should still allow the codebase to compile when configured as empty.

### Standard Interface Binding

Use when the dependency follows a project-wide standard signal interface and only the bound function name changes.

Allow null binding or equivalent compile-safe fallback if the dependency is absent.

### Callout

Use when dependency semantics are not cleanly standardized.

Design rule:
- derive callout parameters from FC functional needs
- do not mirror AUTOSAR or MCAL concepts unless they are truly required by the FC function

Examples:
- an SPI transfer callout should expose buffers and transfer length, not AUTOSAR sequence and job details
- a pin control callout should expose the desired logical level, not board-specific inversion logic

Board inversion, channel mapping, or technology adaptation belongs inside the callout implementation.

## Internal State Guidance

- FC needs initialization behavior at least for internal global variable initialization.
- FC should define internal global variables for DET or internal error tracking.
- FC may define internal fault-state variables when needed.
- Internal global variables should be initialized in the FC init function, not by relying on compiler default initialization semantics.
- Prefer reducing repeated direct operations on global variables in functions. Copy to locals or use structured state where appropriate.

## File Structure Judgment Tips

Use the simple structure by default. Split into `Desc` groups only when there is real complexity, such as:
- multiple function layers
- communication and register abstraction layers
- multi-core or multi-instance decomposition
- separate configuration clusters

Avoid both extremes:
- do not under-specify a complex dependency-heavy FC with a flat file set
- do not over-split a simple FC into many artificial files
