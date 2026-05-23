# References Index

## Purpose

This folder contains the retained implementation-design references for the local FC implementation skill.

Responsibility boundary:

- `rules/*.md`
  - stable implementation rules and judgment criteria
- `grounding/`
  - curated real-project FC grounding baseline, module facts, and normalized patterns
- `schemas/`
  - structured input and intermediate model contracts for requirement, architecture, and detailed design
  - `field_dictionary.md` defines cross-layer field semantics
- `templates/*.md`
  - output shape and document layout
- `semantic-model.md`
  - implementation object model for repeatable generation
- `workflow.md`
  - generation pipeline and validator gate
- `validation_rules.md`
  - current validator contract
- `../scripts/build_generation_bundle.py`
  - helper that converts SRS, architecture, and DD markdown into a reusable YAML bundle skeleton
- `../scripts/validate_generation_bundle.py`
  - validates bundle structure, grounding references, and key cross-layer consistency
- this `README.md`
  - index and minimal loading guidance only
- execution logic stays in `../SKILL.md`

## A. Core Rules

Primary files for routine FC implementation work:

- `rules/implementation-rules.md`
  - overall implementation design rules, boundaries, and validation questions
- `rules/code-structure-rules.md`
  - file families, single-core or multi-core framework, cfg/callout/runtime structure
- `rules/state-and-fault-rules.md`
  - state machine, DET, runtime error, fault, reset, and no-clear rules
- `rules/flowchart-rules.md`
  - when to include flowcharts and what granularity they should use
- `rules/implementation-review-checklist.md`
  - practical checklist for reviewing implementation-level detailed design
- `templates/output-template.md`
  - full detailed design output shape
- `templates/output-template-summary.md`
  - concise coding-oriented output shape

## B. Grounding

Use these when the task is full detailed-design generation or when the style needs to be normalized against real company FCs:

- `grounding/index.yaml`
  - grounding entry index and module-to-pattern mapping
- `grounding/grounding_scope.md`
  - frozen grounding scope and source boundaries
- `grounding/modules/*`
  - per-module summaries and facts
- `grounding/patterns/*`
  - normalized patterns extracted from the reviewed FC set

## C. Working Aids

Use these only when the task needs structured generation consistency:

- `semantic-model.md`
  - normalized implementation object model
- `schemas/*.json`
  - structured contracts for requirement, architecture, and detailed design intermediate models
- `schemas/field_dictionary.md`
  - field-level semantics and authoring rules for cross-layer objects
- `examples/*.yaml`
  - example generation bundles and per-layer objects showing how grounded inputs map into the intermediate model
- `workflow.md`
  - recommended generation sequence
- `validation_rules.md`
  - current validator capability summary
- `golden_checks.md`
  - staged acceptance checklist for the evolving pipeline

## D. Provenance

The rules in this folder are condensed from the local engineering study and code-design study already performed in this workspace.

Those study files are now retained inside this skill:

- `learning/aurix2g-engineering-learning.md`
- `learning/aurix2g-code-design-rules.md`
- `learning/company-code-standards-learning.md`

Routine skill execution should prefer the retained rule files in this folder, not the larger study notes.

## Minimal Loading Contract

For routine implementation design:

1. user requirement / architecture / target FC draft
2. `../SKILL.md`
3. one output template
4. only the specific rule files needed by the question
5. load grounding only when style grounding or pipeline generation is needed

Do not load every rule and template by default.
