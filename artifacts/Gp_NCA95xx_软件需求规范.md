# 《Gp_NCA95xx 软件需求规范》

**Gp_NCA95xx_需求规范**

**Gp_NCA95xx_Requirements Specification**

项目编号/Project number: Gp_NCA95xx
保密性/Security: Internal

**Document Properties**
Status: 草稿
版本: 0.1.0
Author: AI Generated
Created: 2026-05-26

**Approved Versions**
Current Document version **0.1.0** is **TBD**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| 0.1.0 | 草稿 | TBD | TBD | TBD |

## 适用说明

本文档适用于 `Fc_Stack` 项目中 `Gp_NCA95xx` I2C GPIO 扩展器驱动模块的软件需求定义。本文档仅描述软件应满足的需求，不描述详细设计方案、代码实现方案或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| 0.1.0 | 2026-05-26 | AI Generated | 基于 NCA9539-Q1 Datasheet Rev1.0 初始 Draft SRS | 草稿 |

---

## 目录

- [1 目的](#1-目的)
- [2 适用范围](#2-适用范围)
- [3 定义和缩写](#3-定义和缩写)
- [4 概述](#4-概述)
- [5 功能需求](#5-功能需求)
- [6 非功能需求](#6-非功能需求)
- [7 需求来源](#7-需求来源)
- [附录A 需求清单](#附录a-需求清单)
- [附录B 支持和相关性文件](#附录b-支持和相关性文件)

---

## 1 目的

本文档定义 `Gp_NCA95xx` 模块的软件需求，明确模块在 `Fc_Stack` 项目中的功能边界、对外接口、状态行为、配置约束、诊断状态、时序要求、非功能约束和验证要求。

本文档作为 `Gp_NCA95xx` 模块软件架构设计、详细设计、编码实现、单元测试、集成测试和系统测试的上游输入。所有正式需求均应具备需求 ID、来源、约束、验收准则和验证方式。

---

## 2 适用范围

本文档适用于 `Fc_Stack` 项目中 `Gp_NCA95xx` 模块的软件开发、评审、集成、测试和交付活动。

### 2.1 适用对象

- 软件需求工程师
- 软件架构和详细设计工程师
- 软件开发工程师
- 软件测试工程师
- 功能安全工程师
- 项目质量和配置管理人员

### 2.2 适用范围

本文档覆盖 `Gp_NCA95xx` 模块的软件功能、接口、配置、诊断、时序及相关非功能需求，并给出需求来源、验证方式、验证阶段和需求状态。本文档不展开详细设计方案、代码实现方案和测试用例步骤。

---

## 3 定义和缩写

### 3.1 定义

| 术语 | 定义 |
| --- | --- |
| I2C GPIO Expander | 通过 I2C 总线扩展 MCU GPIO 数量的外设芯片 |
| Port | 8 位 I/O 组，本芯片包含 Port 0 (P00-P07) 和 Port 1 (P10-P17) |
| Configuration Register | 控制每引脚输入/输出方向的寄存器 |
| Polarity Inversion | 输入端口读数的逻辑反相功能 |
| Open-Drain Interrupt | 开漏输出中断信号，多设备可共用一线 |
| IoExtDev | Fc_Stack 中外部 IO 扩展器驱动的 AUTOSAR 层级分类 |

### 3.2 缩写

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| NCA9539-Q1 | Novosense NCA9539-Q1 Automotive Grade I2C GPIO Expander | 纳新微 NCA9539-Q1 车规级 I2C GPIO 扩展器 |
| I2C | Inter-Integrated Circuit | 集成电路间总线 |
| GPIO | General Purpose Input/Output | 通用输入输出 |
| SCL | Serial Clock Line | 串行时钟线 |
| SDA | Serial Data Line | 串行数据线 |
| POR | Power-On Reset | 上电复位 |
| INT | Interrupt | 中断输出 |
| ASIL | Automotive Safety Integrity Level | 汽车安全完整性等级 |
| DET | Development Error Tracer | 开发错误追踪 |
| SRS | Software Requirement Specification | 软件需求规范 |
| UT | Unit Test | 单元测试 |
| IT | Integration Test | 集成测试 |

---

## 4 概述

本章仅保留理解需求所需的芯片和驱动背景信息，避免展开实现细节；正式软件责任以下文需求条目为准。

### 4.1 外设芯片介绍

NCA9539-Q1 是纳新微（Novosense）推出的车规级 16 位 I2C GPIO 扩展器，通过 I2C 总线为 MCU 提供额外 16 路 GPIO。芯片通过 A0/A1 硬件地址引脚支持最多 4 片同总线部署，具备开漏中断输出和硬件复位输入。

芯片支持以下功能：

- 16 路独立可配置 I/O（两路 8 位端口）
- I2C Fast-mode 通信（最高 400 kHz）
- 每引脚独立方向配置（输入/输出）
- 输入极性反相
- 输入状态变化中断输出（开漏）
- 硬件复位引脚
- 内部上电复位
- SCL/SDA 噪声滤波
- 5 V 容忍 I/O

### 4.2 驱动功能介绍

`Gp_NCA95xx` 驱动应实现以下软件功能：

- 初始化当前核所有芯片实例，加载配置表并回写默认方向、输出电平、极性
- 周期性中断轮询与输入状态刷新（MainFunction）
- 通过信号 ID 读取指定 GPIO 输入状态
- 通过信号 ID 设置指定 GPIO 输出电平
- 读取芯片故障/诊断信息
- 芯片硬件复位控制
- 运行时方向变更（可配置启用/禁用）
- 极性反相配置（可配置启用/禁用）

驱动所属层级为 **IoExtDev**（外部 IO 扩展器设备层），通过 I2C 总线与 MCU 通信，对外提供 `uint16 Id` 信号接口与上层 ASW 解耦。

### 4.3 外设引脚介绍

| 引脚 | 方向（芯片视角） | Pin 口功能 |
| --- | --- | --- |
| INT | 输出（开漏） | 中断输出，输入状态变化时拉低，需外接上拉电阻至 VDD |
| A1 | 输入 | I2C 地址选择位 1，直连 VDD 或 GND |
| A0 | 输入 | I2C 地址选择位 0，直连 VDD 或 GND |
| RESET | 输入（低有效） | 硬件复位，拉低复位芯片至默认状态，需外接上拉电阻至 VDD |
| P00-P07 | I/O | Port 0 通用 I/O，上电默认为输入 |
| P10-P17 | I/O | Port 1 通用 I/O，上电默认为输入 |
| SCL | 输入 | I2C 串行时钟，需外接上拉电阻至 VDD |
| SDA | I/O（开漏） | I2C 串行数据，需外接上拉电阻至 VDD |
| VDD | 电源 | 供电电压 1.65 V 至 3.6 V |
| VSS | 地 | 接地 |

**软件引脚归属说明**：

- SCL/SDA：由 MCU I2C 外设驱动控制，本模块通过 I2C 抽象层访问，不直接操作引脚
- INT：需确认是否接入 MCU GPIO 并由本驱动采样；若接入则由 MainFunction 轮询或 ISR 响应
- RESET：需确认是否由本驱动 GPIO 控制；若由本驱动控制则提供 ResetChip 接口
- A0/A1：硬件固定连接，软件不控制，仅在配置中记录对应 I2C 地址
- P00-P17：由本驱动通过 I2C 间接控制

### 4.4 状态机介绍

NCA9539-Q1 芯片本身无复杂工作模式状态机（无 Normal/Standby/Sleep 模式切换）。驱动侧定义以下设备状态用于管理芯片初始化和通信故障：

| 状态 | 值 | 说明 | 进入条件 | 退出条件 |
| --- | --- | --- | --- | --- |
| Unknown | 0x00 | 未初始化或状态未知 | 系统启动 / 复位后 | Init 调用成功 |
| Init | 0x11 | 初始化完成，寄存器已按配置回写 | Init 执行完成且无 I2C 错误 | MainFunction 首次运行成功 |
| Normal | 0x21 | 正常运行，I2C 通信正常 | Init 完成且 MainFunction 确认通信正常 | I2C 通信连续失败超过阈值 |
| Fault | 0x71 | I2C 通信故障 | I2C 通信连续失败超过阈值 | I2C 通信恢复或芯片复位 |

状态跳转约束：

- Unknown → Init：仅 Init 调用可触发
- Init → Normal：MainFunction 确认通信正常后自动跳转
- Normal → Fault：连续 I2C 通信失败超过可配阈值
- Fault → Normal：连续 I2C 通信恢复超过可配阈值，或 ResetChip 后重新 Init

### 4.5 通信参数

本芯片通过 I2C 总线与 MCU 通信。

关键通信参数：

- I2C Fast-mode：最高 400 kHz
- 器件寻址：7 位地址，高 5 位固定 `11101`，低 2 位由 A1/A0 引脚决定，R/W 位由 I2C 协议定义

| 参数 | 标准模式 | Fast-mode | 单位 |
| --- | --- | --- | --- |
| SCL 时钟频率 | 0 - 100 | 0 - 400 | kHz |
| 总线空闲时间（STOP 到 START） | ≥ 4.7 | ≥ 1.3 | μs |
| START 保持时间 | ≥ 4.0 | ≥ 0.6 | μs |
| SCL 低电平时间 | ≥ 4.7 | ≥ 1.3 | μs |
| SCL 高电平时间 | ≥ 4.0 | ≥ 0.6 | μs |
| 数据建立时间 | ≥ 250 | ≥ 100 | ns |

设备地址表：

| A1 | A0 | I2C 地址（7-bit） | I2C 地址（8-bit Write/Read） |
| --- | --- | --- | --- |
| L | L | 0x74 | 0xE8 / 0xE9 |
| L | H | 0x75 | 0xEA / 0xEB |
| H | L | 0x76 | 0xEC / 0xED |
| H | H | 0x77 | 0xEE / 0xEF |

---

## 5 功能需求

本章描述模块必须实现的功能行为，包括模式与状态、接口、配置、诊断和错误处理。每条需求使用固定字段描述，以便后续生成设计、测试和追溯矩阵。

### 5.1 模式需求

#### SRS-Gp_NCA95xx-FUNC-0001 设备状态机管理

`FUNC` `ASIL_B` `UT/IT` `Draft` `来源: aurix2g-normative-patterns.md 1.4节, Datasheet-6.3节`

Gp_NCA95xx 模块应维护每个芯片实例的设备状态，支持 Unknown → Init → Normal 的状态流转，并在连续 I2C 通信失败时进入 Fault 状态。

- **状态枚举**：Unknown (0x00)、Init (0x11)、Normal (0x21)、Fault (0x71)
- **前置条件**：对应的芯片配置数据已加载
- **触发条件**：Init 调用触发 Unknown → Init；MainFunction 周期检测触发其余状态跳转
- **异常处理**：连续 I2C 通信失败次数超过可配阈值时从 Normal 进入 Fault；通信恢复后从 Fault 回 Normal
- **验收准则**：覆盖所有合法状态跳转路径，UT 验证每种跳转；IT 验证 I2C 故障注入后状态正确切换

#### SRS-Gp_NCA95xx-FUNC-0002 上电初始化与默认状态恢复

`FUNC` `ASIL_B` `UT/IT` `Draft` `来源: Datasheet-6.3.1节`

Gp_NCA95xx 模块应在 Init 调用后，根据配置数据将每个芯片实例的 Configuration、Output、Polarity Inversion 寄存器回写到指定默认值，使所有 I/O 进入配置定义的初始状态。

- **前置条件**：I2C 总线可用、芯片已完成 POR
- **触发条件**：Gp_NCA95xx_Init() 被调用
- **输出**：Configuration 寄存器 → 配置指定值；Output 寄存器 → 默认输出电平；Polarity 寄存器 → 默认极性
- **异常处理**：任一寄存器写入失败（I2C NACK）则标记该芯片实例状态为 Fault，不继续后续初始化步骤
- **验收准则**：UT 验证 Init 后各寄存器值与配置一致；IT 验证复位后芯片恢复默认行为

#### SRS-Gp_NCA95xx-FUNC-0003 硬件复位控制

`FUNC` `ASIL_B` `UT/IT` `Draft` `来源: Datasheet-6.2.2节`

当 RESET 引脚接入 MCU GPIO 且归属于本驱动时，Gp_NCA95xx 模块应提供芯片硬件复位功能，在调用后拉低 RESET 引脚至少 6 ns，等待复位恢复时间后重新初始化芯片寄存器至默认值。

- **前置条件**：RESET 引脚已配置为本驱动控制的 DIO 通道；芯片实例已配置
- **触发条件**：调用 ResetChip 接口
- **输出**：RESET 引脚拉低 ≥ 6 ns → 恢复高电平 → 等待 ≥ 200 ns → 重新回写配置寄存器
- **范围边界**：若 RESET 引脚不归属于本驱动，本需求不适用，需在配置中显式标记
- **验收准则**：UT 验证 ResetChip 调用后 RESET 引脚时序；IT 验证复位后芯片寄存器恢复默认值

#### SRS-Gp_NCA95xx-FUNC-0004 I/O 方向配置

`FUNC` `QM` `UT/IT` `Draft` `来源: Datasheet-6.5.6节`

Gp_NCA95xx 模块应在 Init 时根据配置数据设置每引脚的输入/输出方向（Configuration Register 0/1），使能位为 1 表示输入（高阻态），为 0 表示输出。

- **前置条件**：芯片实例已完成 Init 且状态为 Normal
- **触发条件**：Init 阶段配置回写；或运行时 SetGpioDirSig 调用（若启用运行时方向变更）
- **输出**：Configuration Register 对应 bit 按配置写入
- **异常处理**：I2C 写入失败则标记芯片 Fault 状态
- **范围边界**：运行时方向变更是否允许由配置开关控制，默认禁止
- **验收准则**：UT 验证配置写入正确；IT 验证写入后引脚实际方向符合预期

### 5.2 接口需求

#### SRS-Gp_NCA95xx-INTF-0001 Init 接口

`INTF` `ASIL_B` `UT/IT` `Draft` `来源: aurix2g-normative-patterns.md 1.1节, Datasheet-6.5节`

```c
void Gp_NCA95xx_Init(void);
```

Gp_NCA95xx 模块应提供 Init 接口，初始化当前核所有已配置的芯片实例：加载配置数据，通过 I2C 回写 Configuration、Output、Polarity Inversion 寄存器至默认值，并将设备状态置为 Init。

- **前置条件**：MCAL I2C 驱动已初始化；配置数据已加载
- **触发条件**：ECU 启动阶段调用
- **输出**：所有已配置芯片实例的寄存器回写完成，设备状态 = Init
- **异常处理**：I2C 写入失败时标记对应芯片为 Fault；部分芯片失败不影响其余芯片初始化
- **验收准则**：UT 验证各寄存器写入序列和默认值；IT 验证多芯片实例并行初始化

#### SRS-Gp_NCA95xx-INTF-0002 MainFunction 接口

`INTF` `ASIL_B` `UT/IT` `Draft` `来源: aurix2g-normative-patterns.md 1.2节`

```c
void Gp_NCA95xx_MainFunction(void);
```

Gp_NCA95xx 模块应提供 MainFunction 周期接口，负责：检测 INT 引脚状态、在中断触发时通过 I2C 读取 Input Port 寄存器刷新输入缓存、检测 I2C 通信连续性并更新设备状态、处理 pending 的输出刷新。

- **前置条件**：Init 已完成
- **触发条件**：按配置周期被调度（建议周期 1-10 ms）
- **输出**：输入状态缓存更新；设备状态按规则跳转；pending 输出操作执行
- **范围边界**：若 INT 引脚未接入 MCU，则输入刷新降级为周期全量轮询 Input Port 寄存器
- **异常处理**：I2C 读取失败累计至故障阈值后切换设备状态为 Fault
- **验收准则**：UT 验证 MainFunction 内部逻辑；IT 验证输入变化到缓存更新的端到端延迟

#### SRS-Gp_NCA95xx-INTF-0003 GPIO 输入读取接口

`INTF` `ASIL_B` `UT/IT` `Draft` `来源: aurix2g-normative-patterns.md 8.8节, Datasheet-6.5.3节`

```c
Std_ReturnType Gp_NCA95xx_GetGpioInSig(uint16 Id_u16, uint8* State_pu8);
```

Gp_NCA95xx 模块应提供 GPIO 输入读取接口，通过 uint16 Id 解析目标芯片实例、端口和引脚编号，返回该引脚的当前输入状态（0 或 1），并根据极性配置自动应用反相。

- **输入**：Id_u16 — 信号 ID（编码 CoreId + ChipIdx + PinIdx）；State_pu8 — 输出状态指针
- **输出**：State_pu8 = 0 或 1（经极性处理后的逻辑电平）
- **返回值**：E_OK（成功）、E_NOT_OK（参数无效或芯片 Fault）
- **前置条件**：芯片实例已 Init 且状态不为 Unknown
- **异常处理**：Id 无效 → 返回 E_NOT_OK，State_pu8 不变；State_pu8 为 NULL → 报告 DET；芯片 Fault → 返回 E_NOT_OK
- **验收准则**：UT 验证各 Id 解析正确性和返回值；IT 验证实际引脚电平读取

#### SRS-Gp_NCA95xx-INTF-0004 GPIO 输出设置接口

`INTF` `ASIL_B` `UT/IT` `Draft` `来源: aurix2g-normative-patterns.md 8.8节, Datasheet-6.5.4节`

```c
Std_ReturnType Gp_NCA95xx_SetGpioOutSig(uint16 Id_u16, uint8 State_u8);
```

Gp_NCA95xx 模块应提供 GPIO 输出设置接口，通过 uint16 Id 解析目标芯片实例、端口和引脚编号，设置该引脚的输出电平（0 或 1），并通过 I2C 写入 Output Port 寄存器。

- **输入**：Id_u16 — 信号 ID；State_u8 — 目标输出电平（仅 0 或 1 有效）
- **返回值**：E_OK（成功）、E_NOT_OK（参数无效或芯片 Fault）
- **前置条件**：目标引脚已配置为输出方向；芯片实例状态为 Normal
- **异常处理**：Id 无效 → 返回 E_NOT_OK；State_u8 非 0/1 → 返回 E_NOT_OK，报告 DET；引脚方向为输入 → 返回 E_NOT_OK；I2C 写入失败 → 返回 E_NOT_OK，标记芯片 Fault
- **验收准则**：UT 验证 Id 解析、参数校验和返回值；IT 验证实际引脚输出电平

#### SRS-Gp_NCA95xx-INTF-0005 设备故障读取接口

`INTF` `ASIL_B` `UT/IT` `Draft` `来源: aurix2g-normative-patterns.md 8.8节`

```c
Std_ReturnType Gp_NCA95xx_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32);
```

Gp_NCA95xx 模块应提供设备故障读取接口，通过 uint16 Id 解析目标芯片实例，返回该芯片的当前故障状态位掩码。

- **输入**：Id_u16 — 信号 ID（编码 CoreId + ChipIdx）；Fault_pu32 — 故障码输出指针
- **输出**：Fault_pu32 — 故障位掩码（0 = 无故障）
- **返回值**：E_OK（成功）、E_NOT_OK（参数无效）
- **故障编码**：Bit0 — I2C 通信错误；Bit1 — 未初始化；Bit2 — 参数无效历史；Bit3 — 配置错误；其余保留
- **前置条件**：芯片实例已配置
- **异常处理**：Id 无效 → 返回 E_NOT_OK；Fault_pu32 为 NULL → 报告 DET
- **范围边界**：本接口命名为 GetDevFaultSig，符合 IoExtDev 层命名规范；不得命名为 GetDiag
- **验收准则**：UT 验证故障位掩码编码正确性；IT 验证 I2C 故障注入后故障码置位

#### SRS-Gp_NCA95xx-INTF-0006 设备模式读取接口

`INTF` `QM` `UT` `Draft` `来源: aurix2g-normative-patterns.md 1.1节`

```c
Std_ReturnType Gp_NCA95xx_GetDevModeInSig(uint16 Id_u16, uint8* DevMode_pu8);
```

Gp_NCA95xx 模块应提供设备模式读取接口，返回指定芯片实例的当前设备状态（Unknown/Init/Normal/Fault）。

- **输入**：Id_u16 — 信号 ID；DevMode_pu8 — 状态输出指针
- **输出**：DevMode_pu8 = 0x00 (Unknown) / 0x11 (Init) / 0x21 (Normal) / 0x71 (Fault)
- **返回值**：E_OK（成功）、E_NOT_OK（Id 无效）
- **前置条件**：芯片实例已配置
- **异常处理**：Id 无效 → 返回 E_NOT_OK；DevMode_pu8 为 NULL → 报告 DET
- **验收准则**：UT 验证状态返回值与内部状态一致

### 5.3 配置需求

#### SRS-Gp_NCA95xx-CFG-0001 芯片实例数量配置

`CFG` `QM` `Review/Test` `Draft` `来源: aurix2g-normative-patterns.md 3.5节, Datasheet-6.5.1节`

Gp_NCA95xx 模块应支持配置每核管理的芯片实例数量，取值范围 0-4，默认值需项目确认。

- **配置项**：`MultiChipNum_u8`
- **有效范围**：0 - 4（对应 A0/A1 的 4 种地址组合）
- **越界处理**：配置值超过 4 应在配置校验阶段报错
- **验收准则**：Review 确认配置范围；Test 验证 0/1/4 实例场景

#### SRS-Gp_NCA95xx-CFG-0002 I2C 设备地址配置

`CFG` `QM` `Review/Test` `Draft` `来源: Datasheet-6.5.1节`

Gp_NCA95xx 模块应支持为每个芯片实例配置 I2C 设备地址，有效值为 0x74/0x75/0x76/0x77，由硬件 A0/A1 引脚连接决定，配置值需与硬件一致。

- **配置项**：`DevAddr_u8`（每芯片实例）
- **有效范围**：0x74, 0x75, 0x76, 0x77
- **约束**：同 I2C 总线上各芯片地址不得重复
- **越界处理**：非法地址值在配置校验阶段报错
- **验收准则**：Review 确认地址与硬件原理图一致；IT 验证各地址芯片可正确通信

#### SRS-Gp_NCA95xx-CFG-0003 默认 I/O 方向配置

`CFG` `QM` `Review/Test` `Draft` `来源: Datasheet-6.5.6节`

Gp_NCA95xx 模块应支持为每个芯片实例配置 16 路 I/O 的默认方向（输入/输出），默认值在 Init 阶段写入 Configuration Register 0/1。

- **配置项**：`DefaultDir_u16`（每芯片实例，bit=1 输入；bit=0 输出）
- **默认值**：0xFFFF（全部输入，与芯片 POR 默认一致）
- **约束**：配置为输出的引脚默认输出电平需在 `DefaultOut_u16` 中同步定义
- **验收准则**：UT 验证 Init 后 Configuration Register 与配置一致

#### SRS-Gp_NCA95xx-CFG-0004 默认输出电平配置

`CFG` `QM` `Review/Test` `Draft` `来源: Datasheet-6.5.4节`

Gp_NCA95xx 模块应支持为每个芯片实例配置默认输出电平，在 Init 阶段写入 Output Register 0/1。仅对方向配置为输出的引脚生效。

- **配置项**：`DefaultOut_u16`（每芯片实例）
- **默认值**：0xFFFF（与芯片 POR 默认一致）
- **约束**：仅影响方向为输出的引脚
- **验收准则**：UT 验证 Init 后 Output Register 与配置一致

#### SRS-Gp_NCA95xx-CFG-0005 I2C 通道配置

`CFG` `QM` `Review/Test` `Draft` `来源: aurix2g-normative-patterns.md 3.2节`

Gp_NCA95xx 模块应支持为每个芯片实例配置 I2C 通道索引和通信速率。

- **配置项**：`I2cChnId_u8`（I2C 通道索引）；`I2cSpeed_u32`（通信速率，默认 400000 Hz）
- **有效范围**：I2cChnId — 依赖 MCU 平台 I2C 通道数；I2cSpeed — ≤ 400000
- **越界处理**：I2cSpeed > 400000 → 配置校验报错
- **验收准则**：Review 确认通道分配；IT 验证 Fast-mode 通信正确

#### SRS-Gp_NCA95xx-CFG-0006 信号 ID 映射配置

`CFG` `QM` `Review/Test` `Draft` `来源: aurix2g-normative-patterns.md 3.4节`

Gp_NCA95xx 模块应支持信号 ID 映射配置，将上层 uint16 Id 映射到 CoreId + ChipIdx + PinIdx，实现 ASW 与硬件解耦。

- **配置项**：`SigMapCfg[]` 数组，每元素包含 `MapCoreId_u32`、`MapChipIdx_u8`、`MapPinIdx_u8`
- **约束**：同一 Id 不得重复映射；PinIdx 范围 0-15（P00-P07 对应 0-7，P10-P17 对应 8-15）
- **越界处理**：PinIdx > 15 → 配置校验报错
- **验收准则**：UT 验证 Id 解析正确映射到 ChipIdx + PinIdx

#### SRS-Gp_NCA95xx-CFG-0007 中断与轮询配置

`CFG` `QM` `Review/Test` `Draft` `来源: Datasheet-6.2.3节`

Gp_NCA95xx 模块应支持配置中断检测模式：INT 引脚轮询模式 或 周期全量轮询模式。含 INT 去抖时间和 MainFunction 周期配置。

- **配置项**：`IntEnable_b`（中断使能）；`IntDebounce_u8`（去抖次数，默认 3）；`PollPeriod_u16`（轮询周期 ms）
- **默认值**：IntEnable = TRUE；Debounce = 3；PollPeriod 需项目确认
- **约束**：若 INT 引脚未接入 MCU，IntEnable 必须为 FALSE，降级为周期全量轮询
- **验收准则**：Review 确认轮询策略；IT 验证中断响应延迟

### 5.4 诊断需求

#### SRS-Gp_NCA95xx-DIAG-0001 I2C 通信错误检测

`DIAG` `ASIL_B` `UT/IT` `Draft` `来源: Datasheet-6.4.5节, aurix2g-normative-patterns.md 6.3节`

Gp_NCA95xx 模块应在每次 I2C 读写操作后检测ACK/NACK响应，连续 NACK 次数超过可配阈值时标记对应芯片实例状态为 Fault，并置位故障码 Bit0。

- **故障触发条件**：连续 I2C NACK 次数 > 阈值
- **故障清除条件**：连续 I2C ACK 次数 > 恢复阈值
- **可配参数**：故障确认阈值（默认 3）、故障恢复阈值（默认 2）
- **验收准则**：UT 验证 NACK 计数逻辑和故障码置位/清除；IT 验证 I2C 故障注入和恢复

#### SRS-Gp_NCA95xx-DIAG-0002 开发错误检测（DET）

`DIAG` `ASIL_B` `UT` `Draft` `来源: construction-rules.md 4节`

Gp_NCA95xx 模块应对所有外部可调用接口实施开发错误检测，包括：NULL 指针参数检测、无效 Id 检测、非法 State 值检测、未初始化访问检测。

- **检测项**：State_pu8/DevMode_pu8/Fault_pu32 为 NULL → 报告 DET；Id 超出配置范围 → 报告 DET；State_u8 非 0/1 → 报告 DET；Init 未调用即调用其他接口 → 报告 DET
- **错误响应**：报告 DET 后返回 E_NOT_OK，不改变输出参数值
- **验收准则**：UT 为每项 DET 检测编写独立测试用例

#### SRS-Gp_NCA95xx-DIAG-0003 故障码编码

`DIAG` `ASIL_B` `UT` `Draft` `来源: aurix2g-normative-patterns.md 6.2节`

Gp_NCA95xx 模块应采用位掩码编码故障信息，每位代表一个故障维度，支持多故障同时标记。GetDevFaultSig 接口返回的故障码格式如下：

- **位定义**：Bit0 — I2C 通信错误；Bit1 — 未初始化；Bit2 — 参数无效历史；Bit3 — 配置错误；Bit4-31 — 保留（值为 0）
- **约束**：Fault = 0 表示无故障；每个故障位独立置位和清除
- **验收准则**：UT 验证所有故障组合的位掩码正确性

#### SRS-Gp_NCA95xx-DIAG-0004 中断状态变化报告

`DIAG` `QM` `UT/IT` `Draft` `来源: Datasheet-6.2.3节`

Gp_NCA95xx 模块应通过 MainFunction 检测 INT 引脚状态或 Input Port 寄存器变化，在输入状态变化时更新输入缓存，并通过 GetDevFaultSig 的可选状态位或独立回调通知上层。

- **触发条件**：INT 引脚拉低或 Input Port 寄存器值变化
- **响应行为**：读取 Input Port 寄存器、更新缓存、清除芯片中断（读操作自动清除）
- **范围边界**：具体的上层通知机制（回调/事件）需项目确认
- **验收准则**：IT 验证输入变化后缓存更新的延迟

---

## 6 非功能需求

### 6.1 时序需求

#### SRS-Gp_NCA95xx-TIM-0001 I2C Fast-mode 操作速率

`TIM` `QM` `Analysis/Test` `Draft` `来源: Datasheet-5.2节`

Gp_NCA95xx 模块的 I2C 通信应在 Fast-mode 下运行，SCL 时钟频率不超过 400 kHz。

- **约束**：f_SCL ≤ 400 kHz
- **验收准则**：Analysis 确认 I2C 驱动配置；Test 测量实际 SCL 频率

#### SRS-Gp_NCA95xx-TIM-0002 RESET 脉冲宽度

`TIM` `QM` `Analysis/Test` `Draft` `来源: Datasheet-5.2节`

ResetChip 接口拉低 RESET 引脚的持续时间应 ≥ 6 ns。

- **约束**：t_w(rst) ≥ 6 ns
- **验收准则**：Analysis 确认 GPIO 操作延迟满足约束；Test 测量 RESET 引脚低电平宽度

#### SRS-Gp_NCA95xx-TIM-0003 RESET 恢复时间

`TIM` `QM` `Analysis/Test` `Draft` `来源: Datasheet-5.2节`

ResetChip 接口在释放 RESET 引脚（拉高）后应等待 ≥ 200 ns 再执行后续 I2C 操作。

- **约束**：t_rec(rst) ≥ 200 ns
- **验收准则**：Analysis 确认软件延迟实现；Test 测量 RESET 高电平到首次 I2C 操作的时间间隔

#### SRS-Gp_NCA95xx-TIM-0004 中断有效响应时间

`TIM` `QM` `Analysis/Test` `Draft` `来源: Datasheet-5.2节`

MainFunction 应确保从 INT 引脚拉低到 Input Port 寄存器读取完成的时间不超过可配上限（参考芯片 t_v(INT_N) ≤ 4 μs + 软件响应延迟）。

- **约束**：t_v(INT_N) ≤ 4 μs（芯片侧）；软件响应延迟 ≤ 1 个 MainFunction 周期
- **验收准则**：Test 测量输入变化到缓存更新的端到端延迟

#### SRS-Gp_NCA95xx-TIM-0005 I2C 总线空闲等待

`TIM` `QM` `Analysis/Test` `Draft` `来源: Datasheet-5.2节`

Gp_NCA95xx 模块在每次 I2C STOP 后应确保总线空闲时间 ≥ 1.3 μs（Fast-mode）再发起下一次 START。此约束由 MCAL I2C 驱动保证，本模块依赖该保证。

- **约束**：t_BUF ≥ 1.3 μs
- **责任归属**：MCAL I2C 驱动保证；本模块在需求中声明依赖
- **验收准则**：Review 确认 MCAL I2C 驱动配置满足 t_BUF 约束

### 6.2 安全等级需求

#### SRS-Gp_NCA95xx-SAFE-0001 ASIL_B 安全完整性

`SAFE` `ASIL_B` `Review` `Draft` `来源: 项目需求`

Gp_NCA95xx 模块的安全等级为 ASIL_B。所有涉及 I/O 输出控制和故障检测的功能需求和接口需求应满足 ASIL_B 安全完整性要求。

- **安全目标**：错误的 GPIO 输出不得导致违反安全目标
- **安全机制**：输出回读校验（Readback）、I2C 通信错误检测、配置校验
- **验收准则**：安全审查确认安全机制覆盖所有安全目标

#### SRS-Gp_NCA95xx-SAFE-0002 输出回读校验

`SAFE` `ASIL_B` `UT/IT` `Draft` `来源: 项目需求, Datasheet-6.5.4节`

Gp_NCA95xx 模块应在每次 SetGpioOutSig 写入 Output Register 后，对安全关键输出执行回读校验：读取 Output Register 确认写入值与预期一致。若不一致应重试并报告故障。

- **触发条件**：SetGpioOutSig 调用完成 I2C 写入
- **重试策略**：回读不一致时重试最多 2 次；3 次失败后标记芯片 Fault
- **范围边界**：回读校验范围限于配置标记为安全关键的输出引脚
- **验收准则**：UT 验证回读逻辑和重试计数；IT 验证故障注入后正确检测

#### SRS-Gp_NCA95xx-SAFE-0003 安全状态定义

`SAFE` `ASIL_B` `Review` `Draft` `来源: aurix2g-normative-patterns.md 4.4节`

Gp_NCA95xx 模块在检测到不可恢复的 I2C 通信故障时，应将受影响芯片实例标记为 Fault 状态，并保留最后一次已知输出值不变（不执行新输出操作）。安全状态恢复需通过 ResetChip 或重新 Init。

- **安全状态触发**：I2C 通信连续失败超过阈值且达到最大重试次数
- **安全状态行为**：停止对该芯片的新 I2C 操作；保持软件侧输出缓存不变；上报 Fault 状态
- **安全状态退出**：芯片硬件复位或重新初始化
- **验收准则**：IT 验证 Fault 状态下不再执行输出操作且缓存不变

### 6.3 编码规范需求

#### SRS-Gp_NCA95xx-CODE-0001 MISRA-C 编码规范

`CODE` `QM` `Inspection` `Draft` `来源: 项目编码规范`

Gp_NCA95xx 模块的 C 源码应遵循 MISRA-C:2012 编码规范，所有规则偏离需有记录和批准。

- **适用标准**：MISRA-C:2012
- **验收准则**：静态分析工具扫描无未批准偏离

#### SRS-Gp_NCA95xx-CODE-0002 命名规范

`CODE` `QM` `Inspection` `Draft` `来源: aurix2g-normative-patterns.md 9.2节`

Gp_NCA95xx 模块的接口函数、类型、枚举、宏和变量命名应遵循 Fc_Stack 命名规范：

- **函数**：`Gp_NCA95xx_<Action><Target>`（如 `Gp_NCA95xx_GetGpioInSig`）
- **类型**：`Gp_NCA95xx_<Name>Type`（`_t` 后缀 TBD）
- **枚举值**：`GP_NCA95xx_<NAME>_<VALUE>_e`
- **变量后缀**：`_u8/_u16/_u32` 表示无符号整数位宽；`_pu8` 表示指针；`_cptst` 表示 const 结构体指针
- **验收准则**：代码审查确认命名一致性

#### SRS-Gp_NCA95xx-CODE-0003 文件结构规范

`CODE` `QM` `Inspection` `Draft` `来源: aurix2g-normative-patterns.md 9.1节`

Gp_NCA95xx 模块的源文件应遵循标准 Fc_Stack 文件结构：

- `Gp_NCA95xx.h` — 公开 API 声明
- `Gp_NCA95xx_Types.h` — 类型、枚举、宏、配置结构体
- `Gp_NCA95xx_Cfg.h` — 预编译配置常量
- `Gp_NCA95xx_CfgData.h` — 集成配置数据
- `Gp_NCA95xx_MemMap.h` — 内存分区映射
- `Gp_NCA95xx.c` — 主实现
- `Gp_NCA95xx_Internal.h` — 内部函数和数据
- `Gp_NCA95xx_Callout.h` — 用户回调函数（如需要）
- **验收准则**：Review 确认文件结构完整性

### 6.4 资源消耗需求

#### SRS-Gp_NCA95xx-RES-0001 内存资源约束

`RES` `QM` `Analysis` `Draft` `来源: 项目资源预算`

Gp_NCA95xx 模块的 ROM/RAM 消耗应在项目预算内。每增加一个芯片实例，RAM 消耗应线性增长。最终 ROM/RAM 值需从 link map 中提取并评审。

- **典型预算**：ROM < 2 KB，RAM < 256 B + N × 64 B（N = 芯片实例数）
- **验收准则**：Analysis — 从 link map 提取实际 ROM/RAM 并评审

#### SRS-Gp_NCA95xx-RES-0002 I2C 总线利用率

`RES` `QM` `Analysis` `Draft` `来源: 项目资源预算`

Gp_NCA95xx 模块的 I2C 总线操作应避免阻塞其他同总线设备。单次 MainFunction 调用中 I2C 操作总时间应可配置上限。

- **约束**：单次 MainFunction 中 I2C 操作总时间应可配（默认 ≤ 1 ms）
- **验收准则**：Analysis — 测量 MainFunction 中 I2C 操作时序

### 6.5 可追溯性需求

#### SRS-Gp_NCA95xx-COMP-0001 需求来源追溯

`COMP` `QM` `Review` `Draft` `来源: rule-engine.md Trace Rules`

Gp_NCA95xx 模块的每条正式需求应至少关联一个上游来源（Datasheet/项目需求/规范），并在 SRS 中标注。

- **验收准则**：Review 确认每条 Ready 需求有来源标注

#### SRS-Gp_NCA95xx-COMP-0002 需求验证追溯

`COMP` `QM` `Review` `Draft` `来源: rule-engine.md Trace Rules`

Gp_NCA95xx 模块的每条需求应定义验证方式、验证阶段和验收准则。验证结果应可追溯到对应需求 ID。

- **验收准则**：Review 确认每条需求有验证方式和验收准则

---

## 7 需求来源

| 来源类别 | 来源名称 | 与本文档关系 | 状态 |
| --- | --- | --- | --- |
| Datasheet | Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN.md | 芯片能力和约束来源 | 已导入 |
| 内置规范 | aurix2g-normative-patterns.md | 接口分类、状态机、配置、诊断、命名模式 | 已参考 |
| 构建规则 | construction-rules.md | 需求字段完整性和状态降级 | 已参考 |
| 提取规则 | extraction-rules.md | 特征提取和软件责任判断 | 已参考 |
| 项目需求 | TBD — 项目需求文档 | 项目支持范围、安全目标、资源预算 | 待补充 |
| 硬件原理图 | TBD | I2C 通道、INT/RESET 引脚连接确认 | 待补充 |

---

## 附录A 需求清单

| 需求ID | 类别 | 需求名称 | 验证方式 | 验证阶段 | 状态 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA95xx-FUNC-0001 | 功能 | 设备状态机管理 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-FUNC-0002 | 功能 | 上电初始化与默认状态恢复 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-FUNC-0003 | 功能 | 硬件复位控制 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-FUNC-0004 | 功能 | I/O 方向配置 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0001 | 接口 | Init 接口 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0002 | 接口 | MainFunction 接口 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0003 | 接口 | GPIO 输入读取接口 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0004 | 接口 | GPIO 输出设置接口 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0005 | 接口 | 设备故障读取接口 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0006 | 接口 | 设备模式读取接口 | UT | UT | Draft |
| SRS-Gp_NCA95xx-CFG-0001 | 配置 | 芯片实例数量配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-CFG-0002 | 配置 | I2C 设备地址配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-CFG-0003 | 配置 | 默认 I/O 方向配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-CFG-0004 | 配置 | 默认输出电平配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-CFG-0005 | 配置 | I2C 通道配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-CFG-0006 | 配置 | 信号 ID 映射配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-CFG-0007 | 配置 | 中断与轮询配置 | Review/Test | Review/IT | Draft |
| SRS-Gp_NCA95xx-DIAG-0001 | 诊断 | I2C 通信错误检测 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-DIAG-0002 | 诊断 | 开发错误检测（DET） | UT | UT | Draft |
| SRS-Gp_NCA95xx-DIAG-0003 | 诊断 | 故障码编码 | UT | UT | Draft |
| SRS-Gp_NCA95xx-DIAG-0004 | 诊断 | 中断状态变化报告 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-TIM-0001 | 时序 | I2C Fast-mode 操作速率 | Analysis/Test | Analysis/IT | Draft |
| SRS-Gp_NCA95xx-TIM-0002 | 时序 | RESET 脉冲宽度 | Analysis/Test | Analysis/IT | Draft |
| SRS-Gp_NCA95xx-TIM-0003 | 时序 | RESET 恢复时间 | Analysis/Test | Analysis/IT | Draft |
| SRS-Gp_NCA95xx-TIM-0004 | 时序 | 中断有效响应时间 | Analysis/Test | Analysis/IT | Draft |
| SRS-Gp_NCA95xx-TIM-0005 | 时序 | I2C 总线空闲等待 | Analysis/Test | Review | Draft |
| SRS-Gp_NCA95xx-SAFE-0001 | 安全 | ASIL_B 安全完整性 | Review | Review | Draft |
| SRS-Gp_NCA95xx-SAFE-0002 | 安全 | 输出回读校验 | UT/IT | UT/IT | Draft |
| SRS-Gp_NCA95xx-SAFE-0003 | 安全 | 安全状态定义 | Review | IT | Draft |
| SRS-Gp_NCA95xx-CODE-0001 | 编码 | MISRA-C 编码规范 | Inspection | Build | Draft |
| SRS-Gp_NCA95xx-CODE-0002 | 编码 | 命名规范 | Inspection | Review | Draft |
| SRS-Gp_NCA95xx-CODE-0003 | 编码 | 文件结构规范 | Inspection | Review | Draft |
| SRS-Gp_NCA95xx-RES-0001 | 资源 | 内存资源约束 | Analysis | Build | Draft |
| SRS-Gp_NCA95xx-RES-0002 | 资源 | I2C 总线利用率 | Analysis | IT | Draft |
| SRS-Gp_NCA95xx-COMP-0001 | 过程 | 需求来源追溯 | Review | Review | Draft |
| SRS-Gp_NCA95xx-COMP-0002 | 过程 | 需求验证追溯 | Review | Review | Draft |

---

## 附录B 支持和相关性文件

| 序号 | 文件名称 | 文件编号/版本 | 来源 | 与本文档关系 |
| --- | --- | --- | --- | --- |
| 1 | Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN.md | Rev 1.0 | Novosense | 芯片能力与约束来源 |
| 2 | aurix2g-normative-patterns.md | — | Fc_Stack | 接口分类、状态机、配置、诊断、命名规范 |
| 3 | construction-rules.md | — | Fc_Stack | 需求字段完整性规则 |
| 4 | extraction-rules.md | — | Fc_Stack | 特征提取和软件责任判断规则 |
| 5 | calibration-rules.md | — | Fc_Stack | 写作校准和颗粒度规则 |
| 6 | srs-output-template.md | — | Fc_Stack | SRS 输出结构和渲染模板 |
| 7 | 项目需求文档 | TBD | 项目 | 项目支持范围和安全目标 |
| 8 | 硬件原理图 | TBD | 硬件 | I2C 通道和引脚连接确认 |
