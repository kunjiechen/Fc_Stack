# Requirement Semantic Model

Use this reference when structured requirement objects, schemas, JSON output, requirement graphs, or stable requirement attributes are needed.

## Core Object

```json
{
  "id": "SRS-MODULE-TYPE-0001",
  "title": "",
  "type": "functional | interface | state | configuration | timing | diagnostic | safety | traceability | validation",
  "module": "",
  "shall": "",
  "rationale": "",
  "source": [
    {
      "document": "",
      "section": "",
      "chunk_id": "",
      "evidence": ""
    }
  ],
  "capability": [],
  "constraints": [],
  "interfaces": [],
  "states": [],
  "configuration": [],
  "timing": [],
  "diagnostics": [],
  "safety": {
    "asil": "",
    "safety_goal": "",
    "mechanism": "",
    "boundary": ""
  },
  "relations": [],
  "ownership": [],
  "verification": {
    "method": "test | analysis | inspection | review",
    "level": "unit | integration | system | review | analysis | inspection",
    "acceptance": ""
  },
  "trace": {
    "upstream": [],
    "verification_intent": [],
    "open_links": []
  },
  "status": "draft | validated | needs_source | conflict | open_issue"
}
```

## Relation Types

- `depends_on`: one requirement requires another.
- `refines`: lower-level requirement refines upper-level requirement.
- `conflicts_with`: semantic conflict requiring resolution.
- `excludes`: project constraint removes a supported capability.
- `transitions_to`: state machine transition.
- `controls`: interface or service controls behavior.
- `observes`: diagnostic/status output observes behavior.
- `verified_by`: requirement has verification intent through test, analysis, inspection, or review.
- `owned_by`: module, layer, or component ownership.

## State Model

```json
{
  "state": "Sleep",
  "entry_trigger": [],
  "entry_guard": [],
  "entry_action": [],
  "exit_trigger": [],
  "exit_guard": [],
  "exit_action": [],
  "allowed_transitions": [],
  "forbidden_transitions": [],
  "observable_outputs": [],
  "timing_constraints": [],
  "diagnostic_behavior": []
}
```

## Capability + Constraint Fusion Pattern

1. Capture supported capability exactly as stated by the source.
2. Capture project restriction independently.
3. Compute final allowed behavior.
4. Preserve excluded capabilities in trace or rationale.
5. Generate final requirement only for allowed behavior unless the user asks to document exclusions.

Example:

```json
{
  "capability": ["Normal", "Standby", "Sleep", "Listen-only"],
  "constraint": ["Listen-only prohibited"],
  "final_allowed": ["Normal", "Standby", "Sleep"],
  "excluded": ["Listen-only"]
}
```

## Requirement Object Hygiene

- Do not duplicate requirements with different wording.
- Normalize naming for modes, signals, service interfaces, pins, and diagnostics.
- Keep requirement prose concise and modal: "The {module} shall ...".
- Put supporting explanation in `rationale`, not in the requirement sentence.
- Mark ambiguity explicitly instead of silently resolving it.
