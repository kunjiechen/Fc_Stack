# Grounding Selection Rules

## Goal

Choose a small, explainable set of grounding modules before generating architecture or detailed design.

Grounding is successful only when the selected modules answer the target FC's concrete design questions.

## Selection Order

1. Match the target layer and device family.
2. Match runtime shape and multi-core shape.
3. Match dependency and callout family.
4. Match configuration evidence in `Conf_*`.
5. Use secondary modules only to correct style drift, not to override the primary family.

## Primary Rules

- If the target FC is `IoExtDev` and uses a polling `MainFunction`, start from:
  - `Gp_TPT1145`
  - `Gp_TLE92104`
  - `Gp_DRV8889`

- If the target FC needs explicit per-core routing or a `CalloutGetCoreId`, prefer:
  - `Gp_TLE92104`
  - `Gp_DRV8889`
  - `IoMcu`

- If the target FC is simpler, chip-centric, and does not need a per-core front layer, prefer:
  - `Gp_TPT1145`

- If the design question is mainly about lower-layer dependency style, `CfgData`, or generated `Conf_*` mapping, add:
  - `IoMcu`

- If the target FC is intentionally lightweight or has no `MainFunction`, use secondary correction samples:
  - `Gp_WkUpSrcP`
  - `Gp_06_Adc3ph`

## Negative Rules

- Do not copy a multi-core pattern from `Gp_TLE92104` or `Gp_DRV8889` when the target FC has no real core routing need.
- Do not inherit conditional external interfaces from `Gp_DRV8889` unless architecture formally freezes them.
- Do not copy transceiver-specific wakeup semantics from `Gp_TPT1145` into unrelated GPIO expander or bridge devices.
- Do not use secondary modules to invent external APIs that are absent from architecture.

## Required Grounding Summary Output

Before generating markdown, record:

- selected grounding modules
- adopted patterns
- rejected patterns
- conf evidence used
- why the selection fits the target FC
