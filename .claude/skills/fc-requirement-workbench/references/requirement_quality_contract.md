# Requirement Quality Contract

## 1. Purpose

This file defines what counts as a good FC requirement package.

It is not only a writing guideline. It is the quality contract for:

- raw extraction gate
- formal requirement gate
- requirement bundle review
- SRS rendering acceptance
- downstream architecture/test consumption

## 2. Core Positioning

A good requirement package must be:

- source-grounded
- software-action-oriented
- validation-aware
- downstream-consumable
- explicit about uncertainty

A good requirement package is not:

- a direct datasheet translation
- a pile of capability notes
- a design document in disguise
- a polished markdown file with weak objects underneath

## 3. Overall Quality Criteria

At minimum, requirement quality should satisfy these points.

### 3.1 Traceable

Every formal requirement must be traceable to at least one upstream source or accepted engineering basis.

If a statement cannot explain where it came from, it is not strong enough for `Ready`.

### 3.2 Actionable

A formal requirement must describe software-owned behavior, not only chip capability or general intention.

Good examples:

- what the software shall do
- when it shall do it
- what output/result is observable
- what happens on error or invalid input

### 3.3 Gate-Correct

Not every extracted item should become a formal requirement.

The bundle must clearly distinguish:

- `formal_requirement`
- `constraint`
- `capability`
- `metadata`
- `evidence`
- `architecture_seed_only`
- `test_seed_only`
- `open_issue`

If this distinction is unclear, the package is not mature enough.

### 3.4 Ready Means Downstream-Usable

`Ready` is not a prose-quality label.

It means the item is sufficiently complete for downstream architecture, detailed design, and test planning.

### 3.5 Constraint-Aware

Safety level, coding standard, and resource budget statements should usually stay as constraints unless explicitly rewritten into software behavior obligations.

### 3.6 Capability-Aware

Chip/project capability notes must not silently become formal requirements.

They may be promoted only after explicit software-responsibility refinement.

### 3.7 Downstream-Consumable

The requirement bundle must support:

- architecture seed export
- test seed export
- coverage analysis
- open issue review

If the markdown reads well but seeds are weak or unstable, the package is still incomplete.

## 4. Formal Requirement Gate

Only items that already express software-owned obligation should enter the formal requirement pool automatically.

Formal requirements should not be:

- module metadata
- pure chip capability descriptions
- nonfunctional policy slogans without software action
- review/evaluation record reminders

## 5. Ready Gate

At minimum, a `Ready` formal requirement should satisfy:

1. source exists
2. software behavior is explicit
3. verification exists
4. execution detail exists
   - trigger, input/output, exception, constraint, or equivalent observable behavior
5. no unresolved gate leakage
   - not obviously still a capability note
   - not obviously still a pure nonfunctional policy line

If these are not met, the item should remain `Draft` or `Open Issue`.

## 6. Capability Promotion Boundary

A capability may be promoted only when:

- project/software ownership is clear
- the action can be rewritten as software behavior
- validation path is definable
- project exclusion is not blocking it

If not, it must remain capability/evidence/constraint/open_issue.

## 7. Bundle Acceptance Questions

Before accepting a requirement bundle, review these questions:

- Which items are formal requirements and why
- Which items were blocked by the raw/formal gate and why
- Which capability notes now look promotable
- Which constraints influence architecture
- Which requirements are still not strong enough for `Ready`

If these questions cannot be answered from the bundle itself, the package is not yet strong enough.
