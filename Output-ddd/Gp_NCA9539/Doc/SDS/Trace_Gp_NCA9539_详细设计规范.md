# 《Gp_NCA9539 详细设计追溯矩阵》

**Trace_Gp_NCA9539_详细设计规范**

项目编号/Project number: Gp_NCA9539
保密性/Security: 内部

**Document Properties**
Status: **草稿**
追溯版本: **V1**
Author: FC Implementation Workbench
Created: 2026-05-28

---

## 1. 追溯范围

本矩阵记录 Requirement (SRS) / Architecture (SDD) → Detailed Design (SDS) 的覆盖追溯关系。覆盖对象包括：外部接口、内部函数、依赖接口/Callout、配置宏参、配置类型、运行变量、运行参数类型、状态机、DET 检查点、故障项、MemMap 段。

---

## 2. Requirement → Detailed Design 追溯

### 2.1 功能需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-FUNC-0001 | 模块初始化与复位恢复 | `Gp_NCA9539_Init` external API, `I2cReadReg` / `I2cWriteReg` / `VerifyRegisterDefault` internal functions, RESET_RECOVERY state, `CalloutDelayUs` / `CalloutDioWrite`, `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` / `GP_NCA9539_CFG_MAX_I2C_RETRY_COUNT` / `GP_NCA9539_CFG_T_REC_RST_MIN_NS` config macros | §6.1.1 Init 执行步骤, §6.2.4 I2cReadReg, §6.2.5 I2cWriteReg, §6.2.7 VerifyRegisterDefault, §6.3.3 CalloutDioWrite, §6.3.6 CalloutDelayUs, §7 状态机 RESET_RECOVERY, §11 配置宏参 | Covered | Init flow 完整（I2C 验证→默认值校验→配置写入→回读校验），状态机含 RESET_RECOVERY |
| SRS-Gp_NCA9539-FUNC-0002 | 多实例管理 | `GP_NCA9539_CFG_INSTANCE_COUNT` config macro, `Gp_NCA9539_InstanceConfigType` / `Gp_NCA9539_InstanceDataType` / `Gp_NCA9539_RuntimeType` types, per-instance arrays in §10/§11 | §10.1 运行变量 (N = INSTANCE_COUNT), §10.2 运行参数类型, §11.1 INSTANCE_COUNT 宏, §11.2 InstanceConfigType | Covered | Id_u16 统一标识，per-instance 独立状态/配置 |

### 2.2 接口需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-INTF-0001 | GPIO 输出控制接口 | `Gp_NCA9539_SetOutputLevel` external API, `I2cWriteReg` / `ValidateInstance` / `ValidatePort` / `RecordFault` internal functions | §6.1.2 SetOutputLevel (prototype + 执行步骤 + 流程 图) | Covered | 同步写 Output Port，仅已配置输出引脚生效 |
| SRS-Gp_NCA9539-INTF-0002 | GPIO 输入读取接口 | `Gp_NCA9539_GetInputLevel` external API, `I2cReadReg` / `ApplyPolarityInversion` / `UpdateInterruptState` internal functions | §6.1.3 GetInputLevel | Covered | 读 Input Port + 极性反转 + INT\ 读清除 |
| SRS-Gp_NCA9539-INTF-0003 | GPIO 方向配置接口 | `Gp_NCA9539_SetDirection` external API, `I2cWriteReg` / `ValidateInstance` / `ValidatePort` internal functions | §6.1.4 SetDirection | Covered | 写 Configuration 寄存器 (bit=1 input, bit=0 output) |
| SRS-Gp_NCA9539-INTF-0004 | 极性反转配置接口 | `Gp_NCA9539_SetPolarityInversion` external API, `I2cWriteReg` / `ValidateInstance` / `ValidatePort` internal functions | §6.1.5 SetPolarityInversion | Covered | 写 Polarity Inversion 寄存器 (bit=1 invert) |
| SRS-Gp_NCA9539-INTF-0005 | I2C 寄存器读写接口 | `I2cReadReg` / `I2cWriteReg` internal functions, `CalloutI2cWrite` / `CalloutI2cRead` dependency APIs, `FC_Reg.h` register constants | §6.2.4 I2cReadReg, §6.2.5 I2cWriteReg, §6.3.1 CalloutI2cWrite, §6.3.2 CalloutI2cRead, §11 FC_Reg.h | Covered | I2C 帧协议完整（START→地址→命令→数据→STOP），含 Burst 交替行为 |
| SRS-Gp_NCA9539-INTF-0006 | 中断状态读取接口 | `Gp_NCA9539_GetInterruptStatus` external API, `CalloutDioRead` dependency API, `UpdateInterruptState` internal function, `IntPort0Pending_b` / `IntPort1Pending_b` runtime variables | §6.1.6 GetInterruptStatus, §6.3.4 CalloutDioRead, §6.2.8 UpdateInterruptState, §10.1 运行变量 | Covered | INT\ 读取 + 端口识别 + 中断标志维护 |

### 2.3 配置需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-CFG-0001 | 实例数量与 I2C 地址配置 | `GP_NCA9539_CFG_INSTANCE_COUNT` config macro, `Gp_NCA9539_InstanceConfigType.I2cAddr_u8` config type field, `FC_Cfg.c` per-instance I2C address table | §11.1 INSTANCE_COUNT, §11.2.1 InstanceConfigType, §11.2.2 FC_Cfg.c | Covered | 1~4 实例编译期配置 + I2C 地址 per-instance |
| SRS-Gp_NCA9539-CFG-0002 | I2C 通信速率配置 | `GP_NCA9539_CFG_I2C_SPEED_MODE` config macro, `Gp_NCA9539_I2cSpeedModeType` config type | §11.1 I2C_SPEED_MODE, §11.2.1 I2cSpeedModeType | Covered | STANDARD (100kHz) / FAST (400kHz) |
| SRS-Gp_NCA9539-CFG-0003 | 上电默认引脚方向配置 | `Gp_NCA9539_PerPortConfigType` config type, `Gp_NCA9539_Init` Init flow (写 Configuration 寄存器 + 回读校验) | §11.2.1 PerPortConfigType, §6.1.1 Init 执行步骤 | Covered | 每端口独立方向/输出初值/极性配置 |

### 2.4 诊断需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-DIAG-0001 | DET 错误报告 | 6 DET checkpoints, `GP_NCA9539_CFG_DEV_ERROR_DETECT` config macro, `Gp_NCA9539_DetBufferType` / `DetBuffer_ast` runtime | §8 DET设计 (6 检查点), §11.1 DEV_ERROR_DETECT, §10.1 DetBuffer_ast | Covered | 实例 ID/未初始化/重复初始化/端口号/NULL 指针/寄存器地址 |
| SRS-Gp_NCA9539-DIAG-0002 | I2C 通信故障诊断 | `Gp_NCA9539_GetFaultStatus` external API, `RecordFault` internal function, 3 fault items in §9, `FaultActive_ab` / `FaultRegAddr_au8` / `FaultType_au8` runtime variables | §6.1.7 GetFaultStatus, §6.2.6 RecordFault, §9.5 故障项表, §10.1 运行变量 | Covered | NACK 检测 + 故障锁存 + GetFaultStatus 读清除 |
| SRS-Gp_NCA9539-DIAG-0003 | 中断状态丢失诊断 | `Gp_NCA9539_GetInterruptStatus` external API, `UpdateInterruptState` internal function, `IntPort0Pending_b` / `IntPort1Pending_b` runtime variables | §6.1.6 GetInterruptStatus, §6.2.8 UpdateInterruptState, §10.1 中断标志变量 | Covered | 双端口独立标志 + Input Port 读清除 |

### 2.5 时序需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-TIM-0001 | 复位释放后初始化等待时间 | `GP_NCA9539_CFG_T_REC_RST_MIN_NS` config macro, `CalloutDelayUs` dependency API, Init execution steps | §11.1 T_REC_RST_MIN_NS, §6.3.6 CalloutDelayUs, §6.1.1 Init 执行步骤 | Covered | RESET\ 释放后等待 ≥200ns (≥1us 安全裕量) |
| SRS-Gp_NCA9539-TIM-0002 | RESET\ 脉冲宽度控制 | `GP_NCA9539_CFG_T_W_RST_MIN_NS` config macro, `CalloutDioWrite` dependency API | §11.1 T_W_RST_MIN_NS, §6.3.3 CalloutDioWrite | Covered | RESET\ 低电平 ≥6ns |
| SRS-Gp_NCA9539-TIM-0003 | 输出端口稳定时间 | `GP_NCA9539_CFG_T_V_Q_MAX_NS` config macro, Init 回读校验步骤 | §11.1 T_V_Q_MAX_NS, §6.1.1 Init 执行步骤 (写后等待) | Covered | 写后等待 ≥300ns 再回读 |
| SRS-Gp_NCA9539-TIM-0004 | 中断响应时间约束 | Architecture note in §6.1.6 GetInterruptStatus constraints | §6.1.6 GetInterruptStatus Basic Constraints | Partially Covered | 芯片侧 4us 参数为硬件约束，软件延迟预算由项目架构确认 |

### 2.6 安全需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-SAFE-0001 | 功能安全等级约束 (ASIL-B) | DET + 寄存器回读校验 + NACK 检测 + 中断丢失防护 | §8 DET, §9 Fault, §11 REG_READBACK_VERIFY_ENABLE, §11 DEV_ERROR_DETECT | Covered | ASIL-B 安全机制覆盖全部安全相关接口 |
| SRS-Gp_NCA9539-SAFE-0002 | 寄存器和配置校验 | `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` config macro, Init 回读校验步骤, 寄存器回读不一致故障项 | §11.1 REG_READBACK_VERIFY_ENABLE, §6.1.1 Init 执行步骤, §9.5 (寄存器回读不一致故障) | Covered | Init 时回读校验。运行期间回读策略待安全分析确认 (R12) |

### 2.7 编码/资源/过程需求

| Requirement ID | Requirement Summary | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 关闭条件 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-CODE-0001 | MISRA C 编码规范 | Implementation constraint (not design-level) | §2 设计输入 (MISRA C:2012) | Covered | 设计阶段记录约束，编码阶段通过静态分析验证 |
| SRS-Gp_NCA9539-RES-0001 | ROM/RAM/Stack 资源消耗约束 | MemMap 7 段, per-instance O(1) RAM | §12 MemMap设计 | Covered | MemMap 段划分支撑 link map 资源计量 |
| SRS-Gp_NCA9539-COMP-0001 | 需求与测试追溯 | 本追溯矩阵 + Review + Check 伴生产物 | §15 伴生评审与追溯产物, 本文档 | Covered | 支持 ASPICE SWE.6 评估 |

---

## 3. Architecture → Detailed Design 追溯

### 3.1 外部接口

| SDD 接口 | SDS 覆盖对象 | SDS 落点 | 覆盖状态 |
| --- | --- | --- | --- |
| `Gp_NCA9539_Init` | External API §6.1.1 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |
| `Gp_NCA9539_SetOutputLevel` | External API §6.1.2 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |
| `Gp_NCA9539_GetInputLevel` | External API §6.1.3 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |
| `Gp_NCA9539_SetDirection` | External API §6.1.4 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |
| `Gp_NCA9539_SetPolarityInversion` | External API §6.1.5 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |
| `Gp_NCA9539_GetInterruptStatus` | External API §6.1.6 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |
| `Gp_NCA9539_GetFaultStatus` | External API §6.1.7 | prototype + 子功能分解 + 执行步骤 + 调用关系 + 流程图 | **一致** |

### 3.2 依赖接口/Callout

| SDD Callout | SDS 覆盖对象 | SDS 落点 | 覆盖状态 | 变化说明 |
| --- | --- | --- | --- | --- |
| `Gp_NCA9539_CalloutI2cWrite` | Dependency/Callout §6.3.1 | prototype + 关联接口 + 执行步骤 + 流程图 | **一致** | — |
| `Gp_NCA9539_CalloutI2cRead` | Dependency/Callout §6.3.2 | prototype + 关联接口 + 执行步骤 + 流程图 | **一致** | — |
| `Gp_NCA9539_CalloutDioWrite` | Dependency/Callout §6.3.3 | prototype + 关联接口 + 执行步骤 + 流程图 | **一致** | — |
| `Gp_NCA9539_CalloutDioRead` | Dependency/Callout §6.3.4 | prototype + 关联接口 + 执行步骤 + 流程图 | **一致** | — |
| `Gp_NCA9539_CalloutGetCoreId` | Dependency/Callout §6.3.5 | prototype + 关联接口 + 执行步骤 + 流程图 | **一致** (Conditional) | — |
| （SDD 无） | `Gp_NCA9539_CalloutDelayUs` §6.3.6 | prototype + 关联接口 + 执行步骤 + 流程图 | **design-addition (R6)** | 新增延时 Callout，D4/D5 驱动 |

### 3.3 配置宏参

| SDD 宏参 | SDS 覆盖对象 | SDS Status | 覆盖状态 |
| --- | --- | --- | --- |
| `GP_NCA9539_CFG_DEV_ERROR_DETECT` | §11.1 (formal) | formal | **一致** |
| `GP_NCA9539_CFG_SW_MAJOR_VERSION` | §11.1 (formal) | formal | **一致** |
| `GP_NCA9539_CFG_SW_MINOR_VERSION` | §11.1 (formal) | formal | **一致** |
| `GP_NCA9539_CFG_INSTANCE_COUNT` | §11.1 (conditional) | conditional | **一致** |
| `GP_NCA9539_CFG_I2C_SPEED_MODE` | §11.1 (conditional) | conditional | **一致** |
| `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` | §11.1 (formal) | formal | **一致** |
| （SDD 无） | `GP_NCA9539_CFG_MAX_I2C_RETRY_COUNT` §11.1 | formal | **design-addition (R1)** |
| （SDD 无） | `GP_NCA9539_CFG_T_REC_RST_MIN_NS` §11.1 | formal | **design-addition (R2)** |
| （SDD 无） | `GP_NCA9539_CFG_T_W_RST_MIN_NS` §11.1 | formal | **design-addition (R3)** |
| （SDD 无） | `GP_NCA9539_CFG_T_V_Q_MAX_NS` §11.1 | formal | **design-addition (R4)** |
| （SDD 无） | `GP_NCA9539_CFG_FAULT_SELF_RECOVERY_ENABLE` §11.1 | formal | **design-addition (R5)** |
| （SDD 无） | `GP_NCA9539_CFG_I2C_NACK_CONSECUTIVE_LIMIT` §11.1 | formal | **design-addition (R8)** |

### 3.4 运行时状态域

| SDD 运行时域 | SDS 覆盖对象 | SDS 落点 | 覆盖状态 |
| --- | --- | --- | --- |
| Instance state machine | `Gp_NCA9539_InstanceState_ae[N]` | §10.1 变量 #1, §10.2.1 InstanceStateType | **一致** |
| Instance runtime data container | `Gp_NCA9539_InstanceData_ast[N]` (含 DirectionCache / PolarityCache / OutputCache / Interrupt flags / FaultRecord) | §10.1 变量 #2-#9, §10.2.1 InstanceDataType | **一致** |
| I2C transaction buffer | `Gp_NCA9539_I2cBuffer_au8[3]` | §10.1 变量 #11, §10.2.1 RuntimeType | **一致** |
| DET runtime buffer | `Gp_NCA9539_DetBuffer_ast` | §10.1 变量 #12, §10.2.1 RuntimeType (pending-confirm) | **一致** (design-addition R7) |
| Fault record | 内含于 InstanceData_ast (FaultActive_b / FaultRegAddr_u8 / FaultType_u8) | §10.1 变量 #7-#9, §10.2.1 FaultRecordType | **一致** |
| Interrupt bookkeeping | 内含于 InstanceData_ast (IntPort0Pending_b / IntPort1Pending_b) | §10.1 变量 #5-#6, §10.2.1 InstanceDataType | **一致** |
| Configuration cache | 内含于 InstanceData_ast (DirectionCache / PolarityCache / OutputCache) | §10.1 变量 #2-#4, §10.2.1 InstanceDataType | **一致** |
| Readback verify state | Init 内部临时变量 | §6.1.1 Init 执行步骤 | **一致** |

### 3.5 MemMap 段

| SDD MemMap | SDS MemMap | 覆盖状态 |
| --- | --- | --- |
| CODE | §12 CODE | **一致** |
| RUNTIME RAM (per core) | §12 RUNTIME RAM | **一致** |
| CONST (global shared) | §12 CONST (global) | **一致** |
| CONST (per core) | §12 CONST (per core) | **一致** |
| REG CONST | §12 REG CONST | **一致** |
| CALIB | §12 CALIB | **一致** |
| CODE RAM COPY | §12 CODE RAM COPY (Conditional) | **一致** |

### 3.6 文件载体

| SDD 文件 | SDS 文件 (§4) | 覆盖状态 |
| --- | --- | --- |
| FC.c | `Gp_NCA9539.c` (Required) | **一致** |
| FC.h | `Gp_NCA9539.h` (Required) | **一致** |
| FC_Types.h | `Gp_NCA9539_Types.h` (Required) | **一致** |
| FC_Cfg.h | `Gp_NCA9539_Cfg.h` (Required) | **一致** |
| FC_CfgData.h | `Gp_NCA9539_CfgData.h` (Required) | **一致** |
| FC_Cfg.c | `Gp_NCA9539_Cfg.c` (Required) | **一致** |
| FC_Reg.h | `Gp_NCA9539_Reg.h` (Required) | **一致** |
| FC_Callout.h | `Gp_NCA9539_Callout.h` (Required) | **一致** |
| FC_Callout.c | `Gp_NCA9539_Callout.c` (Required) | **一致** |
| FC_MemMap.h | `Gp_NCA9539_MemMap.h` (Required) | **一致** |
| FC_Cali.c | `Gp_NCA9539_Cali.c` (Conditional) | **一致** |
| FC_Internal.h | 未创建（无跨文件内部复用需求） | **省略**（有理由） |

---

## 4. 覆盖统计

| 类别 | 总数 | Covered | Partially Covered | 覆盖率 |
| --- | --- | --- | --- | --- |
| SRS Requirements | 22 | 21 | 1 (TIM-0004) | 95% |
| SDD External APIs | 7 | 7 | 0 | 100% |
| SDD Callouts | 5 | 5 | 0 (6 SDS Callouts, +1 design-addition) | 100% |
| SDD Config Macros | 6 | 6 | 0 (12 SDS Macros, +6 design-addition) | 100% |
| SDD Runtime Domains | 8 | 8 | 0 | 100% |
| SDD MemMap Sections | 7 | 7 | 0 | 100% |
| SDD Files | 12 | 11 | 0 (Internal.h 省略有理由) | 92% |
| ChipView D1-D8 Domains | 8 | 8 | 0 | 100% |

---

## 5. 未覆盖/部分覆盖说明

| 对象 | 状态 | 原因 | 关闭条件 |
| --- | --- | --- | --- |
| SRS-Gp_NCA9539-TIM-0004 (中断响应时间约束) | Partially Covered | 软件中断延迟受 MCU 中断延迟 + I2C 通信时间影响，整体延迟预算需集成阶段分配 | 集成测试阶段确认 |
| FC_Internal.h | 省略 | 无跨文件内部复用需求 (implementation-rules §7.3) | 若编码时发现跨文件复用需求，可补充 |
