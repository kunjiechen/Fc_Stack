# Gp_IoMcuAdc FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: IoMcu resource layer
- Role: Wrap MCU ADC resources and provide stable FC-level ADC signal diagnosis/raw-value APIs with per-core ownership checks.
- Best-fit scenario: ADC sampling resource wrapper FC; good reference for raw ADC, diagnosis, polling/background acquisition, and Cfg/CfgData/Callout split.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_IoMcuAdc_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_IoMcuAdc_MainFunction(void)` | Periodic/background processing. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoMcuAdc_GetAdcSigDiag(uint16 Id_u16, uint32* Diag_pu32)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoMcuAdc_GetAdcSigAdcRaw(uint16 Id_u16, uint16* AdcRaw_pu16)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `uint32 Gp_IoMcuAdc_CalloutGetCoreId(void)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoMcuAdc_CalloutInit(uint32 CoreId_u32)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoMcuAdc_CalloutGetDiag(uint32 CoreId_u32, uint8 ChlIdx_u8, uint32* Diag_pu32)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoMcuAdc_CalloutGetAdcRaw(uint32 CoreId_u32, uint8 ChlIdx_u8, uint16* AdcRaw_pu16)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |

## Configuration and Calibration Guidance

- Per-core enable and per-core group count are integration-count/size macros, not feature switches.
- Signal mapping and group/channel binding belong in configuration data, not external APIs.
- Development checks validate init state, ID validity, core ownership, and output pointer.

## Runtime-State Guidance

- Per-core runtime container stores init state, latest diagnosis, ADC raw cache, and interface-check status.
- MainFunction updates resource-side data, while external getters return cached results.

## MemMap Guidance

- CODE for APIs/internal static helpers.
- CONST global/config data for mapping tables.
- CLEAR_FAR_DATA per-core runtime RAM.

## Reusable Architecture Lessons

- Use a resource wrapper when the FC abstracts MCU resources but should not expose raw MCAL calls.
- Use GetDiag and GetAdcRaw as separate APIs when diagnosis and signal value have different semantics.
- Dependency callouts must represent ADC actions; implementation owner may be MCAL/IoMcu/project adaptation.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
