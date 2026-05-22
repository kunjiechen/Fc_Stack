# Gp_TimeRecord FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: Cdd functional component layer
- Role: Record time points during startup/runtime and provide wakeup runtime measurement; optionally flips a test pin for timing observation.
- Best-fit scenario: Lightweight timing/record utility FC; good reference for small modules that should not become heavy architecture frameworks.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_TimeRecord_RecordTimePoint(Gp_TimeRecord_RecordPointType RecordPoint_e)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `float32 Gp_TimeRecord_GetWakeupRunTimeSecond(void)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `void Gp_TimeRecord_CalloutFlipTestDioPin(Gp_TimeRecord_RecordPointType RecordPoint_e)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |

## Configuration and Calibration Guidance

- Test pin flip enable is an optional feature macro.
- Timing conversion factors and selected record points may be const parameters or config data unless compile-time build variant is required.

## Runtime-State Guidance

- Small global runtime record stores timestamps/time deltas.
- No MainFunction is required for simple point recording.

## MemMap Guidance

- CODE for two public APIs.
- CLEAR_FAR_DATA for runtime records.
- CONST for record-point config/conversion constants.

## Reusable Architecture Lessons

- For utility FCs, keep interfaces minimal and avoid unnecessary Init/MainFunction unless lifecycle requires them.
- Optional observation/debug pin behavior belongs behind a feature macro/callout.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
