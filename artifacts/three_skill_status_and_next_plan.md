# Three Skill Status And Next Plan

## 1. Purpose

This note gives a strict status assessment for the current three FC skill lines under this repository.

Scoring principle:

- full score is `10`
- `can run` is not enough
- the score reflects method maturity, stability, validation depth, and upgrade readiness

Current repository reality:

- requirement side carrier: `.claude/skills/fc-requirement-workbench`
- architecture side carrier: `.claude/skills/fc-architecture-workbench`
- detailed-design side carrier: `.claude/skills/fc-implementation-workbench`

Long-term target naming may still evolve to:

- `fc-requirement-design`
- `fc-architecture-design`
- `fc-detailed-design`

But this assessment is based on what is actually implemented now.

## 2. Overall Conclusion

The three skill lines are not at the same maturity level.

- detailed design is clearly the leading line and has already moved from prompt-only generation to a grounded, bundle-based, and validated pipeline shape
- requirement generation has a strong conceptual architecture, but the structured bundle and validation chain are not yet landed in the same way
- architecture generation has useful rule content and output discipline, but it has not yet been upgraded into a bundle-first, validator-first middle layer

So current maturity is asymmetric:

- detailed design: ahead
- requirement: conceptually strong, implementation-medium
- architecture: useful but still in transition

## 3. Score Summary

### 3.1 Requirement Generation

Score: `5.5 / 10`

Reason:

- the requirement workbench already has a relatively strong process concept
- its scope boundary is clearer than before
- it already talks in terms of semantic objects, candidate mapping, pruning, planning, rule engine, and traceability
- but the bundle-first implementation method validated in detailed design has not yet been concretely ported and proven here
- there is no repository-proven requirement bundle helper, no requirement bundle validator, and no demonstrated end-to-end structured pipeline similar to the detailed-design line

Short judgment:

`conceptual framework is good, implementation convergence is not yet complete`

### 3.2 Architecture Generation

Score: `4.5 / 10`

Reason:

- the architecture workbench has useful rules, source-loading guidance, output discipline, and release/version corrections
- it has meaningful architecture thinking around interfaces, config, dependency, MemMap, and runtime-state
- but it is still largely rule-centric and document-centric
- it has not yet been upgraded to a requirement-bundle-consuming, architecture-bundle-producing middle layer
- there is no grounded architecture bundle generator, no architecture validation helper comparable to the detailed-design bundle validation, and no stable freeze-object handoff into detailed design

Short judgment:

`good architecture guidance exists, but the architecture pipeline is not yet structurally modernized`

### 3.3 Detailed Design

Score: `8.0 / 10`

Reason:

- this is the only line that has already concretely landed:
  - grounding baseline
  - schema family
  - field dictionary
  - bundle generation helper
  - bundle validation
  - markdown validation
  - trace convergence
  - decision convergence
  - grounding pattern inference
  - first-pass bundle-to-DD renderer
- it has already proven the core method:
  - grounding first
  - structured model first
  - validation gated
- it can now render a coding-capable DD first draft from a structured bundle
- it can expose real gaps instead of silently hiding them in prose
- what is still missing is mostly regression breadth and upstream porting, not basic operability

Short judgment:

`method foundation is strong and coding-ready, but not yet fully mature as a three-skill family`

## 4. Phase Status Against The Original Detailed-Design Plan

The original detailed-design upgrade plan had six phases. Current status is:

### Phase 0 - Baseline Inventory And Freeze

Status: `8.5 / 10`

What is done:

- the six reference FC families are fixed
- grounding scope and index are landed
- main and secondary baseline roles are defined

What is still missing:

- deeper continuous refresh discipline when new baseline FCs are added later

### Phase 1 - Grounding Baseline Extraction

Status: `8.5 / 10`

What is done:

- module summaries
- module facts
- pattern notes
- selection rules
- decompressed `Conf_IoExtDev` evidence linked in

What is still missing:

- some deeper DET/fault-style extraction
- more standardized module-card completeness across all six modules

### Phase 2 - Structured Input Modeling

Status: `8.5 / 10`

What is done:

- requirement, architecture, and detailed-design schemas
- field dictionary
- examples
- bundle generator
- trace convergence
- decision convergence
- grounding pattern inference

What is still missing:

- requirement-side and architecture-side first-class bundle generation of the same maturity
- stronger semantic extraction beyond current safe heuristics

### Phase 3 - Validator V1

Status: `8.5 / 10`

What is done:

- markdown-level consistency validator
- bundle-level validator
- interface consistency checks
- relationship-link checks
- trace completeness checks

What is still missing:

- broader regression suite
- richer three-layer conflict validation for future requirement/architecture porting

### Phase 4 - Grounding-Driven Generation

Status: `8.0 / 10`

What is done:

- grounding summary template
- generation bundle template
- grounding pattern inference
- workflow guidance
- first-pass bundle-to-markdown renderer
- rendered DD sample already passes markdown-level validator

What is still missing:

- broader multi-module replay
- more refined chapter polish for different FC families

### Phase 5 - Regression Set

Status: `3.5 / 10`

What is done:

- the need is defined
- `Gp_NCA95yy` exists as a real pipeline sample

What is still missing:

- real regression case directory
- golden artifacts
- diff reporting
- multi-module replay coverage

### Phase 6 - Skill Convergence

Status: `7.0 / 10`

What is done:

- skill internals are much cleaner
- references, schemas, grounding, and scripts are inside the skill
- `SKILL.md` is now flow-oriented
- narrative policy docs are landed

What is still missing:

- eventual rename/split strategy if required later
- shared upstream adoption by requirement and architecture lines

## 5. What Has Actually Been Fixed

The recent detailed-design optimization did not just add more files. It fixed six structural problems.

### 5.1 Fixed Problem: Prompt-Only Generation

Before:

- natural-language input could go directly to markdown
- correctness depended too much on prompt behavior

Now:

- generation is increasingly routed through grounding, bundle objects, and validators

### 5.2 Fixed Problem: Weak Real-Engineering Evidence

Before:

- grounding was more idea than enforceable evidence

Now:

- real FC baselines, `Conf_*` assets, module facts, and selection rules exist inside the skill

### 5.3 Fixed Problem: Missing Intermediate Truth Layer

Before:

- markdown was effectively the only truth layer

Now:

- schemas, examples, and generation bundles provide a real intermediate model

### 5.4 Fixed Problem: Hidden Scope Downgrades

Before:

- reserved or pending items could disappear into prose

Now:

- `status`, `decision`, `decision_reason`, `impacts`, `trace_ids`, and `grounding_patterns` are explicit bundle objects

### 5.5 Fixed Problem: No Hard Gate Before Output

Before:

- a document could look complete while still drifting from architecture

Now:

- bundle validation and markdown validation both exist

### 5.6 Fixed Problem: Data Was Ready But Draft Was Not

Before:

- the skill had grounding and schema direction, but no real path from bundle to DD body

Now:

- a first-pass renderer can generate a structured DD draft
- the rendered draft can pass the markdown-level validator
- unresolved gaps are surfaced instead of being hidden by smoother prose

## 6. Current Practical Decision

The detailed-design line has now reached a pragmatic state:

- problems can be surfaced explicitly
- bundle and markdown gates can stop silent drift
- a first-pass DD draft can be rendered from the structured bundle
- coding does not need to wait for perfect document polishing

Current practical rule:

- validator should expose real problems
- renderer should generate a structurally valid and implementation-usable first draft
- automatic repair is optional, not the main near-term priority
- if key issues are visible rather than hidden, coding may continue

This changes the near-term objective from:

- `make the DD perfectly polished before coding`

to:

- `make the DD structurally safe, traceable, and honest enough to support coding`

## 7. Strict Priority Of Next Work

The next plan should not split attention equally across all three skills.

The correct order is:

### Priority 1

Keep the detailed-design line stable and coding-ready.

Reason:

- this line already has the strongest structured base
- it now has grounding, bundle generation, validation, and first-pass rendering
- the near-term target is controlled usability, not over-polishing

### Priority 2

Port the structured-bundle method into requirement generation.

Reason:

- requirement skill already has a strong conceptual architecture
- it now needs implementation convergence, not more conceptual layering

### Priority 3

Port freeze-object logic into architecture generation.

Reason:

- architecture must become the stable middle handoff layer
- it should consume requirement bundle and produce architecture bundle

### Priority 4

Connect all three bundles into one pipeline.

Reason:

- only then can the three skills be called a system rather than three related tools

## 8. Next Plan By Skill

## 8.1 Detailed Design - Next Plan

### Target

Raise from `8.0` to around `8.5+`

### Next Work

- keep grounding / schema / bundle / validator / renderer aligned
- treat renderer output as a coding-capable first draft, not a final editorial artifact
- continue exposing formal dependency gaps, unresolved relationship links, and trace holes instead of hiding them
- use rendered DD output directly as implementation input when core interfaces and constraints are stable
- start regression pack for at least:
  - `Gp_TPT1145`
  - `Gp_TLE92104`
  - `Gp_DRV8889`
  - `Gp_NCA95yy`

### What Is Already Landed

- `detailed_design_quality_contract.md`
- `bundle_to_dd_mapping.md`
- `chapter_generation_rules.md`
- first-pass bundle-to-DD renderer
- bundle validator
- markdown validator

### Success Gate

- generated DD is structurally valid
- architecture drift is visible
- unresolved design gaps are surfaced explicitly
- coding can proceed with the DD as a controlled implementation draft

## 8.2 Requirement Generation - Next Plan

### Target

Raise from `5.5` to around `7.0+`

### Next Work

- define requirement bundle contract
- build raw-input-to-requirement-bundle helper
- define requirement field governance:
  - `status`
  - `decision`
  - `decision_reason`
  - `evidence`
  - `trace_ids`
- add requirement bundle validation
- add appendix/body consistency guard

### Success Gate

- requirement markdown becomes a rendering of requirement bundle objects rather than the first truth source

## 8.3 Architecture Generation - Next Plan

### Target

Raise from `4.5` to around `6.5+`

### Next Work

- define architecture bundle contract
- define explicit interface-freeze rules
- build requirement-bundle-to-architecture-bundle helper
- classify config items as:
  - `formal`
  - `reserved`
  - `conditional`
  - `pending_confirm`
- add architecture bundle validation
- export architecture constraints for detailed-design bundle consumption

### Success Gate

- architecture becomes the stable freeze layer, not just a better-written markdown document

## 9. Recommended Milestone View

### M1

Detailed-design coding-capable rendering line stabilized.

### M2

Requirement bundle generation landed.

### M3

Architecture bundle generation landed.

### M4

Requirement -> Architecture -> Detailed Design bundle chain connected.

### M5

Regression pack covers multiple FC styles.

### M6

Three skills share one method family with unified field dictionary, trace model, and validation policy.

## 10. Final Judgment

If judged strictly, the current system is not yet "three mature skills".

It is:

- one clearly advancing detailed-design pipeline
- one conceptually strong but not yet fully modernized requirement skill
- one useful but still rule-heavy architecture skill

That is not a failure.

It is a normal midpoint.

The important part is that the detailed-design line has already validated the right method:

- grounding first
- structured model first
- traceable decisions
- validation gated
- markdown last

And at the current stage, that line is already practical enough to support coding as long as real gaps are exposed rather than hidden.
