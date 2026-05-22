# 《Gp_NCA95xx 软件架构设计》

**Gp_NCA95xx_软件架构设计**

**Gp_NCA95xx Software Architecture Design**

项目编号/Project number: Gp_NCA95xx
保密性/Security: 内部

**Document Properties**
Status: **草稿**
架构版本: **V1**
架构状态: **Draft**
Author: FC Architecture Workbench
Created: 2026-05-22 18:00

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| V1 | 2026-05-22 | FC Architecture Workbench | 基于 SRS V0.1.0 初始生成架构 V1 Draft | Draft |

---

## 目录

- [1 FC总结介绍](#1-fc总结介绍)
- [2 需求覆盖表](#2-需求覆盖表)
- [3 外部接口设计](#3-外部接口设计)
- [4 配置宏参设计](#4-配置宏参设计)
- [5 全局变量与运行态策略](#5-全局变量与运行态策略)
- [6 内存分配宏定义](#6-内存分配宏定义)
- [7 全局标定参数设计](#7-全局标定参数设计)
- [8 依赖接口设计](#8-依赖接口设计)
- [9 文件列表与文件关系](#9-文件列表与文件关系)
- [10 架构风险与待确认](#10-架构风险与待确认)
- [附录：架构元信息](#附录架构元信息)

---

## 1 FC总结介绍

- **架构版本**: V1
- **架构状态**: Draft
- **生成时间**: 2026-05-22 18:00
- **变更点总结**: 初版生成。基于 Gp_NCA95xx SRS V0.1.0（25 条需求，覆盖功能/接口/配置/诊断/时序/安全/编码/资源/可追溯性 9 个类别）生成 V1 Draft 架构。
- **FC名称**: `Gp_NCA95xx`
- **FC功能介绍**: Gp_NCA95xx 是 NCA9539-Q1 16-bit I2C GPIO 扩展芯片的驱动模块。驱动负责通过 I2C 总线管理最多 4 片芯片实例（每核独立配置），提供 GPIO 输入采样读取、输出控制、中断状态检测、硬件复位和 I2C 通信故障诊断功能。驱动在 ASIL-C 安全等级下实现配置完整性校验、寄存器回读验证和实例间免于干扰。
- **应用场景**: 适用于 AURIX 2G 域控平台中需要通过 I2C 总线扩展 MCU GPIO 数量的场景。典型应用包括 LED 指示控制、按键状态采集、传感器使能控制和通用数字 I/O 扩展。驱动运行于 AUTOSAR BSW 层，由 BswM 或 OS Task 周期调度 MainFunction，对外向上层 SWC 或 IoHwAb 提供语义化的 GPIO 读写接口。
- **架构设计思路**: 采用"外部语义接口 + 内部 I2C 依赖抽象 + 每核独立数据区"的架构模式。外部提供 Port 级和 Pin 级读写接口，通过 `Id_u16` 参数统一寻址实例，内部经 SigMapping 表映射到 `(CoreId, ChipIdx, Port, PinMask)`。I2C 通信通过 Callout 抽象，不直接依赖 MCAL I2C 驱动。输出写入采用异步 pending 机制（SetOutput → 缓存 → MainFunction 统一下发），输入读取采用同步缓存机制（MainFunction 周期刷新 → GetInput 直接返回缓存值）。多核场景下各核维护独立的驱动状态机和数据区，通过 `CalloutGetCoreId` 实现核归属校验。
- **AUTOSAR架构层级**: BSW
- **当前软件架构所处层级**: `IoExtDev`

---

## 2 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| SRS-Gp_NCA95xx-FUNC-0001 | 驱动状态机管理（UNINIT/INIT/NORMAL/FAULT） | `Gp_NCA95xx_Init`, internal runtime state machine in `Gp_NCA95xx.c`, state enum in `Gp_NCA95xx_Types.h` | Covered | 状态转换逻辑在 Init 和 MainFunction 中实现，每核独立状态机。 |
| SRS-Gp_NCA95xx-FUNC-0002 | MainFunction 周期处理（输入采样/中断检测/pending 输出下发） | `Gp_NCA95xx_MainFunction`, dependency interfaces (I2C read/write, DIO read), runtime input/output cache | Covered | 输入采样周期由项目调度配置保证。 |
| SRS-Gp_NCA95xx-INTF-0001 | 初始化接口（配置所有芯片实例） | `Gp_NCA95xx_Init`, config tables in `Gp_NCA95xx_Cfg.c`, `Gp_NCA95xx_CfgData.h` | Covered | Init 依次执行：配置校验 → 地址验证 → 寄存器写入 → 回读校验 → 初始采样。 |
| SRS-Gp_NCA95xx-INTF-0002 | MainFunction 接口（周期调度入口） | `Gp_NCA95xx_MainFunction` | Covered | Non-reentrant，每核独立调用。 |
| SRS-Gp_NCA95xx-INTF-0003 | GPIO 输入读取接口（Port/Pin 级，含极性反转） | `Gp_NCA95xx_GetInputPort`, `Gp_NCA95xx_GetInputPin` | Covered | 读取内部缓存值（MainFunction 已做极性反转处理），同步返回。 |
| SRS-Gp_NCA95xx-INTF-0004 | GPIO 输出写入接口（Port/Pin 级，异步 pending） | `Gp_NCA95xx_SetOutputPort`, `Gp_NCA95xx_SetOutputPin` | Covered | 写入内部 pending 缓存，MainFunction 统一下发到芯片。仅输出方向位生效。 |
| SRS-Gp_NCA95xx-INTF-0005 | 中断状态获取接口 | `Gp_NCA95xx_GetIntStatus` | Covered | 返回自上次读取以来发生输入变化的 Port 和 Pin 信息。 |
| SRS-Gp_NCA95xx-INTF-0006 | 驱动复位接口（硬件复位或软件重新初始化） | `Gp_NCA95xx_Reset` | Covered | 若 RESET 引脚由本驱动控制，执行硬件复位时序后重新初始化；否则仅执行软件重新初始化。 |
| SRS-Gp_NCA95xx-CFG-0001 | I2C 器件地址配置 | Config tables in `Gp_NCA95xx_Cfg.c`, `Gp_NCA95xx_Reg.h` (address constants) | Covered | 地址由硬件 A0/A1 决定，配置表存储 7-bit 地址，驱动转换为 8-bit 读写地址。 |
| SRS-Gp_NCA95xx-CFG-0002 | GPIO 方向配置（输入/输出位掩码） | Config tables, `Gp_NCA95xx_Reg.h` (Configuration Register constants) | Covered | Init 阶段写入 Configuration Register 并回读校验。 |
| SRS-Gp_NCA95xx-CFG-0003 | GPIO 极性反转配置 | Config tables, `Gp_NCA95xx_Reg.h` (Polarity Inversion Register constants) | Covered | Init 阶段写入 Polarity Inversion Register 并回读校验。 |
| SRS-Gp_NCA95xx-CFG-0004 | 默认输出值配置 | Config tables, `Gp_NCA95xx_Reg.h` (Output Port Register constants) | Covered | Init 阶段写入 Output Register 并回读校验。 |
| SRS-Gp_NCA95xx-CFG-0005 | 多实例与多核配置 | Config tables (instance count, chip index, SigMapping), `Gp_NCA95xx_CalloutGetCoreId`, per-core runtime containers | Covered | 每核独立配置数据区和运行时数据区。 |
| SRS-Gp_NCA95xx-DIAG-0001 | I2C 通信故障检测（NACK/超时） | Callout return value handling, internal fault counters, fault state in runtime container | Covered | 连续失败超阈值标记实例 FAULT，连续成功超阈值清除故障标记。 |
| SRS-Gp_NCA95xx-DIAG-0002 | 寄存器回读校验 | `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE`, internal verify logic in Init and MainFunction | Covered | 写入后立即回读比对；不一致时重试一次，仍失败标记 FAULT。 |
| SRS-Gp_NCA95xx-DIAG-0003 | 未初始化访问检测 | DET checks in all external APIs (except Init), `GP_NCA95xx_CFG_DEV_ERROR_DETECT` | Covered | UNINIT/INIT/FAULT 状态下调用功能接口返回 E_NOT_OK 并上报 DET。 |
| SRS-Gp_NCA95xx-DIAG-0004 | 中断异常监控（INT stuck low） | Internal monitoring in `Gp_NCA95xx_MainFunction`, configurable timeout threshold | Covered | INT 持续低电平超过可配置阈值时标记中断通路异常并上报。 |
| SRS-Gp_NCA95xx-TIM-0001 | I2C 总线时序合规（Fast-mode ≤400kHz） | External dependency (MCAL I2C configuration), noted as Analysis verification | Covered | MCAL I2C 驱动配置保证时序合规；本驱动不直接控制 SCL/SDA。 |
| SRS-Gp_NCA95xx-TIM-0002 | 复位时序合规（t_w≥6ns, t_rst≥400ns） | `Gp_NCA95xx_Reset`, `Gp_NCA95xx_CalloutWriteDio` (conditional) | Partially Covered | 仅在 RESET 引脚由本驱动控制时适用；否则由其他模块保证。 |
| SRS-Gp_NCA95xx-TIM-0003 | MainFunction 最大周期约束 | Project scheduling configuration (external), internal WCET documented | Covered | 驱动不强制周期值，由项目架构在调度配置中设定。 |
| SRS-Gp_NCA95xx-SAFE-0001 | ASIL-C 安全完整性 | Overall architecture: register readback, I2C fault detection, FFI, config CRC check | Covered | 所有安全机制在架构中均有对应设计对象。 |
| SRS-Gp_NCA95xx-SAFE-0002 | 配置完整性校验（CRC/版本/合法性检查） | `Gp_NCA95xx_Init` internal validation logic, config CRC and version fields | Covered | Init 阶段校验不通过则拒绝初始化并上报配置故障。 |
| SRS-Gp_NCA95xx-SAFE-0003 | 实例间免于干扰（FFI） | Per-instance data isolation in runtime containers, per-core data separation, I2C address-based hardware isolation | Covered | 代码审查和故障注入验证数据区无交叉访问。 |
| SRS-Gp_NCA95xx-CODE-0001 | 编码标准合规（MISRA C:2012, 命名约定） | File naming: `Gp_NCA95xx_*.h/.c`, function prefix: `Gp_NCA95xx_`, macro prefix: `GP_NCA95xx_CFG_` | Covered | 静态分析工具验证 MISRA 合规；代码走查确认命名。 |
| SRS-Gp_NCA95xx-RES-0001 | 资源消耗评估与记录（ROM/RAM/栈/CPU） | Post-build analysis (map file, WCET measurement) | Covered | 架构设计不产生运行时资源数据；资源消耗在构建后从 map 文件和 WCET 分析获取。 |
| SRS-Gp_NCA95xx-COMP-0001 | 需求追溯完整性 | This architecture document, requirement coverage table | Covered | 每条 SRS 需求在本表中均有对应架构覆盖对象。 |

---

## 3 外部接口设计

### 3.1 `Gp_NCA95xx_Init`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95xx_Init(void)` | Initializes all configured NCA9539-Q1 chip instances on the current core. Performs configuration integrity check, I2C device address verification, register initialization (Configuration, Polarity Inversion, Output), register readback verification, and initial input sampling for each configured instance. | Synchronous | Non-reentrant | `void` | Must be called after MCAL I2C driver initialization. Configuration data must be loaded and valid. Called once per core during startup or fault recovery. Init failure per instance is recorded internally; successful instances remain operational. |

### 3.2 `Gp_NCA95xx_MainFunction`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95xx_MainFunction(void)` | Periodic main processing function. Performs input port sampling via I2C read, INT pin status detection, pending output command execution, and fault state monitoring for all active chip instances on the current core. | Synchronous | Non-reentrant | `void` | Must only be called when driver is in NORMAL state. Called cyclically by BswM or OS Task at a project-configured period. Single execution WCET must not exceed 50% of the configured period. Each core calls its own MainFunction independently. |

### 3.3 `Gp_NCA95xx_GetInputPort`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_GetInputPort(uint16 Id_u16, uint8* PortVal_pu8)` | Returns the polarity-inversion-processed 8-bit input value for a specified Port (0 or 1) of a chip instance. The value is read from the internal cache, which is refreshed by MainFunction. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, instance is not initialized, instance is in FAULT state, or PortVal_pu8 is null. | `Id_u16` must be a valid signal ID mapped to a configured chip instance and Port. `PortVal_pu8` must be non-null. Driver must be in NORMAL state. The returned value already incorporates Polarity Inversion Register configuration. |

### 3.4 `Gp_NCA95xx_GetInputPin`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_GetInputPin(uint16 Id_u16, uint8 PinIdx_u8, uint8* PinVal_pu8)` | Returns the polarity-inversion-processed logic level (0 or 1) for a single specified pin of a chip instance. The value is extracted from the internal Port cache. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, PinIdx_u8 is out of range (0–15), instance is not initialized/available, or PinVal_pu8 is null. | `Id_u16` must be a valid signal ID. `PinIdx_u8` range: 0–7 for Port 0 pins, 8–15 for Port 1 pins. `PinVal_pu8` must be non-null. Driver must be in NORMAL state. |

### 3.5 `Gp_NCA95xx_SetOutputPort`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_SetOutputPort(uint16 Id_u16, uint8 PortVal_u8)` | Writes an 8-bit output value to the pending cache for a specified Port of a chip instance. The actual I2C write to the chip Output Port Register is performed asynchronously by the next MainFunction execution. Only bits configured as output direction take effect on the physical pins. | Asynchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, instance is not initialized/available, or pending queue is full. | `Id_u16` must be a valid signal ID mapped to a configured chip instance and Port. Bits corresponding to input-direction pins are masked internally and do not affect physical pins. Pending queue overflow returns E_NOT_OK. |

### 3.6 `Gp_NCA95xx_SetOutputPin`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_SetOutputPin(uint16 Id_u16, uint8 PinIdx_u8, uint8 PinVal_u8)` | Writes a single-bit output value (0 or 1) to the pending cache for a specified pin of a chip instance. The actual I2C write is performed asynchronously by MainFunction. Only takes effect if the pin is configured as output. | Asynchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, PinIdx_u8 is out of range (0–15), instance is not initialized/available, or the target pin is not configured as output. | `Id_u16` must be a valid signal ID. `PinIdx_u8` range: 0–7 for Port 0 pins, 8–15 for Port 1 pins. `PinVal_u8` must be 0 or 1. If the pin is configured as input, the write is rejected with E_NOT_OK. |

### 3.7 `Gp_NCA95xx_GetIntStatus`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_GetIntStatus(uint16 Id_u16, uint16* IntStatus_pu16)` | Returns the interrupt status word for a chip instance, indicating which pins have experienced an input state change since the last read. Bit 0–7 correspond to Port 0 pins, Bit 8–15 correspond to Port 1 pins. Reading this status clears the internal change-tracking state for the instance. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid, instance is not initialized/available, or IntStatus_pu16 is null. | `Id_u16` must be a valid signal ID. `IntStatus_pu16` must be non-null. The interrupt status reflects change detection performed in MainFunction by comparing current Input Port Register values against the previous cycle's values. |

### 3.8 `Gp_NCA95xx_Reset`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_Reset(uint16 Id_u16)` | Resets a specified chip instance. If the RESET pin is controlled by this driver, performs hardware reset (pulse RESET low for ≥6 ns, wait ≥400 ns recovery). Then re-executes the full initialization sequence. If RESET is managed externally, performs software re-initialization only (restore default register values). | Synchronous | Non-reentrant | `E_OK` on success; `E_NOT_OK` if Id is invalid or the reset/re-initialization sequence fails. | `Id_u16` must be a valid signal ID mapped to a configured instance. During reset, the instance is temporarily unavailable to other API calls. After successful reset, the instance returns to NORMAL state. |

---

## 4 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `GP_NCA95xx_CFG_DEV_ERROR_DETECT` | Global feature switch for development error detection. Controls DET reporting for invalid parameters, uninitialized access, and null pointer checks. | Macro | `STD_ON` | SRS-Gp_NCA95xx-DIAG-0003; aurix2g-normative-patterns-6 Diagnostic Requirements | `Gp_NCA95xx_Cfg.h`; parameter validation blocks in all external API functions except Init. | Formal |
| `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE` | Feature switch for register readback verification after I2C writes. Controls whether Configuration, Polarity Inversion, and Output Register writes are followed by a readback-and-compare check. | Macro | `STD_ON` | SRS-Gp_NCA95xx-DIAG-0002; SRS-Gp_NCA95xx-SAFE-0001 ASIL-C requirement | `Gp_NCA95xx_Cfg.h`; internal register write functions in `Gp_NCA95xx.c` (Init and MainFunction paths). | Formal |
| `GP_NCA95xx_CFG_SW_MAJOR_VERSION` | Software major version number for version checking and configuration compatibility validation. | Macro | `0` | aurix2g-normative-patterns-3 Configuration Requirements; project version management | `Gp_NCA95xx_Cfg.h`; configuration integrity check in `Gp_NCA95xx_Init`. | Formal |
| `GP_NCA95xx_CFG_SW_MINOR_VERSION` | Software minor version number. | Macro | `1` | aurix2g-normative-patterns-3 Configuration Requirements | `Gp_NCA95xx_Cfg.h`; configuration integrity check in `Gp_NCA95xx_Init`. | Formal |
| `GP_NCA95xx_CFG_INT_DETECT_MODE` | Behavior selection macro for interrupt detection strategy. `0` = MainFunction polls INT pin via DIO read callout; `1` = ICU interrupt triggers a callback that wakes MainFunction. | Macro | `0` (polling) | SRS-Gp_NCA95xx-INTF-0005; SRS-4.2 驱动功能介绍 (待定项: 中断处理方式) | `Gp_NCA95xx_Cfg.h`; MainFunction interrupt handling branch; ICU callback registration in Init. | Pending Confirmation |

---

## 5 全局变量与运行态策略

状态：`Empty` — 架构不允许对外提供全局变量输出。

内部运行态策略：

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Driver state machine (per core) | Internal static variable in `Gp_NCA95xx.c` | Read by all external APIs for state check; written by Init and MainFunction. | Set to UNINIT at module load; transitions managed by Init and MainFunction. | `CLEAR_FAR_DATA` per core | Per-core ownership; no cross-core access. |
| Per-instance runtime container (struct array per core) | Internal static array in `Gp_NCA95xx.c` | Read by GetInput*/GetIntStatus; written by Init, SetOutput*, MainFunction. | Allocated per core; initialized in Init; updated during MainFunction cycles. | `CLEAR_FAR_DATA` per core | Per-core ownership; instance array index derived from Id_u16 via SigMapping. |
| Input value cache (per instance, per Port) | Field in per-instance runtime container | Written by MainFunction (I2C read + polarity processing); read by GetInputPort/GetInputPin. | Refreshed each MainFunction cycle. | `CLEAR_FAR_DATA` per core | Updated only in MainFunction (single writer); concurrent reads by getters are safe (last complete value). |
| Pending output cache (per instance, per Port) | Field in per-instance runtime container | Written by SetOutputPort/SetOutputPin; read and cleared by MainFunction for I2C write. | Accumulates output requests between MainFunction cycles. | `CLEAR_FAR_DATA` per core | SetOutput* writes pending flag; MainFunction reads and clears. No concurrent SetOutput and MainFunction on same core. |
| Interrupt change tracking (per instance, 16-bit) | Field in per-instance runtime container | Written by MainFunction (input change detection); read and cleared by GetIntStatus. | Updated each MainFunction cycle; cleared on GetIntStatus read. | `CLEAR_FAR_DATA` per core | Updated in MainFunction; GetIntStatus reads current snapshot. |
| Fault state and counters (per instance) | Field in per-instance runtime container | Written by MainFunction and Init (fault detection); read by all APIs for availability check. | Accumulated over runtime; cleared on successful re-initialization. | `CLEAR_FAR_DATA` per core | Written only in MainFunction/Init paths; read by external APIs for guard checks. |

---

## 6 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | All external API implementations (`Init`, `MainFunction`, `GetInputPort`, `GetInputPin`, `SetOutputPort`, `SetOutputPin`, `GetIntStatus`, `Reset`) and internal static helper functions. | `GP_NCA95xx_CODE_START` | `GP_NCA95xx_CODE_STOP` | `Gp_NCA95xx.c`, `Gp_NCA95xx_Callout.c` | Standard CODE section for driver logic. |
| RUNTIME RAM (per core) | All runtime state: driver state machine, per-instance runtime containers (input cache, output pending cache, interrupt tracking, fault counters/state). | `GP_NCA95xx_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA95xx_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_NCA95xx.c` | Default `CLEAR_FAR_DATA`; per-core with `COREx` notation. No `NO_CLEAR` needed (no warm-reset retention requirement). No `NEAR` needed (no high-frequency ISR access path). |
| CONST (global shared) | Configuration data shared across cores: register default values, I2C address constants, version information. | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `Gp_NCA95xx_Cfg.c`, `Gp_NCA95xx_CfgData.h` | For truly shared configuration constants accessible from all cores. |
| CONST (per core) | Per-core configuration tables: SigMapping tables, per-core instance configuration, per-core chip index mapping. | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_NCA95xx_Cfg.c`, `Gp_NCA95xx_CfgData.h` | Each core has its own configuration data region. `COREx` notation represents the repeated pattern for all managed cores. |
| REG CONST | Register address constants, bit masks, command bytes, and protocol constants for NCA9539-Q1. | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `Gp_NCA95xx_Reg.h` | Register definitions are shared across all cores. Placed in global CONST section. |
| CALIB | Calibration constants. | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_CALI_START` | `GP_NCA95xx_CONST_FAR_DATA_ALIGN4_CALI_STOP` | (not used) | No confirmed calibration parameters. Section retained for future use. |

---

## 7 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。阈值和时序参数均归类为编译期项目配置（`Cfg`），不属于标定流程可调参数。 | `Empty` |

---

## 8 依赖接口设计

### 8.1 `Gp_NCA95xx_CalloutI2cWrite`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutI2cWrite(uint16 Id_u16, const uint8* Data_pcu8, uint16 Size_u16)` | Performs an I2C write operation to the chip instance identified by Id_u16. The data buffer contains the command byte (register address) followed by payload data. The implementation handles device addressing, START/STOP conditions, and ACK/NACK detection. | Synchronous | Reentrant | `E_OK` on successful write with ACK; `E_NOT_OK` on NACK, timeout, or bus error. | `Data_pcu8` must be non-null. `Size_u16` must be ≥1 (command byte + optional payload). The callout implementation must be reentrant to support multi-instance access. | MCAL I2C / IoExtDev / Project Adaptation | SRS-Gp_NCA95xx-INTF-0001 (Init register writes); SRS-Gp_NCA95xx-INTF-0004 (output writes); SRS-Gp_NCA95xx-DIAG-0001 | Formal |

### 8.2 `Gp_NCA95xx_CalloutI2cRead`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutI2cRead(uint16 Id_u16, uint8 RegAddr_u8, uint8* Data_pu8, uint16 Size_u16)` | Performs an I2C read operation from the specified register of the chip instance identified by Id_u16. The implementation handles: write device address + command byte, repeated START, read device address + data bytes, STOP. | Synchronous | Reentrant | `E_OK` on successful read with ACK; `E_NOT_OK` on NACK, timeout, or bus error. | `Data_pu8` must be non-null. `Size_u16` must be ≥1 (NCA9539-Q1 Port registers are 1 byte each). `RegAddr_u8` must be a valid command byte (0x00–0x07). The callout implementation must be reentrant. | MCAL I2C / IoExtDev / Project Adaptation | SRS-Gp_NCA95xx-INTF-0003 (input reads); SRS-Gp_NCA95xx-DIAG-0002 (register readback); SRS-Gp_NCA95xx-DIAG-0001 | Formal |

### 8.3 `Gp_NCA95xx_CalloutReadDio`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutReadDio(uint16 Id_u16, uint8* PinVal_pu8)` | Reads the logic level of the INT pin for the chip instance identified by Id_u16. Used in polling mode (`GP_NCA95xx_CFG_INT_DETECT_MODE = 0`) to detect interrupt assertion (low = interrupt pending). | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on DIO read failure. | `PinVal_pu8` must be non-null. The returned value is 0 (INT asserted, low) or 1 (INT de-asserted, high). The callout must handle any board-level signal inversion. | MCAL DIO / IoMcu / Project Adaptation | SRS-Gp_NCA95xx-FUNC-0002 (MainFunction INT detection); SRS-Gp_NCA95xx-DIAG-0004 (INT stuck-low monitoring) | Formal |

### 8.4 `Gp_NCA95xx_CalloutWriteDio`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95xx_CalloutWriteDio(uint16 Id_u16, uint8 PinVal_u8)` | Controls the logic level of the RESET pin for the chip instance identified by Id_u16. Used by `Gp_NCA95xx_Reset` when the RESET pin is under driver control. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on DIO write failure. | `PinVal_u8` must be 0 (assert RESET, low) or 1 (de-assert RESET, high). The callout must handle board-level signal inversion and ensure the RESET pulse meets datasheet timing (t_w ≥ 6 ns). | MCAL DIO / IoMcu / Project Adaptation | SRS-Gp_NCA95xx-INTF-0006 (Reset); SRS-Gp_NCA95xx-TIM-0002 (reset timing) | Conditional |

### 8.5 `Gp_NCA95xx_CalloutGetCoreId`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `uint32 Gp_NCA95xx_CalloutGetCoreId(void)` | Returns the logical core ID of the calling core. Used by Init and MainFunction to select the correct per-core configuration and runtime data area. | Synchronous | Reentrant | Core ID value (0–5 for AURIX 2G). | Must be callable from any core at any time after OS startup. Return value must be stable for the calling core. | OS / MCAL / Project Adaptation | SRS-Gp_NCA95xx-CFG-0005 (multi-core); SRS-Gp_NCA95xx-FUNC-0001 (per-core state machine) | Formal |

---

## 9 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `Gp_NCA95xx.c` | Required | Driver implementation file. | External API implementations (`Init`, `MainFunction`, `GetInputPort`, `GetInputPin`, `SetOutputPort`, `SetOutputPin`, `GetIntStatus`, `Reset`), internal static helper functions (I2C read/write wrappers, register readback verify, input change detection, fault management), per-core runtime state containers. |
| `Gp_NCA95xx.h` | Required | External interface header file. | External API prototypes, `CODE_START/STOP` section macros. |
| `Gp_NCA95xx_Types.h` | Required | Type definitions header file. | Driver state enum (`GP_NCA95xx_STATE_UNINIT/INIT/NORMAL/FAULT`), per-instance runtime container struct, per-instance configuration container struct, SigMapping entry struct, fault status bit definitions. |
| `Gp_NCA95xx_Cfg.h` | Required | Configuration macro header file. | Feature switches (`DEV_ERROR_DETECT`, `REG_READBACK_VERIFY_ENABLE`, `INT_DETECT_MODE`), version macros (`SW_MAJOR_VERSION`, `SW_MINOR_VERSION`), includes `Std_Types.h` and `Gp_NCA95xx_Reg.h`. |
| `Gp_NCA95xx_Cfg.c` | Required | Configuration data implementation file. | Per-core configuration tables (instance count, per-instance config, SigMapping table), const data under MemMap. |
| `Gp_NCA95xx_CfgData.h` | Required | Configuration data declaration header file. | `extern` declarations for configuration tables and containers, configuration struct type forward references. |
| `Gp_NCA95xx_Reg.h` | Required | I2C register definition header file. | NCA9539-Q1 register addresses (command bytes 0x00–0x07), bit masks, I2C device address constants (0x74–0x77, 0xE8–0xEF), register reset default values (0xFF, 0x00). Includes `Std_Types.h`. |
| `Gp_NCA95xx_Callout.h` | Required | Platform adaptation interface header file. | Callout prototypes for I2C read/write, DIO read/write, and core ID query. |
| `Gp_NCA95xx_Callout.c` | Required | Platform adaptation implementation file. | Callout integration stubs or project adaptation implementations for I2C, DIO, and core ID dependencies. |
| `Gp_NCA95xx_MemMap.h` | Required | Memory section mapping header file. | MemMap macro definitions for CODE, CONST (global and per-core), and RUNTIME RAM sections. Included by all section-managed FC files. |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `Gp_NCA95xx_Cfg.h` | `Std_Types.h` (external) | References `Std_ReturnType`, `uint8`, `uint16`, `uint32`, `boolean`, `STD_ON`, `STD_OFF`. `Std_Types.h` is an external platform header, not created by this FC. |
| `Gp_NCA95xx_Reg.h` | `Std_Types.h` (external) | Register address and bit mask constants use standard integer types (`uint8`, `uint16`). |
| `Gp_NCA95xx_Cfg.h` | `Gp_NCA95xx_Reg.h` | Configuration macros and default values reference register address constants (e.g., `GP_NCA9539_REG_OUTPUT_PORT0`) and reset default values from `Reg.h`. |
| `Gp_NCA95xx_Types.h` | `Gp_NCA95xx_Cfg.h` | Type definitions (enums, structs) depend on configuration macros (e.g., instance count for array sizing, feature switches for struct field inclusion). |
| `Gp_NCA95xx_Callout.h` | `Gp_NCA95xx_Types.h` | Callout prototypes reference FC public types (`Std_ReturnType`) and may use configuration-derived types. |
| `Gp_NCA95xx_CfgData.h` | `Gp_NCA95xx_Types.h` | Configuration data declarations reference types defined in `Types.h` (config container struct, SigMapping struct). |
| `Gp_NCA95xx.h` | `Gp_NCA95xx_CfgData.h` | External API header exposes public APIs and indirectly obtains type visibility through `CfgData.h` → `Types.h` chain. |
| `Gp_NCA95xx.c` | `Gp_NCA95xx.h` | Implements external APIs declared in `Gp_NCA95xx.h`. |
| `Gp_NCA95xx.c` | `Gp_NCA95xx_Callout.h` | Calls I2C, DIO, and core ID callouts for all hardware and platform interactions. |
| `Gp_NCA95xx.c` | `Gp_NCA95xx_MemMap.h` | Places code and runtime data into memory sections via MemMap macros. |
| `Gp_NCA95xx_Cfg.c` | `Gp_NCA95xx_CfgData.h` | Defines configuration tables declared in `CfgData.h`. |
| `Gp_NCA95xx_Cfg.c` | `Gp_NCA95xx_MemMap.h` | Places configuration const data into memory sections. |
| `Gp_NCA95xx_Callout.c` | `Gp_NCA95xx_Callout.h` | Implements callout stubs or project adaptation logic. |
| `Gp_NCA95xx_Callout.c` | `Gp_NCA95xx_MemMap.h` | Places callout adaptation code into memory sections. |
| `Gp_NCA95xx_MemMap.h` | All FC-created section-managed files | Included by `Gp_NCA95xx.c`, `Gp_NCA95xx_Cfg.c`, and `Gp_NCA95xx_Callout.c` at section boundaries for CODE, CONST, and RUNTIME RAM placement. |

---

## 10 架构风险与待确认

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | API 粒度确认（Port 级 vs Pin 级） | SRS 将 API 粒度标记为"待架构确认"。当前架构同时提供 Port 级和 Pin 级接口（`GetInputPort`/`GetInputPin`、`SetOutputPort`/`SetOutputPin`），但项目最终是否需要两种粒度待确认。 | 若仅需 Port 级接口，Pin 级接口为多余实现和测试工作量。若两种都需要，当前设计已覆盖。 | 与架构和硬件团队确认最终 API 粒度需求。若仅需 Port 级，移除 Pin 级接口。 | | 待评审 |
| R2 | 中断检测方式（轮询 vs ICU 回调） | SRS 将中断处理方式标记为"待架构和硬件确认"。当前架构通过 `GP_NCA95xx_CFG_INT_DETECT_MODE` 宏支持两种模式，默认采用轮询模式（MainFunction 周期读取 INT 引脚）。若项目采用 ICU 中断触发方式，需增加回调注册接口和 ISR 集成设计。 | 轮询模式增加 MainFunction 负载；ICU 模式增加中断延迟和 ISR 复杂度。两种模式的 MainFunction 内部处理逻辑有差异。 | 与硬件和架构团队确认 INT 引脚的 MCU 连接方式（DIO 还是 ICU 通道）和中断处理策略。当前默认轮询模式可满足大多数场景。 | | 待评审 |
| R3 | RESET 引脚控制归属 | SRS 将 RESET 引脚控制归属标记为"待架构确认"。当前架构将 `Gp_NCA95xx_CalloutWriteDio` 标记为 Conditional，`Gp_NCA95xx_Reset` 内部根据配置选择硬件复位或软件重新初始化。 | 若 RESET 由其他模块（SBC/PMIC）管理，`CalloutWriteDio` 可移除，Reset 接口仅执行软件重新初始化。 | 与硬件和架构团队确认 RESET 引脚的控制方。 | | 待评审 |
| R4 | 运行时方向/极性变更支持 | SRS 将运行时方向变更和极性变更策略标记为"待项目策略确认"。当前架构不支持运行时变更方向或极性（仅在 Init 时配置），简化了安全设计和状态管理。 | 若项目需要运行时变更（如动态切换引脚为输入/输出），需增加 `SetDirection` 和 `SetPolarity` 接口，并考虑变更时的输出缓存一致性。 | 与项目确认是否需要运行时方向/极性变更。若不需要，当前架构满足需求。 | | 待评审 |
| R5 | I2C 地址探测策略 | SRS 将 Init 阶段的器件地址探测标记为"可选"。当前架构默认执行地址探测（发送器件地址并检测 ACK），增加初始化时间但提前发现硬件连接问题。 | 地址探测增加 Init 执行时间（每个实例约一个 I2C 传输时间）。若跳过探测，不可用实例会在首次寄存器访问时才发现。 | 与项目确认是否需要在 Init 阶段执行 I2C 地址探测。ASIL-C 场景建议保留探测以尽早发现故障。 | | 待评审 |
| R6 | MainFunction 调度周期 | SRS 将 MainFunction 周期标记为"待架构确认"。当前架构不硬编码周期值，由项目在调度配置中设定，驱动仅约束单次 WCET 不超过周期的 50%。 | 周期过长导致输入响应延迟和输出延迟增大；周期过短增加 CPU 负载。 | 与架构团队根据 GPIO 输入响应实时性要求确定 MainFunction 周期（典型建议 ≤5 ms）。 | | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | | 待评审 |

---

## 附录：架构元信息

- **架构版本**: V1
- **架构状态**: Draft
- **生成时间**: 2026-05-22 18:00
- **生成/修订说明**: 基于 Gp_NCA95xx SRS V0.1.0（25 条需求）初始生成 V1 Draft 架构。采用 L3 Deep Review 模式执行：完成显式接口抽取、隐式接口补全、配置/标定分离、依赖边界定义、MemMap 策略和双向追溯验证。
- **版本策略**: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。
- **发布条件**: 所有真实风险项（R1–R6 + R-OTHER）均为 `已评审`。
- **变更点总结【简洁版】**:
  - 初版生成。
  - 外部接口：8 个（Init, MainFunction, GetInputPort/Pin, SetOutputPort/Pin, GetIntStatus, Reset）。
  - 依赖接口：5 个 Callout（I2cWrite, I2cRead, ReadDio, WriteDio [Conditional], GetCoreId）。
  - 配置宏参：5 个 Formal + 1 个 Pending Confirmation。
  - 标定参数：Empty。
  - 文件：10 个（含 Reg.h, Callout.h/c）。
  - MemMap：CODE + RUNTIME RAM per-core + CONST global + CONST per-core。
  - 风险项：6 个待评审 + 1 个其他。

---

## 下一步：评审与发布引导

当前架构状态为 **V1 Draft**。请通过以下方式完成评审：

- **推荐评审方式 1**：直接修改第 10 章风险表中的 `状态` 和 `备注` 列。
- **推荐评审方式 2**：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：需要运行时方向变更接口`。
- 如果所有风险项均认可，可回复：**`全部已评审，R-OTHER 无其他建议，直接发布`**。
- 如果某项需要修改，可回复：**`R3 待修改，备注：RESET 由 SBC 管理，移除 CalloutWriteDio`**。
- 修改完成后仍保持 `V1 Draft`，直到所有真实风险项均为 `已评审` 后发布为 **V1 Released**。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
