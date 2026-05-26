# FC Architecture Semantic Model

Use this file when you want a structured intermediate representation before writing the final architecture Markdown.

Purpose:

- define the minimum object model for FC architecture generation and review
- separate architecture reasoning from final document wording
- support lightweight validation before rendering

This file does not define the final chapter layout. Final output shape still belongs to `references/templates/*.md`.

## 1. Document Envelope

The recommended top-level object is:

```json
{
  "module": "Gp_NCA95xx",
  "architecture_version": "V1",
  "architecture_status": "Draft",
  "output_mode": "Formal Draft",
  "layer": "IoExtDev",
  "change_summary": ["Initial architecture generation."],
  "external_apis": [],
  "dependency_apis": [],
  "binding_items": [],
  "config_macros": [],
  "strategy_items": [],
  "calibration_items": [],
  "runtime_states": [],
  "memmap_sections": [],
  "file_items": [],
  "risk_items": []
}
```

Required top-level fields:

- `module`
- `architecture_version`
- `architecture_status`
- `output_mode`

Recommended top-level fields:

- `layer`
- `change_summary`
- `assumptions`
- `pending_confirmations`
- `requirement_coverage`

## 2. Common Object Rules

All formal architecture objects should follow these common rules:

- have a stable `name` or `id`
- have `evidence`
- have `status`
- have clear ownership or implementation boundary
- avoid duplicating another stronger object

Allowed object `status` values:

- `Formal`
- `Conditional`
- `Pending Confirmation`
- `Not Recommended`

## 3. External API Object

Use for FC-visible external interfaces.

Required fields:

- `name`
- `prototype`
- `description`
- `sync_mode`
- `reentrancy`
- `return_value`
- `constraints`
- `evidence`
- `status`

Recommended fields:

- `category`
- `requirement_ids`
- `notes`

Example:

```json
{
  "name": "Gp_NCA95xx_GetFaultStatus",
  "prototype": "Std_ReturnType Gp_NCA95xx_GetFaultStatus(uint16 Id_u16, uint32* FaultStatus_pu32)",
  "description": "Returns the current fault and diagnostic status for one chip instance.",
  "sync_mode": "Synchronous",
  "reentrancy": "Reentrant",
  "return_value": "E_OK / E_NOT_OK",
  "constraints": [
    "Id_u16 must map to a configured instance.",
    "FaultStatus_pu32 must be non-null."
  ],
  "evidence": ["SRS-Gp_NCA95xx-INTF-0006"],
  "status": "Formal"
}
```

## 4. Dependency API Object

Use for Callout or platform adaptation interfaces.

Required fields:

- `name`
- `prototype`
- `description`
- `implemented_by`
- `evidence`
- `status`

Recommended fields:

- `sync_mode`
- `reentrancy`
- `return_value`
- `constraints`
- `call_scenario`

## 5. Config Macro Object

Use for compile-time configuration macros only.

Required fields:

- `name`
- `purpose`
- `macro_type`
- `default_value`
- `usage_location`
- `evidence`
- `status`

Rules:

- `name` must be ALL_CAPS with `_`
- do not use this object for runtime data, mapping tables, or calibration values

Allowed `macro_type` values:

- `Feature Enable`
- `Development Error Detect`
- `Behavior Selection`
- `Strategy Selection`
- `Dependency Selection`
- `Signal Mapping`
- `Hardware Mapping`
- `Count Size`
- `Timing Threshold`
- `Vendor Version Release`

## 5A. Binding Item Object

Use when architecture needs to freeze not only a dependency API but also the binding boundary between FC logic and dependency provider.

Required fields:

- `name`
- `binding_type`
- `source_side`
- `target_side`
- `binding_mechanism`
- `description`
- `status`

Recommended fields:

- `evidence`
- `notes`

## 6. Calibration Item Object

Use only when the requirement explicitly justifies a calibration parameter.

Required fields:

- `name`
- `type`
- `initial_value`
- `description`
- `status`

Recommended fields:

- `range`
- `usage_location`
- `evidence`

## 6A. Strategy Item Object

Use when strategy semantics are important enough that a macro name alone is not a strong enough architecture carrier.

Required fields:

- `name`
- `strategy_type`
- `selection_scope`
- `backing_reference`
- `description`
- `status`

Recommended fields:

- `evidence`
- `notes`

## 7. Runtime State Object

Use for internal runtime state, caches, counters, or fault bookkeeping.

Required fields:

- `name`
- `owner`
- `read_write_side`
- `lifecycle`
- `memory_section`
- `concurrency_strategy`

Recommended fields:

- `evidence`
- `status`

## 8. MemMap Section Object

Use for CODE / RAM / CONST / CALIB section decisions.

Required fields:

- `name`
- `target_content`
- `start_macro`
- `stop_macro`
- `used_files`
- `notes`

Recommended fields:

- `status`
- `evidence`

## 9. File Item Object

Use for FC-created files and file carriers.

Required fields:

- `name`
- `required_level`
- `responsibility`
- `key_content`

Recommended fields:

- `dependencies`
- `notes`
- `status`

Allowed `required_level` values:

- `Required`
- `Conditional`
- `Optional`

## 10. Risk Item Object

Use for concise or formal review tables.

Required fields:

- `index`
- `title`
- `risk`
- `impact`
- `recommended_action`
- `status`

Recommended fields:

- `remark`
- `evidence`

Allowed `status` values in risk tables:

- `待评审`
- `已评审`
- `待修改`

Quick-draft rule:

- `Quick Draft` should normally keep `3..5` real risk items plus optional `R-OTHER`

## 11. Minimum Validation Targets

Before rendering final Markdown, validate at least:

- metadata exists
- external APIs and dependency APIs are not mixed
- config macros use macro-style identifiers
- runtime states have memory ownership
- MemMap sections have start/stop macro pairs
- file items cover mandatory carriers
- risk items use valid indexes and statuses

## 12. Relationship To Final Output

Recommended mapping:

- `external_apis` -> external interface chapter
- `dependency_apis` -> dependency/callout chapter
- `binding_items` -> dependency binding and adaptation boundary chapter
- `config_macros` -> configuration chapter
- `calibration_items` -> calibration chapter
- `runtime_states` -> runtime-state/global-state chapter
- `memmap_sections` -> MemMap chapter
- `file_items` -> file list and relationship chapter
- `risk_items` -> architecture risk and pending confirmation chapter
