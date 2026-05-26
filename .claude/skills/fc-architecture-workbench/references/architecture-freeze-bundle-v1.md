# Architecture Freeze Bundle V1

## Purpose

This file defines the first contract for the architecture freeze bundle used by `fc-architecture-workbench`.

The goal is to move architecture generation from:

```text
requirement text / architecture seed
-> direct markdown writing
```

to:

```text
requirement-derived input / architecture seed
-> architecture freeze bundle
-> validation
-> markdown rendering
-> implementation constraint export
```

This contract is intentionally narrower than a final long-term schema.
It is the first stable freeze-layer contract that can support:

- interface freezing
- config classification
- file-family freezing
- MemMap freezing
- risk isolation
- implementation boundary export

## 1. Position Inside Architecture Skill

The bundle sits inside the architecture skill workflow:

```text
requirement-derived input
  + architecture seed
  + grounding evidence
  -> architecture freeze bundle
  -> architecture markdown
  -> implementation constraint export
```

Its job is not to re-explain requirements or write implementation detail.
Its job is to freeze the architecture boundary.

## 2. Relationship To `semantic-model.md`

`semantic-model.md` remains the lightweight architecture object model for rendering and review.

This file adds the freeze-layer objects that are still missing there:

- freeze decision objects
- coverage result objects
- rule/grounding evidence objects
- implementation constraint objects

In practice:

- `semantic-model.md` describes `what the architecture contains`
- `architecture-freeze-bundle-v1.md` describes `why it is frozen that way` and `what implementation may or may not do next`

The two documents should stay aligned.
The freeze bundle may embed the semantic-model object groups directly.

## 3. Top-Level Bundle Shape

Recommended top-level object:

```json
{
  "module": "Gp_NCA95yy",
  "architecture_version": "V1",
  "architecture_status": "Draft",
  "output_mode": "Formal Draft",
  "layer": "IoExtDev",
  "grounding_summary": {},
  "input_contract": {},
  "freeze_matrix": [],
  "coverage_result": [],
  "rule_evidence": [],
  "grounding_evidence": [],
  "external_apis": [],
  "dependency_apis": [],
  "binding_items": [],
  "config_macros": [],
  "strategy_items": [],
  "calibration_items": [],
  "runtime_states": [],
  "memmap_sections": [],
  "file_items": [],
  "risk_items": [],
  "implementation_constraints": {},
  "change_summary": []
}
```

Required top-level fields:

- `module`
- `architecture_version`
- `architecture_status`
- `output_mode`
- `freeze_matrix`
- `coverage_result`
- `implementation_constraints`

Recommended top-level fields:

- `layer`
- `grounding_summary`
- `input_contract`
- `rule_evidence`
- `grounding_evidence`
- all semantic object groups
- `change_summary`

## 4. Input Contract Object

Use to record what the freeze bundle consumed.

Recommended shape:

```json
{
  "requirement_input": "artifacts/srs_Gp_NCA95yy.md",
  "architecture_seed": "artifacts/gp_nca95yy_architecture_seed.yaml",
  "grounding_sources": [
    "references/source-grounding-aurix2g-live-baseline.md"
  ],
  "project_constraints": [
    "Current implementation follows AURIX2G per-core config style."
  ]
}
```

Purpose:

- prove the bundle is not free-floating
- make replay and regression easier

## 5. Grounding Summary Object

Use to summarize the selected architecture baseline before freezing.

Recommended fields:

- `module_family`
- `closest_live_patterns`
- `callout_style`
- `memmap_style`
- `multi_core_style`
- `config_split_style`
- `register_carrier_needed`
- `notes`

Example:

```json
{
  "module_family": "IoExtDev",
  "closest_live_patterns": ["Gp_TLE92104", "Gp_TPT1145"],
  "callout_style": "Heavy callout adaptation",
  "memmap_style": "Per-module with per-core CONST/RAM sections",
  "multi_core_style": "Current-core ownership",
  "config_split_style": "Source/config/integration split",
  "register_carrier_needed": true
}
```

## 6. Freeze Matrix Object

This is the core new object.
Each row records one freeze decision from requirement/seed into architecture.

Required fields:

- `source_id`
- `source_type`
- `architecture_target`
- `target_name`
- `freeze_action`
- `freeze_status`
- `reason`

Recommended fields:

- `trace_ids`
- `decision`
- `decision_reason`
- `rule_refs`
- `grounding_refs`
- `implementation_impact`
- `notes`

Allowed `source_type` values:

- `requirement`
- `constraint`
- `architecture_seed`
- `grounding_rule`

Allowed `freeze_action` values:

- `freeze_external_api`
- `freeze_dependency_api`
- `freeze_binding_item`
- `freeze_config_macro`
- `freeze_calibration_item`
- `freeze_runtime_state`
- `freeze_memmap_section`
- `freeze_file_item`
- `reserve`
- `mark_pending_confirm`
- `reject`
- `architecture_only_constraint`

Allowed `freeze_status` values:

- `formal`
- `conditional`
- `reserved`
- `pending_confirm`
- `rejected`

Example:

```json
{
  "source_id": "SRS-GPNCA95YY-IF-0005",
  "source_type": "requirement",
  "architecture_target": "external_api",
  "target_name": "Gp_NCA95yy_GetDevFaultSig",
  "freeze_action": "freeze_external_api",
  "freeze_status": "formal",
  "reason": "Requirement explicitly requires a readable device fault interface.",
  "rule_refs": ["project-style-rules.md"],
  "grounding_refs": ["Gp_TLE92104"],
  "implementation_impact": "Implementation must keep this interface and may not replace it with an internal-only fault path."
}
```

## 7. Coverage Result Object

Use to formally answer requirement coverage questions.

Required fields:

- `requirement_id`
- `coverage_status`
- `coverage_object`
- `reason`

Recommended fields:

- `notes`
- `trace_ids`

Allowed `coverage_status` values:

- `covered`
- `covered_with_constraint`
- `reserved`
- `pending_confirm`
- `not_applicable_at_architecture`
- `not_covered`

Example:

```json
{
  "requirement_id": "SRS-GPNCA95YY-FUNC-0002",
  "coverage_status": "covered_with_constraint",
  "coverage_object": "Gp_NCA95yy_Init + config tables",
  "reason": "Current architecture freezes direction configuration at init phase only."
}
```

## 8. Rule Evidence Object

Use to prove architecture choices are rule-driven.

Required fields:

- `object_group`
- `object_name`
- `rule_source`
- `rule_reason`

Recommended fields:

- `rule_type`
- `notes`

Example:

```json
{
  "object_group": "file_items",
  "object_name": "Gp_NCA95yy_Callout.c",
  "rule_source": "project-style-rules.md",
  "rule_reason": "Modules using callout dependency interfaces must carry both Callout.h and Callout.c."
}
```

## 9. Grounding Evidence Object

Use to prove architecture choices are grounded in live or retained source patterns.

Required fields:

- `object_group`
- `object_name`
- `grounding_source`
- `grounding_reason`

Recommended fields:

- `pattern_name`
- `notes`

Example:

```json
{
  "object_group": "memmap_sections",
  "object_name": "GP_NCA95YY_CONST_FAR_DATA_ALIGN4_COREx",
  "grounding_source": "source-grounding-aurix2g-live-baseline.md",
  "grounding_reason": "Live AURIX2G modules use per-core const sections when config ownership is core-local."
}
```

## 10. Semantic Object Groups

The freeze bundle reuses the existing semantic object groups:

- `external_apis`
- `dependency_apis`
- `binding_items`
- `config_macros`
- `strategy_items`
- `calibration_items`
- `runtime_states`
- `memmap_sections`
- `file_items`
- `risk_items`

These groups should follow `semantic-model.md`, but may include extra freeze-layer fields:

- `trace_ids`
- `freeze_status`
- `decision`
- `decision_reason`
- `rule_refs`
- `grounding_refs`

If both `status` and `freeze_status` exist:

- `status` is the semantic/rendering-facing state
- `freeze_status` is the freeze-governance state

They should normally align.

## 11. Implementation Constraints Object

This object exports hard architecture boundaries for implementation-stage use.

Recommended shape:

```json
{
  "frozen_external_interfaces": [],
  "frozen_dependency_interfaces": [],
  "frozen_binding_items": [],
  "frozen_config_items": [],
  "reserved_capabilities": [],
  "pending_confirm_items": [],
  "implementation_prohibitions": [],
  "implementation_required_areas": []
}
```

Recommended content:

- `frozen_external_interfaces`
  - names or prototypes implementation must not change silently
- `frozen_dependency_interfaces`
  - names or prototypes implementation must not bypass
- `frozen_binding_items`
  - binding boundaries implementation must not bypass or silently collapse
- `frozen_config_items`
  - config boundary implementation must respect
- `reserved_capabilities`
  - abilities implementation must not silently realize
- `pending_confirm_items`
  - items implementation may note but not treat as confirmed facts
- `implementation_prohibitions`
  - explicit “must not do” constraints
- `implementation_required_areas`
  - object areas implementation must preserve because architecture froze them

Example prohibitions:

- do not add new external APIs not frozen by architecture
- do not bypass frozen callout dependency with direct MCAL calls
- do not turn reserved runtime capability into formal implementation behavior

## 12. Validation Targets For V1

Before rendering, validate at least:

- required top-level fields exist
- every `freeze_matrix` row has action, status, and reason
- every `coverage_result` row has status and reason
- all `formal` external/dependency/config/runtime/memmap/file items have evidence
- `reserved` or `pending_confirm` items do not leak into released architecture as formal facts
- `implementation_constraints` are present
- `rule_evidence` exists for non-trivial file/callout/MemMap decisions
- `grounding_evidence` exists when multi-core, Reg.h, or source/config split decisions are asserted

## 13. Minimal V1 Scope

V1 does not need to solve every architecture concern.
It must at least stabilize these areas:

- external interface freeze
- dependency interface freeze
- config classification
- runtime-state freezing
- MemMap freezing
- file-family freezing
- risk/pending-confirm isolation
- implementation boundary export

## 14. Migration Guidance

Use the following migration path:

1. keep `semantic-model.md` as the existing object baseline
2. add freeze-layer objects from this contract
3. build `requirement-derived input / architecture seed -> freeze bundle` helper
4. validate the freeze bundle before rendering markdown
5. export `implementation_constraints` for implementation-stage use

This keeps the current architecture skill usable while upgrading it into a real freeze layer.
