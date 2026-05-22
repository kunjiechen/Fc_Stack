# Gp_SysState FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: BswSys_Gp system layer
- Role: Manage ECU/system phase and state transitions with configurable transition conditions/actions and a recorder for state history.
- Best-fit scenario: System state machine FC; good reference for state ownership, Internal.h, state record buffer, and external/internal API separation.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_SysState_InitMemory(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_SysState_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_SysState_MainFunction(void)` | Periodic/background processing. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Gp_SysState_StateType Gp_SysState_GetState(void)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_SysState_RecordState(Gp_SysState_PhaseAndStateType PhaseAndState_te)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_SysState_SwitchAction(Gp_SysState_SwitchType Switch_te)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `Gp_SysState_RecorderType* Gp_SysState_CalloutGetRecorderPtr(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `uint32 Gp_SysState_CalloutGetTimeStamp(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |

## Configuration and Calibration Guidance

- DEV_ERROR_DETECT is formal only when parameter/state checking is required.
- RTE/BSWM usage macros are behavior-selection/integration macros.
- Record buffer length is a count/size macro.
- State transition table and action/condition mapping belong in config/frame config data.

## Runtime-State Guidance

- Module has memory-init state and module-init state.
- Current state and recorder are internal ownership; Internal.h exposes SetState for internal frame/action code, not external users.
- MainFunction evaluates state transition table and actions.

## MemMap Guidance

- CODE for public/internal state APIs and frame actions.
- CLEAR_FAR_DATA for current state and recorder runtime.
- CONST/CALIB sections for state frame/config tables where project-defined.

## Reusable Architecture Lessons

- Use Internal.h when generated/configured internal action code must access internal state without exposing it externally.
- Keep external state query separate from internal state mutation.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
