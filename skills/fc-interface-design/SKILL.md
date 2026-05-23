---
name: fc-interface-design
description: Use when generating or reviewing FC detailed design documents with architecture-driven external interfaces, internal interfaces, and dependency interfaces. Enforces strict company-style rules for architecture consistency, internal-function consolidation, complexity control, output order, and interface relationship tracing.
---

# FC Interface Design

Use this skill when drafting, reviewing, or correcting FC detailed design content for interface sections.

This skill is the single rule source for FC interface extraction and output in this project. When new interface-design rules are added later, fold them into this file instead of scattering them across multiple prompts or documents.

## Rule Priority

When rules appear to conflict, resolve them in this order:

1. Engineering alignment rules
2. Project documentation enhancement rules
3. Design method
4. Codebase grounding rules
5. Output contract
6. Recommended fields

Do not let recommended structure override mandatory architecture or company-style constraints.

## Interface Layers

Treat interfaces as exactly three layers:

1. External interfaces: formal APIs provided by the module to upper layers.
2. Internal interfaces: `static` internal functions extracted from external-interface subfunctions.
3. Dependency interfaces: formal lower-layer or platform-facing interfaces called by this module.

External interfaces and dependency interfaces are architecture-frozen sets. Internal interfaces are detailed-design artifacts.

## Engineering Alignment Rules

These rules are intended to keep generated design aligned with the prevailing implementation style of the real project codebase.

### Architecture Consistency

- The external interface list must come only from the architecture design.
- The detailed design must fully cover the architecture external interface list.
- Do not add, remove, rename, merge, or split architecture external interfaces.
- Names, prototypes, return values, and core semantics of external interfaces must stay identical to architecture.
- The dependency interface list must come only from the architecture design.
- The detailed design must fully cover the architecture dependency interface list.
- Do not add, remove, rename, merge, or split architecture dependency interfaces.
- Names, prototypes, return values, and core semantics of dependency interfaces must stay identical to architecture.

### No Conditional Interfaces In Architecture

- Architecture must not contain conditional external interfaces.
- Architecture must not contain conditional dependency interfaces.
- An external or dependency interface either formally exists or formally does not exist.

### Internal Interface Boundaries

- Internal interfaces are not architecture-frozen, but they must only serve external-interface implementation.
- Internal interfaces must not introduce new external semantics.
- Internal interfaces must not introduce new dependency semantics.
- Any lower-layer access in external or internal interfaces must map to an architecture-defined dependency interface.
- Do not create hidden lower-layer calls outside the architecture dependency interface list.

### Company-Style And Complexity Constraints

- Internal interfaces must be extracted for reuse, complexity reduction, readability, and company code-rule compliance.
- Do not mechanically create one internal function set per external interface.
- Do not extract trivial wrappers with no reuse value and no meaningful complexity reduction.
- Prefer merging repeated checks, shared decoding, shared register access, shared fault handling, and shared data conversion.
- A good internal function should represent one stable responsibility.
- Internal function count is not a success metric. More internal functions are not inherently better.
- Avoid over-splitting small logic domains such as DET checks, simple fault bit operations, or other lightweight helper actions.
- If several small operations are always used together and do not create excessive complexity, prefer one moderately sized internal function over many tiny ones.
- Internal-function granularity must also consider downstream cost: unit verification scope, interface coverage workload, timing overhead, and maintenance effort.

## Project Documentation Enhancement Rules

These rules are added to improve generated document usability, review efficiency, and traceability. They are useful project rules, but they are not assumed to be direct facts extracted from the existing codebase unless separately confirmed.

### Documentation Structure Enhancement

- Use a stable and review-friendly structure for interface sections.
- Prefer explicit relationship tracing between interface layers.
- Prefer document organization that makes architecture-to-design traceability obvious.

### Documentation Governance Enhancement

- Generated documents may be stricter and more explicit than legacy documents if that improves review quality, as long as engineering alignment rules are not violated.
- Do not let documentation enhancement rules force the design away from the actual codebase pattern.

## Design Method

Always work in this order:

1. Freeze the external interface list from architecture.
2. Freeze the dependency interface list from architecture.
3. Clarify each external interface's function boundary, inputs, outputs, abnormal paths, and execution flow.
4. Decompose each external interface into subfunctions or execution actions.
5. Compare subfunctions across external interfaces and merge repeated actions.
6. Define internal interfaces from the merged common actions.
7. Verify that all lower-layer calls map to architecture dependency interfaces.

Use this method to avoid one-to-one mechanical splitting from external interface to internal function.

When deciding whether a candidate internal function should remain separate, ask:

- Does it significantly reduce duplication across multiple external interfaces?
- Does it materially reduce cyclomatic complexity in the caller?
- Does it represent a stable responsibility instead of a tiny transient step?
- Is its verification and maintenance cost justified by its reuse value?

If the answer is mostly no, merge it back into a larger internal function or keep it in the caller.

## Codebase Grounding Rules

When the target repository already contains FC drivers or adjacent modules in the same layer, do not derive detailed design style from chip semantics alone. Ground the design in the existing codebase pattern first.

### Required Grounding Pass

Before finalizing interface design, inspect representative existing modules in this order:

1. same module layer and same interface family if available
2. same device domain or adjacent driver family if available
3. same platform FC modules that show current company implementation style

Use the grounding pass to determine:

- typical external interface count and shape
- typical dependency interface shape
- whether `CalloutGetCoreId`-style dependencies are standard
- how runtime containers are organized
- how DET or internal error recording is really handled
- typical internal-function granularity
- whether fault management is lightweight or heavy

Grounding sources must come from real project assets such as:

- existing production code
- existing released or maintained architecture/design documents
- existing configuration, callout, and runtime organization in the repository

Do not use model-generated architecture or detailed-design artifacts as grounding sources for the skill itself.
Generated files may be review targets, but they must not become the style reference that teaches the skill what "normal" looks like.

### Grounding Overrides

If generated detailed design is theoretically complete but differs from the dominant codebase pattern, prefer the dominant codebase pattern unless architecture explicitly requires otherwise.

In particular:

- do not over-expand chip-level behavior into many helper functions if peer modules use fewer, thicker helpers
- do not introduce heavy DET helper families if peer modules use one unified access-check function
- do not introduce heavy fault state machines if peer modules use lightweight error flags or compact fault recording
- do not over-specify lower-layer transaction details in FC detailed design if peer modules only define dependency-interface semantics

### Anti-Pattern Checks

Treat the following as warning signs that the design is drifting away from company code style:

- internal function count keeps growing without strong reuse benefit
- DET logic is split into many tiny helpers
- fault handling is split into many tiny helpers
- the design reads like a chip manual decomposition rather than an FC module design
- two naming systems appear for the same internal logic
- the document contains duplicate internal-function sections or overlapping decompositions
- dependency interfaces are described at bus transaction granularity instead of FC dependency granularity

When these signs appear, compress the design back toward the prevailing codebase pattern.

## Output Contract

The output contract belongs to project documentation enhancement. It defines how generated documents should be presented once engineering alignment has already been satisfied.

### Output Order

The detailed design must present interface content in this order:

1. External interfaces
2. Internal interfaces
3. Dependency interfaces

### Relationship Field

Each interface entry must contain both workflow information and relationship information.

Add a dedicated relationship field such as `关联接口` for every interface.

Relationship information must stay consistent with execution steps, subfunction decomposition, and workflow diagrams. Do not introduce hidden calls in the relationship field.

### Relationship Content By Layer

For external interfaces, `关联接口` should show:

- related internal interfaces called by this external interface
- related dependency interfaces directly or indirectly reached by this external interface
- optional related external interfaces in the same functional chain

For internal interfaces, `关联接口` should show:

- upstream external interfaces that call this internal interface
- upstream internal interfaces if any
- downstream internal interfaces if any
- downstream dependency interfaces called by this internal interface

For dependency interfaces, `关联接口` should show:

- calling external interfaces if any direct calls exist
- calling internal interfaces
- supported functional scenarios

## Recommended Fields

These fields are recommended output structure. They must not override the non-negotiable rules or output contract.

### External Interface Entry

For each external interface, include:

- prototype
- purpose and boundary
- sync/async
- reentrancy
- return value
- constraints
- subfunction decomposition
- execution steps
- workflow diagram
- `关联接口`

### Internal Interface Entry

For each internal interface, include:

- name
- category
- scope
- responsibility
- trigger point or call scenario
- consolidation rationale
- major inputs and outputs
- key branches or key checks
- associated external interfaces
- associated dependency interfaces if any
- `关联接口`

### Dependency Interface Entry

For each dependency interface, include:

- prototype
- purpose
- implemented by
- sync/async
- reentrancy
- constraints
- `关联接口`

## Maintenance Rule

When new project rules are provided later:

- first classify them into non-negotiable rules, design method, codebase grounding rules, output contract, or recommended fields
- then update this file in that section
- do not append disconnected rule fragments elsewhere as the primary source

## Review Checklist

Before finishing, verify all of the following:

- external interfaces exactly match architecture
- dependency interfaces exactly match architecture
- no conditional external or dependency interfaces remain
- no hidden lower-layer calls exist outside architecture dependency interfaces
- internal interfaces come from merged repeated subfunctions, not per-interface mechanical splitting
- internal interfaces reduce duplication or complexity in a meaningful way
- internal interfaces are not over-split into many low-value tiny helpers
- small domains such as DET and simple fault handling are merged to reasonable granularity
- the detailed design has been grounded against representative existing modules in the target codebase
- the design follows prevailing company FC style rather than chip-manual decomposition style
- interface output order is external, internal, dependency
- every interface has `关联接口`
- relationship links match workflow and call paths
