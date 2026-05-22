# Gp_CpuLoadMonitor FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: RtMon runtime monitor layer
- Role: Measure per-core CPU load by timing idle/period windows, maintain min/max load and allow resetting observed extremes.
- Best-fit scenario: CPU load monitor FC; good reference for multi-core observation data, per-core runtime buffers and monitoring APIs.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_CpuLoadMonitor_CpuLoadCalcInit(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_CpuLoadMonitor_PeriodTask(void)` | Periodic/background processing. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_CpuLoadMonitor_ResetAllMinMaxCpuLoad(void)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `void Gp_CpuLoadMonitor_CalloutEnableTimer(boolean Enable_b)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |

## Configuration and Calibration Guidance

- Core count, timer selection, slice mask, idle tick tuning and filter time are count/behavior/timing macros when fixed by platform.
- Do not expose per-core buffers as external globals unless explicitly required.

## Runtime-State Guidance

- Per-core runtime buffers hold current load, min/max load, idle timing and measurement state.
- PeriodTask updates measurement window and statistics.

## MemMap Guidance

- CODE for monitor APIs and timing helpers.
- CLEAR_FAR_DATA per-core runtime buffers.
- Configuration macros for platform timer and scaling.

## Reusable Architecture Lessons

- Monitor FCs usually expose observation/reset APIs, not business-control APIs.
- Multi-core observation data should be per-core and owned by the monitor module.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
