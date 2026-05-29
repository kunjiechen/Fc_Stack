# Requirement Grounding Policy

## 1. Purpose

This file defines how `fc-requirement-workbench` selects and records engineering grounding before generating a requirement bundle.

Grounding is the act of anchoring a new module's requirements against existing project reality — real source code, accepted artifacts, and known FC patterns. It answers:

- which existing FC modules are the closest engineering relatives
- which architectural and interface patterns are adopted from those relatives
- which patterns are explicitly rejected and why
- which capabilities observed in source code should not be elevated to formal requirements

Grounding is not a replacement for formal upstream requirements. It is a stabilisation layer that prevents the requirement pipeline from hallucinating interfaces, states, or dependencies that have no basis in the project's engineering reality.

## 2. Grounding Inputs

Grounding consumes three types of input, in order of authority:

### 2.1 Project Source Code (implemented evidence)

When `--source-root` is provided, the pipeline scans the source tree for neighbouring FC modules (`Gp_*` directories) and uses them as evidence of:

- naming conventions (function names, file names, type names)
- interface patterns (which Init/MainFunction/GetInSig/SetOutSig variants are conventional)
- configuration patterns (container layout, instance count handling, multi-core allocation)
- state and fault handling conventions
- project-specific style (error return conventions, DET usage, MemMap sections)

Important: source code is **implemented evidence**, not normative truth. A pattern observed in source code does not automatically become a requirement. It must still pass the formal requirement gate.

### 2.2 Current Accepted Artifacts (acceptance baseline)

Existing accepted SRS, architecture, and detailed design documents serve as:

- rendering baselines (what a good output looks like)
- calibration baselines (what granularity the project expects)
- boundary baselines (what the project considers in-scope vs out-of-scope)

These artifacts define "acceptable" — not "complete" or "correct".

### 2.3 Normative Rule Assets (normative baseline)

Current skill reference files provide the normative baseline:

- `aurix2g-normative-patterns.md`: interface classification, MainFunction rules, layer naming
- `authoring-standard.md`: SRS writing conventions
- `construction-rules.md`: minimum field requirements per category
- `calibration-rules.md`: granularity and boundary preferences

## 3. Grounding Process

### 3.1 Reference Module Discovery

When a source root is available, the pipeline discovers neighbouring FC modules by scanning for `Gp_*` directories. Modules with the same name as the target are excluded. Up to 6 reference modules are recorded.

Reference modules are selected based on co-location in the source tree, not on explicit configuration. This is a heuristic; it should be tightened in later phases with explicit grounding configuration.

### 3.2 Pattern Adoption

Patterns are adopted based on the presence of specific module families in the reference set:

| Trigger (module name contains, case-insensitive) | Adopted Pattern |
|---|---|
| `iomcu` | `iomcu_dependency_integration` — the module depends on IoMcu-layer services; interface contracts must account for cross-layer callouts |
| `tpt1145` | `ioextdev_callout_and_register_pattern` — the module follows IoExtDev register-access conventions; SPI/I2C access, register caching, and RMW semantics apply |
| `drv8889` | `ioextdev_fault_and_state_pattern` — the module has explicit fault/diagnostic state handling; fault readback, error latching, and watchdog interaction patterns apply |

A pattern is "adopted" when the reference module family is present in the source root. Adoption does not mean the pattern is correct for the target module — only that it is the closest available engineering reference.

### 3.3 Pattern Rejection

Patterns may be explicitly rejected when the target module's datasheet or project constraints contradict the pattern. When rejected, the `rejected_patterns` list is populated and the `notes` field explains why.

Currently, rejection is manual (set during grounding input preparation). Automated rejection detection is a future enhancement.

### 3.4 Grounding Mode

The current grounding mode is `codebase_and_current_artifacts` — meaning all three input types (source code, accepted artifacts, normative rules) are used. Future modes may include:

- `explicit_grounding_input`: when a dedicated grounding markdown is provided
- `normative_only`: when no source root is available (fallback to rules alone)

## 4. Grounding Output

Grounding results are recorded in the `grounding_summary` section of the requirement bundle:

```yaml
grounding_summary:
  grounding_mode: "codebase_and_current_artifacts"
  reference_modules:
    - "Gp_06_Adc3ph"
    - "Gp_BTS7x_DIO"
  adopted_patterns:
    - "iomcu_dependency_integration"
  rejected_patterns: []
  notes: "Current grounding is inferred from the accessible project codebase..."
```

## 5. What Grounding Does NOT Do

Grounding does not:

- replace formal upstream requirements with code observations
- automatically promote implemented behaviour to formal requirements
- substitute for architecture-level interface freeze decisions
- override datasheet or project constraint inputs
- guarantee that adopted patterns are correct for the target module

Grounding is a stabilisation layer. It reduces variance; it does not eliminate the need for engineering judgment.

## 6. Grounding Quality Indicators

A grounding summary is considered adequate when:

1. At least one reference module is identified (when source root is available)
2. At least one pattern is adopted or explicitly rejected
3. The `notes` field acknowledges any inference gaps

If the source root is unavailable, `grounding_mode` falls back to `normative_only` and reference_modules / adopted_patterns are empty. This is acceptable but should be explicitly noted.

## 7. Future Enhancements

- Explicit grounding input: allow a dedicated grounding markdown file to specify reference modules and pattern adoption/rejection
- Per-interface grounding: record which specific reference module each interface pattern was drawn from
- Grounding confidence scoring: quantify how closely the target module matches each reference module
- Rejection automation: detect contradictions between datasheet capabilities and adopted patterns
