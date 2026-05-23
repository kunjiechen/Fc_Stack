# Gp_WkUpSrcP Summary

## Why It Matters

`Gp_WkUpSrcP` is a lightweight FC sample that helps prevent every generated detailed design from becoming an oversized chip-driver decomposition.

## Observed Interface Shape

- External interfaces are defined in `Gp_WkUpSrcP.h`.
- Public API is intentionally small:
  - `Init`
  - `GetWkUpSts`

## Runtime Pattern

- Runtime is a direct array indexed by signal or wakeup entity.
- This is useful when the target FC is essentially a state or signal processing module rather than a heavy device-control module.

## Grounding Use

- Use this module to ground:
  - minimal FC structure
  - small runtime-container descriptions
  - non-IoExtDev overdesign avoidance

## Cautions

- Do not use this module to decide lower-layer dependency shape for a register-driven device FC.
