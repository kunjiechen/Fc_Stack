# Formal Requirement Gate

## 1. Purpose

This file defines the gate between raw extracted items and the formal requirement pool.

The key principle is:

```text
not every extracted item is a formal requirement
```

## 2. Disposition Meanings

### `formal_requirement`

Use when the item already expresses software behavior, interface, configuration, timing, or state obligations that can enter the formal requirement pool.

### `constraint`

Use when the item governs downstream design or verification but is not itself a direct software behavior requirement.

Examples:

- ASIL / QM statements
- MISRA / coding standard obligations
- ROM / RAM budget constraints

### `capability`

Use when the item mostly describes chip or project-supported capability, but has not yet been refined into implementation-ready software obligation wording.

### `metadata`

Use for module names, document labels, section titles, and other non-requirement framing content.

### `evidence`

Use when the item is mainly a review, record, or assessment obligation rather than direct software behavior.

### `architecture_seed_only`

Use when the item primarily constrains architectural freeze decisions such as multi-core ownership, memory partitioning, or deployment boundary.

### `test_seed_only`

Use when the item is mainly verification-oriented and should drive test design without being promoted to formal software requirement directly.

### `open_issue`

Use when the item still depends on project confirmation, ownership clarification, or missing engineering decisions.

## 3. Gate Rule

Only items with:

- `disposition = formal_requirement`

may enter the formal requirement pool automatically.

All other items must stay outside the formal pool until a later explicit decision moves them in.

## 4. Why This Gate Exists

Without this gate, the pipeline drifts toward:

```text
extract anything
-> classify roughly
-> convert everything into requirement objects
```

That causes:

- capabilities to be mistaken for requirements
- nonfunctional constraints to be treated like functional behavior
- metadata to leak into downstream seeds

## 5. Immediate Application

During the current phase, the gate should at least prevent these from entering the formal requirement pool by default:

- safety level statements
- coding-standard statements
- resource-budget statements
- module/document metadata

Later phases can expand this gate with richer semantic criteria.
