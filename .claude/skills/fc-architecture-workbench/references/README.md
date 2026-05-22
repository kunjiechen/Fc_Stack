# References Index

## Purpose

This folder contains the retained reference materials used by the local FC architecture skill.

To reduce clutter, use the files by priority instead of reading everything.

## A. Core Rules

These are the primary files for routine FC architecture design:

- `rules/fc-architecture-rules.md`
  - FC file structure, layering, interface placement, MemMap strategy
- `rules/naming-rules.md`
  - identifier naming, type suffixes, variable naming, function naming
- `rules/static-vs-dynamic.md`
  - how to classify config, calibration, runtime state, and dependencies
- `rules/interface-selection.md`
  - when to use standard binding, macro replacement, callout, or fixed integration code
- `templates/output-template.md`
  - default final architecture document shape

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

## D. Source Provenance

The original source PDFs have already been condensed into the Markdown rule files:

- `../archive/G-C046 软件接口命名规范.pdf`
- `../archive/G-C119 FC开发指南（C语言）.pdf`

For routine architecture work, the Markdown condensations are sufficient.

Recommendation:

- keep the PDFs only as provenance or audit backup
- they are not required for daily architecture design
- if you want a cleaner working set, they can be archived outside this folder after confirming the condensed Markdown rules are accepted as the retained source

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
