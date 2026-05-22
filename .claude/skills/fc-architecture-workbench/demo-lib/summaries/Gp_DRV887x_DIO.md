# Gp_DRV887x_DIO FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: IoExtDev external device layer
- Role: Control DRV887x-like external driver chips through DIO/PWM/ADC dependencies, with asynchronous output requests and periodic diagnosis/state-machine handling.
- Best-fit scenario: H-bridge / motor-driver chip FC; good reference for mode control, output request, current readback, diagnosis, recovery, multi-core and multi-instance.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_DRV887x_DIO_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_DRV887x_DIO_MainFunction(void)` | Periodic/background processing. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_DRV887x_DIO_SetDevModeOutSig(uint16 Id_u16, Gp_DRV887x_DIO_DrvModType DrvMode_te)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_DRV887x_DIO_SetDrvOutSig(uint16 Id_u16, uint32 Perd_u32, uint32 Duty_u32, Gp_DRV887x_DIO_DrvDirType Dir_te)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_DRV887x_DIO_GetCurSig(uint16 Id_u16, float32* Cur_pf32, boolean* CurVld_pb)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_DRV887x_DIO_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `uint32 Gp_DRV887x_DIO_CalloutGetCoreId(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `boolean Gp_DRV887x_DIO_CalloutReadDioCh(uint16 ChId_u16)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `void Gp_DRV887x_DIO_CalloutWrDioCh(uint16 ChId_u16, uint8 Lvl_u8)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `void Gp_DRV887x_DIO_CalloutSetPwmPerdAndDuty(uint16 ChId_u16, uint32 Perd_u32, uint32 Duty_u32)` | Hardware/platform action outside FC ownership. | PWM/IoMcu or project adaptation. |
| `void Gp_DRV887x_DIO_CalloutGetAdcRaw(uint16 ChId_u16, uint16* Raw_pu16, boolean* RawVld_pb)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |

## Configuration and Calibration Guidance

- Device count and signal count are count/size macros.
- DEV_ERROR_DETECT is a formal development error detect macro.
- DRV_CUR_RGLN and PHEN/PWM/HALB are feature/behavior-selection macros only when compile-time trim or mode selection is required.
- Hardware channels, chip mapping, thresholds, debounce and recovery parameters belong in config tables unless fixed compile-time strategy is proven.

## Runtime-State Guidance

- Per-chip runtime container stores target/current device mode, output request, current value/validity, fault information, debounce/recovery counters, and state-machine status.
- Setters buffer requests; MainFunction applies requests and performs diagnosis/recovery; getters return cached status.

## MemMap Guidance

- CODE for APIs/state-machine helpers.
- CONST per-core/global sections for chip config and signal mapping.
- CLEAR_FAR_DATA per-core runtime containers.
- CALIB only when confirmed calibration parameters exist.

## Reusable Architecture Lessons

- External chip drivers should expose semantic Set/Get APIs, not raw DIO/PWM/ADC details.
- Hardware actions require callouts for DIO/PWM/ADC/core ID.
- Use MainFunction for deferred hardware update, fault diagnosis, debounce, and recovery.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
