# Three Skill Evolution Recommendations

## 1. Purpose

This note summarizes the direction validated by the detailed-design skill optimization and explains how the same strategy should be propagated into future requirement-generation and architecture-generation skills.

The goal is to avoid three separate document generators drifting apart and instead converge on one shared FC design-generation method.

## 2. Core Conclusion

The recent detailed-design skill optimization shows that stable FC document generation does not come from larger prompts alone.

The validated direction is:

```text
real engineering grounding
-> structured intermediate model
-> trace / decision / pattern convergence
-> automated validation
-> markdown rendering
```

This replaces the older style:

```text
natural-language input
-> direct markdown generation
```

## 3. What The Detailed-Design Skill Actually Improved

The detailed-design skill now proves the value of these changes:

1. grounding is taken from real project FC baselines instead of generic style inference only
2. design inputs are normalized into schema-driven bundle objects
3. `trace_ids`, `decision`, `decision_reason`, `pending_confirm`, `reserved`, and `grounding_patterns` are explicit objects instead of hidden prose
4. validation exists at both bundle level and markdown level
5. markdown is treated as a rendered view, not the only source of truth

These are not detailed-design-only tricks. They are the common generation method that should also be adopted by requirement and architecture skills.

## 4. Shared Direction For All Three Skills

All three FC skills should converge on the following five principles.

### 4.1 Grounding First

Before generation, select and record the real engineering reference set that will shape the output.

Grounding should answer:

- which module family is closest
- which interface style is expected
- whether multi-core or `CalloutGetCoreId` is justified
- which `Conf_*` evidence matters
- which patterns should be adopted or rejected

### 4.2 Structured Model First

Do not generate final markdown directly from raw prose.

Each skill should first produce a structured object model.

Examples:

- requirement bundle
- architecture bundle
- detailed-design bundle

### 4.3 Traceable Decisions

Every downgrade, freeze, reservation, or pending-confirm state must be recorded explicitly.

At minimum:

- `status`
- `decision`
- `decision_reason`
- `impacts`
- `trace_ids`

### 4.4 Validation Gated

Each layer must have automated validation before final publishing.

Validation should check:

- structure correctness
- trace completeness
- upstream/downstream consistency
- grounding legality
- document drift

### 4.5 Document As Rendered View

Markdown should be treated as the final presentation layer only.

The stable source of truth should be:

- grounding assets
- schema contracts
- structured bundle objects
- validator rules

## 5. Recommendations For Requirement Generation

Future `fc-requirement-design` should focus on turning raw input into a stable requirement object layer.

### 5.1 Main Responsibilities

- understand raw input, chip constraints, and project notes
- extract requirement objects with stable IDs
- assign category, source, evidence, and status
- identify `pending_confirm`, `derived`, and `confirmed` items
- record requirement-level decisions when scope boundaries are unclear
- produce a requirement bundle before writing SRS markdown

### 5.2 Key Upgrades To Add

- raw input to requirement bundle conversion
- requirement source and evidence recording
- appendix-to-body consistency checks
- duplicate/conflict detection across requirements
- explicit handling of scope boundaries and project-confirm items

### 5.3 Requirement Skill Success Criteria

The requirement skill should not be judged only by whether the SRS reads well.

It should be judged by whether:

- requirements are complete
- IDs are stable
- categories are correct
- source/evidence are visible
- open issues are explicit

## 6. Recommendations For Architecture Generation

Future `fc-architecture-design` should focus on boundary freezing between requirements and detailed design.

### 6.1 Main Responsibilities

- consume requirement bundle
- freeze external interfaces
- freeze dependency interfaces
- classify config items as `formal`, `reserved`, `conditional`, or `pending_confirm`
- define runtime, MemMap, file family, and risk boundaries
- produce an architecture bundle before writing architecture markdown

### 6.2 Key Upgrades To Add

- requirement to architecture trace
- explicit interface freeze logic
- config-item status tracking
- architecture-level grounding summary
- architecture to detailed-design constraint export
- architecture consistency validation

### 6.3 Architecture Skill Success Criteria

The architecture skill should be judged by whether it freezes the right design boundary.

It succeeds when:

- external interfaces are stable
- dependency interfaces are stable
- reserved items are explicit
- pending confirms are isolated
- detailed design cannot silently drift beyond architecture

## 7. Recommendations For Detailed Design

Detailed design is currently the most advanced of the three, but it still needs to move from "data-ready" to "narrative-stable".

### 7.1 Already Established

- grounding baseline
- schema and bundle layer
- trace convergence
- decision convergence
- grounding pattern inference
- bundle and markdown validation

### 7.2 Next Focus

- detailed-design quality contract
- bundle-to-chapter mapping rules
- chapter-level writing policy
- validator-to-repair guidance
- regression and golden artifact coverage

### 7.3 Detailed Design Success Criteria

It should not only be consistent.

It should also:

- read like an implementation-ready design
- use the right chapter depth
- avoid over-design and under-design
- explain internal decomposition clearly
- keep risks and assumptions in the correct sections

## 8. Recommended Unified Pipeline

The long-term pipeline should be unified as:

```text
raw input
-> requirement bundle
-> architecture bundle
-> detailed-design bundle
-> markdown rendering
-> validation and refinement
```

This is the preferred future shape for the three skill family.

## 9. Near-Term Execution Advice

Do not try to fully rebuild all three skills in parallel immediately.

Recommended order:

1. finish the detailed-design method and stabilize its narrative generation policy
2. port the same grounding and structured-model method into requirement generation
3. port freeze logic and bundle validation into architecture generation
4. connect the three bundles into one continuous chain

This reduces drift and prevents three inconsistent local frameworks from emerging.

## 10. Summary

The most important outcome from the detailed-design optimization is a generation method, not just a set of scripts.

That method is:

- grounding first
- structure first
- traceable decisions
- validation gated
- markdown last

This should become the common evolution direction for:

- `fc-requirement-design`
- `fc-architecture-design`
- `fc-detailed-design`
