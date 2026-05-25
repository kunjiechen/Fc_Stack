# Gp_TLE92104 Grounding Input

## Module Overview

- Module: `Gp_TLE92104`
- Layer: `IoExtDev`
- Platform: `AURIX2G`
- Code path: `IoExtDev/IoExtDev/Gp_TLE92104`
- Configuration path: `Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TLE92104`

## Runtime Pattern

- Supports multi-core runtime ownership.
- Maintains per-core runtime container.
- Provides a periodic `MainFunction` for mode update, output update, and diagnosis.
- Uses callout-based core identification and peripheral adaptation.

## External Interfaces

- `Gp_TLE92104_Init(void)`
- `Gp_TLE92104_MainFunction(void)`
- `Gp_TLE92104_SetHbOutSig(uint16 Id_u16, uint32 EcuPed_u32, uint32 EcuDuty_u32, uint8 Dir_u8)`
- `Gp_TLE92104_GetDevModeInSig(uint16 Id_u16, uint8* DevMode_pu8)`
- `Gp_TLE92104_SetDevModeOutSig(uint16 Id_u16, uint8 DevMode_u8)`
- `Gp_TLE92104_GetDevFaultSig(uint16 Id_u16, uint32* DevFault_pu32)`
- `Gp_TLE92104_GetHBVOUT(uint16 Id_u16, uint16* HBVOUTdata_pu16)`

## Callout Interfaces

- `Gp_TLE92104_CalloutGetCoreId`
- `Gp_TLE92104_CalloutDelayUs`
- `Gp_TLE92104_CalloutSpiSetupEB`
- `Gp_TLE92104_CalloutSpiSyncTransmit`
- `Gp_TLE92104_CalloutSetDoSig`
- `Gp_TLE92104_CalloutGetDiSig`
- `Gp_TLE92104_CalloutSetEcuPwmOutSig`

## Configuration Facts

- `GP_TLE92104_MCAL_EN`
- `GP_TLE92104_DET_EN`
- `GP_TLE92104_CORE0_ENABLE` to `GP_TLE92104_CORE5_ENABLE`
- `GP_TLE92104_CHIP_NUM_IN_COREx`
- `GP_TLE92104_SIG_NUM_IN_COREx`
- `GP_TLE92104_CHIP_INIT_TRY_NUM`
- `GP_TLE92104_CLR_FAULT_MODE_EN`
- `GP_TLE92104_CLR_FAULT_AUTOLY_EN`
- `GP_TLE92104_CFG_WD_EN`
- `GP_TLE92104_EN_CHIP_DELAY_US`
- `GP_TLE92104_FS_CHIP_DELAY_US`
- `GP_TLE92104_PWM_CLOCK_TICKS_PER_US`

## Design Constraints

- DET is enabled in the current configuration.
- Core1 and Core2 are active in the current configuration.
- Memory sections are organized by `Gp_TLE92104_MemMap.h`.
- Interface return values are `E_OK` or `E_NOT_OK`.
