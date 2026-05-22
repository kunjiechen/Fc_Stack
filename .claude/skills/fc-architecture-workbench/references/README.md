# References Index

## Purpose

This folder contains the retained reference materials used by the local FC architecture skill.

To reduce clutter, use the files by priority instead of reading everything.

Responsibility boundary:

- `rules/*.md` owns stable architecture rules and judgment criteria.
- `templates/*.md` owns output shape and document layout.
- this `README.md` owns only the index and the minimal retained loading guidance.
- execution logic stays in `../SKILL.md`, not here.

## A. Core Rules

These are the primary files for routine FC architecture design:

- `rules/fc-architecture-rules.md`
  - FC file structure, layering, interface placement, MemMap strategy
- `rules/release-workflow.md`
  - architecture versioning, draft/release workflow, risk review, release gate
- `rules/naming-rules.md`
  - identifier naming, type suffixes, variable naming, function naming
- `rules/static-vs-dynamic.md`
  - how to classify config, calibration, runtime state, and dependencies
- `rules/interface-selection.md`
  - when to use standard binding, macro replacement, callout, or fixed integration code
- `templates/output-template.md`
  - full architecture document shape
- `templates/output-template-summary.md`
  - concise validated architecture document shape

## B. Project Style

This file captures the local architecture and interface habits learned from the historical project materials:

- `rules/project-style-rules.md`
  - external interface naming and API style
  - header carrier responsibilities
  - local configuration granularity habits
  - local multi-core and callout style

## C. Working Aids

Use these only when doing deeper extraction or detailed design review:

- `templates/extraction-debug-template.md`
  - structured extraction table for requirement analysis
- `semantic-model.md`
  - structured intermediate object model for external APIs, dependency APIs, config macros, runtime states, MemMap sections, file items, and risk items
- `../scripts/check_architecture_markdown.py`
  - lightweight guard for version/status metadata, risk table shape, release gate, and key file-carrier omissions
- `../scripts/validate_architecture_objects.py`
  - validates JSON architecture objects before rendering them into Markdown
- `../scripts/extract_architecture_objects.py`
  - extracts current architecture markdown back into semantic objects JSON for validation or regeneration

These working aids are not stable rule sources and should not be treated as architecture policy documents.

## D. Source Provenance

The original source PDFs have already been condensed into the Markdown rule files:

- `../archive/G-C046 软件接口命名规范.pdf`
- `../archive/G-C119 FC开发指南（C语言）.pdf`

For routine architecture work, the Markdown condensations are sufficient.

Recommendation:

- keep the PDFs only as provenance or audit backup
- they are not required for daily architecture design
- if you want a cleaner working set, they can be archived outside this folder after confirming the condensed Markdown rules are accepted as the retained source

## Minimal Loading Contract

For routine generation or review, load in this order:

1. user requirement / architecture draft / target output file
2. `../SKILL.md`
3. one output template
4. only the specific rule files needed by the question

Do not load all rules, templates, demos, and learning notes by default.

## Minimal Retained Set

If you want the smallest still-usable retained knowledge set, keep at least:

- `../docs/learning/AURIX2G_域控工程软件架构学习记录.md`
- `../docs/guides/AURIX2G_架构设计细节学习与后续设计指导.md`
- `rules/fc-architecture-rules.md`
- `rules/naming-rules.md`
- `rules/static-vs-dynamic.md`
- `rules/interface-selection.md`
- `rules/project-style-rules.md`
- `templates/output-template.md`
