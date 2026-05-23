# Implementation Semantic Model

## Purpose

This file defines the normalized implementation-design objects that should exist before rendering markdown, reviewing a detailed design, or generating coding scaffolds.

This is not a strict machine schema. It is the stable human-readable contract for implementation modeling inside this skill.

## 1. Modeling Principles

- model confirmed facts separately from assumptions
- separate requirement-facing meaning from code-facing structure
- separate external APIs, dependency APIs, and internal helpers
- separate cfg state from runtime state
- treat multi-core ownership as explicit data
- treat state, DET, fault, and MemMap as first-class objects
- allow partial models when source input is incomplete, but mark missing fields clearly

## 2. Top-Level Model

A normal implementation-design package may contain:

- `module_identity`
- `source_inputs`
- `file_items`
- `external_apis`
- `dependency_apis`
- `internal_functions`
- `state_machines`
- `core_models`
- `task_models`
- `cfg_macros`
- `cfg_tables`
- `runtime_states`
- `det_objects`
- `fault_objects`
- `memmap_sections`
- `pending_items`

Recommended convention:

- singular object names represent one item shape
- plural object names represent arrays or collections in the aggregated model

## 3. Object Definitions

### 3.1 `module_identity`

Purpose:

- identifies what FC is being designed and where it belongs

Fields:

- `fc_name`
  - required
  - FC or driver namespace, preserved exactly in project style
- `layer_position`
  - required
  - e.g. `IoExtDev`, `IoHwAb`, `Cdd`, `Srv`
- `purpose`
  - required
  - short statement of the module responsibility
- `execution_model`
  - required
  - `init-only`, `event-driven`, `periodic`, `hybrid`
- `single_or_multi_core`
  - required
  - `single-core`, `multi-core`
- `instance_model`
  - optional
  - `single-instance`, `multi-instance`
- `platform_scope`
  - optional
  - platform or chip family limitation

### 3.2 `source_input`

Purpose:

- records what evidence the implementation design depends on

Fields:

- `source_type`
  - required
  - `requirement`, `architecture`, `chip-manual`, `project-rule`, `reference-fc`, `assumption`
- `source_name`
  - required
- `confidence`
  - required
  - `high`, `medium`, `low`
- `usage_scope`
  - required
  - where this source influences the design
- `notes`
  - optional

### 3.3 `file_item`

Purpose:

- defines one file that should exist in the detailed design or code scaffold

Fields:

- `file_name`
  - required
- `required`
  - required
  - `required`, `optional`, `conditional`
- `responsibility`
  - required
- `key_content`
  - required
- `trigger_condition`
  - optional
  - when the file becomes necessary
- `depends_on`
  - optional
  - file-level dependencies
- `memmap_managed`
  - optional
  - whether this file uses section boundaries

### 3.4 `external_api`

Purpose:

- describes one FC-provided interface visible outside the FC

Fields:

- `name`
  - required
- `prototype`
  - required
- `api_kind`
  - required
  - `init`, `mainfunction`, `service`, `getter`, `setter`, `query`, `control`, `diag`
- `sync_mode`
  - required
  - `synchronous`, `asynchronous`
- `reentrancy`
  - required
  - `reentrant`, `non-reentrant`
- `purpose`
  - required
- `inputs`
  - optional
  - input parameter summary
- `outputs`
  - optional
  - output parameter summary
- `return_value`
  - required
- `preconditions`
  - optional
- `postconditions`
  - optional
- `det_checks`
  - optional
  - linked DET items or brief summary
- `depends_on`
  - optional
  - dependency APIs or internal state assumptions

### 3.5 `dependency_api`

Purpose:

- describes one Callout or other dependency-side interface consumed by the FC

Fields:

- `name`
  - required
- `prototype`
  - required
- `implemented_by`
  - required
  - `MCAL`, `IoMcu`, `IoExtDev`, `Service Layer`, `Project Adaptation`
- `purpose`
  - required
- `sync_mode`
  - required
- `reentrancy`
  - required
- `constraints`
  - optional
- `status`
  - required
  - `formal`, `conditional`, `pending-confirmation`
- `binding_style`
  - optional
  - `callout`, `fixed-link`, `macro-bind`, `table-bind`

### 3.6 `internal_function`

Purpose:

- describes one function that supports implementation but is not a public FC API

Fields:

- `name`
  - required
- `category`
  - required
  - `param-check`, `init-check`, `cfg-access`, `runtime-access`, `state-check`, `state-action`, `data-convert`, `fault-detect`, `fault-response`, `record-helper`, `monitor-helper`
- `scope`
  - required
  - `static`, `internal-header`
- `responsibility`
  - required
- `trigger`
  - required
  - which external API, task, or state-machine flow uses it
- `reads`
  - optional
  - runtime or cfg objects read
- `writes`
  - optional
  - runtime or fault objects written

### 3.7 `state_machine`

Purpose:

- describes one explicit state machine in the implementation design

Fields:

- `name`
  - required
- `state_enum`
  - required
- `switch_enum`
  - optional
- `owner_function`
  - required
  - usually `MainFunction` or one task entry
- `condition_functions`
  - optional
- `action_functions`
  - optional
- `transition_rows`
  - required
  - rows of `current`, `condition`, `action`, `next`
- `record_strategy`
  - optional
  - timestamp, recorder, no-clear, none
- `fault_coupling`
  - optional
  - whether a fault can force transitions

### 3.8 `core_model`

Purpose:

- describes one core's ownership in a multi-core or per-core design

Fields:

- `core_id`
  - required
- `responsibility`
  - required
- `init_entry`
  - optional
- `task_entries`
  - optional
- `cfg_binding`
  - optional
- `runtime_binding`
  - optional
- `shared_objects`
  - optional
- `sync_points`
  - optional

### 3.9 `task_model`

Purpose:

- describes one execution slot or task-like periodic entry

Fields:

- `task_name`
  - required
- `core_id`
  - required if multi-core
- `period`
  - required
  - e.g. `1ms`, `5ms`, `10msA`, `100ms`
- `priority_class`
  - required
  - `high-prio`, `normal`, `background`, `event`
- `owned_actions`
  - required
- `monitor_actions`
  - optional
- `state_machine_owner`
  - optional
- `fault_checks`
  - optional

### 3.10 `cfg_macro`

Purpose:

- describes one compile-time or configuration-header macro

Fields:

- `name`
  - required
- `purpose`
  - required
- `macro_class`
  - required
  - `feature-enable`, `size-count`, `behavior-select`, `timeout`, `retry`, `version`, `platform-select`
- `default_value`
  - required
- `usage_location`
  - required
- `status`
  - required
  - `formal`, `conditional`, `pending-confirmation`, `not-recommended`

### 3.11 `cfg_table`

Purpose:

- describes one table or structured config object that belongs in `Cfg.c`

Fields:

- `name`
  - required
- `scope`
  - required
  - `global`, `per-core`, `per-instance`, `per-channel`
- `row_purpose`
  - required
- `key_fields`
  - required
- `owner`
  - required
  - which file or module side owns it
- `consumer`
  - optional
  - which logic reads it
- `chip_bound`
  - optional
  - whether entries depend on chip resources or registers

### 3.12 `runtime_state`

Purpose:

- describes one runtime object or one runtime object family

Fields:

- `name`
  - required
- `state_class`
  - required
  - `input`, `status`, `intermediate`, `output`, `monitor`, `fault`, `retained`
- `type`
  - required
- `owner`
  - required
- `reader_writer`
  - required
  - should name write side and read side
- `lifecycle`
  - required
  - `init-only`, `periodic`, `event-driven`, `cross-reset`
- `core_affinity`
  - required
  - `global`, `core0`, `core1`, `per-core`, etc.
- `mem_section`
  - required
- `retention`
  - required
  - `clear-on-reset`, `no-clear`, `nvm-backed`, `derived`
- `initial_value_strategy`
  - optional
- `concurrency_note`
  - optional

### 3.13 `det_object`

Purpose:

- describes one development error protection rule set

Fields:

- `mask_name`
  - required
- `trigger_condition`
  - required
- `record_strategy`
  - required
  - `bitmask`, `latest-only`, `buffered`
- `api_scope`
  - required
- `return_strategy`
  - optional
  - how the protected API exits

### 3.14 `fault_object`

Purpose:

- describes one runtime fault design item

Fields:

- `name`
  - required
- `source`
  - required
- `detect_condition`
  - required
- `confirm_rule`
  - optional
- `response_action`
  - required
- `recovery_rule`
  - optional
- `retention_strategy`
  - required
- `reset_relation`
  - optional
  - whether reset may be triggered or used for recovery
- `observable_interface`
  - optional
  - getter or diag exposure if any

### 3.15 `memmap_section`

Purpose:

- describes one memory placement strategy item

Fields:

- `section_kind`
  - required
  - `code`, `runtime`, `const`, `const-per-core`, `no-clear`, `nvm-mirror`, `nocache-shared`
- `start_macro`
  - required
- `stop_macro`
  - required
- `used_by`
  - required
- `note`
  - optional

### 3.16 `pending_item`

Purpose:

- captures a missing or unresolved design dependency

Fields:

- `topic`
  - required
- `reason`
  - required
- `impact`
  - required
- `required_input`
  - required
- `blocking_level`
  - optional
  - `low`, `medium`, `high`

## 4. Object Relationships

Use these relationships when building or reviewing the model:

- `module_identity` owns all other objects
- `file_item` should cover `external_api`, `dependency_api`, `cfg_table`, `runtime_state`, and `memmap_section`
- `external_api` may depend on `dependency_api`, `internal_function`, `det_object`, and `runtime_state`
- `state_machine` is usually owned by one `task_model` or one external periodic API
- `core_model` groups `task_model`, `cfg_table`, and `runtime_state` by core
- `fault_object` may influence `state_machine` and `runtime_state`
- `memmap_section` must explain where `cfg_table` and `runtime_state` live
- `pending_item` may be attached to any object family

## 5. Minimum Completeness Rules

### 5.1 Default Minimum

For a normal coding-oriented detailed design, at least these objects should exist:

- `module_identity`
- `file_items`
- `external_apis`
- `cfg_macros` or `cfg_tables`
- `runtime_states`
- `memmap_sections`

### 5.2 Conditional Minimum

Add these when applicable:

- `dependency_apis`
  - if platform, hardware, or external adaptation exists
- `internal_functions`
  - if logic is non-trivial
- `state_machines`
  - if execution contains explicit mode or phase transitions
- `core_models` and `task_models`
  - if multi-core or periodic ownership matters
- `det_objects`
  - if external APIs require defensive checks
- `fault_objects`
  - if runtime abnormal behavior must be handled

## 6. Design Output Mapping

Typical rendering mapping:

- `module_identity` -> FC summary section
- `file_items` -> file list section
- `external_apis` -> external API section
- `dependency_apis` -> callout/dependency section
- `internal_functions` -> internal function section
- `state_machines` -> state-machine section
- `core_models` and `task_models` -> single-core/multi-core framework section
- `cfg_macros` and `cfg_tables` -> config section
- `runtime_states` -> runtime-state section
- `det_objects` -> DET section
- `fault_objects` -> fault handling section
- `memmap_sections` -> MemMap section
- `pending_items` -> assumptions or risk section

## 7. Practical Usage Rule

Do not start writing the final markdown document until:

1. the top-level object set is known
2. mandatory fields for the active object families are filled
3. assumptions are separated from confirmed facts
4. missing items are captured in `pending_items`

If input is weak, keep the model partial but explicit rather than fabricating absent objects.
