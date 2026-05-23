# Validation Rules V1

## Scope

This validator version focuses on architecture-to-detailed-design consistency for markdown artifacts.

## Current Checks

1. SRS interface-section APIs must align with architecture external interfaces when SRS input is provided.
2. SRS interface-section APIs must align with detailed-design external interfaces when SRS input is provided.
3. External interfaces in detailed design must exactly cover architecture external interfaces.
4. Dependency interfaces in detailed design must exactly cover architecture dependency interfaces.
5. Detailed design external interface first-table headers must contain `关联接口`.
6. Detailed design dependency interface first-table headers must contain `关联接口`.
7. Architecture and detailed-design interface sections must not explicitly declare conditional external or dependency interfaces.
8. `关联接口` references in detailed design must not point to undefined local design objects.

## Intent

The goal is to stop obvious drift such as:

- missing formal dependency interfaces
- SRS / Architecture / DD external-interface drift
- interface count mismatches
- architecture/detail naming drift
- relationship-field omission
- explicit conditional-interface drift
- undefined relationship references

## Future Checks

- internal interface relationship resolution
- traceability against structured requirement model
- config item and risk synchronization
- fault-bit and DET-rule cross-layer consistency
