# Structured Field Dictionary

## Goal

Define a shared vocabulary for requirement, architecture, and detailed-design objects.

Use this file before extending schemas or examples.

## Cross-Layer Fields

- `module`
  - FC short name, for example `Gp_NCA95yy`
  - must match the document family and object prefixes

- `source`
  - source artifact path or source label
  - use a concrete artifact whenever possible

- `status`
  - `draft`: extracted but not yet frozen
  - `ready`: internally prepared and suitable for review
  - `confirmed`: explicitly accepted by project input
  - `pending_confirm`: intentionally held open for project confirmation
  - `derived`: inferred from stronger upstream sources

- `decision`
  - normalized design choice recorded against an input item
  - should be short and action-oriented

- `decision_reason`
  - why the decision was taken
  - should name the driver, such as architecture freeze, grounding evidence, or missing project confirmation

- `impacts`
  - downstream sections or objects touched by the decision
  - prefer dotted paths such as `architecture.external_interfaces`

- `evidence`
  - concrete supporting paths, symbols, or module names
  - use this when the item is grounded in real engineering artifacts

## Requirement Layer

- `category`
  - one of `functional`, `interface`, `config`, `diag`, `timing`, `safety`, `resource`

- `requirements[*].id`
  - stable requirement identifier
  - keep unchanged across SRS, architecture, and detailed design traceability

## Architecture Layer

- `external_interfaces`
  - formal module-facing APIs frozen by architecture

- `dependency_interfaces`
  - formal FC dependency interfaces and callouts frozen by architecture

- `config_items`
  - configuration objects, feature switches, or tables that architecture intentionally names

- `status` in architecture interfaces
  - `formal`: must appear in detailed design
  - `reserved`: named but not implemented in this version
  - `conditional`: only legal when architecture explicitly includes it
  - `pending_confirm`: known candidate but not frozen yet

## Detailed Design Layer

- `grounding_modules`
  - selected grounding modules actually used for this target
  - must be a subset of `references/grounding/index.yaml`

- `relationship_links`
  - links between external, internal, and dependency objects
  - each name should resolve to a defined object in the detailed design set or a formal architecture interface

- `assumptions`
  - statements the design currently relies on
  - use only when the fact is not frozen upstream

- `risks`
  - known instability or project exposure
  - use when the open issue can affect generated correctness

## Grounding-Oriented Fields

- `grounding_patterns`
  - optional list of normalized patterns adopted from grounding
  - examples: `per_core_runtime_container`, `chip_mainfunction_pattern`
  - may be inferred from formal dependency interfaces, config switches, and selected grounding modules when the evidence is explicit

- `grounding_rejections`
  - optional list of patterns intentionally not adopted
  - use this for patterns that are present in reference modules but intentionally excluded from the target architecture

- `conf_evidence`
  - optional list of `Conf_*` file names or symbols that justify config or callout design

- `cfg_objects`
  - optional list of real `Cfg.c` configuration objects extracted from grounding modules
  - use this to drive `15. 配置宏参设计` with actual config containers, fields, and per-core or per-chip layout cues
  - prefer this over requirement-only config-point guesses when source `Cfg.c` is available

## Authoring Rules

- Record downgraded requirements instead of silently deleting them.
- Prefer `evidence` plus `decision_reason` together when the item is grounded in project code.
- Keep markdown rendering downstream from these structured objects; do not let markdown become the only source of truth.
