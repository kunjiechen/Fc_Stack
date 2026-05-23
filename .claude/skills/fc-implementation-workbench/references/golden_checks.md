# Golden Checks

## P0 Checks

- Grounding index covers the frozen FC baseline.
- IoExtDev primary modules have code-path and conf-path evidence.
- Structured schemas exist for requirements, architecture, and detailed design.
- Markdown validator checks architecture/DD interface consistency.

## P1 Checks

- A generation bundle example exists for a real target module.
- The validator catches forbidden conditional interfaces in architecture or DD interface sections.
- The validator checks that `关联接口` references do not point to undefined local design objects.

## P2 Checks

- Requirement, architecture, and detailed design cross-layer conflicts are checked.
- Regression cases produce stable markdown diff results.
