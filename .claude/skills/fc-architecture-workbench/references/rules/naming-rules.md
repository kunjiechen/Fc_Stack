# Naming Rules

This reference condenses the naming guidance from:
- `../../archive/G-C046 软件接口命名规范.pdf`

Routine use note:
- the main naming guidance needed for later FC architecture work has already been extracted into this Markdown file
- the original PDF is useful mainly as provenance or audit backup

Use this file when generating FC names, functions, global variables, typedefs, structs, enums, and local variables.

## Core Identifier Pattern

The standard full variable pattern is:

`<Id>_<pp>{<Dd>}1-n_<xx><dt>`

Example:

`CrCtl_nMinShOff_C`

Meaning:
- `Id`: FC identifier or namespace
- `pp`: physical or logical subject of the variable
- `Dd`: description fields in CamelCase
- `xx`: extension indicating the variable category
- `dt`: data type suffix

## Namespace Preservation

When the requirement or source document gives an explicit FC/module name, preserve that exact module prefix as the C namespace by default.

Examples:
- FC name `Gp_DRV8889` -> functions use `Gp_DRV8889_Init`, `Gp_DRV8889_MainFunction`, `Gp_DRV8889_CalloutDioWrite`
- FC name `Gp_NCA9539` -> functions use `Gp_NCA9539_Init`, `Gp_NCA9539_CalloutI2cWrite`
- FC name `DRV8876` -> functions use `DRV8876_Init`, `DRV8876_Set...`
- FC name `Gp_TJA1043` -> functions use `Gp_TJA1043_Init`, `Gp_TJA1043_CalloutDioWrite`

Do not silently normalize underscore-separated FC names into CamelCase namespaces:
- forbidden unless explicitly requested by the user: `GpDrv8889_Init`
- forbidden unless explicitly requested by the user: `GpNca9539_Init`

This preservation rule applies to:
- external function names
- dependency/callout function names (必须包含 `<FC>_Callout` 前缀，禁止使用不绑定 FC 的通用名如 `FC_CalloutDioWrite`)
- typedef names
- enum names and enum values
- struct names
- global/static object names
- file relationship examples

Only configuration macro identifiers are converted to all caps, as defined in the configuration macro naming section.

If a legacy source file already uses a different namespace style, report the mismatch and ask whether to preserve the user-provided FC name or follow the legacy source style. Do not mix both styles inside the same generated architecture.

## Configuration Macro Naming

Configuration macro identifiers are an exception to normal CamelCase C identifier guidance.

Rules:
- configuration macro identifiers must be ALL_CAPS
- allowed characters are `A-Z`, `0-9`, and `_`
- the FC/module name portion must also be converted to uppercase
- examples: `GP_TJA1043_CFG_DEV_ERROR_DETECT`, `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`, `GP_DRV887X_CFG_DEV_ERROR_DETECT`
- forbidden: `Gp_NCA9539_CFG_DEV_ERROR_DETECT` (大小写混用), `Drv8876_CFG_SW_MAJOR_VERSION` (下划线缺失), `FC_CFG_DEV_ERROR_DETECT` (通用 `FC_` 前缀缺少模块命名空间)
- this rule applies only to macro identifiers, not file names, function names, type names, struct members, or configuration object names
- 禁止生成软件版本宏 `CFG_SW_MAJOR_VERSION` / `CFG_SW_MINOR_VERSION`

## Field Rules

### `Id`

- use the FC name as the top-level namespace
- keep it consistent across functions, types, variables, and files

### `pp`

- use lowercase letters
- use a short noun or standardized abbreviation
- prefer a single clear concept such as speed, level, mode, counter, index, buffer

Examples from the source convention:
- `adc`
- `lvl`
- `mod`

### `Dd`

- use CamelCase
- use ordered descriptive keywords
- numbers may appear at the end when indexing same-category items

### `xx`

Use exactly one category marker where the rule requires it:
- `k` calibration variable
- `v` interface-visible global variable
- `l` file-internal global variable

### `dt`

Use the C-style encoded data type suffix.

Common base suffixes:
- `b` boolean
- `u8`, `u16`, `u32`, `u64`
- `s8`, `s16`, `s32`, `s64`
- `f32`, `f64`
- `st` struct
- `e` enum
- `t` typedef-defined type
- `f` function

Common extensions:
- `p` pointer
- `a` array
- `c` const

Examples:
- `u8`
- `pu16`
- `ast`
- `cu64`
- `tst`

## Function Naming

Function pattern:

`<Id>_{<Dd>}1-n`

Examples:
- `ModeCtrl_GetCurrentState`
- `Can_Init`
- `Pwm_SetOutputLevel`

Guidance:
- use the FC identifier as prefix
- preserve the FC identifier exactly as given, including underscores, unless the user explicitly requests another namespace style
- use action-oriented CamelCase for the rest
- prefer clear verbs such as `Init`, `MainFunction`, `Get`, `Set`, `Read`, `Write`, `Update`

## Global Variables

Pattern:

`<Id>_<pp>{<Dd>}1-n_<xx><dt>`

Examples:
- `CurrSample_cntOverTempFault_lu32`
- `CurrSample_thdOverTempFaultCnt_ku32`
- `CurrSample_flgOverTempFault_vb`

Interpretation:
- `_l...` is file-internal state
- `_k...` is calibration
- `_v...` is interface-visible global variable according to the naming spec

When working with FC architecture generation, still follow the FC architecture rule that external interfaces should be function-based rather than global-variable-based.

## Local Variables

Pattern:

`{<Dd>}1-n_<dt>`

Examples:
- `TmpVal_f32`
- `CoreId_u8`
- `FaultCnt_u16`

## Typedef Naming

Pattern:

`<Id>_<Dd>1-nType`

Example:

`ModeCtrl_CtrlSigType`

## Struct Naming

Pattern:

```c
typedef struct [<Id>_]<Dd>1-n
{
    ...
}[<Id>_]<Dd>1-nType;
```

Example:

```c
typedef struct Can_TxQue
{
    uint8 TxCnt_u8;
    uint8 TxStatus_u8;
} Can_TxQueType;
```

Global variable using a struct type:
- `Can_queChgBusTxQue_ltst`

Local variable using a struct type:
- `ChgBusTxQue_tst`

## Enum Naming

Pattern:

```c
typedef enum <Id>_<Dd>1-n
{
    <Id>_<Dd>1-n_e
}<Id>_<Dd>1-nType;
```

Use enum values and enum type names consistently with the FC namespace.

## Architecture-Generation Checks

When generating names, explicitly check for:
- missing FC namespace prefix
- use of mixed naming styles inside the same FC
- missing `xx` marker on global variables
- misuse of calibration marker for normal configuration
- overlong or implementation-driven callout names
- unwanted normalization of explicit FC names such as `Gp_DRV8889` into `GpDrv8889`

Prefer names that reflect FC intent, not technology leakage.
