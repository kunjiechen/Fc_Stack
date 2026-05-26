# Company Code Standards Learning Notes

## Purpose

This note captures the local company coding and FC standards that materially affect implementation-level detailed design output.

这些笔记主要整理自以下规范材料：

- `Standard/Conversion/Code/FC_Code_Standard.md`
- `Standard/Conversion/Code/G-C119 FC开发指南（C语言）/G-C119 FC开发指南（C语言）.md`
- `Standard/Conversion/Code/G-C046 软件接口命名规范/G-C046 软件接口命名规范.md`
- `Standard/Conversion/Code/G-C045 软件模块命名规范/G-C045 软件模块命名规范.md`
- `Standard/Conversion/Code/MemoryLayout段定义/MemoryLayout段定义.md`
- `Standard/Conversion/Code/C代码注释关键字/C代码注释关键字.md`

## 1. File-Family And Layering Constraints

- The standard FC file family is not optional in spirit. `FC.c/.h`, `FC_Types.h`, `FC_Cfg.h`, `FC_CfgData.h`, `FC_Cfg.c`, and `FC_MemMap.h` are the default baseline.
- `FC_Cali.c` is optional and usually absent for normal BSW FCs unless real calibration objects exist.
- `FC_Callout.c/.h` belongs to the dependency-interface layer. It is not a general dumping place for FC logic.
- Complex FCs may split source files by subfeature, but the main realize-interface entry still belongs in `FC.c/.h`.
- Layer boundaries are explicit:
  - realize interface layer
  - function layer
  - dependency interface layer
- Cross-layer communication should use functions, not variable interfaces.

## 2. External Interface Rules

- BSW FCs should not expose global variables as interfaces.
- `Init` and `MainFunction` are primary realize-interface layer objects.
- Non-`MainFunction` external APIs should normally use `Std_ReturnType`.
- For asynchronous multi-core or multi-instance FCs, external interfaces typically locate cfg/runtime ownership and then update or read internal state.
- `Std_ReturnType` at the realize-interface layer usually represents defensive-check success or failure, not business semantics.

## 3. Defensive-Check Rules

- Defensive checks belong mainly to the external interface layer.
- Standard checks include:
  - initialization completed
  - input range valid
  - output pointer not null
- On defensive-check failure:
  - do not execute business logic
  - record DET-style information
  - return `E_NOT_OK`
- Internal helpers should not duplicate these checks unless a special reason exists.

## 4. Naming Constraints

- Customer-facing or exchangeable FC identifiers should use the `Gp_` vendor namespace style.
- FC code symbols use the FC code-space prefix, but chip-model suffixes should not leak into code-level identifiers.
- Variable naming follows the structured style:
  - `<Id>_<pp>{<Dd>}_{1-n}<xx><dt>`
- Common storage or visibility suffix intent matters:
  - `l` for local static
  - `v` for globally visible const config
  - `k` for calibration const
- Data-type suffixes are mandatory design information, not cosmetic naming.

## 5. MemMap Constraints

- MemMap define names follow a strict ordered shape:
  - `FCNAME_PART1_[ALIGN]_[CORE]_[ASIL]_[DESC]_START/STOP`
- Section-part order cannot be rearranged.
- The design should explicitly decide:
  - code sections
  - clear/no-clear RAM sections
  - init-data sections
  - const-data sections
  - per-core sections
  - optional safety or custom descriptors such as `CALI`
- `MemMap.h` is expected to support repeated inclusion for section switching.

## 6. Detailed-Design Extraction Hints From Comment Standards

- Internal types, enums, structs, local variables, global variables, internal functions, and interface functions can be documented in table form when source comments follow the standard tags.
- Internal function comment blocks define a stable extraction shape:
  - function name
  - service ID
  - sync/async
  - reentrancy
  - parameters
  - return value
  - description
- This supports implementation-level detailed design sections that mirror source-code review and traceability.

## 7. What This Changes In The Skill

- The skill should treat company standards as stronger than generic engineering habits.
- The skill should prefer function-layer decomposition over variable coupling.
- The skill should describe interface behavior as:
  - defensive checks
  - cfg/runtime lookup
  - subfunction execution
  - dependency invocation
  - result publication
- The skill should preserve MemMap naming and file-family rigor as first-class design outputs.
