# IoMcu Family Summary

## Why It Matters

The `IoMcu` family is the most important lower-layer grounding source in this baseline. It shows how the platform side of FCs is actually shaped in this engineering codebase.

Representative modules reviewed:

- `Gp_IoMcuDio`
- `Gp_IoMcuIcu`
- `Gp_IoMcuAdc`
- `Gp_IoMcuPwm`

## Grounding Value

- Generated `CfgData` headers are standard entry points.
- Multi-core routing through `CalloutGetCoreId` and `cfgCont[core]` / `rtCont[core]` is explicit in implementation.
- Callout options can be configurable per signal or per channel.

## What This Family Should Answer

- What does a normal lower-layer dependency interface look like in this repository
- When should `CalloutGetCoreId` be considered standard
- How are `cfgCont` and `rtCont` typically split
- How does `Conf_*` naming map to FC/module naming
- What kind of callout configurability is normal

## Use In Detailed-Design Generation

For IoExtDev target modules:

- use `IoMcu` to shape dependency interfaces
- use `IoMcu` to justify per-core runtime/config patterns
- use `IoMcu` to avoid inventing lower-layer API styles that do not exist in the real project

## Cautions

- `IoMcu` is a provider family, not the target FC style baseline for all external interfaces.
- Use it primarily for dependency and platform-shape grounding, not for chip-domain behavior decomposition.
