# Gp_IoMcuDio FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: IoMcu resource layer
- Role: Wrap MCU DIO resources and expose semantic direction, input level, and output level operations by logical signal ID.
- Best-fit scenario: DIO resource wrapper FC; good reference for simple input/output/direction APIs and lightweight resource encapsulation.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_IoMcuDio_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoMcuDio_SetDioSigDir(uint16 Id_u16, Gp_IoMcuDio_DirType Dir_t)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoMcuDio_GetDioSigLvlIn(uint16 Id_u16, boolean* LvlIn_pb)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoMcuDio_SetDioSigLvlOut(uint16 Id_u16, boolean LvlOut_b)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `uint32 Gp_IoMcuDio_CalloutGetCoreId(void)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `Std_ReturnType Gp_IoMcuDio_CalloutInit(uint32 CoreId_u32)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `boolean Gp_IoMcuDio_CalloutSetDir(uint32 CoreId_u32, uint8 ChlIdx_u8, Gp_IoMcuDio_DirType Dir_t)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `boolean Gp_IoMcuDio_CalloutGetLvlIn(uint32 CoreId_u32, uint8 ChlIdx_u8, boolean* LvlIn_pb)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `boolean Gp_IoMcuDio_CalloutSetLvlOut(uint32 CoreId_u32, uint8 ChlIdx_u8, boolean LvlOut_b)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |

## Configuration and Calibration Guidance

- Per-core enable and signal count are count/size macros.
- Logical signal-to-channel mapping belongs in Cfg/CfgData.
- Do not create one macro for every Get/Set interface.

## Runtime-State Guidance

- Runtime state is small: init state and interface-check/error state.
- No MainFunction is needed for direct DIO operations unless project behavior adds periodic scanning.

## MemMap Guidance

- CODE for APIs.
- CONST for mapping tables.
- CLEAR_FAR_DATA for init/error runtime state.

## Reusable Architecture Lessons

- For simple resource wrappers, keep API count small and semantic: SetDir, GetLvlIn, SetLvlOut.
- Use callout abstraction for DIO operations; do not bind FC directly to a concrete DIO driver.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
