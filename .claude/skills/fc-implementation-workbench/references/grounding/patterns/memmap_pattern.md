# MemMap Pattern

## Baseline

Reviewed modules consistently place interfaces and runtime through module-local MemMap headers.

Observed variants:

- normal `CODE_START/STOP`
- data-section routing through module-specific MemMap
- `CODE_RAM_COPY` variant in `Gp_06_Adc3ph`

## Rules

- Always describe MemMap from grounded module evidence.
- Do not collapse all memory-section strategies into a generic one-size-fits-all paragraph.
