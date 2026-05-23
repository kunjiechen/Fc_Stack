# 《Gp_NCA95yy 软件架构设计》

**Gp_NCA95yy_Architecture Design**

项目编号/Project number: Gp_NCA95yy
保密性/Security: **内部使用**

**Document Properties**
Status: **Draft**
架构版本: **V1**
架构状态: **Draft**
输出模式: **Formal Draft**
生成时间: 2026-05-23

---

**Approved Versions**

Current Document version **V1** is **Draft**.

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| V1 | Draft | TBD | TBD | TBD |

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| V1 | 2026-05-23 | AI-generated | 初版生成，基于 SRS Gp_NCA95yy Draft | Draft |

---

## 1. FC总结介绍

- **架构版本**: V1
- **架构状态**: Draft
- **输出模式**: Formal Draft
- **生成时间**: 2026-05-23
- **变更点总结**: 初版生成，基于 `Gp_NCA95yy` SRS (Draft) 需求提取。
- **FC名称**: `Gp_NCA95yy`
- **FC功能介绍**: `Gp_NCA95yy` 是 NCA9539-Q1 16-bit I2C GPIO 扩展器芯片的驱动模块，封装芯片初始化、GPIO 方向配置、输入读取（含极性反转）、输出写入（含读改写保护）、中断检测与响应、芯片复位恢复，以及 I2C 通信故障诊断和 DET 错误检测功能。
- **应用场景**: 当 MCU 需要通过 I2C 总线扩展额外 16 路 GPIO（Port 0: P00-P07, Port 1: P10-P17），且同一 I2C 总线上最多挂载 4 片 NCA9539-Q1 芯片时，由本模块向上层提供引脚级 GPIO 访问和芯片级故障诊断能力。
- **架构设计思路**: 采用 IoExtDev 层标准 FC 架构，对外提供稳定的语义化读写接口和故障诊断接口，通过固定的 Callout 依赖接口抽象底层通信和当前核获取，通过配置表管理多芯片实例的地址、默认方向、默认输出和极性映射。MainFunction 周期检测 INT 中断并更新内部状态。DET 机制覆盖所有对外接口的参数有效性检查。
- **AUTOSAR架构层级**: ECU Abstraction Layer
- **当前软件架构所处层级**: IoExtDev

---

## 2. 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| SRS-GPNCA95YY-FUNC-0001 | 驱动初始化 | `Gp_NCA95yy_Init` + config tables | Covered | Init 遍历配置表加载默认方向/输出/极性到各芯片寄存器。 |
| SRS-GPNCA95YY-FUNC-0002 | GPIO 方向配置 | `Gp_NCA95yy_Init` (Init-phase) | Covered with constraint | 方向配置默认仅在 Init 阶段生效；运行时修改若项目后续确认需要，应触发架构升级而非保留条件接口。 |
| SRS-GPNCA95YY-FUNC-0003 | GPIO 输入读取 | `Gp_NCA95yy_GetGpInSig` | Covered | 通过 I2C 读取 Input Port 寄存器并应用极性反转。 |
| SRS-GPNCA95YY-FUNC-0004 | GPIO 输出写入 | `Gp_NCA95yy_SetGpOutSig` | Covered | 读改写机制保护同 port 其他 bit。 |
| SRS-GPNCA95YY-FUNC-0005 | 输入极性反转配置 | `Gp_NCA95yy_Init` (Init-phase) | Covered with constraint | 极性配置默认仅在 Init 阶段生效；运行时修改若项目后续确认需要，应触发架构升级而非保留条件接口。 |
| SRS-GPNCA95YY-FUNC-0006 | 中断检测与响应 | `Gp_NCA95yy_MainFunction` + CalloutReadDio (INT pin) | Covered | MainFunction 采样 INT 引脚，读 Input Port 识别变化引脚。 |
| SRS-GPNCA95YY-FUNC-0007 | 芯片复位处理 | Internal recovery logic + `Gp_NCA95yy_MainFunction` | Covered | 检测不一致或上层请求时恢复寄存器。外部 RESET 触发源待确认。 |
| SRS-GPNCA95YY-FUNC-0008 | MainFunction 周期处理 | `Gp_NCA95yy_MainFunction` | Covered | INT 采样、中断评估、pending 输入变化上报。 |
| SRS-GPNCA95YY-IF-0001 | Init 接口 | `Gp_NCA95yy_Init(void)` | Covered | 无返回值，故障通过内部标记记录。 |
| SRS-GPNCA95YY-IF-0002 | MainFunction 接口 | `Gp_NCA95yy_MainFunction(void)` | Covered | 无返回值，周期调度。 |
| SRS-GPNCA95YY-IF-0003 | GPIO 输入读取接口 | `Gp_NCA95yy_GetGpInSig(uint16 Id_u16, uint8* State_pu8)` | Covered | 返回 E_OK / E_NOT_OK。 |
| SRS-GPNCA95YY-IF-0004 | GPIO 输出写入接口 | `Gp_NCA95yy_SetGpOutSig(uint16 Id_u16, uint8 State_u8)` | Covered | 读改写，返回 E_OK / E_NOT_OK。 |
| SRS-GPNCA95YY-IF-0005 | 故障诊断信息读取接口 | `Gp_NCA95yy_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` | Covered | 位掩码输出 I2C 错误、未初始化、初始化失败、中断异常。 |
| SRS-GPNCA95YY-IF-0006 | DET 错误检测 | DET mechanism (all external APIs) | Covered | 空指针、Id 越界、未初始化、参数范围检测，触发 DET ReportError。 |
| SRS-GPNCA95YY-CFG-0001 | I2C 设备地址配置 | `Gp_NCA95yy_Cfg.c` / `Gp_NCA95yy_CfgData.h` config table | Covered | 有效地址枚举 0x74-0x77。 |
| SRS-GPNCA95YY-CFG-0002 | 芯片实例数量配置 | `Gp_NCA95yy_Cfg.h` macro + config table | Covered | 0..4，0 时所有接口不执行芯片访问。 |
| SRS-GPNCA95YY-CFG-0003 | GPIO 默认方向配置 | `Gp_NCA95yy_Cfg.c` config table | Covered | 每芯片 Port 0/1 方向位图。 |
| SRS-GPNCA95YY-CFG-0004 | GPIO 默认输出电平配置 | `Gp_NCA95yy_Cfg.c` config table | Covered | 每芯片 Port 0/1 输出位图。 |
| SRS-GPNCA95YY-CFG-0005 | 中断使能与去抖配置 | `Gp_NCA95yy_Cfg.c` config table | Covered | 每芯片中断使能开关 + 去抖阈值。 |
| SRS-GPNCA95YY-DIAG-0001 | I2C 通信故障检测 | FaultState (runtime) + `GetDevFaultSig` | Covered | NACK/超时后置位 Bit 0，恢复后清除。 |
| SRS-GPNCA95YY-DIAG-0002 | 未初始化访问检测 | DET (all external APIs except Init) | Covered | 未初始化实例访问时 DET + E_NOT_OK。 |
| SRS-GPNCA95YY-DIAG-0003 | 中断异常监控 | FaultState (runtime) + `GetDevFaultSig` | Covered | INT 持续有效超时后置位 Bit 3。 |
| SRS-GPNCA95YY-DIAG-0004 | 参数有效性检查 | DET (all external APIs) | Covered | Id 越界、空指针、State 非 0/1、方向不匹配检查。 |
| SRS-GPNCA95YY-TIM-0001 | I2C 总线时序约束 | Dependency: I2C callout /底层 I2C 驱动 | Covered | 由底层 I2C 驱动保证，模块级不重复保证。 |
| SRS-GPNCA95YY-TIM-0002 | 复位恢复时序 | Internal reset recovery logic | Covered | t_rec(rst) >= 200ns + t_rst >= 400ns 等待。 |
| SRS-GPNCA95YY-TIM-0003 | 中断响应时序 | `MainFunction` period configuration | Covered | t_v(INT_N)/t_rst(INT_N) 由芯片硬件保证。 |
| SRS-GPNCA95YY-TIM-0004 | MainFunction 调用周期 | Project schedule config | Covered | 建议 1-10ms，通过配置项设定，执行时间 < 50% 周期。 |
| SRS-GPNCA95YY-SAFE-0001 | 安全等级要求 | All architecture objects | Covered | ASIL-D 约束所有功能、接口和实现。 |
| SRS-GPNCA95YY-CODE-0001 | 编码规范符合性 | All C source/header files | Covered | MISRA-C:2012 静态分析验证。 |
| SRS-GPNCA95YY-RES-0001 | 资源消耗约束 | Linker map measurement | Covered | 设计阶段评估，集成阶段实测。 |

---

## 3. 外部接口设计

### 3.1 `Gp_NCA95yy_Init`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95yy_Init(void)` | Initializes all configured chip instances on the current core: for each chip, writes the default direction, output level, and polarity inversion values from the configuration table to the chip registers and transitions the chip to the ready state. | Synchronous | Non-reentrant | `void` | Must be called after the underlying I2C driver is initialized. If the chip count is 0, returns immediately. All chips must be in reset-released state before this call. |

### 3.2 `Gp_NCA95yy_MainFunction`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `void Gp_NCA95yy_MainFunction(void)` | Periodic drive function: samples the INT pin state for each chip, evaluates pending interrupt conditions, reads Input Port registers to identify changed input pins, reports interrupt events to the upper layer, and monitors interrupt anomaly (INT stuck low). | Synchronous | Non-reentrant | `void` | Must be called periodically at the configured cycle (recommended 1-10 ms). Returns immediately if no chip instance is initialized. Must not block or wait indefinitely. |

### 3.3 `Gp_NCA95yy_GetGpInSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95yy_GetGpInSig(uint16 Id_u16, uint8* State_pu8)` | Reads the input state of the specified GPIO pin: resolves Id_u16 to chip/port/pin, reads the corresponding Input Port register via I2C, applies the polarity inversion configuration, and returns the logical pin state. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on invalid Id, uninitialized chip, null pointer, or I2C read failure. | `Id_u16` must encode a valid chip/port/pin within the configured range. `State_pu8` must be non-null. On failure, `*State_pu8` is not modified. |

### 3.4 `Gp_NCA95yy_SetGpOutSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95yy_SetGpOutSig(uint16 Id_u16, uint8 State_u8)` | Sets the output level of the specified GPIO pin using a read-modify-write sequence: reads the current Output Port register via I2C, modifies the target bit, and writes back the entire register to protect other bits in the same port. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on invalid Id, uninitialized chip, invalid State (not 0 or 1), or I2C communication failure. | `Id_u16` must encode a valid chip/port/pin within the configured range. `State_u8` must be 0 or 1. On failure, the Output Port register is not modified. |

### 3.5 `Gp_NCA95yy_GetDevFaultSig`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95yy_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` | Returns the current fault and diagnostic status for the specified chip instance as a bit-mask. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on invalid Id, uninitialized chip, or null pointer. | `Id_u16` must resolve to a configured chip instance. `Fault_pu32` must be non-null. Fault bits: Bit 0 — I2C communication error; Bit 1 — chip uninitialized; Bit 2 — initialization failed; Bit 3 — interrupt anomaly (INT stuck low timeout); Bit 4-31 — reserved. |

---

## 4. 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `GP_NCA95YY_CFG_DEV_ERROR_DETECT` | Global feature switch for development error detection (DET) across all external APIs. | Macro | `STD_ON` | SRS-GPNCA95YY-IF-0006; SRS-GPNCA95YY-DIAG-0004 | `Gp_NCA95yy_Cfg.h`; all external API entry points. | Formal |
| `GP_NCA95YY_CFG_RUNTIME_DIRECTION_CHANGE` | Reserved switch for future architecture version if runtime GPIO direction change is formally introduced. Current V1 architecture does not expose a runtime direction API. | Macro | `STD_OFF` | SRS-GPNCA95YY-FUNC-0002 (项目确认) | `Gp_NCA95yy_Cfg.h` reservation only; not tied to any V1 external API. | Reserved |
| `GP_NCA95YY_CFG_RUNTIME_POLARITY_CHANGE` | Reserved switch for future architecture version if runtime polarity change is formally introduced. Current V1 architecture does not expose a runtime polarity API. | Macro | `STD_OFF` | SRS-GPNCA95YY-FUNC-0005 (项目确认) | `Gp_NCA95yy_Cfg.h` reservation only; not tied to any V1 external API. | Reserved |
| `GP_NCA95YY_SW_MAJOR_VERSION` | Major version number of the module. | Macro | `1` | AUTOSAR standard module versioning. | `Gp_NCA95yy_Cfg.h` | Formal |
| `GP_NCA95YY_SW_MINOR_VERSION` | Minor version number of the module. | Macro | `0` | AUTOSAR standard module versioning. | `Gp_NCA95yy_Cfg.h` | Formal |
| `GP_NCA95YY_SW_PATCH_VERSION` | Patch version number of the module. | Macro | `0` | AUTOSAR standard module versioning. | `Gp_NCA95yy_Cfg.h` | Formal |

---

## 5. 全局变量与运行态策略

状态：**Empty** — 架构不允许对外提供全局变量输出。

内部运行态策略：

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Per-chip init state | `Gp_NCA95yy.c` | Written by `Init`; read by all external APIs. | Set in `Init`, cleared on reset. | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx` | Per-core ownership. |
| Per-chip input cache | `Gp_NCA95yy.c` | Written by `MainFunction`; read by `GetGpInSig` (optional cache-hit path). | Updated each `MainFunction` cycle on INT event. | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx` | Per-core; `MainFunction` writer, external API reader. |
| Per-chip output cache | `Gp_NCA95yy.c` | Written by `SetGpOutSig` / `Init`; read by `SetGpOutSig` (RMW source). | Updated on each output write. | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx` | Per-core; read-write within synchronous API context. |
| Per-chip fault state (bit-mask) | `Gp_NCA95yy.c` | Written by `Init`, `MainFunction`, external APIs on fault; read by `GetDevFaultSig`. | Updated on fault detection and recovery. | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx` | Per-core ownership. |
| Per-chip debounce counter | `Gp_NCA95yy.c` | Written by `MainFunction`; internal only. | Incremented each cycle while INT is low. | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx` | Per-core; `MainFunction` only. |

---

## 6. 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | External API implementations and internal static helper functions. | `GP_NCA95YY_CODE_START` | `GP_NCA95YY_CODE_STOP` | `Gp_NCA95yy.c`, `Gp_NCA95yy_Callout.c` | Standard code section. |
| CONST | Configuration constants shared across cores (if any global mapping data exists). | `GP_NCA95YY_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_NCA95YY_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `Gp_NCA95yy_Cfg.c` | Used for truly global const data. |
| CONST PER-CORE | Per-core configuration constants: chip instance config tables, default direction/output/polarity tables, I2C address tables, interrupt enable and debounce tables. | `GP_NCA95YY_CONST_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA95YY_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_NCA95yy_Cfg.c` | Per-core const data is the primary pattern because chip instances and configuration are core-local. |
| RUNTIME RAM | Runtime variables: per-chip init state, input cache, output cache, fault state, debounce counters. | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA95YY_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `Gp_NCA95yy.c` | Default `CLEAR_FAR_DATA`; per-core since runtime state is core-owned. |
| CALIB | Calibration constants. | `GP_NCA95YY_CONST_FAR_DATA_ALIGN4_CALI_START` | `GP_NCA95YY_CONST_FAR_DATA_ALIGN4_CALI_STOP` | `Gp_NCA95yy_Cali.c` | Empty — no confirmed calibration parameters. |

---

## 7. 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。 | `Empty` |

---

## 8. 依赖接口设计

### 8.1 `Gp_NCA95yy_CalloutI2cWrite`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95yy_CalloutI2cWrite(uint8 Addr_u8, uint8 Reg_u8, const uint8* Data_pcu8, uint16 Size_u16)` | Writes data bytes to the specified register of an I2C device. Used for writing Configuration, Output Port, and Polarity Inversion registers. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on NACK, arbitration loss, or timeout. | `Addr_u8` is the 7-bit I2C device address. `Reg_u8` is the Command Byte (register address). `Data_pcu8` must be non-null; `Size_u16` is 1 or 2 for single-port or dual-port writes. | Project Adaptation / IoExtDev | SRS-GPNCA95YY-FUNC-0001 (Init writes); SRS-GPNCA95YY-FUNC-0004 (output write); chip manual I2C interface. | Formal |

### 8.2 `Gp_NCA95yy_CalloutI2cRead`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95yy_CalloutI2cRead(uint8 Addr_u8, uint8 Reg_u8, uint8* Data_pu8, uint16 Size_u16)` | Reads data bytes from the specified register of an I2C device. Used for reading Input Port, Output Port, Configuration, and Polarity Inversion registers. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on NACK, arbitration loss, or timeout. | `Addr_u8` is the 7-bit I2C device address. `Reg_u8` is the Command Byte. `Data_pu8` must be non-null; `Size_u16` is 1 or 2 for single-port or dual-port reads. | Project Adaptation / IoExtDev | SRS-GPNCA95YY-FUNC-0003 (input read); SRS-GPNCA95YY-FUNC-0006 (interrupt Input Port read); chip manual I2C interface. | Formal |

### 8.3 `Gp_NCA95yy_CalloutReadDio`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA95yy_CalloutReadDio(uint16 Id_u16, uint8* State_pu8)` | Reads the logical state of the INT pin for the specified chip instance. Used by `MainFunction` to detect interrupt assertion. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` on invalid Id or read failure. | `Id_u16` resolves to the chip instance whose INT pin is to be read. `State_pu8` must be non-null. INT pin is active-low; the callout returns the raw MCU GPIO state. | IoMcu / Project Adaptation | SRS-GPNCA95YY-FUNC-0006 (INT detection); SRS-GPNCA95YY-FUNC-0008 (MainFunction INT sampling). | Formal |

### 8.4 `Gp_NCA95yy_CalloutGetCoreId`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `uint32 Gp_NCA95yy_CalloutGetCoreId(void)` | Returns the current core ID used by the FC to select per-core configuration and runtime containers. | Synchronous | Reentrant | Current core ID. | Returned core ID must be valid, enabled in configuration, and usable as per-core index. | Project Adaptation / Platform | Existing per-core FC pattern in current codebase; per-core runtime and MemMap strategy in this architecture. | Formal |

---

## 9. 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `Gp_NCA95yy.c` | Required | Module implementation file. | External API implementations (`Init`, `MainFunction`, `GetGpInSig`, `SetGpOutSig`, `GetDevFaultSig`), internal static helpers (chip register R/W, RMW, Id decode, fault management, reset recovery), runtime state containers. |
| `Gp_NCA95yy.h` | Required | External interface header file. | External API prototypes, `CODE_START` / `CODE_STOP`. |
| `Gp_NCA95yy_Types.h` | Required | Type definition header file. | Chip state enum, fault bit mask defines, per-chip runtime container struct, configuration table struct types. |
| `Gp_NCA95yy_Cfg.h` | Required | Configuration macro header file. | `GP_NCA95YY_CFG_DEV_ERROR_DETECT`, version macros, conditional feature switches, chip count macro, core enable macros. |
| `Gp_NCA95yy_Cfg.c` | Required | Configuration data implementation file. | Per-core per-chip config tables (I2C address, default direction, default output, default polarity, interrupt enable, debounce threshold), Id-to-chip mapping tables. |
| `Gp_NCA95yy_CfgData.h` | Required | Configuration data declaration header file. | `extern` declarations of config tables and mapping tables. |
| `Gp_NCA95yy_Reg.h` | Required | Register definition header file. | NCA9539-Q1 register addresses (Command Bytes 0x00-0x07), bit masks, register reset default values, I2C address enumerations. |
| `Gp_NCA95yy_Callout.h` | Required | Platform adaptation interface header file. | Callout prototypes: `CalloutGetCoreId`, `CalloutI2cWrite`, `CalloutI2cRead`, `CalloutReadDio`. |
| `Gp_NCA95yy_Callout.c` | Required | Platform adaptation implementation file. | Project-specific core ID binding, I2C transaction binding, INT pin DIO routing, board-level adaptation stubs. |
| `Gp_NCA95yy_MemMap.h` | Required | Memory section mapping header file. | MemMap macro definitions for CODE, CONST, RUNTIME RAM, and CALIB sections. |
| `Gp_NCA95yy_Cali.c` | Optional | Calibration data file. | Empty — reserved for future calibration parameters. |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `Gp_NCA95yy_Reg.h` | `Std_Types.h` (external) | Register address and bit mask definitions depend on standard integer types. |
| `Gp_NCA95yy_Cfg.h` | `Std_Types.h` (external); `Gp_NCA95yy_Reg.h` | Configuration macros reference standard types (`STD_ON`/`STD_OFF`); includes `Reg.h` for register default values used in config defaults. |
| `Gp_NCA95yy_Types.h` | `Gp_NCA95yy_Cfg.h` | Type definitions depend on configuration macros (chip count) and standard types. |
| `Gp_NCA95yy_CfgData.h` | `Gp_NCA95yy_Types.h` | Config table declarations use FC types. |
| `Gp_NCA95yy_Callout.h` | `Gp_NCA95yy_Types.h` | Callout prototypes reference FC types and standard return type. |
| `Gp_NCA95yy.h` | `Gp_NCA95yy_CfgData.h` | External API prototypes indirectly depend on config data types. |
| `Gp_NCA95yy.c` | `Gp_NCA95yy.h`, `Gp_NCA95yy_Callout.h`, `Gp_NCA95yy_MemMap.h` | Implements external APIs; uses callouts for I2C/DIO access; places code and runtime data via MemMap. |
| `Gp_NCA95yy_Cfg.c` | `Gp_NCA95yy_CfgData.h`, `Gp_NCA95yy_MemMap.h` | Defines config tables and project data; places const data via MemMap. |
| `Gp_NCA95yy_Callout.c` | `Gp_NCA95yy_Callout.h`, `Gp_NCA95yy_MemMap.h` | Implements project adaptation stubs; places code via MemMap. |
| `Gp_NCA95yy_Cali.c` | `Gp_NCA95yy_CfgData.h`, `Gp_NCA95yy_MemMap.h` | Optional; defines calibration data if needed. |
| `Gp_NCA95yy_MemMap.h` | All FC-created section-managed files | Included by all FC files at section boundaries (code start/stop, data start/stop). |

---

## 10. 架构风险与待确认

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | 运行时方向/极性修改策略 | SRS 将运行时方向修改 (`FUNC-0002`) 和极性修改 (`FUNC-0005`) 标记为"由项目确认"。当前 V1 架构不提供运行时修改接口，仅保留配置开关预留位。 | 若项目后续确需支持运行时修改，需升级架构版本并正式新增外部接口，而不是在 V1 中保留条件接口。 | 与项目确认是否需要在后续版本中支持运行时方向和极性修改。 | | 待评审 |
| R2 | INT 引脚 DIO 读取方式 | 当前架构通过 `Gp_NCA95yy_CalloutReadDio` 抽象 INT 引脚读取。不同项目的 INT 引脚接入方式可能不同（直接 MCU GPIO / IoMcu 信号 / 专用中断线）。 | 若项目已有标准的 IoExtDev INT 处理机制，Callout 接口形式可能需要调整。 | 与硬件团队和 IoMcu 团队确认 INT 引脚接入方式和读取路径。 | | 待评审 |
| R3 | RESET 引脚归属 | SRS 将 RESET 引脚操作标记为"不属于本模块软件责任"，但又提及"若项目明确将 RESET 引脚归属本驱动"的可能性。 | 若 RESET 归属本模块，需增加 RESET 引脚控制 Callout 和复位触发接口。 | 确认 RESET 引脚的软件控制归属。当前架构假设 RESET 由硬件或上层复位管理模块控制。 | | 待评审 |
| R4 | 中断事件上报机制 | SRS 描述 MainFunction 应"向上层报告中断事件"，但未明确上报方式（回调注册 / 事件标记 / 状态查询）。 | 影响 MainFunction 的输出接口设计和内部事件管理结构。 | 确认中断事件的上报方式：通过 `GetDevFaultSig` 轮询还是注册回调函数通知。 | | 待评审 |
| R5 | 极性反转的作用范围 | SRS 说明极性反转仅影响 Input Port 读取结果。需确认对配置为输出的引脚，极性反转寄存器的值是否有意义，以及是否需要在输出路径上做极性处理。 | 影响 `SetGpOutSig` 和 `GetGpInSig` 的内部逻辑。 | 芯片手册确认：Polarity 寄存器对 Output Port 行为无影响。当前架构据此设计。 | | 待评审 |
| R6 | 故障恢复的连续成功阈值 | SRS-DIAG-0001 提到 I2C 通信故障清除条件为"连续成功次数达到项目定义阈值后清除"，但阈值数值待定。 | 影响故障恢复逻辑的 debounce 参数。 | 建议默认值 3 次连续成功，待项目确认后写入配置表。 | | 待评审 |
| R7 | 多核部署策略 | SRS 多处提及"当前核"，暗示可能存在多核部署。架构已采用 per-core MemMap 和 per-core 配置表设计，但未展开多核间的芯片分配和资源隔离策略。 | 若多核场景下不同核访问同一 I2C 总线上的不同芯片，需确认 I2C 总线资源的并发访问保护机制。 | 确认多核部署场景：不同核是否共享同一 I2C 总线，以及 I2C 驱动的并发保护策略。 | | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | | 待评审 |

---

## 附录：架构元信息

- 架构版本: V1
- 架构状态: Draft
- 生成时间: 2026-05-23
- 生成/修订说明: 基于 `Gp_NCA95yy` SRS (Draft) 需求文档初版生成。
- 版本策略: 仅正式架构文件 + 需求文档触发大版本升级，例如 V1 -> V2。
- 发布条件: 所有真实风险项均为 `已评审`。
- 变更点总结【简洁版】:
  - 初版生成。
  - 5 个 Formal 外部接口: `Init`, `MainFunction`, `GetGpInSig`, `SetGpOutSig`, `GetDevFaultSig`。
  - 4 个 Formal Callout: `CalloutGetCoreId`, `CalloutI2cWrite`, `CalloutI2cRead`, `CalloutReadDio`。
  - 4 个 Formal + 2 个 Reserved + 3 个版本宏。
  - 完整的 MemMap、文件列表、文件关系和依赖接口设计。
  - 8 条待评审风险项（含 R-OTHER）。

---

## 下一步：评审与发布引导

当前架构状态为 **V1 Draft**，需完成风险评审后方可发布。

- **推荐评审方式 1**: 直接修改第 10 章风险表中的 `状态` 和 `备注`。
- **推荐评审方式 2**: 在当前窗口回复，例如 `R1、R3 已评审；R2 待修改，备注：INT 改用 IoMcu 信号读取`。
- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。
- 如果某项需要修改，可回复：`R4 待修改，备注：改为回调注册方式上报中断事件`。
- 修改完成后仍保持 V1 Draft，直到所有真实风险项均为 `已评审` 后发布为 V1 Released。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
