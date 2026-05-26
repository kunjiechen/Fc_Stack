# Requirement Bundle Contract

## 1. Purpose

This file defines the stable structure of a `requirement_bundle` — the formal source-of-truth for a single FC module's requirement layer.

The bundle is not a rendering artifact. It is the structured intermediary that:

- captures every formal requirement with source, status, and verification evidence
- records every gating decision (what entered the formal pool, what was excluded, and why)
- exports architecture seeds and test seeds for downstream consumption
- supports byte-exact regression comparison and automated validation

## 2. Bundle Top-Level Structure

A requirement bundle is a single YAML or JSON document with 10 top-level sections:

```yaml
module_identity:    # who this bundle describes
source_inventory:   # what sources were used
grounding_summary:  # what reference patterns were adopted or rejected
requirements:       # the formal requirement pool
raw_gate_summary:   # gate disposition of every raw input item
coverage_matrix:    # raw-item → formal-requirement coverage
open_issues:        # unresolved items consolidated from all sources
architecture_seed:  # downstream architecture-consumable objects
test_seed:          # downstream test-consumable objects
generation_notes:   # metadata about this bundle's generation run
```

All 10 sections are mandatory. Sections may be empty (`[]`, `{}`, or zero counts) but must be present.

## 3. `module_identity`

| Field | Type | Description |
|---|---|---|
| `module_name` | string | Human-readable module name, e.g. `Gp_NCA95yy` |
| `module_abbr` | string | Normalized uppercase abbreviation, e.g. `GPNCA95YY` |
| `layer` | string | AUTOSAR layer: `IoExtDev`, `IoMcu`, `Cdd`, or `Srv` |
| `project` | string | Project identifier, e.g. `FcStack` |
| `safety_level` | string | ASIL level: `QM`, `ASIL-A`, `ASIL-B`, `ASIL-C`, or `ASIL-D` |
| `input_document` | string | Path to the primary datasheet or grounding markdown input |
| `source_root` | string | Absolute path to the project source root used as implemented evidence, or empty string |

## 4. `source_inventory`

A list of `SourceInventoryEntry` objects describing every source consumed during bundle generation:

| Field | Type | Description |
|---|---|---|
| `source_type` | string | One of: `markdown`, `raw_requirement_input`, `codebase` |
| `source_name` | string | File path or identifier for this source |
| `role` | string | One of: `datasheet_or_reference_input`, `project_requirement_input`, `implemented_evidence` |
| `confidence` | string | `high`, `medium`, or `low` |
| `notes` | string | Free-text description of how this source was used |

At minimum, the `markdown`-type primary input must be present. The `codebase` entry is present only when a source root was provided.

## 5. `grounding_summary`

| Field | Type | Description |
|---|---|---|
| `grounding_mode` | string | Currently `codebase_and_current_artifacts` |
| `reference_modules` | list[string] | Nearby FC module names discovered in the source root (up to 6) |
| `adopted_patterns` | list[string] | Pattern labels adopted for this module |
| `rejected_patterns` | list[string] | Pattern labels explicitly rejected (with reason in `notes` when populated) |
| `notes` | string | Generation-time caveats about grounding quality |

## 6. `requirements`

A list of requirement items. Each item has the following fields:

### 6.1 Identity & Classification

| Field | Type | Description |
|---|---|---|
| `requirement_id` | string | Engineering ID, e.g. `SRS-GPNCA95YY-FUNC-0001` |
| `semantic_id` | string | Internal pipeline ID, e.g. `REQ-GPNCA95YY-FUNCTIONAL-0001` |
| `type` | string | Requirement category: `functional`, `interface`, `configuration`, `diagnostic`, `timing`, `state` |
| `bundle_type` | string | Extended type: one of the `type` values, plus `safety`, `coding`, `resource` |
| `title` | string | Short human-readable title in Chinese or English |
| `function_name` | string | Resolved C function name for interface requirements, empty string otherwise |

### 6.2 Behavior Specifications

| Field | Type | Description |
|---|---|---|
| `shall` | string | The normative "software shall" statement |
| `pre_condition` | string | Preconditions that must hold before the behavior is valid |
| `trigger` | string | Event or condition that triggers the behavior |
| `input` | string | Expected inputs |
| `output` | string | Expected outputs or observable results |
| `exception` | string | Error and exception behavior |
| `constraint` | string | Governing constraints, dependencies, or caveats |

### 6.3 Verification & Evidence

| Field | Type | Description |
|---|---|---|
| `verification` | string | Verification method description |
| `source` | list[SourceRef] | Upstream source references (document, chunk_id, heading_path, content_type, evidence) |

### 6.4 Status & Decision

| Field | Type | Description |
|---|---|---|
| `status` | string | One of: `ready`, `draft`, `open_issue` |
| `decision` | string | `accepted_for_downstream`, `needs_refinement`, `needs_confirmation`, `hold_for_resolution` |
| `decision_reason` | string | Human-readable explanation of the decision |

### 6.4.1 Status Semantics

- **`ready`**: The requirement meets the Ready Gate defined in `requirement_quality_contract.md`. It is sufficiently complete for downstream architecture, detailed design, and test planning.
- **`draft`**: The requirement exists but is not yet downstream-ready. Either execution details (trigger, input, output, exception) are insufficient, validation findings exist, or the source is missing.
- **`open_issue`**: A validation error blocks this requirement. It must be resolved before it can be promoted to `draft` or `ready`.

### 6.5 Traceability

| Field | Type | Description |
|---|---|---|
| `trace.source_ids` | list[string] | Source chunk IDs this requirement traces to |
| `trace.tests` | list[string] | Test IDs linked to this requirement |
| `trace.verification_levels` | list[string] | Verification levels, e.g. `Review`, `Analysis`, `Test` |
| `trace.coverage_status` | string | `covered`, `partial_covered`, or `uncovered` |
| `trace.linked_raw_items` | list[object] | Raw input items linked to this requirement |

### 6.6 Validation Context

| Field | Type | Description |
|---|---|---|
| `validation` | list[ValidationFinding] | Validation findings specific to this requirement |
| `global_validation_context` | list[ValidationFinding] | Global findings applicable to the entire module |

## 7. `raw_gate_summary`

Records the disposition of every raw input item after passing through the formal requirement gate.

| Field | Type | Description |
|---|---|---|
| `counts` | object | Count of items per disposition: `formal_requirement`, `constraint`, `capability`, `evidence`, `metadata`, `architecture_seed_only`, `test_seed_only`, `open_issue` |
| `formal_requirement_items` | list[GateItem] | Items admitted to the formal requirement pool |
| `constraint_items` | list[GateItem] | Items kept as nonfunctional constraints |
| `capability_items` | list[GateItem] | Items kept as chip/project capability notes |
| `evidence_items` | list[GateItem] | Items kept as evidence obligations |
| `metadata_items` | list[GateItem] | Items filtered as document metadata |
| `architecture_seed_items` | list[GateItem] | Items routed only to architecture seed |
| `test_seed_items` | list[GateItem] | Items routed only to test seed |
| `open_issue_items` | list[GateItem] | Items pending project confirmation |

### 7.1 GateItem Structure

| Field | Type | Description |
|---|---|---|
| `raw_id` | string | Original raw item ID, e.g. `RAW-GPNCA95YY-FUNC-0002` |
| `category` | string | `FUNC`, `INTF`, `CFG`, or `NFR` |
| `title` | string | Derived title from raw input |
| `description` | string | Normalized description |
| `gate_reason` | string | Why this disposition was assigned |
| `source_detail` | string | Original source reference |
| `linked_formal_requirements` | list[string] | Formal requirement IDs linked to this raw item |
| `promotion_candidate` | bool | Whether this item is a candidate for promotion (capability items only) |
| `promotion_reason` | string | Explanation of promotion status |

## 8. `coverage_matrix`

A flat list mapping each raw input item to its coverage status.

| Field | Type | Description |
|---|---|---|
| `raw_id` | string | Raw item ID |
| `category` | string | `FUNC`, `INTF`, `CFG`, or `NFR` |
| `title` | string | Raw item title |
| `source` | string | Source reference |
| `status` | string | `covered`, `uncovered`, or `excluded_by_gate` |
| `matched_requirements` | list[string] | Formal requirement IDs that cover this raw item |

Items with `status: excluded_by_gate` are intentionally outside the formal pool and must not be reported as coverage gaps.

## 9. `open_issues`

A consolidated list of all open issues from three sources: requirement status, global validation findings, coverage gaps, and raw-gate open items.

| Field | Type | Description |
|---|---|---|
| `type` | string | Source of the issue: `requirement_status`, `global_validation`, `coverage_gap`, `raw_open_issue` |
| `requirement_id` | string | Affected requirement ID (for `requirement_status` type) |
| `title` | string | Short description |
| `status` | string | Current status (for `requirement_status` type) |
| `reason` | string | Why this is open |
| `severity` | string | `error`, `warning`, or `info` (for `global_validation` type) |
| `rule` | string | Validation rule that triggered this (for `global_validation` type) |
| `recommendation` | string | Suggested resolution |
| `raw_id` | string | Raw item ID (for `raw_open_issue` type) |
| `matched_requirements` | list[string] | Linked formal requirements (for `coverage_gap` type) |

## 10. `architecture_seed`

Structured objects intended for consumption by `fc-architecture-workbench`. This is not a formal architecture document.

| Field | Type | Description |
|---|---|---|
| `module_name` | string | Module name |
| `layer` | string | AUTOSAR layer |
| `external_interface_candidates` | list[InterfaceCandidate] | Deduplicated interface candidates with function names |
| `config_item_candidates` | list[ConfigCandidate] | Configuration items requiring architecture freeze |
| `timing_constraints` | list[TimingConstraint] | Timing constraints extracted from requirements |
| `state_concerns` | list[StateConcern] | State machine concerns |
| `diagnostic_concerns` | list[DiagnosticConcern] | Fault and diagnostic responsibilities |
| `pending_confirm_items` | list[PendingItem] | Requirements needing architecture-level confirmation |
| `constraint_items` | list[GateItem] | Nonfunctional constraints from raw gate |
| `architecture_only_items` | list[GateItem] | Items gated as `architecture_seed_only` |
| `capability_notes` | list[GateItem] | Capability notes for architecture awareness |

### 10.1 InterfaceCandidate

| Field | Type | Description |
|---|---|---|
| `requirement_id` | string | Source requirement ID |
| `function_name` | string | Resolved C function name |
| `purpose` | string | One-line description of what the interface does |
| `status` | string | `ready`, `draft`, or `open_issue` |

## 11. `test_seed`

Structured objects intended for test case generation. This is not a formal test plan.

| Field | Type | Description |
|---|---|---|
| `module_name` | string | Module name |
| `verification_items` | list[VerificationItem] | Per-requirement verification details |
| `test_only_items` | list[GateItem] | Items gated as `test_seed_only` |
| `excluded_nonfunctional_items` | list[GateItem] | Nonfunctional constraints excluded from test seed |

### 11.1 VerificationItem

| Field | Type | Description |
|---|---|---|
| `requirement_id` | string | Source requirement ID |
| `title` | string | Requirement title |
| `verification` | string | Verification method and scope |
| `trigger` | string | Trigger condition |
| `input` | string | Test inputs |
| `expected_output` | string | Expected observable results |
| `exception_path` | string | Error and exception paths to cover |
| `acceptance_basis` | string | Acceptance criteria (derived from constraint or shall) |
| `status` | string | `ready`, `draft`, or `open_issue` |

## 12. `generation_notes`

| Field | Type | Description |
|---|---|---|
| `source_root_used` | bool | Whether a codebase source root was provided |
| `raw_requirement_input_used` | bool | Whether raw requirement input was provided |
| `coverage_gap_count` | int | Number of raw items not covered (excluding `excluded_by_gate`) |
| `raw_gate_counts` | object | Copy of `raw_gate_summary.counts` for quick inspection |
| `notes` | list[string] | Generation-time caveats |

## 13. Downstream Consumption Contracts

### 13.1 Architecture Skill (`fc-architecture-workbench`)

The architecture skill consumes `architecture_seed` as its primary input from the requirement layer. It must:

- read `external_interface_candidates` to freeze interface signatures
- read `config_item_candidates` to define configuration containers
- read `timing_constraints` to validate scheduling feasibility
- read `state_concerns` and `diagnostic_concerns` to allocate runtime state and fault handling
- read `pending_confirm_items` to identify items needing architecture-level resolution
- read `constraint_items` to enforce ASIL, resource, and coding constraints
- read `capability_notes` to avoid re-deriving capability-vs-requirement decisions

The architecture skill must not re-derive requirement decisions. It consumes the seed as evidence of what the requirement layer has already resolved.

### 13.2 Test Generation

Test generation consumes `test_seed`. Each `VerificationItem` provides the minimum information needed to draft a test case: trigger, input, expected output, exception path, and acceptance basis. Items with `status: draft` or `status: open_issue` require resolution before test case finalization.

### 13.3 Bundle Validation

The `bundle_validation.json` output (generated by `bundle_validation.py`) is the formal gate report for the bundle. Its `summary.is_passed` field is the single boolean signal for CI/pre-push hooks.

## 14. Stability Guarantees

- The 10 top-level section names are stable. Renaming them is a breaking change.
- Fields marked as mandatory in this contract are guaranteed to be present. Optional fields may be empty strings or empty lists.
- The `requirement_id` format (`SRS-{MODULE}-{TYPE}-{NNNN}`) is stable.
- Gate disposition values (`formal_requirement`, `constraint`, `capability`, `evidence`, `metadata`, `architecture_seed_only`, `test_seed_only`, `open_issue`) are stable.
- Requirement status values (`ready`, `draft`, `open_issue`) are stable.
- New fields may be added at any level without breaking existing consumers.
