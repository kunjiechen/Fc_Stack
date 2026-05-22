# Gp_IoSigAdc FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: IoSigSrv signal service layer
- Role: Provide signal-level ADC service above resource ADC, including diagnosis, raw reading, converted value, validity and calibration/scale handling.
- Best-fit scenario: ADC signal service FC above raw MCU resources; good reference for converted physical value, raw value, and diagnosis separation.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_IoSigAdc_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoSigAdc_GetAdcSigDiag(uint16 Id_u16, uint32* Diag_pu32)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoSigAdc_GetAdcSigAdc(uint16 Id_u16, uint32* Adc_pu32)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_IoSigAdc_GetAdcSigAdcRaw(uint16 Id_u16, uint16* AdcRaw_pu16)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `uint32 Gp_IoSigAdc_CalloutGetCoreId(void)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoSigAdc_CalloutInit(uint32 CoreId_u32)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoSigAdc_CalloutGetDiag(uint32 CoreId_u32, uint8 ChlIdx_u8, uint32* Diag_pu32)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoSigAdc_CalloutGetAdc(uint32 CoreId_u32, uint8 ChlIdx_u8, uint32* Adc_pu32)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |
| `boolean Gp_IoSigAdc_CalloutGetAdcRaw(uint32 CoreId_u32, uint8 ChlIdx_u8, uint16* AdcRaw_pu16)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |

## Configuration and Calibration Guidance

- Per-core signal counts are count/size macros.
- Signal mapping, conversion parameters, and diagnosis handling belong in configuration/calibration data.
- Calibration sections are justified only when conversion coefficients or signal calibration values are formal project data.

## Runtime-State Guidance

- Runtime caches diagnosis, converted ADC value, raw ADC value, validity, and init/check status.
- Internal helpers separate GetDiag, CheckDiag, GetAdc, GetAdcRaw, and raw-to-value conversion.

## MemMap Guidance

- CODE for service APIs and conversion helpers.
- CONST for mapping/config tables.
- CALIB const sections for conversion/calibration parameters when confirmed.
- CLEAR_FAR_DATA for cached values and validity state.

## Reusable Architecture Lessons

- Use a signal service FC when the user-facing concept is a physical/signal value rather than raw hardware.
- Expose raw, converted, and diagnosis APIs separately only when each is a formal consumer need.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
