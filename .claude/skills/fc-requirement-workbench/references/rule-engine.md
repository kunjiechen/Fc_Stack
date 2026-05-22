# Requirement Rule Engine

Use this reference when validating requirement quality, conflicts, coverage, or traceability.

## Completeness Rules

Check whether the requirement set covers:

- Initialization and default state.
- Normal behavior.
- State transitions and forbidden transitions.
- Interface inputs, outputs, callbacks, pins, registers, service interfaces, and ownership.
- Configuration parameters, allowed ranges, defaults, and invalid values.
- Timing constraints, delays, timeouts, debounce, sampling, and wake/sleep timing.
- Diagnostic and fault behavior.
- Exception and recovery paths.
- Safety mechanisms, ASIL boundary, safety assumptions, and freedom-from-interference if applicable.
- Verification method and acceptance criteria.

Common missing-pair rules:

- Sleep implies Wake behavior.
- Mode control implies mode query/status behavior.
- Diagnostic event implies detection condition, reporting path, and clearing behavior.
- Configurable parameter implies range validation and default value.
- External signal implies ownership and electrical/logical interpretation.

## Consistency Rules

Flag conflicts between:

- Initial state and configured startup state.
- Supported modes and prohibited modes.
- State transitions and forbidden project policy.
- Timing values from different sources.
- Service interface ownership and pin/register ownership.
- AUTOSAR layer responsibility and software requirement ownership.
- Safety requirement and non-safety diagnostic behavior.

Conflict output format:

```json
{
  "rule": "state_consistency",
  "severity": "error | warning | info",
  "items": ["REQ-1", "REQ-2"],
  "problem": "",
  "suggested_resolution": ""
}
```

## Constraint Rules

Validate:

- Mode restrictions.
- Configuration ranges and enumerations.
- Hardware capability boundaries.
- Project feature exclusions.
- ASIL boundary and safety ownership.
- Variant-specific behavior.
- Resource limits such as channels, instances, buffers, interrupts, or wake sources.

## Ownership Rules

For automotive FC and transceiver-style modules, explicitly check ownership for:

- TXD
- RXD
- WAKE
- INH
- ERR_N
- STB_N
- EN
- SPI/I2C/register access
- MCU interrupt lines
- AUTOSAR service interfaces
- DEM/DET reporting
- EcuM/BswM/ComM interaction

## Trace Rules

Every accepted requirement should have:

- At least one upstream source.
- A validation method.
- A verification intent or open verification placeholder.
- An open verification marker if evidence is still unavailable.

When generating SRS documents, treat these as internal generation and validation
rules. Do not render a standalone "trace rule" section in the output document
unless the user explicitly asks for process rules.

SRS generation rules:

- Every formal requirement must have at least one upstream source.
- Every formal requirement must define verification method, verification stage, and acceptance criteria.
- Requirements with insufficient source evidence must remain `Draft`, `needs_source`, or `open_issue`; they must not be marked `Ready`.
- A datasheet-supported capability is not automatically a project-supported requirement.
- Project-prohibited capabilities must be excluded from final supported behavior while retaining their source/constraint rationale.
- Downstream SDD, code, and test artifacts should reference the generated `SRS-*` requirement IDs, but the SRS document should normally show only source inputs, not downstream trace process rules.

Status guidance:

- `validated`: source, constraints, and verification are adequate.
- `needs_source`: engineering plausible but source evidence is missing.
- `conflict`: source or requirement conflict exists.
- `open_issue`: decision or ownership is unresolved.

## Anti-Hallucination Rules

- If the source says a feature is supported, do not require the project to use it unless a project constraint or requirement says so.
- If the project prohibits a capability, do not include it in final supported behavior.
- If timing is implied by text such as "wait 8 us before sampling", classify it as timing behavior.
- If a requirement cannot be verified, rewrite it or mark it invalid.
- If a requirement uses "normal", "stable", "fast", "robust", or "multiple" without a measurable boundary, flag it.
