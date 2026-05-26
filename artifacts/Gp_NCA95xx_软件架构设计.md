# Gp_NCA95xx FC 软件架构

## 1. FC总结介绍

- 架构版本: `V1`
- 架构状态: `Released`
- 输出模式: `Released`
- 生成时间: 2026-05-26
- 变更点总结: 初版生成，基于 Gp_NCA95xx SRS V0.1.0 生成完整 IoExtDev 架构。全部风险项已评审通过，发布为 V1 Released。
- FC名称: `Gp_NCA95xx`
- FC功能介绍: Gp_NCA95xx 模块是 NCA9539-Q1 车规级 16 位 I2C GPIO 扩展器的 IoExtDev 层驱动，通过 I2C 总线为 MCU 提供额外 16 路 GPIO 控制能力。模块负责芯片实例的初始化（寄存器默认值回写）、周期性输入状态刷新与中断轮询、通过 uint16 信号 ID 提供 GPIO 输入读取和输出设置接口、芯片故障检测与诊断上报、以及可选的硬件复位控制。驱动支持最多 4 片同总线芯片实例，每引脚独立方向配置，并满足 ASIL_B 安全完整性要求。
- 应用场景: 适用于 MCU 自身 GPIO 资源不足、需要通过 I2C 总线扩展额外数字 I/O 的汽车电子控制单元场景。典型应用包括车身域控制器中多达 4 片 NCA9539-Q1 的联合部署，提供最多 64 路额外 GPIO 供上层 ASW 通过信号 ID 解耦访问。
- 架构设计思路: 采用信号 ID 解耦模式，上层 ASW 通过 uint16 Id 访问 GPIO，驱动内部通过 SigMapCfg 映射解析 CoreId + ChipIdx + PinIdx。外部接口均为函数式语义 API（Get/Set/GetDevFault/GetDevMode），不暴露全局变量。I2C 通信通过 Callout 抽象，不直接依赖 MCAL I2C 驱动。DIO 操作（INT 引脚采样、RESET 引脚控制）通过 Callout 适配。芯片寄存器地址和位定义收敛于 Gp_NCA95xx_Reg.h。MainFunction 承担周期性输入刷新、I2C 通信连续性检测、设备状态机推进和 pending 输出处理。安全机制包括输出回读校验（Readback）和安全状态定义（Fault 时停止新输出操作）。
- AUTOSAR架构层级: `IoExtDev`
- 当前软件架构所处层级: `IoExtDev`

---

## 2. 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| SRS-Gp_NCA95xx-FUNC-0001 | 设备状态机管理（Unknown→Init→Normal→Fault） | Internal runtime state: DevState per chip; `Init` triggers Unknown→Init; `MainFunction` drives remaining transitions. | Covered | Fault threshold/recovery threshold as config data. |
| SRS-Gp_NCA95xx-FUNC-0002 | 上电初始化与默认状态恢复 | `Gp_NCA95xx_Init` writes Configuration/Output/Polarity registers via I2C callout; runtime direction/output/polarity cache initialized. | Covered | I2C write failure → Fault per chip instance. |
| SRS-Gp_NCA95xx-FUNC-0003 | 硬件复位控制（条件接口） | Conditional external API `Gp_NCA95xx_ResetChip`; runtime container reset logic; DIO Write callout for RESET pin. | Covered | Conditional on `GP_NCA95xx_CFG_RESET_PIN_OWNED`. |
| SRS-Gp_NCA95xx-FUNC-0004 | I/O 方向配置 | Init writes Configuration Register per config; optional runtime direction change via `Gp_NCA95xx_SetGpioDirSig` (conditional). | Partially Covered | Runtime direction change interface not in SRS INTF list; added as conditional. |
| SRS-Gp_NCA95xx-INTF-0001 | Init 接口 | `void Gp_NCA95xx_Init(void)` | Covered | External API section. |
| SRS-Gp_NCA95xx-INTF-0002 | MainFunction 接口 | `void Gp_NCA95xx_MainFunction(void)` | Covered | External API section. |
| SRS-Gp_NCA95xx-INTF-0003 | GPIO 输入读取接口 | `Std_ReturnType Gp_NCA95xx_GetGpioInSig(uint16 Id_u16, uint8* State_pu8)` | Covered | External API section. |
| SRS-Gp_NCA95xx-INTF-0004 | GPIO 输出设置接口 | `Std_ReturnType Gp_NCA95xx_SetGpioOutSig(uint16 Id_u16, uint8 State_u8)` | Covered | External API section. |
| SRS-Gp_NCA95xx-INTF-0005 | 设备故障读取接口 | `Std_ReturnType Gp_NCA95xx_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` | Covered | External API section. |
| SRS-Gp_NCA95xx-INTF-0006 | 设备模式读取接口 | `Std_ReturnType Gp_NCA95xx_GetDevModeInSig(uint16 Id_u16, uint8* DevMode_pu8)` | Covered | External API section. |
| SRS-Gp_NCA95xx-CFG-0001 | 芯片实例数量配置 | Config data: `MultiChipNum_u8` in `Gp_NCA95xx_CfgData.h`. | Covered | Per-core configuration table. |
| SRS-Gp_NCA95xx-CFG-0002 | I2C 设备地址配置 | Config data: `DevAddr_u8` per chip in config table. | Covered | Valid values 0x74-0x77. |
| SRS-Gp_NCA95xx-CFG-0003 | 默认 I/O 方向配置 | Config data: `DefaultDir_u16` per chip; used in Init register write. | Covered | Configuration table in CfgData. |
| SRS-Gp_NCA95xx-CFG-0004 | 默认输出电平配置 | Config data: `DefaultOut_u16` per chip; used in Init register write. | Covered | Configuration table in CfgData. |
| SRS-Gp_NCA95xx-CFG-0005 | I2C 通道配置 | Config data: `I2cChnId_u8` and `I2cSpeed_u32` per chip. | Covered | Configuration table in CfgData. |
| SRS-Gp_NCA95xx-CFG-0006 | 信号 ID 映射配置 | Config data: `SigMapCfg[]` array in `Gp_NCA95xx_CfgData.h`. | Covered | Maps uint16 Id → CoreId + ChipIdx + PinIdx. |
| SRS-Gp_NCA95xx-CFG-0007 | 中断与轮询配置 | Config data: `IntEnable_b`, `IntDebounce_u8`, `PollPeriod_u16` per chip. | Covered | Configuration table in CfgData. |
| SRS-Gp_NCA95xx-DIAG-0001 | I2C 通信错误检测 | `MainFunction` NACK counting logic; `Gp_NCA95xx_GetDevFaultSig` fault code Bit0; config data for thresholds. | Covered | Fault confirm/recovery threshold as config data. |
| SRS-Gp_NCA95xx-DIAG-0002 | 开发错误检测（DET） | DET checks in every external API; controlled by `GP_NCA95xx_CFG_DEV_ERROR_DETECT`. | Covered | NULL pointer, invalid Id, invalid State, uninit access. |
| SRS-Gp_NCA95xx-DIAG-0003 | 故障码编码 | `Gp_NCA95xx_GetDevFaultSig` returns 32-bit fault mask; bit definitions in `Gp_NCA95xx_Types.h`. | Covered | Bit0-Bit3 defined; Bit4-31 reserved. |
| SRS-Gp_NCA95xx-DIAG-0004 | 中断状态变化报告 | `MainFunction` INT pin polling → Input Port register read → cache update. | Covered | Upper notification mechanism → risk item. |
| SRS-Gp_NCA95xx-TIM-0001 | I2C Fast-mode 操作速率 | I2C speed ≤ 400 kHz; responsibility delegated to MCAL I2C config and callout implementation. | Covered | SRS declares dependency on MCAL I2C guarantee. |
| SRS-Gp_NCA95xx-TIM-0002 | RESET 脉冲宽度 ≥ 6 ns | `Gp_NCA95xx_ResetChip` internal timing logic via DIO Write callout + delay. | Covered | Delay mechanism → conditional callout. |
| SRS-Gp_NCA95xx-TIM-0003 | RESET 恢复时间 ≥ 200 ns | `Gp_NCA95xx_ResetChip` post-release delay before re-init. | Covered | Delay callout or busy-wait. |
| SRS-Gp_NCA95xx-TIM-0004 | 中断有效响应时间 | `MainFunction` polling cycle ≤ MainFunction period. | Covered | Response latency bounded by MainFunction period. |
| SRS-Gp_NCA95xx-TIM-0005 | I2C 总线空闲等待 ≥ 1.3 μs | Responsibility delegated to MCAL I2C driver; SRS declares dependency. | Covered | No FC-level implementation needed. |
| SRS-Gp_NCA95xx-SAFE-0001 | ASIL_B 安全完整性 | Output readback (SAFE-0002), I2C fault detection (DIAG-0001), config validation. | Covered | Safety mechanisms in architecture. |
| SRS-Gp_NCA95xx-SAFE-0002 | 输出回读校验 | `MainFunction` post-write Output Register readback; retry logic (max 2 retries, 3 attempts total); config macro `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE`. | Covered | Internal consistency-check feature, not external API. |
| SRS-Gp_NCA95xx-SAFE-0003 | 安全状态定义 | Fault state → stop new I2C output ops; retain last output cache; require ResetChip or re-Init to exit. | Covered | Runtime behavior in MainFunction. |
| SRS-Gp_NCA95xx-CODE-0001 | MISRA-C 编码规范 | Build-time static analysis; not an architecture object. | Covered | Inspection-level requirement. |
| SRS-Gp_NCA95xx-CODE-0002 | 命名规范 | Applied throughout all external APIs, types, macros, and files in this architecture. | Covered | Verified in interface/type/file naming. |
| SRS-Gp_NCA95xx-CODE-0003 | 文件结构规范 | File list section defines all standard carriers. | Covered | See Section 9. |
| SRS-Gp_NCA95xx-RES-0001 | 内存资源约束 | ROM < 2 KB, RAM < 256 B + N×64 B; verified post-build from link map. | Covered | Analysis-level; noted in risk table. |
| SRS-Gp_NCA95xx-RES-0002 | I2C 总线利用率 | Single MainFunction I2C total time ≤ 1 ms configurable. | Covered | Analysis-level; config data for time budget. |
| SRS-Gp_NCA95xx-COMP-0001 | 需求来源追溯 | Each requirement in SRS carries source; architecture coverage maps back to SRS IDs. | Covered | This coverage table. |
| SRS-Gp_NCA95xx-COMP-0002 | 需求验证追溯 | Verification methods and acceptance criteria defined in SRS; architecture provides the implementation basis. | Covered | Process-level requirement. |

---

## 3. 外部接口设计

### 3.1 `Gp_NCA95xx_Init`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95xx_Init(void)` | Initializes all configured chip instances on the current core: loads configuration data, writes Configuration, Output, and Polarity Inversion registers to default values via I2C, and sets each chip device state to Init. If any chip fails I2C write, that chip is marked Fault while remaining chips continue initialization. | Synchronous | Non-reentrant | `void` | Must be called once during ECU startup after MCAL I2C driver is ready and configuration data is loaded. Must be called before any other Gp_NCA95xx API. |

### 3.2 `Gp_NCA95xx_MainFunction`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95xx_MainFunction(void)` | Periodic processing function. Detects INT pin state (or performs full Input Port polling if INT is unavailable), refreshes input state cache when changes are detected, monitors I2C communication continuity and updates device state (Init→Normal, Normal→Fault, Fault→Normal), processes pending output refresh operations, and executes output readback verification for safety-critical pins. | Synchronous | Non-reentrant | `void` | Must be called periodically after Init at the configured MainFunction period (recommended 1-10 ms). Must not be called before Init. |

### 3.3 `Gp_NCA95xx_GetGpioInSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_GetGpioInSig(uint16 Id_u16, uint8* State_pu8)` | Reads the current input state of a GPIO pin identified by the signal ID. Returns the logic level (0 or 1) after applying polarity inversion as configured. Reads from the cached input state maintained by MainFunction. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, chip is in Fault or Unknown state, or State_pu8 is NULL | Id_u16 must map to a configured signal. State_pu8 must be non-NULL. Chip instance must be initialized and not in Unknown state. DET is reported for NULL pointer or invalid Id. |

### 3.4 `Gp_NCA95xx_SetGpioOutSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_SetGpioOutSig(uint16 Id_u16, uint8 State_u8)` | Sets the output level of a GPIO pin identified by the signal ID. Updates the output cache and triggers an I2C write to the Output Port register. If the pin direction is input, returns E_NOT_OK. If I2C write fails, marks the chip Fault. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, State_u8 is not 0 or 1, pin direction is input, chip is Fault/Unknown, or I2C write fails | Id_u16 must map to a configured signal. State_u8 must be 0 or 1. Target pin must be configured as output. Chip must be in Normal state. DET is reported for invalid Id or illegal State_u8 value. |

### 3.5 `Gp_NCA95xx_GetDevFaultSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` | Returns the current fault status bitmask for the chip instance identified by the signal ID. Fault bits: Bit0=I2C communication error, Bit1=uninitialized, Bit2=invalid parameter history, Bit3=configuration error, Bit4-31=reserved. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid or Fault_pu32 is NULL | Id_u16 must map to a configured chip instance. Fault_pu32 must be non-NULL. DET is reported for NULL pointer or invalid Id. |

### 3.6 `Gp_NCA95xx_GetDevModeInSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_GetDevModeInSig(uint16 Id_u16, uint8* DevMode_pu8)` | Returns the current device state of the chip instance identified by the signal ID: 0x00=Unknown, 0x11=Init, 0x21=Normal, 0x71=Fault. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid or DevMode_pu8 is NULL | Id_u16 must map to a configured chip instance. DevMode_pu8 must be non-NULL. DET is reported for NULL pointer or invalid Id. |

---

## 4. 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `GP_NCA95xx_CFG_DEV_ERROR_DETECT` | Global feature switch for Development Error Detection. Controls NULL pointer checks, invalid Id detection, illegal State value detection, and uninitialized access detection in all external APIs. | Macro | `STD_ON` | SRS-Gp_NCA95xx-DIAG-0002 | `Gp_NCA95xx_Cfg.h`; all external API entry points in `Gp_NCA95xx.c`. | `Formal` |
| `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE` | Enables output register readback verification after SetGpioOutSig for safety-critical output pins. When enabled, MainFunction reads back the Output Register and compares against the expected value, retrying up to 2 times on mismatch. | Macro | `STD_ON` | SRS-Gp_NCA95xx-SAFE-0002 | `Gp_NCA95xx_Cfg.h`; `Gp_NCA95xx_MainFunction` readback logic in `Gp_NCA95xx.c`. | `Formal` |
| `GP_NCA95xx_CFG_RUNTIME_DIR_CHANGE_ENABLE` | Enables runtime I/O direction change via `Gp_NCA95xx_SetGpioDirSig`. When disabled (default), direction is set only during Init and cannot be changed at runtime. | Macro | `STD_OFF` | SRS-Gp_NCA95xx-FUNC-0004, SRS-Gp_NCA95xx-CFG-0003 | `Gp_NCA95xx_Cfg.h`; `Gp_NCA95xx_SetGpioDirSig` compile guard in `Gp_NCA95xx.c`. | `Formal` |
| `GP_NCA95xx_CFG_RESET_PIN_OWNED` | Indicates whether the RESET pin is connected to an MCU GPIO controlled by this FC. When enabled, `Gp_NCA95xx_ResetChip` external API and RESET-related DIO Write callout are compiled in. | Macro | `STD_OFF` | SRS-Gp_NCA95xx-FUNC-0003 | `Gp_NCA95xx_Cfg.h`; `Gp_NCA95xx_ResetChip` compile guard in `Gp_NCA95xx.c`. | `Conditional` |
| `GP_NCA95xx_CFG_SW_MAJOR_VERSION` | Software major version number. | Macro | `0` | Standard FC metadata convention. | `Gp_NCA95xx_Cfg.h`; version reporting. | `Formal` |
| `GP_NCA95xx_CFG_SW_MINOR_VERSION` | Software minor version number. | Macro | `1` | Standard FC metadata convention. | `Gp_NCA95xx_Cfg.h`; version reporting. | `Formal` |

---

## 5. 全局变量与运行态策略

状态：`Empty`

架构不允许对外提供全局变量输出。所有状态通过函数接口访问（GetDevFaultSig、GetDevModeInSig）。

内部运行态策略：

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Per-chip device state (DevState: Unknown/Init/Normal/Fault) | `Gp_NCA95xx.c` internal container. | Written by `Init` and `MainFunction`; read by `GetDevModeInSig` and `GetDevFaultSig`. | Set to Unknown on power-up; Init → Init state; MainFunction → Normal or Fault. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership; no cross-core sharing. |
| Per-chip input state cache (16-bit per chip) | `Gp_NCA95xx.c` internal container. | Written by `MainFunction` after I2C Input Port read; read by `GetGpioInSig`. | Initialized to 0xFFFF in `Init`; refreshed each MainFunction cycle. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |
| Per-chip output state cache (16-bit per chip) | `Gp_NCA95xx.c` internal container. | Written by `SetGpioOutSig` (request) and `Init` (default); read by `MainFunction` for I2C write and readback verify. | Initialized from `DefaultOut_u16` in `Init`; updated on SetGpioOutSig calls. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership; SetGpioOutSig caller and MainFunction share same core. |
| Per-chip direction cache (16-bit per chip) | `Gp_NCA95xx.c` internal container. | Written by `Init` and optional `SetGpioDirSig`; read by `SetGpioOutSig` for direction validation. | Initialized from `DefaultDir_u16` in `Init`. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |
| Per-chip polarity cache (16-bit per chip) | `Gp_NCA95xx.c` internal container. | Written by `Init`; read by `GetGpioInSig` for polarity inversion. | Initialized from config in `Init`. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |
| Per-chip fault status (32-bit bitmask) | `Gp_NCA95xx.c` internal container. | Written by `MainFunction` and external APIs on error; read by `GetDevFaultSig`. | Initialized to 0 in `Init`; bits set/cleared during runtime. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |
| Per-chip I2C NACK/ACK counters | `Gp_NCA95xx.c` internal container. | Written and read by `MainFunction` during I2C communication continuity check. | Reset to 0 in `Init`; incremented/reset each MainFunction cycle. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |
| Per-chip INT debounce counter | `Gp_NCA95xx.c` internal container. | Written and read by `MainFunction` during INT pin polling. | Reset to 0 in `Init`. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |
| DET error flags | `Gp_NCA95xx.c` internal container. | Written by external API entry points on parameter error; read internally. | Reset to 0 in `Init`. | Runtime RAM (`CLEAR_FAR_DATA_ALIGN4_COREx`) | Per-core ownership. |

---

## 6. 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | External API implementations (`Init`, `MainFunction`, `GetGpioInSig`, `SetGpioOutSig`, `GetDevFaultSig`, `GetDevModeInSig`, `ResetChip`), internal static helper functions (Id parsing, register read/write helpers, state machine logic, I2C communication logic, readback verification). | `GP_NCA95xx_CODE_START` | `GP_NCA95xx_CODE_STOP` | `Gp_NCA95xx.c`, `Gp_NCA95xx_Callout.c` | Standard code section. |
| RUNTIME RAM | Per-core runtime state container (device state, input/output/direction/polarity caches, fault status, NACK/ACK counters, debounce counters, DET flags, readback retry counters per chip instance). | `GP_NCA95xx_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA95xx_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_NCA95xx.c` | Default CLEAR_FAR_DATA for startup initialization safety. `COREx` represents per-core homogeneous sections (e.g., `CORE0`-`CORE5`). |
| CONST | Shared configuration constants: global macro values, register bit definitions from `Gp_NCA95xx_Reg.h`, shared mapping table type definitions. | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `Gp_NCA95xx_Cfg.c` | Global const data shared across cores. |
| CONST PER-CORE | Per-core configuration tables: `SigMapCfg[]` array, per-chip config data (`DevAddr_u8`, `DefaultDir_u16`, `DefaultOut_u16`, `I2cChnId_u8`, `I2cSpeed_u32`, `IntEnable_b`, `IntDebounce_u8`, `PollPeriod_u16`), fault threshold constants (`FaultConfirmThreshold`, `FaultRecoveryThreshold`). | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_NCA95xx_Cfg.c`, `Gp_NCA95xx_CfgData.h` | Each core owns its chip instances; per-core const data reflects core-local configuration. |
| CALIB | 当前无确认的全局标定参数。 | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_CALI_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_CALI_STOP` | `Gp_NCA95xx_Cali.c` (optional) | 仅在后续确认标定参数后产生实际内容。当前保留段宏定义以备扩展。 |

---

## 7. 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。 | `Empty` |

---

## 8. 依赖接口设计

### 8.1 `Gp_NCA95xx_CalloutI2cWrite`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutI2cWrite(uint16 Id_u16, const uint8* Data_pcu8, uint16 Size_u16)` | Writes Size_u16 bytes to the I2C device identified by Id_u16. Data_pcu8 contains the complete I2C payload (register address + data bytes). The callout implementation handles I2C device addressing, START/STOP generation, and ACK/NACK checking. | Synchronous | Reentrant | `E_OK` on successful I2C write with ACK; `E_NOT_OK` on NACK or communication failure. | Data_pcu8 must be non-NULL. Size_u16 must be > 0 and ≤ max I2C payload. Id_u16 must map to a configured chip instance. | Project Adaptation (MCAL I2C driver binding) | SRS-Gp_NCA95xx-FUNC-0002 (Init register write), SRS-Gp_NCA95xx-INTF-0004 (SetGpioOutSig I2C write), SRS-Gp_NCA95xx-FUNC-0004 (direction config write). | `Formal` |

### 8.2 `Gp_NCA95xx_CalloutI2cRead`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutI2cRead(uint16 Id_u16, uint8 RegAddr_u8, uint8* Data_pu8, uint16 Size_u16)` | Reads Size_u16 bytes from register RegAddr_u8 of the I2C device identified by Id_u16. The callout implementation performs the I2C write (register address) then I2C read (data) sequence, handling repeated START or STOP-START as needed. | Synchronous | Reentrant | `E_OK` on successful I2C read with ACK; `E_NOT_OK` on NACK or communication failure. | Data_pu8 must be non-NULL. Size_u16 must be > 0. Id_u16 must map to a configured chip instance. RegAddr_u8 must be a valid NCA9539-Q1 register address. | Project Adaptation (MCAL I2C driver binding) | SRS-Gp_NCA95xx-INTF-0002 (MainFunction Input Port read), SRS-Gp_NCA95xx-SAFE-0002 (readback read), SRS-Gp_NCA95xx-FUNC-0001 (state check read). | `Formal` |

### 8.3 `Gp_NCA95xx_CalloutReadDio`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutReadDio(uint16 Id_u16, uint8* State_pu8)` | Reads the logic level of the DIO pin identified by Id_u16, used for INT pin state sampling in MainFunction. Returns 0 for low level, 1 for high level. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid or State_pu8 is NULL. | State_pu8 must be non-NULL. Id_u16 must map to a configured INT pin DIO channel. | IoMcu / Project Adaptation (DIO driver binding) | SRS-Gp_NCA95xx-INTF-0002 (INT pin polling), SRS-Gp_NCA95xx-CFG-0007 (interrupt detection). | `Conditional` |

### 8.4 `Gp_NCA95xx_CalloutWriteDio`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutWriteDio(uint16 Id_u16, uint8 State_u8)` | Sets the logic level of the DIO pin identified by Id_u16, used for RESET pin control in ResetChip. State_u8 = 0 drives the pin low; State_u8 = 1 drives the pin high. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid or State_u8 is not 0 or 1. | State_u8 must be 0 or 1. Id_u16 must map to a configured RESET pin DIO channel. | IoMcu / Project Adaptation (DIO driver binding) | SRS-Gp_NCA95xx-FUNC-0003 (hardware reset control). | `Conditional` |

### 8.5 `Gp_NCA95xx_CalloutGetCoreId`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `uint32 Gp_NCA95xx_CalloutGetCoreId(void)` | Returns the current core ID. Used for SigMapCfg lookup to filter signal mappings belonging to the calling core. | Synchronous | Reentrant | Core ID value (platform-dependent range). | Must be callable at any time after platform startup. | MCAL / Platform Adaptation | SRS-Gp_NCA95xx-CFG-0006 (signal ID mapping per core). | `Formal` |

### 8.6 `Gp_NCA95xx_CalloutDelayUs`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95xx_CalloutDelayUs(uint32 DelayUs_u32)` | Provides a blocking microsecond-level delay. Used in ResetChip for RESET pulse width (≥ 6 ns) and reset recovery time (≥ 200 ns) timing enforcement. | Synchronous | Non-reentrant | `void` | DelayUs_u32 should support microsecond resolution. Used only in ResetChip path (conditional). | MCAL / Platform Adaptation | SRS-Gp_NCA95xx-TIM-0002, SRS-Gp_NCA95xx-TIM-0003. | `Conditional` |

---

## 9. 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `Gp_NCA95xx.c` | Required | 模块主实现文件。 | 外部接口实现（Init、MainFunction、GetGpioInSig、SetGpioOutSig、GetDevFaultSig、GetDevModeInSig、ResetChip）、内部静态函数（Id 解析、寄存器读写辅助、状态机逻辑、I2C 通信逻辑、回读校验）、运行态容器访问。 |
| `Gp_NCA95xx.h` | Required | 对外接口头文件。 | 外部 API 原型声明、CODE_START/CODE_STOP 段宏。 |
| `Gp_NCA95xx_Types.h` | Required | 类型定义头文件。 | 设备状态枚举（Unknown/Init/Normal/Fault）、故障码位掩码定义（Bit0-Bit3）、芯片配置容器类型、信号映射类型、运行态容器类型。 |
| `Gp_NCA95xx_Cfg.h` | Required | 配置宏头文件。 | 全局功能开关（DEV_ERROR_DETECT、REG_READBACK_VERIFY_ENABLE、RUNTIME_DIR_CHANGE_ENABLE、RESET_PIN_OWNED）、软件版本宏。 |
| `Gp_NCA95xx_Cfg.c` | Required | 配置数据实现文件。 | 每核配置常量定义：SigMapCfg 映射表、芯片配置表（DevAddr、DefaultDir、DefaultOut、I2cChnId、I2cSpeed）、中断/轮询配置、故障阈值常量。 |
| `Gp_NCA95xx_CfgData.h` | Required | 配置数据声明头文件。 | 配置表类型声明、extern 配置数据声明、MultiChipNum 声明。 |
| `Gp_NCA95xx_Reg.h` | Required | 外设寄存器定义头文件。 | NCA9539-Q1 寄存器地址（Input Port 0/1、Output Port 0/1、Polarity Inversion 0/1、Configuration 0/1）、寄存器默认值常量、I2C 设备地址常量（0x74-0x77）。 |
| `Gp_NCA95xx_Callout.h` | Required | 平台适配接口头文件。 | Callout 原型声明（I2cWrite、I2cRead、ReadDio、WriteDio、GetCoreId、DelayUs）。 |
| `Gp_NCA95xx_Callout.c` | Required | 平台适配实现/stub 文件。 | Callout 适配实现框架或集成 stub；项目在集成阶段填充 MCAL DIO/I2C 绑定和平台代码。 |
| `Gp_NCA95xx_MemMap.h` | Required | 内存段映射头文件。 | 模块所有 MemMap 宏映射（CODE、CLEAR_FAR_DATA_COREx、CONST_GLOBAL、CONST_COREx、CALI）。 |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `Gp_NCA95xx_Reg.h` | `Std_Types.h` (external) | 外设寄存器地址、位定义和协议常量依赖标准整数类型 uint8/uint16/uint32；`Std_Types.h` 不由本 FC 创建。 |
| `Gp_NCA95xx_Cfg.h` | `Std_Types.h` (external) | 引用 `STD_ON`/`STD_OFF` 等 AUTOSAR 标准宏和 `uint8`/`uint16`/`uint32` 类型；`Std_Types.h` 不由本 FC 创建。 |
| `Gp_NCA95xx_Cfg.h` | `Gp_NCA95xx_Reg.h` | 配置宏（如 REG_READBACK_VERIFY_ENABLE）和默认值可能引用寄存器符号。 |
| `Gp_NCA95xx_Types.h` | `Gp_NCA95xx_Cfg.h` | 类型定义依赖配置宏开关（如 RESET_PIN_OWNED 控制 ResetChip 相关类型）和标准类型。 |
| `Gp_NCA95xx_Callout.h` | `Gp_NCA95xx_Types.h` | Callout 原型引用 FC 公开类型和设备状态枚举。 |
| `Gp_NCA95xx_CfgData.h` | `Gp_NCA95xx_Types.h` | 声明配置数据类型和 extern 配置对象。 |
| `Gp_NCA95xx.h` | `Gp_NCA95xx_CfgData.h` | 暴露正式外部 API，通过 CfgData 间接获得公开类型和配置数据声明。 |
| `Gp_NCA95xx.c` | `Gp_NCA95xx.h` | 实现对外接口，获取 API 原型声明。 |
| `Gp_NCA95xx.c` | `Gp_NCA95xx_Callout.h` | 通过 Callout 访问 I2C 通信、DIO 操作、CoreId 和 Delay 依赖。 |
| `Gp_NCA95xx.c` | `Gp_NCA95xx_MemMap.h` | 在 CODE 和 RUNTIME RAM 段边界处包含，放置代码和运行态数据。 |
| `Gp_NCA95xx_Cfg.c` | `Gp_NCA95xx_CfgData.h` | 定义配置表和项目数据常量。 |
| `Gp_NCA95xx_Cfg.c` | `Gp_NCA95xx_MemMap.h` | 在 CONST 段边界处包含，放置配置常量。 |
| `Gp_NCA95xx_Callout.c` | `Gp_NCA95xx_Callout.h` | 实现或承载 Callout 适配 stub。 |
| `Gp_NCA95xx_Callout.c` | `Gp_NCA95xx_MemMap.h` | 在 CODE 段边界处包含，放置适配代码。 |

---

## 10. 架构风险与待确认

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | INT 引脚归属确认 | INT 引脚是否接入 MCU GPIO 并由本驱动采样尚未确认。若不接入，MainFunction 降级为周期全量轮询 Input Port 寄存器（已按 SRS 支持降级）。 | 影响 MainFunction 输入刷新策略：INT 触发模式 vs 全量轮询模式。中断响应延迟和 I2C 总线利用率不同。 | 确认硬件原理图中 INT 引脚的连接方式，填入 CFG-0007 的 IntEnable_b 配置。若 INT 未接入，ReadDio callout 改为 Conditional。 | | `已评审` |
| R2 | RESET 引脚归属确认 | RESET 引脚是否接入 MCU GPIO 且归属于本驱动尚未确认。若不归属，Gp_NCA95xx_ResetChip 外部接口和 WriteDio/DelayUs callout 不适用。 | 影响外部接口集：ResetChip 接口和两个 Conditional callout 是否编译。 | 确认硬件原理图中 RESET 引脚的连接方式。若不归属本驱动，将 GP_NCA95xx_CFG_RESET_PIN_OWNED 设为 STD_OFF 并移除 ResetChip 接口。 | | `已评审` |
| R3 | 上层输入变化通知机制 | SRS DIAG-0004 要求"通过 GetDevFaultSig 的可选状态位或独立回调通知上层"，具体机制未定。当前架构仅实现缓存更新，未定义主动通知方式。 | 上层 ASW 若依赖主动通知（回调/事件），当前架构不满足；若上层自行周期轮询 GetGpioInSig，则已满足。 | 确认是否需要回调通知机制。若需要，增加 Callout/回调接口设计。若不需要，DIAG-0004 的范围边界标注已满足。 | | `已评审` |
| R4 | 运行时方向变更接口 | SRS FUNC-0004 提及运行时 SetGpioDirSig 调用，但 SRS INTF 章节未定义该接口的原型和需求 ID。当前架构将其作为 Conditional 外部接口，由 GP_NCA95xx_CFG_RUNTIME_DIR_CHANGE_ENABLE 控制。 | 若项目需要运行时方向变更，需补充正式的 INTF 需求和接口原型；若不需要，宏默认 STD_OFF 即可。 | 确认项目是否需要运行时方向变更功能。若不需要，当前架构已满足。若需要，补充接口原型到 SRS 和架构。 | | `已评审` |
| R5 | I2C 通信故障恢复策略细节 | SRS DIAG-0001 定义了故障确认阈值（默认 3）和恢复阈值（默认 2），但恢复后的动作（仅清除 Fault 状态 vs 重新初始化芯片寄存器）未明确。当前架构在 Fault→Normal 转换后不清除已有输出缓存。 | 若恢复后需要重新回写寄存器，MainFunction 的恢复逻辑需要额外步骤。 | 确认恢复策略：Fault→Normal 后是否需要重新回写所有配置寄存器。当前默认仅清除故障状态，保留输出缓存不变。 | | `已评审` |
| R6 | 多核配置数据归属 | 每个核的芯片实例和 SigMapCfg 是否需要独立配置，或者部分芯片实例可跨核共享访问，尚未确认。当前架构采用每核独立 CONST 段和每核运行态容器。 | 若配置数据跨核共享，CONST 段从 COREx 改为 GLOBAL；若运行态跨核访问，需增加并发保护。 | 确认多核部署方案：每核独立芯片实例 vs 跨核共享。当前默认每核独立。 | | `已评审` |
| R7 | 内存资源预算确认 | SRS RES-0001 定义典型预算 ROM < 2 KB, RAM < 256 B + N×64 B。实际消耗需从 link map 提取后评审。 | 若实际超预算，可能需要优化运行态容器结构或配置表压缩。 | 实现完成后从 link map 提取实际 ROM/RAM 值并与预算对比。 | | `已评审` |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | | `已评审` |

---

## 附录：架构元信息

- 架构版本: `V1`
- 架构状态: `Released`
- 生成时间: 2026-05-26
- 生成/修订说明: 初版生成，基于 `Gp_NCA95xx_软件需求规范.md` V0.1.0 生成完整 IoExtDev 架构。全部风险项已评审通过，发布为 V1 Released。
- 版本策略: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。
- 发布条件: 所有真实风险项均为 `已评审`。（已满足）
- 变更点总结【简洁版】:
  - 初版生成。
  - 6 个正式外部接口（Init、MainFunction、GetGpioInSig、SetGpioOutSig、GetDevFaultSig、GetDevModeInSig）+ 1 个条件接口（ResetChip）。
  - 6 个配置宏参（含 1 个 Conditional）+ 完整配置数据表设计。
  - 6 个依赖接口（2 个 Formal I2C Callout + 1 个 Formal GetCoreId + 1 个 Conditional ReadDio + 1 个 Conditional WriteDio + 1 个 Conditional DelayUs）。
  - 10 个 FC 文件（含 Reg.h、Callout.h/c）+ MemMap 5 段布局（CODE / RUNTIME RAM / CONST GLOBAL / CONST PER-CORE / CALIB 保留）。
  - 7 个架构风险项（R1-R7）+ R-OTHER，全部已评审。发布为 V1 Released。

---

**Input Documents:**
- `Gp_NCA95xx_软件需求规范.md` V0.1.0 (2026-05-26)
