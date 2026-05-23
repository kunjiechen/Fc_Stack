---
name: fc-implementation-workbench
description: Use when the user wants to design, review, refine, or draft FC implementation-level detailed design and coding scaffolds for embedded automotive software, including single-core or multi-core framework, cfg layout, DET flow, state machine, internal functions, runtime-state, fault handling, and Callout/MemMap strategy.
---

# FC Implementation Workbench

## 1. Purpose

This skill is the current implementation carrier for FC detailed-design generation and implementation-oriented review.

Its job is to bridge:

```text
Requirement / Architecture / Reference FC / Chip Constraint
  -> Grounding Selection
  -> Structured Design Objects
  -> Detailed Design Generation
  -> Validation
  -> Refinement
```

This skill supports:

- implementation-oriented detailed design generation
- FC coding scaffold design
- single-core and multi-core framework design
- cfg/cfgdata/callout layout design
- DET and runtime error flow design
- state machine design
- internal function extraction and layering
- interface subfunction decomposition and execution-step design
- runtime-state and NoClear design
- fault handling and reset-coupling design
- implementation review and refinement
- grounding-driven design normalization against real project FCs
- structured-input and validator-assisted detailed design stability

This skill does not replace:

- requirement generation
- system architecture generation
- final business algorithm invention without source basis
- chip-register truth verification when the chip manual is missing

## 2. Scope Boundary

This is an implementation-design skill, not a full source-code autopilot.

It should produce outputs at one of these levels:

1. implementation summary
2. formal detailed design markdown
3. coding scaffold plan
4. implementation review findings
5. code-generation-ready design objects

It may define:

- file lists
- API families
- per-core runtime containers
- cfg tables
- state enums and switch tables
- DET strategy
- fault-state objects
- internal function responsibilities
- MemMap sections

It must not invent as facts:

- chip timing values
- register addresses
- project-specific signal IDs
- exact fault thresholds
- exact NVM block bindings

When such facts are missing, mark them as assumptions or pending confirmation.

## 3. Source Priority

Priority order:

```text
User requirement
-> User architecture / design draft
-> Project local coding rules
-> This skill's retained implementation rules
-> Grounding baseline summaries from real project FCs
-> AI inference
```

If sources conflict:

- prefer the explicit current project input
- prefer architecture constraints over demo habits
- use retained rules as default style only
- use grounding as style evidence, not as architecture override
- do not silently overwrite user-specified naming or layering

## 4. Primary Sources

Use only the minimum source set needed.

Rule layer:

- `references/rules/implementation-rules.md`
- `references/rules/code-structure-rules.md`
- `references/rules/state-and-fault-rules.md`
- `references/rules/flowchart-rules.md`
- `references/rules/implementation-review-checklist.md`

Grounding layer:

- `references/grounding/index.yaml`
- `references/grounding/grounding_scope.md`
- selected files under `references/grounding/modules/`
- selected files under `references/grounding/patterns/`

Model layer:

- `references/semantic-model.md`
- `references/schemas/requirements.schema.json`
- `references/schemas/architecture.schema.json`
- `references/schemas/detailed_design.schema.json`
- `references/schemas/field_dictionary.md`

Workflow layer:

- `references/workflow.md`
- `references/validation_rules.md`

Templates:

- `references/templates/output-template.md`
- `references/templates/output-template-summary.md`

## 4.1 Source Loading Strategy

Default minimal loading:

1. read the user requirement, architecture draft, implementation draft, or target FC file
2. read this `SKILL.md`
3. read one output template
4. read `references/workflow.md` if the task is full generation or workflow refactor
5. load only the specific grounding, rule, and schema files needed for the current task

Load `references/grounding/index.yaml` and `grounding_scope.md` when:

- the task is a new FC detailed design
- the module family or layer is unclear
- you need to choose representative reference FCs

Load selected files under `references/grounding/modules/` when:

- you need evidence for interface shape
- you need evidence for `CalloutGetCoreId`, per-core runtime, cfg/runtime split, or MainFunction style
- you need IoExtDev normalization against real project FCs

Load selected files under `references/grounding/patterns/` when:

- you need normalized style rules distilled from the reference modules

Load `code-structure-rules.md` when the task concerns:

- file families
- single-core or multi-core framework
- cfg layout
- callout placement
- runtime container shape
- MemMap strategy

Load `state-and-fault-rules.md` when the task concerns:

- state machine
- DET
- runtime error
- fault handling
- reset/no-clear coupling

Load `flowchart-rules.md` when the task concerns:

- output-shape decisions for control flow
- interface execution sequence presentation
- state-machine visualization
- fault or initialization flow visualization

Load `implementation-rules.md` when the task is broad:

- new detailed design generation
- full implementation review
- implementation-level conflict resolution

Load `implementation-review-checklist.md` when the task concerns:

- formal implementation-design review
- coding-readiness review
- generated-design quality checks
- checklist-based acceptance or rejection

Load `semantic-model.md` and the schema files when:

- you need structured design objects
- you need generation consistency across modules
- you are converting raw input, SRS, architecture, and detailed design into a stable intermediate model

## 5. When To Use This Skill

Use this skill when the user asks for:

- FC detailed design
- implementation design
- coding-oriented design
- cfg design
- DET design
- state machine code design
- internal function decomposition
- runtime-state design
- fault handling design
- single-core or multi-core framework design
- implementation review or cleanup

Do not use this skill when the task is only:

- pure requirement extraction
- pure system architecture generation
- generic C tutoring without FC context

## 6. Inputs

Typical inputs:

- FC requirement document
- FC architecture document
- chip manual or register manual
- company coding rules
- interface naming rules
- fault/diagnostic strategy
- existing FC code or similar reference FC
- target output mode

Input sufficiency classification:

- `L1`
  - requirement + architecture
  - enough for a draft detailed design
- `L2`
  - requirement + architecture + company rules + reference FC
  - enough for a coding-oriented detailed design
- `L3`
  - requirement + architecture + company rules + chip manual + reference FC
  - enough for strong implementation design and scaffold guidance

If the input is below `L2`, explicitly preserve assumptions.

## 7. Core Implementation Object Model

Before writing markdown, first normalize the task into implementation objects.

Use this conceptual model:

- `module_identity`
- `layer_position`
- `file_items`
- `external_apis`
- `dependency_apis`
- `internal_functions`
- `state_machines`
- `core_model`
- `task_model`
- `cfg_macros`
- `cfg_tables`
- `runtime_states`
- `fault_objects`
- `det_objects`
- `memmap_sections`
- `pending_items`

Detailed fields live in `references/semantic-model.md`.

For interface-heavy outputs, do not stop at API purpose statements. The design should normally explain:

- what subfunctions each interface triggers
- in what execution order those subfunctions run
- which internal helpers participate
- where DET, state checks, cfg access, runtime writes, fault checks, and callouts occur
- a flowchart representation when the interface behavior is not trivial

## 8. Execution Flow

### 8.1 Input Understanding

Determine:

- FC name
- layer position
- single-core or multi-core
- synchronous or asynchronous behavior
- whether periodic `MainFunction` is needed
- whether external-device register access exists
- whether NoClear/reset continuity is needed
- whether state machine exists or should exist

### 8.2 Grounding Pass

Before finalizing a new detailed design, choose the minimum useful grounding set from:

- `Gp_TPT1145`
- `Gp_TLE92104`
- `Gp_DRV8889`
- `Gp_WkUpSrcP`
- `Gp_06_Adc3ph`
- `IoMcu`

Use the grounding pass to decide:

- external interface rhythm
- dependency interface shape
- whether `CalloutGetCoreId` is warranted
- whether per-core runtime containers are appropriate
- how heavy the internal fault and state design should be
- how cfg and `Conf_*` mapping should be described

Do not load every module summary by default. Choose the modules that match the target FC layer and behavior.

### 8.3 Structured Modeling

For full generation work, normalize the inputs into an intermediate model before markdown:

1. requirement facts
2. architecture-frozen external interfaces
3. architecture-frozen dependency interfaces
4. internal interfaces derived from repeated responsibilities
5. cfg/runtime/fault/state objects
6. relationship links
7. assumptions and pending confirmations

Use the schema files under `references/schemas/` as the structure contract.

### 8.4 Execution-Level Selection

Choose only the depth that the task needs.

`Quick Design`

- concise implementation plan
- key APIs, files, cfg, runtime, and pending issues

`Formal Detailed Design`

- complete markdown document
- file family, APIs, cfg, state machine, runtime, DET, fault, MemMap
- interface execution steps and subfunction decomposition
- flowchart sections for key external and internal flows
- grounding choices and architecture-consistency preservation

`Code Scaffold Mode`

- coding skeleton guidance
- file inventory
- per-file responsibility
- interface signatures
- runtime containers

`Review Mode`

- findings first
- focus on design defects, missing pieces, layering violations, testability risks

### 8.5 Validation Gate

For full detailed-design generation, run validation before finalizing:

- architecture and detailed design external-interface consistency
- architecture and detailed design dependency-interface consistency
- formal dependency-interface coverage
- required `关联接口` field presence
- obvious unresolved relationship reference drift

Use `scripts/validate_fc_docs.py` for the current markdown validator baseline.

### 8.6 Output-Mode Selection

Default:

- concise validated output -> `output-template-summary.md`

Use full template only when:

- the user explicitly wants a formal detailed design
- the module is safety-critical or structurally complex
- the task asks for code-generation-ready design detail

## 9. Implementation Design Rules

Compact execution summary:

- always separate configuration state from runtime state
- prefer `Cfg.h + CfgData.h + Cfg.c` for stable project-bound configuration
- prefer `Callout` for hardware, platform, or project adaptation variability
- treat DET as development-use protection, not as full fault handling
- treat state machine as explicit object: enums + condition checks + actions + switch table
- for multi-core, prefer explicit per-core containers and explicit sync points
- keep external APIs stable and keep internal helpers hidden by default
- runtime variables must have ownership, lifecycle, and read/write side defined
- `MemMap` and `NoClear` are implementation design objects, not afterthoughts

Long-form rules live in:

- `references/rules/implementation-rules.md`
- `references/rules/code-structure-rules.md`
- `references/rules/state-and-fault-rules.md`

## 10. Single-Core And Multi-Core Handling

When designing framework code:

- choose single-core only if there is one execution owner and no cross-core state
- choose multi-core when runtime state, tasks, monitoring, or initialization is split by core

For multi-core output, always state:

1. core ownership
2. per-core task entry
3. per-core cfg and runtime container strategy
4. shared-state list
5. synchronization points

## 11. Detailed Design Minimum Coverage

For a coding-oriented detailed design, the output should normally cover:

- FC summary
- file list
- external APIs
- dependency APIs / callouts
- cfg macros and cfg tables
- global/public type strategy
- internal function decomposition
- state machine
- runtime-state design
- DET flow
- fault handling
- MemMap strategy
- single-core or multi-core model
- pending confirmations

For each non-trivial external API, dependency API, and key internal control flow, the output should also cover:

- subfunction decomposition
- ordered execution steps
- participating internal functions
- fault/DET insertion points
- a flowchart section when sequence reasoning matters

If any of these is intentionally omitted, explain why.

## 12. Validation Focus

Validate the design against these questions:

1. Can coding start from this design without guessing file structure?
2. Can cfg, runtime, and callout boundaries be implemented without re-architecture?
3. Are state-machine transitions explicit enough for coding?
4. Are DET and fault handling separated?
5. Is multi-core ownership explicit where needed?
6. Are internal functions decomposed by responsibility rather than by accidental code order?
7. Are runtime variables owned, typed, and lifecycle-defined?
8. Are assumptions clearly isolated from confirmed facts?
9. Does the design stay aligned with architecture-frozen external and dependency interface sets?
10. Is the selected style grounded in real project FC evidence instead of pure chip-manual decomposition?

## 13. Review Mode Rules

If the user asks for review:

- findings first
- prioritize defects, omissions, incorrect layering, interface leakage, state/fault confusion, cfg/runtime mixing, or multi-core ambiguity
- include file or section references where possible
- summary only after findings

## 14. Output Discipline

Keep user-facing progress updates high-level.

Do not expose internal rule-file names unless the user asks.

In final outputs:

- list only user-facing business inputs as formal inputs
- do not present retained learning files as user inputs
- distinguish confirmed decisions from assumptions

## 15. Deliverable Strategy

This skill may produce one or more of:

- implementation summary
- detailed design markdown
- implementation object checklist
- coding scaffold plan
- review findings
- grounding summary
- validation result summary

If the user asks for actual source creation after the design, this skill should first ensure the design is sufficiently explicit, then derive code from the design rather than skipping straight to implementation.
