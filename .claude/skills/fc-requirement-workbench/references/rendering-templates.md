# Rendering Templates

Use this reference when generating SRS, requirement trace matrices, coverage matrices, or validation reports.

For full SRS document generation, prefer `srs-output-template.md`. This file keeps auxiliary rendering patterns for trace matrices, coverage matrices, validation reports, and compact requirement snippets.

## SRS Requirement Template

```markdown
### {id} {title}

- Type: {type}
- Source: {document} / {section} / {chunk_id}
- Requirement: The {module} shall {observable_behavior}.
- Rationale: {why_this_requirement_exists}
- Constraint: {project_or_hardware_constraints}
- Verification: {method} at {level}; acceptance: {acceptance_criteria}
- Trace: upstream={source_ids}; verification_intent={verification_ids_or_TBD}
- Status: {status}
```

## Requirement Sentence Patterns

Functional:

```text
The {module} shall {perform_behavior} when {condition}.
```

Interface:

```text
The {module} shall {provide/consume/control/report} {interface} with {owner} when {condition}.
```

State:

```text
The {module} shall transition from {source_state} to {target_state} when {trigger} and {guard_condition}.
```

Timing:

```text
The {module} shall {perform_behavior} within/after/before {time_value} under {condition}.
```

Configuration:

```text
The {module} shall accept {parameter} values in the range {range} and reject values outside this range.
```

Diagnostic:

```text
The {module} shall detect {fault_condition} and report {diagnostic_event/status} when {detection_condition}.
```

Safety:

```text
The {module} shall {safety_behavior} to support {safety_goal} within {asil_or_boundary}.
```

## SRS Section Skeleton

```markdown
# Software Requirement Specification - {Module}

## 1. Scope
## 2. References
## 3. Terms And Abbreviations
## 4. Requirement Overview
## 5. Functional Requirements
## 6. Interface Requirements
## 7. State And Mode Requirements
## 8. Configuration Requirements
## 9. Timing Requirements
## 10. Diagnostic Requirements
## 11. Safety Requirements
## 12. Traceability
## 13. Validation Summary
## 14. Open Issues
```

## Trace Matrix Template

| Source | Requirement | Verification Intent | Status |
|---|---|---|---|
| {source_id} | {requirement_id} | {verification_intent} | {status} |

## Coverage Matrix Template

| Requirement | Type | Source Covered | Verification Intent Covered | Gap |
|---|---|---:|---:|---|
| {requirement_id} | {type} | Yes/No | Yes/No | {gap} |

## Validation Report Template

```markdown
# Requirement Validation Report - {Module}

## Summary

- Total requirements: {count}
- Validated: {count}
- Needs source: {count}
- Conflicts: {count}
- Open issues: {count}

## Findings

| Severity | Rule | Requirement | Finding | Recommendation |
|---|---|---|---|---|
| error | {rule} | {id} | {finding} | {recommendation} |

## Coverage Gaps

| Requirement | Missing Item | Impact | Suggested Action |
|---|---|---|---|
| {id} | {source/verification/interface/exception} | {impact} | {action} |
```

## Example Capability Fusion Output

Input:

```text
Datasheet supports: Normal, Standby, Sleep, Listen-only.
Project constraint: Listen-only is prohibited.
```

Output:

```markdown
### SRS-TJA1043-STATE-0001 Supported Operating Modes

- Type: state
- Source: datasheet / Operating Modes; project_requirements / Mode Policy
- Requirement: The TJA1043 driver shall support Normal, Standby, and Sleep operating modes.
- Rationale: The datasheet supports these modes and project policy excludes Listen-only mode.
- Constraint: Listen-only mode shall not be exposed as a supported project mode.
- Verification: test; acceptance: mode request interfaces accept Normal, Standby, and Sleep and reject Listen-only.
- Trace: upstream=DS-OPERATING-MODES, PRJ-MODE-POLICY; verification_intent=MODE-REQUEST-TEST-TBD
- Status: validated
```
