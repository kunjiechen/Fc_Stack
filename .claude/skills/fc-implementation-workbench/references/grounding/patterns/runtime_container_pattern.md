# Runtime Container Pattern

## Baseline Families

- direct signal/chip runtime array:
  - `Gp_WkUpSrcP`
  - `Gp_TPT1145`

- per-core runtime container:
  - `Gp_TLE92104`
  - `Gp_DRV8889`
  - `Gp_06_Adc3ph`
  - `IoMcu`

## Rules

- Choose runtime pattern from grounded module family first.
- Only use per-core runtime when there is real evidence for:
  - `CalloutGetCoreId`
  - per-core configuration containers
  - signal mapping or chip ownership tied to core
