# Gp_NCA95xx 需求-架构追溯矩阵

## 1. 说明

本文档提供 SRS 需求 ↔ 架构对象的双向追溯。正向：每条 SRS 需求 → 架构覆盖对象。反向：每个架构对象 → 来源 SRS 需求。

## 2. 正向追溯：SRS → Architecture

| SRS Requirement ID | Category | Architecture Coverage Object | Object Type | Coverage Status |
| --- | --- | --- | --- | --- |
| SRS-Gp_NCA95xx-FUNC-0001 | FUNC | DevState runtime state; Init/MainFunction | Runtime State + External API | Covered |
| SRS-Gp_NCA95xx-FUNC-0002 | FUNC | `Gp_NCA95xx_Init`; I2C Write callout; config data (DefaultDir/DefaultOut) | External API + Dependency + Config Data | Covered |
| SRS-Gp_NCA95xx-FUNC-0003 | FUNC | `Gp_NCA95xx_ResetChip` (conditional); WriteDio callout; DelayUs callout; `GP_NCA95xx_CFG_RESET_PIN_OWNED` | External API + Dependency + Config Macro | Covered |
| SRS-Gp_NCA95xx-FUNC-0004 | FUNC | `Gp_NCA95xx_Init` direction write; `Gp_NCA95xx_SetGpioDirSig` (conditional); `GP_NCA95xx_CFG_RUNTIME_DIR_CHANGE_ENABLE` | External API + Config Macro | Covered |
| SRS-Gp_NCA95xx-INTF-0001 | INTF | `Gp_NCA95xx_Init` | External API | Covered |
| SRS-Gp_NCA95xx-INTF-0002 | INTF | `Gp_NCA95xx_MainFunction` | External API | Covered |
| SRS-Gp_NCA95xx-INTF-0003 | INTF | `Gp_NCA95xx_GetGpioInSig` | External API | Covered |
| SRS-Gp_NCA95xx-INTF-0004 | INTF | `Gp_NCA95xx_SetGpioOutSig` | External API | Covered |
| SRS-Gp_NCA95xx-INTF-0005 | INTF | `Gp_NCA95xx_GetDevFaultSig` | External API | Covered |
| SRS-Gp_NCA95xx-INTF-0006 | INTF | `Gp_NCA95xx_GetDevModeInSig` | External API | Covered |
| SRS-Gp_NCA95xx-CFG-0001 | CFG | `MultiChipNum_u8` in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-CFG-0002 | CFG | `DevAddr_u8` per chip in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-CFG-0003 | CFG | `DefaultDir_u16` per chip in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-CFG-0004 | CFG | `DefaultOut_u16` per chip in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-CFG-0005 | CFG | `I2cChnId_u8`, `I2cSpeed_u32` per chip in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-CFG-0006 | CFG | `SigMapCfg[]` array in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-CFG-0007 | CFG | `IntEnable_b`, `IntDebounce_u8`, `PollPeriod_u16` per chip in config table | Config Data | Covered |
| SRS-Gp_NCA95xx-DIAG-0001 | DIAG | MainFunction NACK counting + Fault state transition; `Gp_NCA95xx_GetDevFaultSig` Bit0; fault threshold config data | Runtime Logic + External API + Config Data | Covered |
| SRS-Gp_NCA95xx-DIAG-0002 | DIAG | `GP_NCA95xx_CFG_DEV_ERROR_DETECT`; DET checks in all external API entry points | Config Macro + Runtime Logic | Covered |
| SRS-Gp_NCA95xx-DIAG-0003 | DIAG | Fault bit definitions in `Gp_NCA95xx_Types.h`; `Gp_NCA95xx_GetDevFaultSig` | Types + External API | Covered |
| SRS-Gp_NCA95xx-DIAG-0004 | DIAG | MainFunction INT polling + Input Port read + cache update; ReadDio callout | Runtime Logic + Dependency | Covered |
| SRS-Gp_NCA95xx-TIM-0001 | TIM | I2C speed constraint delegated to MCAL I2C config | Dependency | Covered |
| SRS-Gp_NCA95xx-TIM-0002 | TIM | ResetChip internal timing via DelayUs callout | Dependency | Covered |
| SRS-Gp_NCA95xx-TIM-0003 | TIM | ResetChip post-release delay via DelayUs callout | Dependency | Covered |
| SRS-Gp_NCA95xx-TIM-0004 | TIM | MainFunction polling period bounds response latency | Runtime Logic | Covered |
| SRS-Gp_NCA95xx-TIM-0005 | TIM | t_BUF constraint delegated to MCAL I2C driver | Dependency (declared) | Covered |
| SRS-Gp_NCA95xx-SAFE-0001 | SAFE | Output readback (SAFE-0002) + I2C fault detection (DIAG-0001) + config validation | Architecture-wide | Covered |
| SRS-Gp_NCA95xx-SAFE-0002 | SAFE | `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE`; MainFunction readback + retry logic; I2C Read callout | Config Macro + Runtime Logic + Dependency | Covered |
| SRS-Gp_NCA95xx-SAFE-0003 | SAFE | Fault state behavior in MainFunction (stop new I2C ops, retain output cache) | Runtime Logic | Covered |
| SRS-Gp_NCA95xx-CODE-0001 | CODE | MISRA-C compliance (build-time) | Process | Covered |
| SRS-Gp_NCA95xx-CODE-0002 | CODE | Naming applied across all identifiers | Naming Convention | Covered |
| SRS-Gp_NCA95xx-CODE-0003 | CODE | File list (Section 9 of architecture) | File Structure | Covered |
| SRS-Gp_NCA95xx-RES-0001 | RES | ROM/RAM budget; post-build link map analysis | Process | Covered |
| SRS-Gp_NCA95xx-RES-0002 | RES | I2C bus time budget; MainFunction time guard config | Config Data | Covered |
| SRS-Gp_NCA95xx-COMP-0001 | COMP | Each SRS requirement has source annotation | Process | Covered |
| SRS-Gp_NCA95xx-COMP-0002 | COMP | Each SRS requirement has verification method and acceptance criteria | Process | Covered |

## 3. 反向追溯：Architecture → SRS

### 3.1 外部接口

| Architecture Object | Source SRS Requirement(s) |
| --- | --- |
| `Gp_NCA95xx_Init` | FUNC-0001, FUNC-0002, FUNC-0004, INTF-0001, CFG-0003, CFG-0004 |
| `Gp_NCA95xx_MainFunction` | FUNC-0001, INTF-0002, DIAG-0001, DIAG-0004, SAFE-0002, SAFE-0003, TIM-0004 |
| `Gp_NCA95xx_GetGpioInSig` | INTF-0003 |
| `Gp_NCA95xx_SetGpioOutSig` | INTF-0004, SAFE-0002 |
| `Gp_NCA95xx_GetDevFaultSig` | INTF-0005, DIAG-0001, DIAG-0003 |
| `Gp_NCA95xx_GetDevModeInSig` | INTF-0006, FUNC-0001 |
| `Gp_NCA95xx_ResetChip` (conditional) | FUNC-0003, TIM-0002, TIM-0003 |

### 3.2 配置宏参

| Architecture Object | Source SRS Requirement(s) |
| --- | --- |
| `GP_NCA95xx_CFG_DEV_ERROR_DETECT` | DIAG-0002 |
| `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE` | SAFE-0002 |
| `GP_NCA95xx_CFG_RUNTIME_DIR_CHANGE_ENABLE` | FUNC-0004 |
| `GP_NCA95xx_CFG_RESET_PIN_OWNED` | FUNC-0003 |
| `GP_NCA95xx_CFG_SW_MAJOR_VERSION` | Standard FC convention |
| `GP_NCA95xx_CFG_SW_MINOR_VERSION` | Standard FC convention |

### 3.3 依赖接口

| Architecture Object | Source SRS Requirement(s) |
| --- | --- |
| `Gp_NCA95xx_CalloutI2cWrite` | FUNC-0002, INTF-0001, INTF-0004, FUNC-0004 |
| `Gp_NCA95xx_CalloutI2cRead` | INTF-0002, SAFE-0002, DIAG-0001 |
| `Gp_NCA95xx_CalloutReadDio` (conditional) | INTF-0002, CFG-0007 |
| `Gp_NCA95xx_CalloutWriteDio` (conditional) | FUNC-0003 |
| `Gp_NCA95xx_CalloutGetCoreId` | CFG-0006 |
| `Gp_NCA95xx_CalloutDelayUs` (conditional) | TIM-0002, TIM-0003 |

### 3.4 运行态

| Architecture Object | Source SRS Requirement(s) |
| --- | --- |
| DevState per chip | FUNC-0001, SAFE-0003 |
| Input/Output/Direction/Polarity caches | FUNC-0002, INTF-0003, INTF-0004, FUNC-0004 |
| Fault status bitmask | DIAG-0001, DIAG-0003, INTF-0005 |
| NACK/ACK counters | DIAG-0001 |
| INT debounce counter | CFG-0007 |
| Readback retry counters | SAFE-0002 |
| DET error flags | DIAG-0002 |

### 3.5 文件载体

| Architecture Object | Source SRS Requirement(s) |
| --- | --- |
| `Gp_NCA95xx.c` / `.h` | CODE-0003, all INTF requirements |
| `Gp_NCA95xx_Types.h` | CODE-0002, CODE-0003, DIAG-0003 |
| `Gp_NCA95xx_Cfg.h` | CODE-0003, CFG-0001 through CFG-0007 |
| `Gp_NCA95xx_Cfg.c` / `CfgData.h` | CODE-0003, all CFG requirements |
| `Gp_NCA95xx_Reg.h` | CFG-0002 (I2C device address constants), register definitions |
| `Gp_NCA95xx_Callout.h` / `.c` | CODE-0003, dependency abstraction |
| `Gp_NCA95xx_MemMap.h` | CODE-0003, RES-0001 |

## 4. 未覆盖项

无。全部 35 条 SRS 需求均有对应的架构覆盖对象。

## 5. 待确认项影响的可追溯性

| Pending Risk | Affected SRS Requirements | Affected Architecture Objects |
| --- | --- | --- |
| R1 (INT pin ownership) | CFG-0007, DIAG-0004 | ReadDio callout status (Formal ↔ Conditional) |
| R2 (RESET pin ownership) | FUNC-0003, TIM-0002, TIM-0003 | ResetChip API, WriteDio/DelayUs callout status |
| R3 (notification mechanism) | DIAG-0004 | Potential new callback/callout |
| R4 (runtime dir change) | FUNC-0004 | SetGpioDirSig API, CFG_RUNTIME_DIR_CHANGE_ENABLE |
| R5 (fault recovery strategy) | DIAG-0001 | MainFunction recovery logic detail |
| R6 (multi-core config) | CFG-0001, CFG-0006 | CONST section (GLOBAL ↔ COREx) |
| R7 (resource budget) | RES-0001, RES-0002 | Post-build verification |
