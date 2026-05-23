# Internal Function Granularity Pattern

## Baseline

Reviewed modules support a moderate granularity:

- central public API entry
- chip or channel helper layer
- platform/bus helper layer

Best concrete evidence:

- `Gp_DRV8889` uses `ChipMainFunction`
- `Gp_TLE92104` separates core selection, chip handling, and bus activity
- `IoMcu` separates validation, channel handling, and callout routing

## Rules

- Prefer stable helper responsibilities over micro-splitting.
- Merge repeated access checks and shared bus/helper logic when grounded modules do so.
- Use chip-level helper functions when a repeated per-chip loop exists.
