# Trace_Gp_NCA9539_软件架构设计

**SRS → Architecture 追溯矩阵**

项目编号/Project number: Gp_NCA9539
架构版本: V1
架构状态: Draft
追溯日期: 2026-05-28

---

## 1. 覆盖对象

| SRS Requirement ID | SRS Summary | Architecture Element | Element Type | Coverage Status | Architecture Location | Design Decision |
| --- | --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA9539-FUNC-0001 | 模块初始化与复位恢复 | `Gp_NCA9539_Init` | External API | Covered | §3.1 | Init 流程包含 I2C 可达性验证、默认值校验、目标配置写入、回读校验。RESET\ 释放后等待 >= 200ns。状态机 UNINIT→NORMAL。 |
| SRS-Gp_NCA9539-FUNC-0001 | 模块初始化与复位恢复 | Instance state machine (UNINIT/NORMAL/RESET_RECOVERY) | Runtime State | Covered | §5 row 1 | 复位恢复通过状态机转换触发重新初始化流程。 |
| SRS-Gp_NCA9539-FUNC-0001 | 模块初始化与复位恢复 | `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` | Config Macro | Covered | §4 | 初始化时回读 Configuration/Output Port 寄存器并比较。 |
| SRS-Gp_NCA9539-FUNC-0002 | 多实例管理 | `Id_u16` parameter in all external APIs | External API | Covered | §3 all APIs | 实例标识 0~3 对应 I2C 地址 0x74~0x77。 |
| SRS-Gp_NCA9539-FUNC-0002 | 多实例管理 | `GP_NCA9539_CFG_INSTANCE_COUNT` | Config Macro | Covered | §4 | 编译期配置实例数量上限（1~4）。 |
| SRS-Gp_NCA9539-FUNC-0002 | 多实例管理 | Per-instance runtime state arrays | Runtime State | Covered | §5 rows 1-2 | 每实例独立存储状态、方向/极性/输出缓存、中断标志、故障记录。 |
| SRS-Gp_NCA9539-INTF-0001 | GPIO 输出控制接口 | `Gp_NCA9539_SetOutputLevel` | External API | Covered | §3.2 | 同步写 Output Port 寄存器（0x02/0x03）。仅已配置为输出的引脚生效。 |
| SRS-Gp_NCA9539-INTF-0001 | GPIO 输出控制接口 | `Gp_NCA9539_CalloutI2cWrite` | Dependency API | Covered | §8.1 | I2C 写操作 Callout 承载 Output Port 寄存器写入。 |
| SRS-Gp_NCA9539-INTF-0002 | GPIO 输入读取接口 | `Gp_NCA9539_GetInputLevel` | External API | Covered | §3.3 | 同步读 Input Port 寄存器（0x00/0x01）。返回极性反转后的逻辑值。 |
| SRS-Gp_NCA9539-INTF-0002 | GPIO 输入读取接口 | `Gp_NCA9539_CalloutI2cRead` | Dependency API | Covered | §8.2 | I2C 读操作 Callout 承载 Input Port 寄存器读取。 |
| SRS-Gp_NCA9539-INTF-0003 | GPIO 方向配置接口 | `Gp_NCA9539_SetDirection` | External API | Covered | §3.4 | 同步写 Configuration 寄存器（0x06/0x07）。1=输入，0=输出。 |
| SRS-Gp_NCA9539-INTF-0003 | GPIO 方向配置接口 | `Gp_NCA9539_CalloutI2cWrite` | Dependency API | Covered | §8.1 | 复用 I2C 写 Callout。 |
| SRS-Gp_NCA9539-INTF-0004 | 极性反转配置接口 | `Gp_NCA9539_SetPolarityInversion` | External API | Covered | §3.5 | 同步写 Polarity Inversion 寄存器（0x04/0x05）。1=反转。 |
| SRS-Gp_NCA9539-INTF-0004 | 极性反转配置接口 | `Gp_NCA9539_CalloutI2cWrite` | Dependency API | Covered | §8.1 | 复用 I2C 写 Callout。 |
| SRS-Gp_NCA9539-INTF-0005 | I2C 寄存器读写接口 | Internal static `I2cReadReg` / `I2cWriteReg` | Internal Function | Covered | §3 (not externally exposed) | 内部封装 I2C 帧协议。对外不可见。 |
| SRS-Gp_NCA9539-INTF-0005 | I2C 寄存器读写接口 | `Gp_NCA9539_CalloutI2cWrite` / `Gp_NCA9539_CalloutI2cRead` | Dependency API | Covered | §8.1, §8.2 | I2C 读写 Callout 承载底层 I2C 帧传输。 |
| SRS-Gp_NCA9539-INTF-0005 | I2C 寄存器读写接口 | `Gp_NCA9539_Reg.h` | File Carrier | Covered | §9.1 | 寄存器地址、I2C 设备基地址和地址掩码常量。 |
| SRS-Gp_NCA9539-INTF-0006 | 中断状态读取接口 | `Gp_NCA9539_GetInterruptStatus` | External API | Covered | §3.6 | 查询 INT\ 引脚电平及触发端口（bit0: port0, bit1: port1）。 |
| SRS-Gp_NCA9539-INTF-0006 | 中断状态读取接口 | `Gp_NCA9539_CalloutDioRead` | Dependency API | Covered | §8.4 | INT\ 引脚电平读取 Callout。 |
| SRS-Gp_NCA9539-INTF-0006 | 中断状态读取接口 | Interrupt bookkeeping (IntPort0Pending/IntPort1Pending) | Runtime State | Covered | §5 row 6 | 记录未处理的中断端口，防止丢失。 |
| SRS-Gp_NCA9539-CFG-0001 | 实例数量与 I2C 地址配置 | `GP_NCA9539_CFG_INSTANCE_COUNT` | Config Macro | Covered | §4 | 编译期配置实例数量（1~4）。 |
| SRS-Gp_NCA9539-CFG-0001 | 实例数量与 I2C 地址配置 | Per-instance I2C address in `FC_Cfg.c` | Config Data | Covered | §9.1 `FC_Cfg.c` | 每实例 I2C 地址在配置表中指定。 |
| SRS-Gp_NCA9539-CFG-0002 | I2C 通信速率配置 | `GP_NCA9539_CFG_I2C_SPEED_MODE` | Config Macro | Covered | §4 | STANDARD / FAST 编译期选择。 |
| SRS-Gp_NCA9539-CFG-0003 | 上电默认引脚方向配置 | Per-instance default config tables in `FC_Cfg.c` | Config Data | Covered | §9.1 `FC_Cfg.c` | 默认方向/输出值/极性配置表。 |
| SRS-Gp_NCA9539-CFG-0003 | 上电默认引脚方向配置 | `Gp_NCA9539_Init` | External API | Covered | §3.1 | Init 流程中按配置表写入并回读校验。 |
| SRS-Gp_NCA9539-DIAG-0001 | DET 错误报告 | `GP_NCA9539_CFG_DEV_ERROR_DETECT` | Config Macro | Covered | §4 | DET 全局开关，默认 STD_ON。 |
| SRS-Gp_NCA9539-DIAG-0001 | DET 错误报告 | Parameter validation in all external APIs | Internal Logic | Covered | §3 (constraints), §5 row 4 | 非法实例 ID、未初始化、非法端口号、NULL 指针、非法寄存器地址的检测和报告。 |
| SRS-Gp_NCA9539-DIAG-0001 | DET 错误报告 | Per-core DET runtime buffer | Runtime State | Covered | §5 row 4 | DET 错误信息存储，newest-error overwrite。 |
| SRS-Gp_NCA9539-DIAG-0002 | I2C 通信故障诊断 | `Gp_NCA9539_GetFaultStatus` | External API | Covered | §3.7 | 查询最近 I2C NACK 故障：故障标志、寄存器地址、故障类型。 |
| SRS-Gp_NCA9539-DIAG-0002 | I2C 通信故障诊断 | Fault record in instance runtime data | Runtime State | Covered | §5 row 5 | NACK 故障 latched until read。 |
| SRS-Gp_NCA9539-DIAG-0003 | 中断状态丢失诊断 | Interrupt bookkeeping per instance | Runtime State | Covered | §5 row 6 | 多端口同时触发分别记录；Input Port 读取前不丢弃。 |
| SRS-Gp_NCA9539-DIAG-0003 | 中断状态丢失诊断 | `Gp_NCA9539_GetInterruptStatus` | External API | Covered | §3.6 | 返回所有 pending 端口的中断状态。 |
| SRS-Gp_NCA9539-TIM-0001 | 复位释放后初始化等待时间 | Internal timing in `Gp_NCA9539_Init` | Internal Logic | Covered | §3.1 constraints | RESET\ 释放后 >= 200ns 延迟再发起 I2C。 |
| SRS-Gp_NCA9539-TIM-0002 | RESET\ 脉冲宽度控制 | Internal pulse width in reset path | Internal Logic | Covered | §8.3 constraints | >= 6ns 低电平保持（Callout 实现层确保）。 |
| SRS-Gp_NCA9539-TIM-0003 | 输出端口稳定时间 | Internal timing in write-verify path | Internal Logic | Covered | §3.2 | Output Port 写后 >= 300ns 再回读。 |
| SRS-Gp_NCA9539-TIM-0004 | 中断响应时间约束 | Architecture note in `GetInterruptStatus` | Architecture Constraint | Partially Covered | §3.6 | 芯片侧 4us 为硬件约束；软件整体中断延迟预算待详细设计分配。 |
| SRS-Gp_NCA9539-SAFE-0001 | 功能安全等级约束 | Document-level ASIL-B constraint | Architecture Constraint | Covered | §1, §4, §5 | DET + 回读校验 + NACK 检测 + 中断丢失防护构成安全机制组合。 |
| SRS-Gp_NCA9539-SAFE-0002 | 寄存器和配置校验 | `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` | Config Macro | Covered | §4 | 回读校验功能开关，默认 STD_ON。 |
| SRS-Gp_NCA9539-SAFE-0002 | 寄存器和配置校验 | Init readback verification logic | Internal Logic | Covered | §3.1 | 初始化时回读 Configuration/Output Port。运行期间回读策略待定（R4）。 |
| SRS-Gp_NCA9539-CODE-0001 | MISRA C 编码规范 | (Implementation constraint) | Process Constraint | Covered | N/A (architecture only) | 架构阶段记录；实现阶段静态分析验证。 |
| SRS-Gp_NCA9539-RES-0001 | ROM/RAM/Stack 资源消耗约束 | MemMap sections (§6) | MemMap | Covered | §6 | 7 个 MemMap 段支撑资源分区计量。 |
| SRS-Gp_NCA9539-RES-0001 | ROM/RAM/Stack 资源消耗约束 | File list (§9) | File Carrier | Covered | §9 | 12 个文件载体明确资源归属。 |
| SRS-Gp_NCA9539-COMP-0001 | 需求与测试追溯 | `Trace_Gp_NCA9539_软件架构设计.md` | Traceability Artifact | Covered | This document | 需求→架构追溯关系记录。 |

---

## 2. 覆盖统计

| 需求总数 | Covered | Partially Covered | Pending Confirmation | Not Covered |
| --- | --- | --- | --- | --- |
| 22 | 21 | 1 | 0 | 0 |

Partially Covered 说明：
- **SRS-Gp_NCA9539-TIM-0004**: 中断响应时间约束中芯片侧 4us 参数已作为硬件约束记录；软件整体中断延迟预算（MCU 中断延迟 + I2C 通信时间 + 软件处理时间）的分配待详细设计阶段完成。架构层面已识别约束并预留。

---

## 3. 架构元素 → SRS 反向追溯

| Architecture Element | Element Type | Covered SRS Requirements |
| --- | --- | --- |
| `Gp_NCA9539_Init` | External API | FUNC-0001, CFG-0003, TIM-0001, SAFE-0002 |
| `Gp_NCA9539_SetOutputLevel` | External API | INTF-0001, TIM-0003 |
| `Gp_NCA9539_GetInputLevel` | External API | INTF-0002 |
| `Gp_NCA9539_SetDirection` | External API | INTF-0003 |
| `Gp_NCA9539_SetPolarityInversion` | External API | INTF-0004 |
| `Gp_NCA9539_GetInterruptStatus` | External API | INTF-0006, DIAG-0003, TIM-0004 |
| `Gp_NCA9539_GetFaultStatus` | External API | DIAG-0002 |
| `Gp_NCA9539_CalloutI2cWrite` | Dependency API | INTF-0001, INTF-0003, INTF-0004, INTF-0005 |
| `Gp_NCA9539_CalloutI2cRead` | Dependency API | INTF-0002, INTF-0005 |
| `Gp_NCA9539_CalloutDioWrite` | Dependency API | FUNC-0001, TIM-0002 |
| `Gp_NCA9539_CalloutDioRead` | Dependency API | INTF-0006 |
| `Gp_NCA9539_CalloutGetCoreId` | Dependency API | FUNC-0002 (multi-core support) |
| `GP_NCA9539_CFG_DEV_ERROR_DETECT` | Config Macro | DIAG-0001, SAFE-0001 |
| `GP_NCA9539_CFG_INSTANCE_COUNT` | Config Macro | CFG-0001, FUNC-0002 |
| `GP_NCA9539_CFG_I2C_SPEED_MODE` | Config Macro | CFG-0002 |
| `GP_NCA9539_CFG_REG_READBACK_VERIFY_ENABLE` | Config Macro | SAFE-0002, FUNC-0001 |
| `GP_NCA9539_CFG_SW_MAJOR_VERSION` | Config Macro | (project CM requirement) |
| `GP_NCA9539_CFG_SW_MINOR_VERSION` | Config Macro | (project CM requirement) |
| `Gp_NCA9539_Reg.h` | File Carrier | INTF-0005 |
| Instance state machine | Runtime State | FUNC-0001 |
| Instance runtime data container | Runtime State | FUNC-0002, INTF-0001, INTF-0002, INTF-0003, INTF-0004 |
| DET runtime buffer | Runtime State | DIAG-0001 |
| Fault record | Runtime State | DIAG-0002 |
| Interrupt bookkeeping | Runtime State | DIAG-0003, INTF-0006 |

---

## 4. 设计决策记录

| 决策ID | 决策项 | 决策 | 理由 | 影响范围 |
| --- | --- | --- | --- | --- |
| D01 | MainFunction 是否需要 | 不需要 | 无周期采样/状态机推进/去抖/看门狗/缓冲请求处理需求。所有 GPIO 操作均为同步 I2C 读写，立即返回结果。 | §1, §3 (no MainFunction), §5 (no MainFunction-related state) |
| D02 | 操作粒度 | 端口级（8位） | SRS 接口需求以端口为粒度。单引脚操作可通过位掩码在应用层处理，无需增加额外 API。 | §3 (SetOutputLevel/GetInputLevel/SetDirection/SetPolarityInversion 均为 port 参数) |
| D03 | 依赖表达方式 | 全部 Callout | I2C 读写和 DIO 控制均为硬件适配层，涉及 MCU 外设绑定和板级映射，符合 Callout 选择条件（项目特定、硬件适配、参数反映 FC 意图）。 | §8 (5 Callout APIs), §9 (Callout.h/.c Required) |
| D04 | FC_Reg.h 是否需要 | Required | NCA9539-Q1 有 8 个寄存器的地址、I2C 设备地址格式、寄存器复位默认值等需要独立常量载体。 | §9 (Reg.h Required), §6 (REG CONST section) |
| D05 | 标定项是否需要 | 空 | IoExtDev 族默认无标定参数。所有阈值和时序参数均为编译期配置。SRS 无标定流程要求。 | §7 (Empty) |
| D06 | 中断清除时机 | 自动（read-clear） | 芯片硬件特性：Input Port 读取后 INT\ 自动恢复高电平。软件侧在 GetInputLevel 调用后清除对应的中断 bookkeeping 标志。 | §3.6, §5 row 6 |
| D07 | 多核策略 | Per-core infrastructure (conditional) | Grounding baseline 确认 IoExtDev 族存在多核部署先例。当前架构包含 per-core 基础设施，若项目确认为单核，可在详细设计阶段简化。 | §5, §6, §8.5 |
| D08 | I2C Burst 行为处理 | 芯片自动处理（同寄存器对交替） | 芯片硬件在 burst read/write 时自动在 port 0 和 port 1 的同类型寄存器间交替。软件只需按顺序提供/接收数据，无需额外控制逻辑。 | §8.1, §8.2 Description |

---

## 5. 关闭条件

| 条件ID | 条件描述 | 关闭标准 |
| --- | --- | --- |
| C01 | R1 关闭 | SRS 正式发布（Ready 比例 >= 80%）且架构覆盖表重新核对无差异 |
| C02 | R2 关闭 | 项目确认芯片实例数量及 A0/A1 连接方式 |
| C03 | R3 关闭 | 项目确认中断处理策略（轮询/ISR/混合） |
| C04 | R4 关闭 | 安全分析确认运行期间回读策略 |
| C05 | R5 关闭 | 项目确认 I2C 总线速率 |
| C06 | R6 关闭 | 项目确认 MCU 端 RESET\ 和 INT\ GPIO 引脚分配 |
| C07 | R7 关闭 | 安全分析确认安全机制充分性 |
| C08 | R8 关闭 | 项目确认是否需要 Deinit/Reinit |
| C09 | R9 关闭 | 项目确认多核部署需求 |
