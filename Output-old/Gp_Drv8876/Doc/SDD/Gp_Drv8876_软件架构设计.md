# 《Gp_Drv8876 软件架构设计》

**Gp_Drv8876_软件架构设计**

**Gp_Drv8876 Software Architecture Design**

项目编号/Project number: Gp_Drv8876
保密性/Security: 内部

**Document Properties**
Status: **草稿**
架构版本: **V1**
架构状态: **Draft**
Author: FC Architecture Workbench
Created: 2026-05-27 15:30

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| V1 | 2026-05-27 | FC Architecture Workbench | 基于 SRS V1 Draft 生成初版架构，覆盖外部接口、Callout 依赖、配置宏参、运行时策略、MemMap 与文件族 | Draft |

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

## 1. FC总结介绍

- **架构版本**: `V1`
- **架构状态**: `Draft`
- **生成时间**: 2026-05-27 15:30
- **变更点总结**: 初版生成
- **FC名称**: `Gp_Drv8876`
- **FC功能介绍**: `Gp_Drv8876` 是 IoExtDev 层外部 H 桥电机驱动模块，负责通过 MCU 的 DIO/PWM/ADC 资源控制 DRV8876 芯片。模块提供芯片模式管理（Sleep/Active）、H 桥输出控制（Coast/Brake/Forward/Reverse）、nFAULT 故障读取、IPROPI 电流反馈采集以及开发错误检测能力。控制模式（PH/EN、PWM）和电流调节模式由 PMODE/IMODE 锁存配置决定，模块通过 Callout 抽象硬件资源访问，不直接操作 MCAL 或寄存器。
- **应用场景**: 适用于需要 DRV8876 驱动刷式直流电机的汽车电子控制单元。上层控制算法通过语义化的 Set/Get 接口下发模式请求和输出控制，模块负责将逻辑请求映射为芯片引脚控制序列并处理休眠唤醒时序。故障诊断和电流反馈通过周期 MainFunction 异步采样和去抖后上报。
- **架构设计思路**: 采用异步请求-周期处理模式。外部 Set 接口立即缓存上层请求并校验参数合法性；MainFunction 周期执行状态机推进、nSLEEP 时序管理（tSLEEP/tWAKE）、nFAULT 采样去抖、IPROPI ADC 采集和输出控制下发。Get 接口同步返回缓存的最新状态。所有硬件访问通过 Callout 抽象为平台适配边界，不绑定具体 MCAL 实现。多核场景下按 Core ID 隔离运行时数据与配置表。
- **AUTOSAR架构层级**:
- **当前软件架构所处层级**: `IoExtDev`

---

## 2. 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| SRS-GPDRV8876-FUNC-0001 | 初始化默认状态控制 | `Gp_Drv8876_Init`, per-core runtime container, config default mode | Covered | Init 加载配置并将各实例置为配置定义的默认安全状态（Sleep/Coast/Brake） |
| SRS-GPDRV8876-FUNC-0002 | Sleep 与 Active 模式切换 | `Gp_Drv8876_SetDevModeOutSig`, `Gp_Drv8876_MainFunction` 时序管理 | Covered | Set 接口缓存模式请求；MainFunction 控制 nSLEEP 并管理 tSLEEP/tWAKE |
| SRS-GPDRV8876-FUNC-0003 | H 桥输出状态控制 | `Gp_Drv8876_SetHbOutSig`, `Gp_Drv8876_MainFunction` 输出下发 | Covered | Set 接口校验并缓存；MainFunction 根据控制模式查真值表输出 EN/IN1、PH/IN2 |
| SRS-GPDRV8876-FUNC-0004 | 独立半桥输出控制边界 | `Gp_Drv8876_SetHalfBridgeOutSig` | Pending Confirmation | 接口原型已预留；是否交付取决于项目是否启用独立半桥模式 |
| SRS-GPDRV8876-FUNC-0005 | 模式锁存处理 | `Gp_Drv8876_MainFunction` 锁存序列 | Covered | PMODE/IMODE 软件可控时执行 Sleep→改配置→Active 序列 |
| SRS-GPDRV8876-INTF-0001 | 初始化接口 | `Gp_Drv8876_Init(void)` | Covered | 外部接口 §3.1 |
| SRS-GPDRV8876-INTF-0002 | 芯片模式设置接口 | `Gp_Drv8876_SetDevModeOutSig` | Covered | 外部接口 §3.2 |
| SRS-GPDRV8876-INTF-0003 | 芯片模式读取接口 | `Gp_Drv8876_GetDevModeInSig` | Covered | 外部接口 §3.3 |
| SRS-GPDRV8876-INTF-0004 | H 桥输出设置接口 | `Gp_Drv8876_SetHbOutSig` | Covered | 外部接口 §3.4 |
| SRS-GPDRV8876-INTF-0005 | 半桥输出设置接口 | `Gp_Drv8876_SetHalfBridgeOutSig` | Pending Confirmation | 外部接口 §3.5；独立半桥模式待确认 |
| SRS-GPDRV8876-INTF-0006 | 故障读取接口 | `Gp_Drv8876_GetDevFaultSig` | Covered | 外部接口 §3.6 |
| SRS-GPDRV8876-INTF-0007 | 电流反馈读取接口 | `Gp_Drv8876_GetCurrentRaw` | Covered | 外部接口 §3.7 |
| SRS-GPDRV8876-CFG-0001 | 实例与信号映射配置 | Per-core config table, SigMapping, Core ID check | Covered | `Gp_Drv8876_Cfg.h/.c/CfgData.h` 承载 |
| SRS-GPDRV8876-CFG-0002 | 控制模式配置 | PMODE enum in config container | Covered | 每实例 PMODE 枚举，决定真值表选择 |
| SRS-GPDRV8876-CFG-0003 | 电流调节模式配置 | IMODE enum in config container | Covered | 每实例 IMODE 枚举，决定诊断解释边界 |
| SRS-GPDRV8876-CFG-0004 | PWM 参数配置 | PWM resource binding and range in config table | Covered | 周期/占空比单位与边界为配置表参数 |
| SRS-GPDRV8876-CFG-0005 | 电流反馈配置 | ADC channel, RIPROPI, AIPROPI in config table | Covered | 配置参数支持原始 ADC 读取与换算 |
| SRS-GPDRV8876-DIAG-0001 | 开发错误检测 | DET macro + runtime DET bookkeeping | Covered | `GP_DRV8876_CFG_DEV_ERROR_DETECT` 宏 + 接口层参数校验 |
| SRS-GPDRV8876-DIAG-0002 | nFAULT 低有效语义 | `Gp_Drv8876_GetDevFaultSig`, MainFunction 采样 | Covered | MainFunction 周期采样 nFAULT 并更新软件故障位 |
| SRS-GPDRV8876-DIAG-0003 | 逐周期电流斩波指示边界 | Fault status bit + IMODE context in MainFunction | Covered | MainFunction 根据 IMODE 和当前输出状态区分/聚合故障位 |
| SRS-GPDRV8876-DIAG-0004 | 过流响应软件边界 | nFAULT 读取 + IMODE 配置 → 软件诊断责任边界 | Covered | 架构明确软件仅读取和上报；OCP 限流/重试由芯片内部执行 |
| SRS-GPDRV8876-TIM-0001 | Sleep 进入等待时间 | MainFunction 时序管理 + delay Callout | Covered | nSLEEP 拉低后等待 tSLEEP (≥1ms) 再标记 Sleep 完成 |
| SRS-GPDRV8876-TIM-0002 | Active 唤醒等待时间 | MainFunction 时序管理 + delay Callout | Covered | nSLEEP 拉高后等待 tWAKE (≥1ms) 再允许输出控制 |
| SRS-GPDRV8876-TIM-0003 | PWM 输入频率边界 | Config table PWM range validation | Covered | 频率上限 100kHz 由配置约束和接口校验保证 |
| SRS-GPDRV8876-SAFE-0001 | QM 安全等级管理 | 架构 QM 标识 | Covered | 不分配 ASIL 目标，不做功能安全架构 |
| SRS-GPDRV8876-SAFE-0002 | 输出误动作防护边界 | 接口前置条件检查 + 状态机 guard | Covered | 未初始化/无效ID/唤醒未完成/Sleep状态下拒绝输出控制 |
| SRS-GPDRV8876-CODE-0001 | 编码规范符合性要求 | 命名规范、文件族结构符合项目规则 | Covered | 架构命名和文件结构遵循 project-style-rules |
| SRS-GPDRV8876-RES-0001 | MCU 资源占用约束 | Config table resource binding + resource conflict check | Covered | 每实例 DIO/PWM/ADC 资源在配置表中声明 |
| SRS-GPDRV8876-COMP-0001 | 需求追溯完整性 | Requirement Coverage 表 + Trace 文档 | Covered | 每条 SRS 需求在本表中显式覆盖 |

---

## 3. 外部接口设计

### 3.1 `Gp_Drv8876_Init`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_Drv8876_Init(void)` | Initializes the Gp_Drv8876 module for the current core. Loads per-core instance configuration, initializes runtime state containers for each configured instance, and sets all control outputs (nSLEEP, EN/IN1, PH/IN2, PMODE, IMODE) to the configured default safe state. Must be called once per core before any other Gp_Drv8876 API on that core. | Synchronous | Non-reentrant | None. | MCU DIO/PWM/ADC resources must be initialized upstream. Configuration data must be accessible. Repeated calls reload configuration and re-initialize runtime state per project convention. Invalid configurations are marked unavailable and do not produce undefined H-bridge outputs. |

### 3.2 `Gp_Drv8876_SetDevModeOutSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_Drv8876_SetDevModeOutSig(uint16 Id_u16, uint8 DevMode_u8)` | Requests a Sleep or Active device mode for the target instance. The request is buffered immediately; the actual nSLEEP pin transition and tSLEEP/tWAKE timing are handled asynchronously in `Gp_Drv8876_MainFunction`. | Asynchronous (buffered request) | Non-reentrant | `E_OK` on successful buffering; `E_NOT_OK` if uninitialized, `Id_u16` invalid, cross-core access, or `DevMode_u8` illegal. | Module must be initialized. `Id_u16` must resolve to a valid current-core instance. `DevMode_u8` must be a defined sleep or active mode constant. Invalid requests do not change the buffered request or pin state. |

### 3.3 `Gp_Drv8876_GetDevModeInSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_Drv8876_GetDevModeInSig(uint16 Id_u16, uint8* DevMode_pu8)` | Reads the last accepted software device mode for the target instance. Returns the buffered request state, not a physically confirmed chip mode. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if uninitialized, `Id_u16` invalid, cross-core access, or `DevMode_pu8` is NULL. | Module must be initialized. Output pointer must be non-NULL. On failure, the output parameter is not written. |

### 3.4 `Gp_Drv8876_SetHbOutSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_Drv8876_SetHbOutSig(uint16 Id_u16, uint8 HbState_u8, uint32 Period_u32, uint32 Duty_u32)` | Requests an H-bridge output state (Coast, Brake, Forward, Reverse) with PWM parameters for the target instance. The request is buffered; actual EN/IN1 and PH/IN2 pin updates are applied in `Gp_Drv8876_MainFunction` after truth-table mapping per the configured control mode (PH/EN or PWM). | Asynchronous (buffered request) | Non-reentrant | `E_OK` on successful buffering; `E_NOT_OK` if uninitialized, `Id_u16` invalid, instance not in Active software mode, `HbState_u8` illegal, `Duty_u32 > Period_u32`, or control mode does not support the requested state. | Module must be initialized. Target instance must be in Active software mode. Duty must not exceed period. PWM parameter units and range are defined per config table. Illegal requests do not change the buffered request or pin state. |

### 3.5 `Gp_Drv8876_SetHalfBridgeOutSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_Drv8876_SetHalfBridgeOutSig(uint16 Id_u16, uint8 HalfBridge_u8, uint8 OutState_u8)` | Requests an individual half-bridge output state for OUT1 or OUT2 when the instance is configured for independent half-bridge control mode. Sets the corresponding half-bridge to low-side or high-side conduction. The request is buffered; actual INx pin update is applied in `Gp_Drv8876_MainFunction`. If the project does not enable independent half-bridge mode, this interface may be excluded from the build or return `E_NOT_OK` unconditionally. | Asynchronous (buffered request) | Non-reentrant | `E_OK` on success; `E_NOT_OK` if mode mismatch, half-bridge ID invalid, output state illegal, or instance not in Active software mode. | Instance must be configured for independent half-bridge mode (PMODE=Hi-Z latched). `HalfBridge_u8` selects OUT1 or OUT2. `OutState_u8` selects low-side or high-side conduction. |

### 3.6 `Gp_Drv8876_GetDevFaultSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_Drv8876_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` | Reads the current software fault status bitmask for the target instance. The fault status is updated periodically by `Gp_Drv8876_MainFunction` via nFAULT pin sampling. The bitmask aggregates nFAULT low-active indication; without additional hardware measurement, UVLO, CPUV, OCP, and TSD root causes cannot be distinguished solely by software. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if uninitialized, `Id_u16` invalid, cross-core access, or `Fault_pu32` is NULL. | Module must be initialized. Output pointer must be non-NULL. nFAULT DIO channel must be configured. On failure, the output parameter is not written. |

### 3.7 `Gp_Drv8876_GetCurrentRaw`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_Drv8876_GetCurrentRaw(uint16 Id_u16, uint16* Raw_pu16)` | Reads the most recent IPROPI ADC raw value for the target instance. The ADC value is updated periodically by `Gp_Drv8876_MainFunction`. Current-to-voltage conversion (V_IPROPI = I_PROPI * R_IPROPI) and trip-point derivation (I_TRIP * AIPROPI = VREF / RIPROPI) may be performed at a higher layer or within the driver if a converted-current API is later confirmed. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if uninitialized, `Id_u16` invalid, cross-core access, `Raw_pu16` is NULL, or IPROPI ADC channel not configured. | Module must be initialized. Output pointer must be non-NULL. IPROPI ADC channel must be configured. On failure, the output parameter is not written. |

### 3.8 `Gp_Drv8876_MainFunction`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_Drv8876_MainFunction(void)` | Periodic processing function for the current core. Drives the per-instance state machine, applies buffered mode/H-bridge/half-bridge requests to DIO/PWM outputs, manages nSLEEP tSLEEP/tWAKE timing via delay callout, samples nFAULT with debounce, reads IPROPI ADC, updates software fault status, and performs PMODE/IMODE re-latch sequences when requested. Must be called cyclically by the operating system or scheduler for the owning core. | Asynchronous (periodic) | Non-reentrant | None. | Module must be initialized. Callout dependencies (DIO, PWM, ADC, GetCoreId, delay) must be operational. This function is the sole writer of hardware output pins and the sole updater of runtime fault and current-feedback state. |

---

## 4. 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `GP_DRV8876_CFG_DEV_ERROR_DETECT` | Global feature switch for development error detection. Controls DET reporting for uninitialized access, invalid parameters, null pointers, cross-core access, and configuration errors. | Macro | `STD_ON` | SRS-GPDRV8876-DIAG-0001; AURIX2G platform DET pattern | `Gp_Drv8876_Cfg.h`, external API parameter checks | Formal |
| `GP_DRV8876_CFG_SW_MAJOR_VERSION` | Software major version number for version checking. | Macro | `1` | AURIX2G platform versioning convention | `Gp_Drv8876_Cfg.h`, version check API | Formal |
| `GP_DRV8876_CFG_SW_MINOR_VERSION` | Software minor version number for version checking. | Macro | `0` | AURIX2G platform versioning convention | `Gp_Drv8876_Cfg.h`, version check API | Formal |
| `GP_DRV8876_CFG_MAINFUNCTION_ENABLE` | Compile-time switch for MainFunction scheduling. When `STD_OFF`, MainFunction is excluded from the build and all APIs operate synchronously (blocking tSLEEP/tWAKE delays). | Macro | `STD_ON` | SRS R6 MainFunction strategy; Gp_DRV887x_DIO demo pattern | `Gp_Drv8876_Cfg.h`, `Gp_Drv8876_MainFunction` | Conditional |
| `GP_DRV8876_CFG_HALF_BRIDGE_ENABLE` | Compile-time switch for independent half-bridge control support. When `STD_ON`, `Gp_Drv8876_SetHalfBridgeOutSig` and related logic are compiled. | Macro | `STD_OFF` | SRS-GPDRV8876-FUNC-0004 (Open Issue); SRS R2 | `Gp_Drv8876_Cfg.h`, `Gp_Drv8876.c` | Conditional |

---

## 5. 全局变量与运行态策略

状态：`Empty` — 架构不允许对外提供全局变量输出。

内部运行态策略：

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Per-instance runtime container (per core) | Internal static array in `Gp_Drv8876.c` | Read by all external Get APIs for cached state return; written by Init and MainFunction. | Allocated per core at module load; initialized by `Gp_Drv8876_Init`; updated each MainFunction cycle. | `CLEAR_FAR_DATA` per core | Per-core ownership; no cross-core access. Core ID validated on each external API call. |
| Software device mode (per instance) | Field in per-instance runtime container | Read by `GetDevModeInSig`; written by `SetDevModeOutSig` (buffered) and MainFunction (applied). | Initialized to config default in Init; updated on mode request and MainFunction completion. | `CLEAR_FAR_DATA` per core | Per-core ownership. |
| Buffered H-bridge output request (per instance) | Field in per-instance runtime container | Read by MainFunction for output application; written by `SetHbOutSig`. | Initialized to default safe output in Init; updated by SetHbOutSig and consumed by MainFunction. | `CLEAR_FAR_DATA` per core | Per-core ownership. |
| Fault status bitmask and debounce counter (per instance) | Field in per-instance runtime container | Read by `GetDevFaultSig`; written by MainFunction (nFAULT sampling + debounce). | Initialized to no-fault in Init; updated each MainFunction cycle. | `CLEAR_FAR_DATA` per core | Per-core ownership. |
| IPROPI ADC cached raw value (per instance) | Field in per-instance runtime container | Read by `GetCurrentRaw`; written by MainFunction (ADC acquisition). | Initialized to 0 in Init; updated each MainFunction cycle. | `CLEAR_FAR_DATA` per core | Per-core ownership. |
| nSLEEP timing state machine (per instance) | Field in per-instance runtime container | Read/written by MainFunction during Sleep/Active transitions. | Initialized to IDLE in Init; managed by MainFunction tSLEEP/tWAKE sequencing. | `CLEAR_FAR_DATA` per core | Per-core ownership. |
| DET error record (per core) | Internal static variable in `Gp_Drv8876.c` | Read by DET reporting; written by external API defensive checks. | Initialized in Init; overwritten on each detected error. | `CLEAR_FAR_DATA` per core | Per-core ownership. |

---

## 6. 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | All external API implementations, internal static helper functions, state machine logic, truth-table mapping, and MainFunction processing. | `GP_DRV8876_CODE_START` | `GP_DRV8876_CODE_STOP` | `Gp_Drv8876.c`, `Gp_Drv8876_Callout.c` | Standard CODE section for driver logic. |
| RUNTIME RAM (per core) | All runtime state: per-instance runtime containers, device mode state, buffered output requests, fault debounce counters, fault status bitmasks, ADC cached values, nSLEEP timing state, and DET error records. | `GP_DRV8876_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `GP_DRV8876_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_Drv8876.c` | Per-core clear-on-init data. `COREx` notation represents the repeated pattern for all managed cores. |
| CONST (per core) | Per-core configuration tables: SigMapping table (ID→Core/Chip/Channel/Hardware resource mapping), per-instance config (PMODE, IMODE, default mode, default output, timing parameters). | `GP_DRV8876_CONST_FAR_DATA_ALIGN4_COREx_START` | `GP_DRV8876_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_Drv8876_Cfg.c`, `Gp_Drv8876_CfgData.h` | Each core has its own configuration data region. `COREx` notation represents the repeated pattern for all managed cores. |
| CONST (global shared) | Version information, module-wide constants shared across all cores. | `GP_DRV8876_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_DRV8876_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `Gp_Drv8876_Cfg.c`, `Gp_Drv8876_CfgData.h` | For truly shared configuration constants accessible from all cores. |

---

## 7. 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。tSLEEP/tWAKE 时序、nFAULT 去抖次数、ADC 采样周期等阈值和时序参数均归类为编译期项目配置（`Cfg`），不属于标定流程可调参数。 | `Empty` |

---

## 8. 依赖接口设计

### 8.1 `Gp_Drv8876_CalloutGetCoreId`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `uint32 Gp_Drv8876_CalloutGetCoreId(void)` | Returns the identifier of the currently executing core. Used by all external APIs to validate that the calling context matches the configured core ownership of the target instance, and to prevent cross-core access. Called at the entry of every external API that takes an `Id_u16` parameter. | Synchronous | Reentrant | Core ID value (platform-defined width). | Must be available before `Gp_Drv8876_Init` is called. Return value must be stable for the duration of the call. | Project Adaptation / BswSys_Gp | SRS-GPDRV8876-CFG-0001 (Core ID mapping); AURIX2G multi-core pattern (source grounding §5) | Formal |

### 8.2 `Gp_Drv8876_CalloutWrDioCh`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `void Gp_Drv8876_CalloutWrDioCh(uint16 ChId_u16, uint8 Lvl_u8)` | Sets the logical output level of a DIO channel identified by `ChId_u16`. Used by the FC to control nSLEEP, EN/IN1, PH/IN2, PMODE, and IMODE pins. Board-specific inversion and pin mapping are handled inside the callout implementation. Called from `Gp_Drv8876_Init` (default output setup) and `Gp_Drv8876_MainFunction` (mode/output/pin updates). | Synchronous | Reentrant | None. | `ChId_u16` must be a valid DIO channel configured in the project integration. `Lvl_u8` is the logical level (0 = low, non-zero = high); physical inversion is the callout's responsibility. | MCAL / IoMcu / Project Adaptation | SRS-GPDRV8876-FUNC-0001/0002/0003/0005; Gp_DRV887x_DIO demo pattern | Formal |

### 8.3 `Gp_Drv8876_CalloutReadDioCh`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `uint8 Gp_Drv8876_CalloutReadDioCh(uint16 ChId_u16)` | Reads the logical input level of a DIO channel identified by `ChId_u16`. Used by the FC to sample the nFAULT pin. Board-specific inversion is handled inside the callout implementation so the FC receives a logical level where 0 = fault active (low), 1 = no fault (high). Called from `Gp_Drv8876_MainFunction` during fault sampling. | Synchronous | Reentrant | Logical input level: 0 for nFAULT active (fault), non-zero for nFAULT inactive (no fault). | `ChId_u16` must be a valid DIO channel configured for input. The callout MUST apply inversion so the return value reflects logical fault semantics, not raw pin voltage. | MCAL / IoMcu / Project Adaptation | SRS-GPDRV8876-DIAG-0002; SRS-GPDRV8876-INTF-0006 | Formal |

### 8.4 `Gp_Drv8876_CalloutSetPwmPerdAndDuty`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `void Gp_Drv8876_CalloutSetPwmPerdAndDuty(uint16 ChId_u16, uint32 Perd_u32, uint32 Duty_u32)` | Sets the PWM period and duty cycle for the specified PWM channel. Used by the FC to drive EN/IN1 and PH/IN2 with PWM waveforms in PWM control mode. Called from `Gp_Drv8876_MainFunction` when applying H-bridge output requests. In PH/EN mode, this callout may be used for speed control on the EN pin. | Synchronous | Reentrant | None. | `ChId_u16` must be a valid PWM channel. `Perd_u32` and `Duty_u32` units are defined by the project configuration (e.g., ticks, microseconds). `Duty_u32` must not exceed `Perd_u32`; this is validated by the FC before calling. | MCAL / IoMcu / Project Adaptation | SRS-GPDRV8876-FUNC-0003; SRS-GPDRV8876-CFG-0004; Gp_DRV887x_DIO demo pattern | Formal |

### 8.5 `Gp_Drv8876_CalloutGetAdcRaw`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `void Gp_Drv8876_CalloutGetAdcRaw(uint16 ChId_u16, uint16* Raw_pu16, boolean* RawVld_pb)` | Reads the raw ADC conversion result for the specified ADC channel and indicates whether the result is valid. Used by the FC to acquire IPROPI current feedback. Called from `Gp_Drv8876_MainFunction` during periodic current sampling. | Synchronous | Reentrant | None (results via output parameters). | `ChId_u16` must be a valid ADC channel. `Raw_pu16` and `RawVld_pb` must be non-NULL. The callout writes the raw ADC value and sets validity. | MCAL / IoMcu / Signal Service | SRS-GPDRV8876-INTF-0007; SRS-GPDRV8876-CFG-0005; Gp_DRV887x_DIO demo pattern | Formal |

### 8.6 `Gp_Drv8876_CalloutDelayUs`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `void Gp_Drv8876_CalloutDelayUs(uint32 DelayUs_u32)` | Provides a blocking or non-blocking delay for the specified duration in microseconds. Used by the FC during nSLEEP tSLEEP and tWAKE timing management in MainFunction. The callout implementation may be a simple busy-wait, a hardware timer-based delay, or a no-op if the caller manages timing externally. | Synchronous / Asynchronous (implementation-defined) | Reentrant | None. | `DelayUs_u32` minimum value is 1000 (1 ms) per datasheet tSLEEP/tWAKE. The callout must guarantee at least the requested delay. | Project Adaptation / MCAL | SRS-GPDRV8876-TIM-0001; SRS-GPDRV8876-TIM-0002; AURIX2G delay callout pattern (source grounding §4) | Conditional |

---

## 9. 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `Gp_Drv8876.c` | Required | Driver implementation file. | External API implementations (`Init`, `MainFunction`, `SetDevModeOutSig`, `GetDevModeInSig`, `SetHbOutSig`, `SetHalfBridgeOutSig`, `GetDevFaultSig`, `GetCurrentRaw`), internal static helper functions, per-core runtime state containers, state machine logic, truth-table mapping, fault debounce, and timing management. |
| `Gp_Drv8876.h` | Required | External interface header file. | External API prototypes, module version information. |
| `Gp_Drv8876_Types.h` | Required | Type definitions header file. | Device mode enum (`GP_DRV8876_DEVMODE_SLEEP`, `GP_DRV8876_DEVMODE_ACTIVE`), H-bridge output state enum (`GP_DRV8876_HBSTATE_COAST`, `GP_DRV8876_HBSTATE_BRAKE`, `GP_DRV8876_HBSTATE_FORWARD`, `GP_DRV8876_HBSTATE_REVERSE`), half-bridge output state enum, PMODE enum, IMODE enum, fault status bitmask definitions, per-instance config container struct, per-instance runtime container struct, SigMapping entry struct. |
| `Gp_Drv8876_Cfg.h` | Required | Configuration macro header file. | Feature switches (`GP_DRV8876_CFG_DEV_ERROR_DETECT`, `GP_DRV8876_CFG_MAINFUNCTION_ENABLE`, `GP_DRV8876_CFG_HALF_BRIDGE_ENABLE`), version macros, core enable switches, per-core instance counts. Includes `Std_Types.h`. |
| `Gp_Drv8876_Cfg.c` | Required | Configuration data implementation file. | Per-core configuration tables (instance count, per-instance config container array, SigMapping table), const data under MemMap. |
| `Gp_Drv8876_CfgData.h` | Required | Configuration data declaration header file. | `extern` declarations for configuration tables and containers, config container struct forward references. |
| `Gp_Drv8876_Callout.h` | Required | Platform adaptation interface header file. | Callout prototypes: `Gp_Drv8876_CalloutGetCoreId`, `Gp_Drv8876_CalloutWrDioCh`, `Gp_Drv8876_CalloutReadDioCh`, `Gp_Drv8876_CalloutSetPwmPerdAndDuty`, `Gp_Drv8876_CalloutGetAdcRaw`, `Gp_Drv8876_CalloutDelayUs`. |
| `Gp_Drv8876_Callout.c` | Required | Platform adaptation implementation file. | Callout integration stubs or project adaptation implementations. |
| `Gp_Drv8876_MemMap.h` | Required | Memory section mapping header file. | MemMap macro definitions for CODE, CONST (per-core and global), and RUNTIME RAM sections. Included by all section-managed FC files. |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `Gp_Drv8876_Cfg.h` | `Std_Types.h` (external) | References `Std_ReturnType`, `uint8/uint16/uint32`, `boolean`, `STD_ON/STD_OFF`. `Std_Types.h` is an external platform header, not created by this FC. |
| `Gp_Drv8876_Types.h` | `Gp_Drv8876_Cfg.h` | Type definitions (enums, structs) depend on configuration macros (e.g., instance count for array sizing, feature switches for struct field inclusion). |
| `Gp_Drv8876_Callout.h` | `Gp_Drv8876_Types.h` | Callout prototypes reference FC public types and standard types. |
| `Gp_Drv8876_CfgData.h` | `Gp_Drv8876_Types.h` | Configuration data declarations reference types defined in `Types.h` (config container struct, SigMapping struct). |
| `Gp_Drv8876.h` | `Gp_Drv8876_CfgData.h` | External API header exposes public APIs and obtains type visibility through `CfgData.h` → `Types.h` → `Cfg.h` chain. |
| `Gp_Drv8876.c` | `Gp_Drv8876.h` | Implements external APIs declared in `Gp_Drv8876.h`. |
| `Gp_Drv8876.c` | `Gp_Drv8876_Callout.h` | Calls hardware and platform callouts for all DIO, PWM, ADC, delay, and core-ID dependencies. |
| `Gp_Drv8876.c` | `Gp_Drv8876_MemMap.h` | Places code and runtime data into memory sections via MemMap macros. |
| `Gp_Drv8876_Cfg.c` | `Gp_Drv8876_CfgData.h` | Defines configuration tables declared in `CfgData.h`. |
| `Gp_Drv8876_Cfg.c` | `Gp_Drv8876_MemMap.h` | Places configuration const data into memory sections. |
| `Gp_Drv8876_Callout.c` | `Gp_Drv8876_Callout.h` | Implements callout stubs or project adaptation logic. |
| `Gp_Drv8876_Callout.c` | `Gp_Drv8876_MemMap.h` | Places callout adaptation code into memory sections. |
| `Gp_Drv8876_MemMap.h` | All FC-created section-managed files | Included by `Gp_Drv8876.c`, `Gp_Drv8876_Cfg.c`, and `Gp_Drv8876_Callout.c` at section boundaries for CODE, CONST, and RUNTIME RAM placement. |

---

## 10. 架构风险与待确认

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | PMODE/IMODE 软硬件控制方式 | PMODE 和 IMODE 由 MCU DIO 控制还是由硬件固定分压，影响是否需要为 PMODE/IMODE 分配 CalloutWrDioCh 通道以及模式重锁存序列是否可执行。 | 外部接口 §3.4 真值表选择；依赖接口 CalloutWrDioCh 通道数；MainFunction 锁存逻辑。 | 项目确认 PMODE/IMODE 引脚连接方式。若硬件固定，则作为只读配置约束，不分配 DIO 通道。 | | 待评审 |
| R2 | MainFunction 调度策略 | SRS R6 明确标记 MainFunction 为中等风险。当前架构采用异步 MainFunction 模式，若项目要求纯同步接口（去掉 MainFunction），需调整外部接口同步语义和时序管理方式。 | 外部接口 §3.8；配置宏 `GP_DRV8876_CFG_MAINFUNCTION_ENABLE`；所有 Set 接口同步性。 | 项目确认是否需要 MainFunction 周期调度，或改为同步阻塞接口。 | | 待评审 |
| R3 | 独立半桥模式启用 | 项目是否支持独立半桥控制模式未确认。若不支持，`Gp_Drv8876_SetHalfBridgeOutSig` 和 `GP_DRV8876_CFG_HALF_BRIDGE_ENABLE` 应移除或固定返回 `E_NOT_OK`。 | 外部接口 §3.5；配置宏 `GP_DRV8876_CFG_HALF_BRIDGE_ENABLE`。 | 项目确认是否需要独立半桥模式。若不支持，建议接口降级为明确拒绝边界，不纳入正式交付。 | | 待评审 |
| R4 | 初始化默认安全状态 | SRS 未确认默认状态是 Sleep、Coast 还是 Brake。当前架构通过配置表的 per-instance default mode 字段承载，具体值待项目给出。 | `Gp_Drv8876_Init` 行为；配置表 default mode 字段默认值。 | 项目确认上电默认安全状态。 | | 待评审 |
| R5 | 电流反馈接口形态 | 当前架构仅提供 ADC 原始值读取（`GetCurrentRaw`），是否需要在驱动内换算为 mA 值并提供 `GetCurrent` 类接口待确认。 | 外部接口 §3.7；依赖接口 CalloutGetAdcRaw；配置表 RIPROPI/AIPROPI 参数用途。 | 项目确认返回 ADC 原始值、mA 值或两者均支持。若需 mA 接口，架构需新增换算逻辑和 `GetCurrent` API。 | | 待评审 |
| R6 | nFAULT 诊断粒度与故障位定义 | 仅凭 nFAULT 低有效无法区分 UVLO/CPUV/OCP/TSD；是否需要结合其他信号细分故障、故障位掩码的具体 bit 定义未确认。 | 外部接口 §3.6 `Fault_pu32` 位定义；`Gp_Drv8876_Types.h` 故障位掩码常量。 | 项目确认故障位定义和是否需要结合 ADC/VM 采样作故障细分。 | | 待评审 |
| R7 | PWM 参数单位与范围 | H 桥输出接口的 `Period_u32`/`Duty_u32` 单位（ticks/us/ns）和有效范围未确认，影响配置表参数校验边界。 | 外部接口 §3.4；配置表 PWM 参数校验。 | 项目确认 PWM 时间单位和周期/占空比范围。 | | 待评审 |
| R8 | Delay Callout 必要性 | tSLEEP/tWAKE 时序是否需要专用 CalloutDelayUs，还是由 MainFunction 的调用周期自然满足（≥1ms 周期即可隐式满足 tSLEEP/tWAKE）。 | 依赖接口 §8.6；MainFunction 时序管理逻辑。 | 若 MainFunction 调用周期 ≥1ms，可移除 CalloutDelayUs 并依赖周期自然满足时序；否则保留。 | | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议。 | 待评审 |

---

## 附录：架构元信息

- **架构版本**: `V1`
- **架构状态**: `Draft`
- **生成时间**: 2026-05-27 15:30
- **生成/修订说明**: 基于 SRS-Gp_Drv8876 V1 Draft 生成初版架构。采用 IoExtDev 层异步请求-周期处理模式，DIO/PWM/ADC/GetCoreId/Delay 依赖通过 Callout 抽象。外部接口覆盖 Init、MainFunction、模式读写、H 桥/半桥输出设置、故障读取和电流反馈。
- **版本策略**: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。
- **发布条件**: 所有真实风险项均为 `已评审`。
- **变更点总结【简洁版】**:
  - 初版生成。
  - 外部接口：Init, SetDevModeOutSig, GetDevModeInSig, SetHbOutSig, SetHalfBridgeOutSig, GetDevFaultSig, GetCurrentRaw, MainFunction。
  - Callout 依赖：GetCoreId, WrDioCh, ReadDioCh, SetPwmPerdAndDuty, GetAdcRaw, DelayUs。
  - 配置：DEV_ERROR_DETECT, MAINFUNCTION_ENABLE, HALF_BRIDGE_ENABLE, 版本宏。
  - MemMap：CODE, CLEAR_FAR_DATA (per-core), CONST (per-core), CONST (global)。
  - 文件族：9 个文件（含 Callout.h/.c，无 Reg.h/Cali.c）。

---

## 下一步：评审与发布引导

当前架构状态为 **V1 Draft**。请通过以下方式完成评审：

- **推荐评审方式 1**：直接修改第 10 章风险表中的 `状态` 和 `备注` 列。
- **推荐评审方式 2**：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：默认状态为 Coast`。
- 如果所有风险项均认可，可回复：**`全部已评审，R-OTHER 无其他建议，直接发布`**。
- 如果某项需要修改，可回复：**`R5 待修改，备注：新增 GetCurrent 接口返回 mA 值`**。
- 修改完成后仍保持 `V1 Draft`，直到所有真实风险项均为 `已评审` 后发布为 **V1 Released**。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
