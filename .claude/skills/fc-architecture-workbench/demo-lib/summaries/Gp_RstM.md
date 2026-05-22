# Gp_RstM FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: BswSys_Gp system layer
- Role: Analyze/reset reasons, perform controlled reset, manage retained NoClear data, exchange reset information and trigger safe-state handling.
- Best-fit scenario: Reset management and retained lifecycle-data FC; good reference for system APIs, NoClear data and NVM/callout interactions.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_RstM_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_RstM_InitOne(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_RstM_InitTwo(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_RstM_PerformReset(uint8 RstId_u8, uint8 CoreId_u8, uint8 RstType_u8)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_RstM_GetLastRstTypeInfo(uint8* RstTypePlt_pu8, uint8* RstTypeMcal_pu8, uint8* RstId_pu8, uint8* RstCoreId_pu8)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `uint16 Gp_RstM_GetErrRstTotalCount(void)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `uint8 Gp_RstM_GetSafeStateInfo(void)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_RstM_NoClearDataRecord(uint16 DataId_u16, uint16 DataLen_u16, uint8* Data_pu8)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_RstM_GetNoClearDataAddr(uint16 DataId_u16, uint32* DataAddr_u32)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_RstM_NoClearDataSaveToNvm(void)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `void Gp_RstM_CalloutGetRstInfo(uint8* PltRstType_pu8, uint8* McalRstType_pu8)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `void Gp_RstM_CalloutClearColdResetStatus(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `void Gp_RstM_CalloutPerformRst(uint8 RstType_u8)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `Std_ReturnType Gp_RstM_CalloutGetNvMStatus(void)` | Hardware/platform action outside FC ownership. | NVM/service layer or project adaptation. |
| `Std_ReturnType Gp_RstM_CalloutDataSaveToNvm(uint16 DataId_u16, uint8* Data_pu8)` | Hardware/platform action outside FC ownership. | NVM/service layer or project adaptation. |
| `Std_ReturnType Gp_RstM_CalloutDataReadFromNvm(uint16 DataId_u16)` | Hardware/platform action outside FC ownership. | NVM/service layer or project adaptation. |
| `void Gp_RstM_CalloutSafeStateL1Enter(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `void Gp_RstM_CalloutSafeStateL2Enter(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |

## Configuration and Calibration Guidance

- Reset retry thresholds/counts are compile-time strategy macros only if fixed by system design.
- Reset IDs, NoClear data IDs and NVM mapping belong in config tables.
- Project type selection is behavior-selection macro when build variants differ.

## Runtime-State Guidance

- NoClear retained data stores reset records and data exchange across reset lifecycle.
- CRC/double-save pattern protects retained data integrity.
- Init phases separate early reset info capture from later NVM/safe-state handling.

## MemMap Guidance

- NO_CLEAR is justified because lifecycle requires reset retention.
- CONST for reset ID/config tables.
- CODE for system APIs and reset analysis helpers.

## Reusable Architecture Lessons

- Use NO_CLEAR only when retained lifecycle data is explicitly required.
- System-layer FCs may expose system APIs, but platform reset/NVM/safe-state actions remain callouts.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
