# External Interface Pattern

## Baseline

Use architecture-frozen external interfaces as the only allowed public API set for generated detailed design.

Grounding evidence:

- interface-rich IoExtDev: `Gp_TPT1145`
- compact IoExtDev: `Gp_TLE92104`, `Gp_DRV8889`
- lightweight FC: `Gp_WkUpSrcP`
- compact multi-core Cdd: `Gp_06_Adc3ph`

## Rules

- Prefer the smallest stable public API set that matches real module responsibility.
- Do not infer extra public APIs from chip capability alone.
- If a reference module implements optional external APIs behind compile-time switches, treat that as implementation evidence only, not architecture permission.
