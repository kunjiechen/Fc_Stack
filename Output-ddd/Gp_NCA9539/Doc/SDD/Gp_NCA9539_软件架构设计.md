# 《Gp_NCA9539 软件架构设计》

**Gp_NCA9539_软件架构设计**

**Gp_NCA9539 Software Architecture Design**

项目编号/Project number: Gp_NCA9539
保密性/Security: 内部

**Document Properties**
Status: **草稿**
架构版本: **V1**
架构状态: **Draft**
Author: FC Architecture Workbench
Created: 2026-05-28

**Approved Versions**

Current Document version **V1** is **Draft**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| V1 | Draft | TBD | TBD | TBD |

## 适用说明

本文档适用于 `Gp_NCA9539` 模块的软件架构设计定义。本文档描述模块的外部接口、依赖接口、配置宏参、运行时策略、内存分配与文件族设计，不描述详细实现方案、代码细节或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| V1 | 2026-05-28 | FC Architecture Workbench | 初版生成：基于 NCA9539-Q1 Datasheet Rev1.0 芯片架构视图及 SRS V0.1.0。I2C IoExtDev 架构族，8 个外部接口 + 5 个 Callout 依赖 + 6 个配置宏参 + 8 个运行时状态域 + 7 个 MemMap 段 + 12 个文件载体。MainFunction 判定为不需要。 | Draft |

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
- **生成时间**: 2026-05-28
- **变更点总结**: 初版生成。
- **FC名称**: `Gp_NCA9539`
- **FC功能介绍**: Gp_NCA9539 是 NCA9539-Q1 16位 I2C 总线 GPIO 扩展器芯片的驱动模块。模块通过 I2C 接口（最高 400 kHz Fast-mode）访问芯片的 8 个内部寄存器，实现两个 8 位 GPIO 端口（端口 0: P00~P07，端口 1: P10~P17）的输入读取、输出控制、方向配置和极性反转功能。模块支持最多 4 个芯片实例（通过 A0/A1 硬件地址引脚区分，I2C 地址 0x74~0x77），各实例独立管理。模块提供开漏中断输出（INT\）的监控与响应、硬件复位（RESET\）控制，并内置开发错误检测（DET）、I2C 通信故障诊断和寄存器回读校验等安全机制。
- **应用场景**: 适用于汽车电子、工业自动化等场景中需要通过 I2C 总线扩展 MCU GPIO 引脚的场合。芯片通过 AEC-Q100 Grade 1 认证，工作温度 -40°C 至 125°C，满足 ASIL-B 功能安全等级要求。典型应用包括多路数字输入采集、LED 驱动控制、继电器控制、按键矩阵扫描等。
- **架构设计思路**: 模块采用同步接口设计，所有 GPIO 操作（读写、方向配置、极性反转）均通过 I2C 总线同步完成并立即返回结果，无需 MainFunction 周期调度。外部接口以端口（8 位）为操作粒度，Instance ID（`Id_u16`）统一标识芯片实例。依赖接口全部采用 Callout 机制隔离硬件适配：I2C 读写操作、RESET\ 引脚控制和 INT\ 引脚读取均抽象为 Callout，由项目集成层绑定具体 MCU I2C 外设和 GPIO 引脚。模块内部维护 per-instance 运行时状态（初始化状态、故障记录、中断状态），支持多核场景下的 per-core 数据隔离。配置宏参控制 DET 开关、实例数量、I2C 速率模式和寄存器回读校验等编译期决策。寄存器地址、命令字等硬件常量由 `FC_Reg.h` 独立承载。
- **AUTOSAR架构层级**:
- **当前软件架构所处层级**: `IoExtDev`

说明：
- 当前软件架构所处层级填写项目的正式层级名，如 `IoExtDev`、`IoHwAb`、`Srv`、`Cdd` 等。
- 若项目已有固定层级归属，直接落正式结论，不展开过程性讨论。
- 版本号仅使用 `V1`、`V2`、`V3` 这种整数大版本，不使用 `V1.0`、`V1.1`。
- 仅需求文档输入时生成 `V1`；正式架构文件 + 需求文档输入时升级到下一大版本；草稿架构更新不升级版本。

---

## 2. 需求覆盖表

| Requirement ID | Requirement Summary | Architecture Coverage | Coverage Status | Notes |
| --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-FUNC-0001 | 模块初始化与复位恢复 | `Gp_NCA9539_Init` external API, runtime states (UNINIT→NORMAL→RESET_RECOVERY), `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` config macro, RUNTIME RAM per-instance containers, MemMap CLEAR_FAR_DATA section. | Covered | Init 流程含 I2C 可达性验证、寄存器默认值校验、目标方向/输出/极性配置写入及回读。复位恢复通过状态机转换触发重新初始化。 |
| SRS-Gp_NCA9539-FUNC-0002 | 多实例管理 | `Id_u16` parameter in all external APIs, `GP_NCA9539_CFG_INSTANCE_COUNT` config macro, per-instance runtime state arrays, per-instance configuration tables in `FC_Cfg.c`. | Covered | 实例标识 0~3 对应 I2C 地址 0x74~0x77。各实例初始化状态、配置和中断状态独立存储。 |
| SRS-Gp_NCA9539-INTF-0001 | GPIO 输出控制接口 | `Gp_NCA9539_SetOutputLevel` external API. | Covered | 同步写 Output Port 寄存器（端口 0: 0x02，端口 1: 0x03）。仅已配置为输出的引脚生效。内部调用 I2C Callout Write。 |
| SRS-Gp_NCA9539-INTF-0002 | GPIO 输入读取接口 | `Gp_NCA9539_GetInputLevel` external API. | Covered | 同步读 Input Port 寄存器（端口 0: 0x00，端口 1: 0x01）。返回极性反转后的逻辑值。内部调用 I2C Callout Read。 |
| SRS-Gp_NCA9539-INTF-0003 | GPIO 方向配置接口 | `Gp_NCA9539_SetDirection` external API. | Covered | 同步写 Configuration 寄存器（端口 0: 0x06，端口 1: 0x07）。bit=1 输入，bit=0 输出。内部调用 I2C Callout Write。 |
| SRS-Gp_NCA9539-INTF-0004 | 极性反转配置接口 | `Gp_NCA9539_SetPolarityInversion` external API. | Covered | 同步写 Polarity Inversion 寄存器（端口 0: 0x04，端口 1: 0x05）。bit=1 反转。内部调用 I2C Callout Write。 |
| SRS-Gp_NCA9539-INTF-0005 | I2C 寄存器读写接口 | Internal static functions `I2cReadReg` / `I2cWriteReg`, `Gp_NCA9539_CalloutI2cWrite` / `Gp_NCA9539_CalloutI2cRead` dependency APIs, `FC_Reg.h` register address constants. | Covered | 内部封装 I2C 帧协议：START→器件地址(W)→命令字节→数据→STOP（写）/重复 START→器件地址(R)→数据→NACK→STOP（读）。Burst 行为由芯片自动处理（同寄存器对交替）。 |
| SRS-Gp_NCA9539-INTF-0006 | 中断状态读取接口 | `Gp_NCA9539_GetInterruptStatus` external API, `Gp_NCA9539_CalloutDioRead` dependency API, runtime interrupt bookkeeping in per-instance state. | Covered | 查询 INT\ 引脚电平及触发端口。Input Port 读取后自动清除对应端口中断（芯片特性）。多端口同时触发时分别记录。 |
| SRS-Gp_NCA9539-CFG-0001 | 实例数量与 I2C 地址配置 | `GP_NCA9539_CFG_INSTANCE_COUNT` config macro, per-instance I2C address configuration in `FC_Cfg.c` / `FC_CfgData.h`. | Covered | 编译期配置实例数量（1~4）。每实例 I2C 地址在配置表中指定。 |
| SRS-Gp_NCA9539-CFG-0002 | I2C 通信速率配置 | `GP_NCA9539_CFG_I2C_SPEED_MODE` config macro. | Covered | 编译期选择 STANDARD (100kHz) 或 FAST (400kHz)。速率参数传递给 I2C Callout 实现层。 |
| SRS-Gp_NCA9539-CFG-0003 | 上电默认引脚方向配置 | `FC_Cfg.c` per-instance default direction configuration table, `Gp_NCA9539_Init` flow. | Covered | 初始化时按配置表写入 Configuration 寄存器并回读校验。未指定的引脚保持默认输入状态。 |
| SRS-Gp_NCA9539-DIAG-0001 | DET 错误报告 | `GP_NCA9539_CFG_DEV_ERROR_DETECT` config macro, DET runtime bookkeeping in per-core state, parameter validation in all external APIs. | Covered | 检测：实例 ID 越界、未初始化访问、端口号非法、NULL 指针、寄存器地址越界。DET 报告遵循 AUTOSAR DET 规范。 |
| SRS-Gp_NCA9539-DIAG-0002 | I2C 通信故障诊断 | `Gp_NCA9539_GetFaultStatus` external API, runtime fault bookkeeping (fault instance, fault register address, fault type). | Covered | 检测从机 NACK 响应，记录最近一次通信故障详情。 |
| SRS-Gp_NCA9539-DIAG-0003 | 中断状态丢失诊断 | Runtime interrupt state bookkeeping in per-instance state, `Gp_NCA9539_GetInterruptStatus` API. | Covered | 记录各端口中断状态直到 Input Port 读取完成。多端口同时触发时分别保留各自状态。 |
| SRS-Gp_NCA9539-TIM-0001 | 复位释放后初始化等待时间 | Internal timing in `Gp_NCA9539_Init` flow. | Covered | Init 流程中在 RESET\ 释放后等待 >= 200ns（安全裕量）再发起 I2C 通信。 |
| SRS-Gp_NCA9539-TIM-0002 | RESET\ 脉冲宽度控制 | Internal pulse width control in reset handling path. | Covered | RESET\ 低电平保持时间 >= 6ns（安全裕量），由 CalloutDioWrite 实现层确保。 |
| SRS-Gp_NCA9539-TIM-0003 | 输出端口稳定时间 | Internal timing in write-verify path. | Covered | Output Port 写后等待 >= 300ns 再回读验证。 |
| SRS-Gp_NCA9539-TIM-0004 | 中断响应时间约束 | Architecture note in `Gp_NCA9539_GetInterruptStatus` constraints. | Partially Covered | 芯片侧 4us 参数为硬件特性约束。软件中断延迟受 MCU 中断延迟 + I2C 通信时间影响，整体延迟预算待详细设计阶段分配。 |
| SRS-Gp_NCA9539-SAFE-0001 | 功能安全等级约束 | Document-level ASIL-B constraint, `GP_NCA9539_CFG_DEV_ERROR_DETECT`, `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE`, runtime fault bookkeeping. | Covered | ASIL-B 适用于所有 GPIO 输出/输入/中断功能。安全机制包括 DET、寄存器回读校验、I2C NACK 检测、中断丢失防护。 |
| SRS-Gp_NCA9539-SAFE-0002 | 寄存器和配置校验 | `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` config macro, Init 流程中的回读校验逻辑。 | Covered | 初始化时回读 Configuration/Output Port 寄存器。运行期间回读策略（周期/状态切换触发）待详细设计定义。 |
| SRS-Gp_NCA9539-CODE-0001 | MISRA C 编码规范 | Implementation constraint (not architectural). | Covered | 架构阶段记录约束；实现阶段通过静态分析工具验证。 |
| SRS-Gp_NCA9539-RES-0001 | ROM/RAM/Stack 资源消耗约束 | MemMap sections (§6), file list (§9). | Covered | 资源消耗在 link map 阶段评估；每实例 RAM 消耗 O(1)；MemMap 段划分支撑资源计量。 |
| SRS-Gp_NCA9539-COMP-0001 | 需求与测试追溯 | This document + `Trace_Gp_NCA9539_软件架构设计.md`. | Covered | 本架构文档及配套追溯文件共同支撑 ASPICE SWE.6 评估。 |

说明：
- 本表是校验结论，不是需求抽取调试表。
- 不展示候选接口、反向追踪过程、低置信度推理过程或遗漏矩阵。
- `Coverage Status` 取值：`Covered`、`Partially Covered`、`Pending Confirmation`。

---

## 3. 外部接口设计

每个函数优先单独描述，避免 PDF 生成时因超宽表格影响可读性。

### 3.1 `Gp_NCA9539_Init`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_Init(uint16 Id_u16, const Gp_NCA9539_InitConfigType* Config_pcst)` | Initializes the specified chip instance. Verifies I2C accessibility, validates register default values against chip reset defaults, configures port directions, output initial values, and polarity inversion settings per the provided configuration, then performs readback verification of Configuration and Output Port registers. Must be called once per instance before any other API on that instance. | Synchronous | Non-reentrant | `E_OK` on successful initialization; `E_NOT_OK` if instance already initialized, I2C communication fails, register default verification fails, or readback mismatch occurs. | `Id_u16` must map to a configured instance (0 to `GP_NCA9539_CFG_INSTANCE_COUNT`-1). `Config_pcst` must be non-null. Instance must be in UNINIT state. RESET\ pin must be high and VDD stable before calling. A delay >= 200ns after RESET\ release is enforced internally before first I2C communication. Initialization is per-instance and non-reentrant. |

### 3.2 `Gp_NCA9539_SetOutputLevel`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_SetOutputLevel(uint16 Id_u16, uint8 Port_u8, uint8 OutputValue_u8)` | Writes the 8-bit output value to the Output Port register of the specified port (0 or 1) on the specified chip instance via I2C. Only pins configured as outputs are affected; pins configured as inputs ignore the corresponding output bit. | Synchronous | Reentrant | `E_OK` on successful I2C write; `E_NOT_OK` if instance not initialized, port number invalid (>1), or I2C communication fails. | `Id_u16` must reference an initialized instance. `Port_u8` must be 0 or 1. `OutputValue_u8`: bit=0 drives LOW, bit=1 drives HIGH (open-drain: high requires external pull-up). Original output value retained on failure. |

### 3.3 `Gp_NCA9539_GetInputLevel`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_GetInputLevel(uint16 Id_u16, uint8 Port_u8, uint8* InputValue_pu8)` | Reads the 8-bit input port value from the Input Port register of the specified port (0 or 1) on the specified chip instance via I2C. The returned value reflects the actual pin level after polarity inversion (if configured). Input Port registers reflect actual pin levels regardless of pin direction configuration. | Synchronous | Reentrant | `E_OK` on successful I2C read; `E_NOT_OK` if instance not initialized, port number invalid, `InputValue_pu8` is NULL, or I2C communication fails. | `Id_u16` must reference an initialized instance. `Port_u8` must be 0 or 1. `InputValue_pu8` must be non-null (DET reported if NULL). Output pointer content unchanged on failure. |

### 3.4 `Gp_NCA9539_SetDirection`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_SetDirection(uint16 Id_u16, uint8 Port_u8, uint8 Direction_u8)` | Writes the 8-bit direction configuration to the Configuration register of the specified port (0 or 1) on the specified chip instance via I2C. Each bit independently controls the corresponding pin direction: bit=1 configures as input (high-impedance), bit=0 configures as output. | Synchronous | Reentrant | `E_OK` on successful I2C write; `E_NOT_OK` if instance not initialized, port number invalid, or I2C communication fails. | `Id_u16` must reference an initialized instance. `Port_u8` must be 0 or 1. `Direction_u8`: 1=input, 0=output. Switching a pin from output to input may trigger a spurious interrupt. Original configuration retained on failure. |

### 3.5 `Gp_NCA9539_SetPolarityInversion`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_SetPolarityInversion(uint16 Id_u16, uint8 Port_u8, uint8 Polarity_u8)` | Writes the 8-bit polarity inversion configuration to the Polarity Inversion register of the specified port (0 or 1) on the specified chip instance via I2C. Each bit independently controls whether the corresponding input pin value is inverted: bit=1 inverts the logic level read from the Input Port register, bit=0 preserves the original polarity. Polarity inversion affects only Input Port register reads; it does not affect Output Port registers or actual pin levels. | Synchronous | Reentrant | `E_OK` on successful I2C write; `E_NOT_OK` if instance not initialized, port number invalid, or I2C communication fails. | `Id_u16` must reference an initialized instance. `Port_u8` must be 0 or 1. `Polarity_u8`: 1=invert, 0=no inversion. Original configuration retained on failure. |

### 3.6 `Gp_NCA9539_GetInterruptStatus`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_GetInterruptStatus(uint16 Id_u16, uint8* IntStatus_pu8)` | Queries the interrupt status of the specified chip instance. Reads the INT\ pin level via Callout and returns which port(s) triggered the interrupt. Bit 0: port 0 interrupt pending, Bit 1: port 1 interrupt pending. The interrupt is automatically cleared by the chip when the corresponding Input Port register is read (read-clear mechanism). This API preserves internal interrupt bookkeeping until the application reads the Input Port register. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if instance not initialized or `IntStatus_pu8` is NULL. | `Id_u16` must reference an initialized instance. `IntStatus_pu8` must be non-null (DET reported if NULL). INT\ pin must be connected to MCU and configured as input (via Callout). Output pointer content unchanged on failure. |

### 3.7 `Gp_NCA9539_GetFaultStatus`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints |
| --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_GetFaultStatus(uint16 Id_u16, uint32* FaultStatus_pu32)` | Returns the current fault and diagnostic status for the specified chip instance. Reports the most recent I2C communication fault details: whether a fault occurred, the fault register address, and the fault type (e.g., NACK). Fault information is latched until read via this API. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if instance not initialized or `FaultStatus_pu32` is NULL. | `Id_u16` must reference an initialized instance. `FaultStatus_pu32` must be non-null (DET reported if NULL). Fault status is cleared after successful read. |

说明：
- 接口原型按项目正式风格展示，写出完整 C 函数原型。
- 函数名前缀必须保留输入中的 FC/驱动名称，不得自动 CamelCase 化。
- `Description` 使用英文完整句子，描述函数做什么、何时调用、返回值含义。
- `Basic Constraints` 简述初始化前置条件、参数范围、输出指针非空、当前核归属、调用时序等。
- `Init` 和 `MainFunction`（如存在）必须列入本节。
- 所有对外接口在此列出，不做接口遗漏。
- 若接口很短，可合并为一个总表；若接口描述、约束或原型较长，必须使用单函数小表。
- 若存在故障检测、诊断判定或异常状态上报，本节默认应包含一个可读取的故障/诊断状态接口。

---

## 4. 配置宏参设计

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `GP_NCA9539_CFG_DEV_ERROR_DETECT` | Global feature switch for development error detection. Controls DET reporting for invalid instance ID, uninitialized access, invalid port number, NULL pointer, and invalid register address. | Development Error Detect | `STD_ON` | SRS-Gp_NCA9539-DIAG-0001, ASIL-B safety requirement. | `FC_Cfg.h`, parameter validation in all external APIs. | Formal |
| `GP_NCA9539_CFG_SW_MAJOR_VERSION` | Major version number of the Gp_NCA9539 module software. | Vendor Version Release | `1` | Project configuration management requirement. | `FC_Cfg.h`, version reporting. | Formal |
| `GP_NCA9539_CFG_SW_MINOR_VERSION` | Minor version number of the Gp_NCA9539 module software. | Vendor Version Release | `0` | Project configuration management requirement. | `FC_Cfg.h`, version reporting. | Formal |
| `GP_NCA9539_CFG_INSTANCE_COUNT` | Number of NCA9539-Q1 chip instances on the I2C bus. Valid range: 1 to 4. | Count Size | `1` | SRS-Gp_NCA9539-CFG-0001, Datasheet-A0/A1 addressing (max 4 addresses). | `FC_Cfg.h`, `FC_Types.h` (array sizing), `FC_Cfg.c` (config table dimension). | Conditional |
| `GP_NCA9539_CFG_I2C_SPEED_MODE` | I2C bus speed mode selection. `GP_NCA9539_I2C_SPEED_STANDARD` for Standard-mode (100 kHz) or `GP_NCA9539_I2C_SPEED_FAST` for Fast-mode (400 kHz). | Behavior Selection | `GP_NCA9539_I2C_SPEED_FAST` | SRS-Gp_NCA9539-CFG-0002, Datasheet-Dynamic Characteristics (max 400 kHz Fast-mode). | `FC_Cfg.h`, passed to I2C Callout implementation layer. | Conditional |
| `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` | Enables readback verification of Configuration and Output Port registers during initialization. When enabled, Init reads back written register values and compares against expected values. Verification failure causes Init to return `E_NOT_OK`. | Feature Enable | `STD_ON` | SRS-Gp_NCA9539-SAFE-0002 (register readback verification), ASIL-B safety requirement. | `FC_Cfg.h`, `Gp_NCA9539_Init` flow. | Formal |

说明：
- 仅体现通过必要性检查的正式配置宏参。
- `Macro or Parameter` 必须是全大写 C 宏标识符，只允许 `A-Z`、`0-9`、`_`；FC 名称部分也必须转为大写。
- 不体现各核内配置宏参（如 `CORE0_ENABLE` ~ `CORE5_ENABLE`）、各核实例数、核内映射表、硬件绑定明细。
- 如果某子功能已存在正式外部接口控制，则不再重复体现该子功能配置宏开关，除非需求明确要求编译期开关。
- 行为选择宏不是强制项；只有确实存在编译期实现分支时才保留。
- 不为运行态变量、标定参数、每个外部接口、内部 helper 或硬件映射项生成宏。
- `Status` 取值：`Formal`（需求明确确认）、`Conditional`（待条件满足）、`Pending Confirmation`（待确认）、`Not Recommended`。

---

## 5. 全局变量与运行态策略

状态：`Empty` — 架构不允许对外提供全局变量输出。

内部运行态策略：

| Runtime State Area | Owner | Read/Write Side | Lifecycle | Memory Section | Concurrency Strategy |
| --- | --- | --- | --- | --- | --- |
| Instance state machine (per instance) | Internal static array `Gp_NCA9539_InstanceState_ae` in `FC.c` | Read by all external APIs for state check; written by Init. | Set to UNINIT at module load; transitions: UNINIT→NORMAL on Init success; NORMAL→RESET_RECOVERY on reset detection; RESET_RECOVERY→NORMAL on re-init success. | `CLEAR_FAR_DATA` per core | Per-core ownership; no cross-core access. State transitions are non-preemptible within the same instance. |
| Instance runtime data container (per instance) | Internal static struct array `Gp_NCA9539_InstanceData_ast` in `FC.c` | Read by GetInputLevel, GetInterruptStatus, GetFaultStatus; written by Init, SetOutputLevel, SetDirection, SetPolarityInversion, I2C read/write paths. | Allocated per configured instance; initialized in Init; updated during API calls. Contains: current direction cache, current polarity cache, current output cache, interrupt pending flags per port, last fault record. | `CLEAR_FAR_DATA` per core | Per-core ownership. Caches are updated after successful I2C operations. Interrupt flags are set on INT\ detection and cleared on Input Port read. |
| I2C transaction buffer (per call) | Internal stack/static buffer `Gp_NCA9539_I2cBuffer_au8` in `FC.c` | Written by SetOutputLevel, SetDirection, SetPolarityInversion before I2C write; read by GetInputLevel after I2C read. | Stack-local or static buffer allocated per API call. | `CLEAR_FAR_DATA` per core (if static) | Per-core ownership. Buffer sized for max I2C transaction (command byte + 2 data bytes for burst). |
| DET runtime buffer (per core) | Internal static array `Gp_NCA9539_DetBuffer_ast` in `FC.c` (conditional on `GP_NCA9539_CFG_DEV_ERROR_DETECT == STD_ON`) | Written by parameter validation on error; read by DET reporting module. | Allocated per core when DET enabled. Newest-error overwrite policy. | `CLEAR_FAR_DATA` per core | Per-core ownership. DET errors are reported immediately on detection. |
| Fault record (per instance) | Field within instance runtime data container | Written by I2C write/read on NACK; read by GetFaultStatus; cleared on GetFaultStatus read. | Set on first NACK after last clear; latched until read. Contains: fault flag, fault register address, fault type (NACK). | `CLEAR_FAR_DATA` per core | Per-instance; protected by same-core synchronous access. |
| Interrupt bookkeeping (per instance) | Fields within instance runtime data container: `IntPort0Pending_b`, `IntPort1Pending_b` | Set by GetInterruptStatus when INT\ is active; cleared when application reads the corresponding Input Port register. | Updated on each GetInterruptStatus call and each GetInputLevel call. | `CLEAR_FAR_DATA` per core | Per-instance. Both port interrupt flags can be pending simultaneously. Flags preserved until explicit Input Port read clears the chip-side interrupt. |
| Configuration cache (per instance) | Fields within instance runtime data container: `DirectionCache_au8[2]`, `PolarityCache_au8[2]`, `OutputCache_au8[2]` | Written by SetDirection, SetPolarityInversion, SetOutputLevel after successful I2C write; read by readback verification in Init and runtime verification. | Initialized in Init; updated on each successful write operation. | `CLEAR_FAR_DATA` per core | Per-instance. Used for readback verification comparison and for avoiding unnecessary I2C writes. |
| Readback verify state (per Init call) | Local/temporary variables in `Gp_NCA9539_Init` | Read/write within Init scope. | Created at Init entry; discarded at Init return. | Stack (or `CLEAR_FAR_DATA` if static) | Single-call scope; no concurrency concern. |

说明：
- 若无用户明确指令，本节对外全局变量保持 `Empty`。
- 内部运行态策略表用于说明运行时数据的归属、读写关系和生命周期。

---

## 6. 内存分配宏定义

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | All external API implementations (`Gp_NCA9539_Init`, `Gp_NCA9539_SetOutputLevel`, `Gp_NCA9539_GetInputLevel`, `Gp_NCA9539_SetDirection`, `Gp_NCA9539_SetPolarityInversion`, `Gp_NCA9539_GetInterruptStatus`, `Gp_NCA9539_GetFaultStatus`) and internal static helper functions (`I2cReadReg`, `I2cWriteReg`, parameter validation). | `GP_NCA9539_CODE_START` | `GP_NCA9539_CODE_STOP` | `FC.c`, `FC_Callout.c` | Standard CODE section for driver logic. |
| RUNTIME RAM (per core) | All runtime state: instance state machine array, instance runtime data container array (direction/polarity/output caches, interrupt flags, fault records), I2C transaction buffer (if static), DET runtime buffer (conditional, per core). | `GP_NCA9539_CLEAR_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA9539_CLEAR_FAR_DATA_ALIGN4_COREx_STOP` | `FC.c` | Default `CLEAR_FAR_DATA`; per-core with `COREx` notation. Instance count determines array dimensions. DET buffer row conditional on `GP_NCA9539_CFG_DEV_ERROR_DETECT == STD_ON`. |
| CONST (global shared) | Configuration data shared across cores: register reset default values, I2C device address constants, version information. | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `FC_Cfg.c`, `FC_CfgData.h` | For truly shared read-only data accessible from all cores. |
| CONST (per core) | Per-core configuration tables: per-instance default direction configuration, per-instance default output value, per-instance default polarity configuration, per-instance I2C address mapping. | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_COREx_START` | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `FC_Cfg.c`, `FC_CfgData.h` | Each core has its own configuration data region. `COREx` notation represents the repeated pattern for all managed cores. |
| REG CONST | Register address constants (0x00~0x07), I2C device base address (0x74), I2C device address mask (0x07), register reset default values, bit position constants for interrupt status encoding. | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `FC_Reg.h` | Register definitions are shared across all cores. Required because FC controls an I2C register-based external device. |
| CALIB | Reserved for future calibration parameters. | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_CALI_START` | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_CALI_STOP` | `FC_Cali.c` / `FC_CfgData.h` | Currently empty. No calibration parameters confirmed for this IoExtDev module. Thresholds and timing parameters are classified as compile-time configuration. |
| CODE RAM COPY | Reserved for latency-critical code paths (e.g., ISR-context interrupt handling). | `GP_NCA9539_CODE_RAM_COPY_START` | `GP_NCA9539_CODE_RAM_COPY_STOP` | `FC.c` | Conditional. Only required if interrupt handling is implemented in ISR context with strict latency constraints. Currently reserved; activation decision pending interrupt handling strategy confirmation (R3). |

说明：
- 本节采用完整版 MemMap 输出形态。
- 若存在多核按核分段，可使用 `COREx` 总结同构规律，但不得遗漏判断架构正确性所需的段类别。
- `CONST` 不能默认只给 GLOBAL；若存在按核 const 对象、每核配置表或每核 static const 数据，必须增加 `CONST (per core)`。
- 涉及 SPI/I2C/寄存器通信的外设 FC，必须独立列出 `REG CONST` 行，不得将其合并到 `CONST` 中。
- 不将 `NO_CLEAR`、`NEAR` 等条件段作为默认正式推荐；仅在需求明确要求时才体现，并在 Notes 中说明依据。

---

## 7. 全局标定参数设计

| Parameter Name | Type | Initial Value | Description | Status |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的全局标定参数。阈值和时序参数均归类为编译期项目配置（`Cfg`），不属于标定流程可调参数。IoExtDev 族模块默认无标定项。 | `Empty` |

说明：
- 若存在正式标定参数，应体现参数名、类型、初始值和描述。
- 若无明确标定需求，不得为填表而虚构标定项；使用上方的 `Empty` 行即可。
- `Status` 取值：`Formal`（需求明确确认）、`Conditional`（待确认）、`Empty`（无标定项）。

---

## 8. 依赖接口设计

每个依赖接口优先单独描述，避免 Callout 原型、约束、证据和实现边界导致表格过宽。

### 8.1 `Gp_NCA9539_CalloutI2cWrite`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_CalloutI2cWrite(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` | Performs an I2C write transaction to the specified chip instance. The FC calls this callout to write a command byte followed by data bytes to a register. The I2C frame format is: START → device address(W) → command byte → data byte(s) → STOP. The callout implementation handles the I2C peripheral control, device addressing (7-bit address derived from instance configuration and A0/A1 pins), and ACK/NACK checking. Burst write (alternating between port 0 and port 1 registers) is supported by the chip; the callout transmits the data sequence as provided. | Synchronous | Reentrant | `E_OK` on successful I2C write with ACK from slave; `E_NOT_OK` if slave NACK, bus arbitration lost, or timeout. | `Id_u16` identifies the I2C device. `Data_pu8` must be non-null; the first byte is the command byte (register address), followed by data bytes. `Size_u16` includes the command byte (minimum 2). Callout implementation must be reentrant to support multi-instance access from different cores or ISR context. | Project Adaptation (MCU I2C peripheral driver binding) | SRS-Gp_NCA9539-INTF-0005 (I2C register R/W), Datasheet-I2C Interface §A5 (frame protocol, device addressing, burst behavior), Datasheet-SCL/SDA pins §A2. | Formal |

### 8.2 `Gp_NCA9539_CalloutI2cRead`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_CalloutI2cRead(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` | Performs an I2C read transaction from the specified chip instance. The FC calls this callout to write a command byte (register address) then read data bytes from the chip. The I2C frame format is: START → device address(W) → command byte → repeated START → device address(R) → read data byte(s) → NACK → STOP. The callout implementation handles the I2C peripheral control, device addressing, and ACK/NACK checking. Burst read (alternating between port 0 and port 1 registers) is supported by the chip; the callout returns the data sequence as received. | Synchronous | Reentrant | `E_OK` on successful I2C read with data; `E_NOT_OK` if slave NACK, bus arbitration lost, or timeout. | `Id_u16` identifies the I2C device. `Data_pu8` must be non-null; the first byte written is the command byte, subsequent bytes are read data. `Size_u16` is the number of data bytes to read (excluding the command byte write phase). Callout implementation must be reentrant. | Project Adaptation (MCU I2C peripheral driver binding) | SRS-Gp_NCA9539-INTF-0005 (I2C register R/W), Datasheet-I2C Interface §A5 (frame protocol, burst read behavior). | Formal |

### 8.3 `Gp_NCA9539_CalloutDioWrite`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_CalloutDioWrite(uint16 Id_u16, uint8 Level_u8)` | Controls the RESET\ pin level for the specified chip instance. The FC calls this callout to drive the RESET\ pin low to reset the chip or high to release the reset. The callout implementation handles the MCU GPIO pin mapping, level translation, and any board-specific inversion logic. | Synchronous | Reentrant | `E_OK` on successful pin level set; `E_NOT_OK` if pin control fails. | `Id_u16` identifies the chip instance (maps to the corresponding RESET\ GPIO pin). `Level_u8`: `0` for low (reset asserted), `1` for high (reset released). RESET\ low pulse width must meet >= 6ns minimum duration; the FC manages the timing when calling this callout. Callout implementation must be reentrant. | Project Adaptation (MCU DIO driver binding) | SRS-Gp_NCA9539-FUNC-0001 (reset recovery), SRS-Gp_NCA9539-TIM-0002 (RESET pulse width), Datasheet-RESET\ pin §A2 (required connection, external pull-up), Datasheet-Reset §A7. | Formal |

### 8.4 `Gp_NCA9539_CalloutDioRead`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_CalloutDioRead(uint16 Id_u16, uint8* Level_pu8)` | Reads the INT\ pin level for the specified chip instance. The FC calls this callout to determine whether the interrupt output is active (low). The callout implementation handles the MCU GPIO pin mapping and any board-specific inversion logic. | Synchronous | Reentrant | `E_OK` on successful pin level read; `E_NOT_OK` if pin read fails. | `Id_u16` identifies the chip instance (maps to the corresponding INT\ GPIO pin). `Level_pu8` must be non-null; returns `0` for active (low), `1` for inactive (high). INT\ is open-drain; external pull-up is required. Callout implementation must be reentrant. | Project Adaptation (MCU DIO driver binding) | SRS-Gp_NCA9539-INTF-0006 (interrupt status read), Datasheet-INT\ pin §A2 (open-drain, external pull-up required), Datasheet-Interrupt §A6. | Formal |

### 8.5 `Gp_NCA9539_CalloutGetCoreId`

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCA9539_CalloutGetCoreId(uint8* CoreId_pu8)` | Returns the identifier of the currently executing CPU core. The FC uses this callout to select the correct per-core runtime data and configuration tables when deployed in a multi-core environment. | Synchronous | Reentrant | `E_OK` on success; `E_NOT_OK` if core ID cannot be determined. | `CoreId_pu8` must be non-null. Callout implementation must be reentrant and safe to call from any core. | Project Adaptation (platform core identification) | Grounding baseline: IoExtDev family live project `Gp_TLE92104` uses `CalloutGetCoreId`. Multi-core is a real architectural constraint confirmed by live AURIX2G project patterns. | Conditional |

说明：
- 本节仅体现依赖接口（Callout 原型、宏替换钩子），不与 FC 对外接口混排。
- `Description` 使用英文完整句子。
- 当 FC 需要操作 DIO、PWM、ADC、SPI、I2C、外部芯片引脚/寄存器或平台资源时，应抽象为依赖接口/Callout。
- 每个依赖接口必须展示完整 C 原型、英文描述、同步/异步、可重入性、返回值语义、基本约束、实现边界、证据和状态。
- 依赖接口/Callout 函数名前缀必须保留输入中的 FC/驱动名称。
- 若依赖接口较多或内容较长，必须使用单函数小表；只有依赖接口很短时才允许合并为一个总表。
- Callout 原型中不允许使用数组形参写法（如 `TxData_au8[]`），必须使用指针形参。
- SPI/I2C transfer size 默认使用 `uint16 Size_u16`；16bit SPI 帧使用 `uint16*` 数据指针，byte-oriented I2C 使用 `uint8*` 数据指针。
- `Implemented By` 可为 `MCAL`、`IoMcu`、`IoExtDev`、`Service Layer` 或 `Project Adaptation`。
- `Status` 取值：`Formal`、`Conditional`、`Pending Confirmation`、`Not Recommended`。
- 不允许 FC 直接调用裸 MCAL API、直接操作寄存器或直接绑定具体驱动。

---

## 9. 文件列表与文件关系

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `Gp_NCA9539.c` | Required | Driver implementation file. | External API implementations (`Init`, `SetOutputLevel`, `GetInputLevel`, `SetDirection`, `SetPolarityInversion`, `GetInterruptStatus`, `GetFaultStatus`), internal static helper functions (`I2cReadReg`, `I2cWriteReg`, parameter validation), per-core runtime state containers (instance state machine array, instance runtime data array, I2C transaction buffer, DET buffer). |
| `Gp_NCA9539.h` | Required | External interface header file. | External API prototypes, `CODE_START/STOP` section macros, inclusion of `Gp_NCA9539_Cfg.h` and `Gp_NCA9539_CfgData.h`. |
| `Gp_NCA9539_Types.h` | Required | Type definitions header file. | Instance state enum (`UNINIT`, `NORMAL`, `RESET_RECOVERY`), runtime data container struct, init configuration struct, fault status bit definitions, I2C speed mode enum. Includes `Gp_NCA9539_Cfg.h` for config-aware type sizing. |
| `Gp_NCA9539_Cfg.h` | Required | Configuration macro header file. | Feature switches (`DEV_ERROR_DETECT`, `REG_READBACK_VERIFY_ENABLE`), version macros (`SW_MAJOR_VERSION`, `SW_MINOR_VERSION`), count macros (`INSTANCE_COUNT`), behavior selection (`I2C_SPEED_MODE`). Includes `Std_Types.h` and `Gp_NCA9539_Reg.h`. |
| `Gp_NCA9539_Cfg.c` | Required | Configuration data implementation file. | Per-core configuration tables: per-instance default direction, per-instance default output value, per-instance default polarity inversion, per-instance I2C address. Placed under CONST MemMap sections. |
| `Gp_NCA9539_CfgData.h` | Required | Configuration data declaration header file. | `extern` declarations for configuration tables and containers, configuration struct type forward references. Placed under CONST MemMap sections. |
| `Gp_NCA9539_Reg.h` | Required | Register definition header file for the NCA9539-Q1 I2C GPIO expander. | Register addresses (Input Port 0/1: 0x00/0x01, Output Port 0/1: 0x02/0x03, Polarity Inversion 0/1: 0x04/0x05, Configuration 0/1: 0x06/0x07), I2C device base address (0x74) and address mask (0x07), register reset default values, interrupt status bit encoding constants. Required because FC controls an I2C register-based external device. |
| `Gp_NCA9539_Callout.h` | Required | Platform adaptation interface header file. | Callout prototypes: `CalloutI2cWrite`, `CalloutI2cRead`, `CalloutDioWrite`, `CalloutDioRead`, `CalloutGetCoreId`. Required because Callout dependencies exist. |
| `Gp_NCA9539_Callout.c` | Required | Platform adaptation implementation file. | Callout integration stubs or project adaptation implementations: I2C peripheral binding, DIO pin mapping (RESET\, INT\), core ID retrieval. Required because Callout dependencies exist. |
| `Gp_NCA9539_MemMap.h` | Required | Memory section mapping header file. | MemMap macro definitions for CODE, CLEAR_FAR_DATA (per core), CONST (global and per-core), REG CONST, CALIB, and CODE RAM COPY sections. Included by all section-managed FC files. |
| `Gp_NCA9539_Cali.c` | Conditional | Calibration implementation file. | Reserved for future calibration parameters. Currently empty; only generated if calibration parameters are confirmed. IoExtDev family default: no calibration. |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `Gp_NCA9539_Cfg.h` | `Std_Types.h` (external) | References `Std_ReturnType`, `uint8`/`uint16`/`uint32`, `boolean`, `STD_ON`/`STD_OFF`. `Std_Types.h` is an external platform header, not created by this FC. |
| `Gp_NCA9539_Reg.h` | `Std_Types.h` (external) | Register address, I2C device address, and reset default value constants use standard integer types. `Std_Types.h` is not created by this FC. |
| `Gp_NCA9539_Cfg.h` | `Gp_NCA9539_Reg.h` | Configuration macros (`REG_READBACK_VERIFY_ENABLE`) and config defaults reference register addresses and reset default values from `Reg.h`. |
| `Gp_NCA9539_Types.h` | `Gp_NCA9539_Cfg.h` | Type definitions (enums, structs) depend on configuration macros (e.g., `INSTANCE_COUNT` for array sizing, `DEV_ERROR_DETECT` for struct field inclusion). |
| `Gp_NCA9539_Callout.h` | `Gp_NCA9539_Types.h` | Callout prototypes reference FC public types and standard types. |
| `Gp_NCA9539_CfgData.h` | `Gp_NCA9539_Types.h` | Configuration data declarations reference types defined in `Types.h` (InitConfig struct, per-instance config container struct). |
| `Gp_NCA9539.h` | `Gp_NCA9539_CfgData.h` | External API header exposes public APIs and indirectly obtains type visibility through `CfgData.h` → `Types.h` chain. |
| `Gp_NCA9539.c` | `Gp_NCA9539.h` | Implements external APIs declared in `Gp_NCA9539.h`. |
| `Gp_NCA9539.c` | `Gp_NCA9539_Callout.h` | Calls hardware and platform callouts for all I2C, DIO, and core-ID dependencies. |
| `Gp_NCA9539.c` | `Gp_NCA9539_MemMap.h` | Places code and runtime data into memory sections via MemMap macros. |
| `Gp_NCA9539_Cfg.c` | `Gp_NCA9539_CfgData.h` | Defines configuration tables declared in `CfgData.h`. |
| `Gp_NCA9539_Cfg.c` | `Gp_NCA9539_MemMap.h` | Places configuration const data into memory sections (global and per-core CONST). |
| `Gp_NCA9539_Callout.c` | `Gp_NCA9539_Callout.h` | Implements callout stubs or project adaptation logic. |
| `Gp_NCA9539_Callout.c` | `Gp_NCA9539_MemMap.h` | Places callout adaptation code into CODE memory section. |
| `Gp_NCA9539_MemMap.h` | All FC-created section-managed files | Included by `Gp_NCA9539.c`, `Gp_NCA9539_Cfg.c`, and `Gp_NCA9539_Callout.c` at section boundaries for CODE, CONST (global/per-core), RUNTIME RAM, and CALIB placement. |

说明：
- 文件名和 C 标识符中的 `FC` 已替换为实际模块名前缀 `Gp_NCA9539`，保留下划线和大小写。
- 不在本节列出内部学习记录、规则文件或 demo 文件。
- `Std_Types.h` 等平台标准头文件应体现在文件关系中，但不列入本 FC 的待创建文件列表。
- 本 FC 涉及 I2C 寄存器通信，已增加 `Gp_NCA9539_Reg.h`。
- 本 FC 存在 Callout 依赖，已同时列出 `Gp_NCA9539_Callout.h` 与 `Gp_NCA9539_Callout.c`。
- `Gp_NCA9539_MemMap.h` 已作为所有 section-managed FC 文件的包含关系体现。

---

## 10. 架构风险与待确认

填写说明：
- 可以直接修改下表的 `状态` 和 `备注`，也可以在当前窗口直接回复，例如：`R1、R3 已评审；R4 待修改，备注：按 xxx 方案调整`。
- `状态` 只允许填写：`待评审`、`已评审`、`待修改`。
- 若某条为 `待修改` 且 `备注` 为空，则默认按 `Recommended Action` 执行修改；若 `备注` 不为空，则优先按备注执行。
- 若希望直接发布，请将所有真实风险项标为 `已评审`，并将 `R-OTHER` 填为 `已评审` / `备注：无其他建议`。

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | SRS 需求状态 | 当前 SRS 中 22 条需求全部为 Draft 状态（Ready 比例 = 0%）。需求可能发生变更，架构方案存在修订风险。 | §2 需求覆盖表、§3 外部接口、§4 配置宏参、§8 依赖接口 | 建议在需求评审完成后重新对照架构覆盖表，确认无新增/删除/变更需求。 | | 待评审 |
| R2 | 芯片实例数量 | 项目实际使用的 NCA9539-Q1 芯片数量未明确（A0/A1 引脚连接方式未提供）。当前架构假设 1~4 个实例可配置。 | §4 `GP_NCA9539_CFG_INSTANCE_COUNT`、§5 运行时容器数组维度、§9 `FC_Cfg.c` 配置表规模 | 请项目确认硬件设计中实际使用的芯片数量及各实例的 A0/A1 连接方式（I2C 地址）。 | | 待评审 |
| R3 | 中断处理策略 | 中断采用轮询还是 ISR 方式未明确。若采用 ISR 方式，`GetInterruptStatus` 需标记为 ISR-safe，可能需要 CODE RAM COPY 段优化中断延迟。 | §3 `Gp_NCA9539_GetInterruptStatus` 的可重入性约束、§6 CODE RAM COPY 段、§8 `CalloutDioRead` 的中断上下文要求 | 请项目确认中断处理架构（轮询 / ISR / 混合）。 | | 待评审 |
| R4 | 运行期间寄存器回读策略 | SAFE-0002 要求运行期间回读 Configuration 寄存器，但回读频率和触发条件未定义（"在详细设计阶段定义"）。若采用周期回读策略，可能需要增加 `MainFunction`。当前架构判定 `MainFunction` 不需要，基于寄存器回读在初始化阶段和状态切换时执行。 | §1 架构设计思路（MainFunction 判定）、§5 运行时策略（是否需要周期回读状态机） | 请在安全分析阶段确定回读策略：若仅初始化时回读 → 架构不变；若需周期回读 → 增加 `MainFunction`，调整 §3、§5、§6。 | | 待评审 |
| R5 | I2C 通信速率 | 项目实际使用的 I2C 速率（Standard 100kHz 或 Fast 400kHz）未明确。当前架构默认 Fast-mode。 | §4 `GP_NCA9539_CFG_I2C_SPEED_MODE`、时序参数约束 | 请项目确认 I2C 总线速率。 | | 待评审 |
| R6 | RESET\ 和 INT\ 引脚映射 | RESET\ 和 INT\ 引脚各连接到 MCU 的哪个 GPIO 未明确，影响 Callout 硬件绑定设计。 | §8 `CalloutDioWrite`、`CalloutDioRead` 的 `Id_u16` 到 GPIO 映射 | 请项目确认 MCU 端 RESET\ 和 INT\ 的 GPIO 引脚分配。 | | 待评审 |
| R7 | ASIL-B 安全机制 | ASIL-B 要求的具体安全机制（寄存器冗余存储、端到端校验等）未经安全分析确认。当前架构实现了 DET + 寄存器回读校验 + NACK 检测 + 中断丢失防护，但未包含寄存器冗余存储等更高级别安全机制。 | §3 外部接口、§5 DET bookkeeping、§4 配置宏参 | 请在安全分析阶段确认安全机制的充分性，必要时补充。 | | 待评审 |
| R8 | 去初始化/重初始化接口 | SRS 风险表中标记了 `Deinit` 和 `Reinit` 接口为待确认。当前架构未包含这两个外部接口。 | §3 外部接口列表（是否增加 `Deinit`/`Reinit`） | 请项目确认是否需要运行时动态卸载/重初始化能力。 | | 待评审 |
| R9 | 多核部署 | 当前架构包含 per-core 基础设施（CalloutGetCoreId、per-core RUNTIME RAM、per-core CONST），但多核是否为项目实际需求未明确。IoExtDev 族 grounding baseline 确认多核为真实架构约束。 | §5 per-core 运行时容器、§6 per-core MemMap 段、§8 `CalloutGetCoreId` | 请项目确认是否需要多核部署。若单核，可简化 per-core 为全局单例。 | | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议。 | 待评审 |

说明：
- 每条风险项必须有稳定索引，便于用户在窗口中直接引用。
- 必须保留 `R-OTHER` / `其他` 行，供用户自行填写其他方面的建议。
- `备注` 用于记录用户的具体确认意见或修改意见。
- 若任一真实风险项仍为 `待评审` 或 `待修改`，架构状态必须保持 `Draft`。
- 所有真实风险项均为 `已评审` 后，才允许从 `Draft` 发布为 `Released`。

---

## 附录：架构元信息

- **架构版本**: `V1`
- **架构状态**: `Draft`
- **生成时间**: 2026-05-28
- **生成/修订说明**: 初版生成。基于 SRS V0.1.0 + NCA9539-Q1 芯片架构视图。
- **版本策略**: 仅正式架构文件 + 需求文档触发大版本升级，例如 `V1 -> V2`。
- **发布条件**: 所有真实风险项均为 `已评审`。
- **变更点总结【简洁版】**:
  - 初版生成。
  - 外部接口：7 个（Init, SetOutputLevel, GetInputLevel, SetDirection, SetPolarityInversion, GetInterruptStatus, GetFaultStatus）。
  - MainFunction 判定：不需要（无周期采样/状态机推进/去抖/看门狗/缓冲请求处理需求）。
  - 依赖接口：5 个 Callout（I2cWrite, I2cRead, DioWrite, DioRead, GetCoreId）。
  - 配置宏参：6 个（DET, Version×2, InstanceCount, I2cSpeed, ReadbackVerify）。
  - MemMap 段：7 个（CODE, RUNTIME RAM per core, CONST global, CONST per core, REG CONST, CALIB, CODE RAM COPY conditional）。
  - 文件载体：12 个（含 Cali.c 条件文件）。
  - 标定项：空（IoExtDev 族默认无标定）。
  - 风险项：9 条真实风险 + R-OTHER。

---

## 下一步：评审与发布引导

当前架构状态为 **V1 Draft**。请通过以下方式完成评审：

- **推荐评审方式 1**：直接修改第 10 章风险表中的 `状态` 和 `备注` 列。
- **推荐评审方式 2**：在当前窗口回复，例如 `R1、R2 已评审；R5 待修改，备注：按 Standard-mode 配置`。
- 如果所有风险项均认可，可回复：**`全部已评审，R-OTHER 无其他建议，直接发布`**。
- 如果某项需要修改，可回复：**`R5 待修改，备注：改为 Fast-mode 400kHz`**。
- 修改完成后仍保持 `V1 Draft`，直到所有真实风险项均为 `已评审` 后发布为 **V1 Released**。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
