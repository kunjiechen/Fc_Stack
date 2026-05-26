# Gp_TPT1145 Summary

## Why It Matters

`Gp_TPT1145` is a strong IoExtDev grounding sample for an interface-rich chip driver with `Init + MainFunction + multiple control/query APIs`, while still keeping a relatively direct per-chip runtime organization.

## Observed Interface Shape

- External interfaces are declared in `Gp_TPT1145.h`.
- Representative API set:
  - `Init`
  - `MainFunction`
  - mode set/get
  - wakeup reason query
  - wakeup mode set
  - transceiver status and flag access
- This module shows that one IoExtDev FC can legitimately expose several semantically stable external interfaces without forcing excessive internal decomposition in the document.

## Runtime Pattern

- Runtime container is a direct chip-indexed array.
- Access pattern is simple:
  - read config from `Gp_TPT1145_cfgCont_vcatst[...]`
  - read/write runtime from `Gp_TPT1145_rtCont_latst[...]`
- This is a good grounding sample when the target module is chip-centric and does not require a per-core container front layer.

## Dependency Style

- The module depends on generated `CfgData` and MemMap conventions.
- 对应配置资产位于 `src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TPT1145`。
- Concrete conf evidence:
  - `Gp_TPT1145_CfgData.h` exports `Gp_TPT1145_cfgCont_vcatst[GP_TPT1145_MAX_CHIP_NUM]`
  - `Gp_TPT1145_CfgData.h` uses dedicated far-data alignment macros
  - `Gp_TPT1145_Callout.h` exposes `Gp_TPT1145_CbkReportWakeup` and `Gp_TPT1145_SpiTransSync`
- It behaves like a callout/platform-adapted FC even when the header itself is interface-focused.
- Use this sample for:
  - external interface count and naming rhythm
  - chip runtime item grouping
  - status/wakeup/fault query style

## Cautions

- Do not over-copy transceiver-specific semantics into unrelated GPIO-expander designs.
- Use this module for interface rhythm and chip-runtime organization, not for chip-specific function decomposition.
