# References Index

## Purpose

This folder contains the retained implementation-design references for the local FC implementation skill.

Responsibility boundary:

- `rules/*.md`
  - stable implementation rules and judgment criteria
- `templates/*.md`
  - output shape and document layout
- `semantic-model.md`
  - implementation object model for repeatable generation
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

## B. Working Aids

Use these only when the task needs structured generation consistency:

- `semantic-model.md`
  - normalized implementation object model

## C. Provenance

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

Do not load every rule and template by default.
