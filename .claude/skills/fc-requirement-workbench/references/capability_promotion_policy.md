# Capability Promotion Policy

## 1. Purpose

This file defines when a raw extracted capability may be promoted into the formal requirement pool.

Core principle:

```text
capability is not requirement by default
```

A capability may become a formal requirement only when enough software-facing evidence exists.

## 2. Promotion Preconditions

A capability is promotable only when at least one of the following is true:

1. the project raw input explicitly assigns software responsibility
2. an accepted architecture or detailed design artifact already consumes it as a frozen obligation
3. current codebase evidence shows the project has really implemented it and it is not marked as optional/project-specific only
4. the capability can be rewritten into a verifiable software action with clear trigger, input/output, and error path

If none of the above are true, keep the item as `capability`, `evidence`, or `open_issue`.

## 3. Promotion Gate Questions

Before promoting a capability, answer:

- who owns this behavior in software
- what exact software action is required
- what triggers it
- what output or observable result exists
- how it is verified
- whether project constraints limit or exclude it

If those answers cannot be stated clearly, the item must not become a formal requirement yet.

## 4. Typical Examples

### Keep as capability

- chip supports a diagnostic pin but project wiring/ownership is unclear
- chip supports runtime polarity inversion but project has not decided to expose runtime control
- chip supports multiple modes but project uses only one fixed mode

### Promote to formal requirement

- project raw input explicitly says software shall provide `GetGpInSig`
- current architecture freeze already requires `MainFunction` periodic interrupt polling
- accepted output already defines a stable software-owned error interface

## 5. Output Expectation

Every capability item should eventually carry:

- `promotion_candidate`: true/false
- `promotion_reason`
- `linked_formal_requirements`

This allows the requirement bundle to explain whether a capability was consumed, deferred, or excluded.
