# Three Skill Upgrade Roadmap

## 1. Purpose

This roadmap turns the high-level evolution recommendations into an actionable upgrade sequence for:

- `fc-requirement-design`
- `fc-architecture-design`
- `fc-detailed-design`

The goal is to avoid parallel overreach and define a dependency-aware path from the current detailed-design-centered prototype to a consistent three-skill FC generation system.

## 2. Planning Principles

This roadmap follows four planning principles:

1. do not rebuild all three skills deeply at the same time
2. stabilize one layer before forcing downstream automation
3. prefer shared methods over skill-local shortcuts
4. promote only what can be validated

## 3. Current Baseline

### 3.1 Already Established In Detailed Design

The current detailed-design carrier under `.claude/skills/fc-implementation-workbench` already has:

- grounding baseline
- structured schemas
- bundle generation helper
- bundle validation
- markdown validation
- trace convergence
- decision convergence
- grounding pattern inference

### 3.2 Not Yet Established System-Wide

The following are still missing across the full three-skill chain:

- requirement bundle generation as a first-class upstream stage
- architecture bundle generation as a first-class middle stage
- shared cross-skill field dictionary governance
- stable chapter-generation policy for detailed-design narrative
- regression coverage across multiple FC families

## 4. Dependency Order

The recommended dependency order is:

```text
1. stabilize detailed-design narrative policy
2. build requirement bundle generation
3. build architecture bundle generation
4. connect requirement -> architecture -> detailed design
5. add regression and repair guidance
```

Reason:

- detailed design already has the strongest data foundation
- requirement and architecture should inherit the validated method, not invent a separate one
- architecture depends on requirement object stability
- detailed design depends on architecture freeze stability

## 5. Skill-By-Skill Upgrade Strategy

## 5.1 Detailed Design

### Objective

Move from "data-ready" to "narrative-stable".

### P0

- define detailed-design quality contract
- define bundle-to-chapter mapping
- define chapter-level writing policy
- define when to weaken or omit sections

### P1

- build first-pass markdown renderer from detailed-design bundle
- connect validator output to repair suggestions
- add chapter-level acceptance checks

### P2

- add regression cases and golden artifacts
- refine repair automation
- stabilize cross-module output consistency

### Deliverables

- `detailed_design_quality_contract.md`
- `bundle_to_dd_mapping.md`
- `chapter_generation_rules.md`
- first-pass detailed-design renderer
- detailed-design regression pack

### Success Criteria

- generated DD is implementation-oriented, not just information-complete
- chapter depth is controlled
- assumptions and risks land in correct sections
- internal decomposition is understandable
- style remains stable across multiple FCs

## 5.2 Requirement Design

### Objective

Turn raw input interpretation into a stable requirement object layer.

### P0

- define requirement bundle contract
- map raw input fields to requirement categories
- define requirement source and evidence policy
- define requirement `status` and `decision` usage rules

### P1

- build raw-input-to-requirement-bundle helper
- build requirement appendix/body consistency checks
- build duplicate/conflict detection

### P2

- add project confirmation and scope-boundary reasoning templates
- add requirement regression samples
- connect requirement bundle directly into architecture generation

### Deliverables

- requirement bundle generation helper
- requirement validation helper
- requirement source/evidence rules
- requirement examples and regression cases

### Success Criteria

- requirements are extracted with stable IDs
- category and status are correct
- source/evidence are visible
- pending-confirm items are isolated
- SRS markdown becomes a rendering of requirement objects

## 5.3 Architecture Design

### Objective

Freeze interfaces and design boundaries between requirements and detailed design.

### P0

- define architecture bundle contract
- define interface-freeze rules
- define config item status policy
- define architecture grounding summary policy

### P1

- build requirement-to-architecture bundle helper
- add external/dependency interface trace propagation
- add config formal/reserved/pending tracking
- add architecture consistency validation

### P2

- export downstream constraints for detailed design
- add architecture regression cases
- add drift detection between architecture bundle and rendered markdown

### Deliverables

- architecture bundle generator
- architecture validation helper
- interface-freeze rules
- architecture examples and regression cases

### Success Criteria

- external interfaces are stably frozen
- dependency interfaces are stably frozen
- reserved and pending items are explicit
- detailed design cannot silently exceed architecture

## 6. Shared Assets To Govern Centrally

The following should be treated as shared cross-skill assets, not owned by just one skill:

- grounding module index
- field dictionary
- status taxonomy
- decision taxonomy
- trace conventions
- validation severity policy

If these drift across skills, the pipeline will become inconsistent even if each skill looks locally correct.

## 7. Recommended Near-Term Sequencing

### Stage 1

Finish detailed-design narrative strategy.

Do now:

- quality contract
- chapter mapping
- chapter writing policy

Do not do yet:

- heavy requirement rewrite
- heavy architecture rewrite

### Stage 2

Introduce requirement bundle generation.

Do now:

- raw input extraction model
- requirement field governance
- requirement validation

Do not do yet:

- deep architecture rendering automation

### Stage 3

Introduce architecture bundle generation.

Do now:

- interface freeze logic
- config-item classification
- trace propagation

Do not do yet:

- full downstream repair automation

### Stage 4

Connect the three bundles.

Do now:

- requirement bundle feeds architecture bundle
- architecture bundle feeds detailed-design bundle
- cross-layer validators compare all three

### Stage 5

Expand regression and repair.

Do now:

- multi-module regression cases
- golden artifacts
- validator to repair guidance

## 8. What To Avoid

Avoid these common traps:

- using historical bad DDs as hidden gold standards
- pushing all intelligence into one giant prompt
- treating markdown as the only truth source
- building requirement, architecture, and DD skills with different status vocabularies
- adding repair automation before consistency rules are stable

## 9. Immediate Recommended Next Documents

The next highest-value documents to create are:

1. `detailed_design_quality_contract.md`
2. `bundle_to_dd_mapping.md`
3. `chapter_generation_rules.md`
4. requirement bundle contract note
5. architecture bundle contract note

The first three should come first because they unlock higher-quality detailed-design rendering and provide the clearest reusable method for the other two skills.

## 10. Summary

The three-skill system should not be expanded by equal parallel effort.

It should be expanded by:

1. stabilizing detailed-design narrative policy
2. turning requirement extraction into structured bundles
3. turning architecture freeze into structured bundles
4. connecting the three layers through traceable, validated handoff objects

This sequence minimizes rework and gives the later requirement and architecture skills a proven method to inherit instead of another generation style to debug.
