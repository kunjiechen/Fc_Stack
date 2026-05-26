# Gp_TLE92104 Summary

## Why It Matters

`Gp_TLE92104` is the strongest grounding sample in this set for a multi-core IoExtDev FC with explicit `CalloutGetCoreId`, per-core runtime indirection, chip-level configuration blocks, and a live `MainFunction` control loop.

## Observed Interface Shape

- External interfaces are defined in `Gp_TLE92104.h`.
- The exposed API set is compact and semantically focused:
  - `Init`
  - `MainFunction`
  - output control
  - mode get/set
  - fault get
  - register/status query

## Multi-core Grounding Value

- The implementation explicitly calls `Gp_TLE92104_CalloutGetCoreId()` and uses per-core runtime/config routing.
- This makes it a high-value grounding source for deciding:
  - whether a target FC should use `CalloutGetCoreId`
  - whether runtime should be indexed as `rtCont[core]`
  - how `Id -> chip -> runtime` access should be described in detailed design

## Dependency Style

- Callout dependencies include:
  - `CalloutGetCoreId`
  - signal output and input helpers
  - delay helpers
  - SPI setup/transmit helpers
- 对应配置资产位于 `src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TLE92104`。
- Concrete conf evidence:
  - `Gp_TLE92104_Cfg.h` enables `GP_TLE92104_MCAL_EN` and `GP_TLE92104_DET_EN`
  - `Gp_TLE92104_Cfg.h` shows active core split at `CORE1` and `CORE2`
  - `Gp_TLE92104_Cfg.h` exports `Gp_TLE92104_cfgSigMap_vcatst[GP_TLE92104_SIG_NUM]`
  - `Gp_TLE92104_Callout.h` exposes `CalloutGetCoreId`, SPI, delay, DIO, and PWM callouts
- This sample proves that dependency interfaces should be captured at FC/platform semantic level, not at raw bus-transaction narrative level only.

## Internal Design Clues

- The module clearly separates:
  - core selection
  - chip traversal
  - chip mode control
  - bus transaction helpers
  - diagnosis
- This is the best local baseline for a GPIO-expander-like FC that also needs mode/fault polling behavior.

## Cautions

- Do not blindly inherit all SPI-driven chip complexity if the target device is simpler.
- Reuse the per-core and dependency-shape patterns, then compress internal decomposition according to target complexity.
