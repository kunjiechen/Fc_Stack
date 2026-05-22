# 《Gp_NCA95yy 软件需求规范》

**Gp_NCA95yy_需求规范**

**Gp_NCA95yy_Requirements Specification**

项目编号/Project number:Gp_NCA95yy
保密性/Security:**内部使用**

**Document Properties**
Status:**草稿**
版本:**Draft**
Author:待填写
Created:待填写

**Approved Versions**
Current Document version **Draft** is **TBD**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| Draft | 草稿 | TBD | TBD | TBD |

## 适用说明

本文档适用于 `Gp_NCA95yy` 项目中 `Gp_NCA95yy` I2C GPIO 扩展器驱动的软件需求定义。本文档仅描述软件应满足的需求，不描述详细设计方案、代码实现方案或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| Draft | 待填写 | 待填写 | 初版生成，基于 NCA9539-Q1 Datasheet Rev1.0 | Draft |

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

本文档定义 `Gp_NCA95yy` 模块的软件需求，明确模块在项目中的功能边界、对外接口、状态行为、配置约束、诊断状态、时序要求、非功能约束和验证要求。

本文档作为 `Gp_NCA95yy` 模块软件架构设计、详细设计、编码实现、单元测试、集成测试和系统测试的上游输入。所有正式需求均应具备需求 ID、来源、约束、验收准则和验证方式。

---

## 2 适用范围

本文档适用于 `Gp_NCA95yy` 模块的软件开发、评审、集成、测试和交付活动。

### 2.1 适用对象

- 软件需求工程师
- 软件架构和详细设计工程师
- 软件开发工程师
- 软件测试工程师
- 功能安全工程师
- 项目质量和配置管理人员

### 2.2 适用范围

本文档覆盖 `Gp_NCA95yy` 模块的软件功能、接口、配置、诊断、时序及相关非功能需求，并给出需求来源、验证方式、验证阶段和需求状态。本文档不展开详细设计方案、代码实现方案和测试用例步骤。

---

## 3 定义和缩写

### 3.1 定义

| 术语 | 定义 |
| --- | --- |
| 对外支持行为 | 项目要求模块通过接口、配置或状态对外提供的软件行为。 |
| 硬件能力 | 芯片或平台具备的能力，不自动等同于软件需求。 |
| 软件责任 | 项目明确要求模块实现、拒绝、配置、验证或报告的行为。 |
| 读改写 | 对单 bit 输出操作时，需先读取同 port 当前输出寄存器值，修改目标 bit 后再整体写回，以保护同 port 其他 bit 不被破坏。 |

### 3.2 缩写

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| SRS | Software Requirement Specification | 软件需求规范 |
| UT | Unit Test | 单元测试 |
| IT | Integration Test | 集成测试 |
| ST | System Test | 系统测试 |
| ASIL | Automotive Safety Integrity Level | 汽车安全完整性等级 |
| QM | Quality Management | 质量管理等级 |
| GPIO | General Purpose Input/Output | 通用输入输出 |
| I2C | Inter-Integrated Circuit | 双线串行总线 |
| POR | Power-On Reset | 上电复位 |
| DET | Development Error Tracer | 开发错误追踪 |
| SCL | Serial Clock Line | I2C 串行时钟线 |
| SDA | Serial Data Line | I2C 串行数据线 |
| INT | Interrupt | 中断信号 |

---

## 4 概述

本章仅保留理解需求所需的芯片和驱动背景信息，避免展开实现细节；正式软件责任以下文需求条目为准。

### 4.1 外设芯片介绍

`Gp_NCA95yy` 驱动封装 NCA9539-Q1 芯片（Novosense），该芯片是一款 16-bit I2C GPIO 扩展器，通过 I2C 总线为 MCU 提供额外的 16 路 GPIO 扩展能力。

芯片支持以下功能：

- 16 位 GPIO 扩展（P00-P07 为 Port 0，P10-P17 为 Port 1）
- I2C 通信接口（标准模式 100 kHz / 快速模式 400 kHz），通过 A0/A1 硬件地址引脚支持同总线挂载最多 4 片芯片
- 输入极性反转配置，开漏低有效中断输出 (INT)，低有效硬件复位 (RESET)，内部上电复位 (POR)
- 供电电压 1.65 V 至 3.6 V，5 V 耐压 I/O 端口，AEC-Q100 Grade 1 认证

### 4.2 驱动功能介绍

`Gp_NCA95yy` 驱动应实现以下软件功能：

- 通过 I2C 总线初始化并管理 NCA9539-Q1 芯片实例，提供引脚级 GPIO 输入读取和输出写入接口（输出含读改写保护）
- 支持 GPIO 方向（输入/输出）和输入极性反转的初始化配置
- 通过 MainFunction 周期性检测 INT 中断状态，提供芯片故障诊断信息读取接口
- 所有对外接口实现 DET 错误检测机制

### 4.3 外设引脚介绍

| 引脚 | 方向 | Pin口功能 |
| --- | --- | --- |
| INT | 输出(芯片→MCU) | 开漏低有效中断输出，需上拉电阻至 VDD；任一输入引脚状态变化时触发 |
| A1, A0 | 输入 | I2C 地址选择位，接 VDD 或 GND，支持 4 个设备地址 |
| RESET | 输入(MCU→芯片) | 低有效硬件复位，需上拉电阻至 VDD；复位脉宽 >= 6 ns |
| SCL | 输入 | I2C 串行时钟，需上拉电阻至 VDD；内置噪声滤波器 |
| SDA | 双向(开漏) | I2C 串行数据，需上拉电阻至 VDD；内置噪声滤波器 |
| P00-P07 | 双向 | Port 0 GPIO (8 bit)，上电默认配置为输入 |
| P10-P17 | 双向 | Port 1 GPIO (8 bit)，上电默认配置为输入 |
| VDD, VSS | 电源/地 | 供电电压 1.65 V 至 3.6 V |

### 4.4 寄存器映射

NCA9539-Q1 内部包含 4 对 8-bit 寄存器（Port 0 和 Port 1 各一组），通过命令字节 (Command Byte) 寻址：

| 命令字节 | 寄存器对 | 访问属性 | 上电默认值 |
| --- | --- | --- | --- |
| 00h / 01h | Input Port 0 / 1 | 只读 | 0xFF |
| 02h / 03h | Output Port 0 / 1 | 读/写 | 0xFF |
| 04h / 05h | Polarity Inversion 0 / 1 | 读/写 | 0x00 |
| 06h / 07h | Configuration 0 / 1 | 读/写 | 0xFF |

核心语义：Configuration 寄存器 bit=1 → 输入（高阻态），bit=0 → 输出；Input Port 寄存器始终反映引脚实际电平；Output Port 寄存器仅对配置为输出的引脚生效。

### 4.5 I2C 通信参数

- 器件地址：7-bit 固定部分 `11101` + A1 + A0 + R/W bit；支持地址 0x74/0x75/0x76/0x77
- 时钟频率：最高 400 kHz (Fast-mode)；总线空闲 >= 1.3 us，SCL LOW >= 1.3 us，SCL HIGH >= 0.6 us
- 写入同一寄存器对的两个 port 时数据连续发送，无需重新发送命令字节；详细的时序约束见 6.1 节

---

## 5 功能需求

本章描述模块必须实现的功能行为，包括模式与初始化、接口、配置和诊断。每条需求使用固定字段描述，以便后续生成设计、测试和追溯矩阵。

### 5.1 模式需求

#### SRS-GPNCA95YY-FUNC-0001 驱动初始化

`功能需求` `ASIL-D` `Test / UT/IT` `Draft` `来源: 芯片手册-6.3.1 POR；原始需求-初始化`

`Gp_NCA95yy` 模块应在 Init 接口中完成当前核所有已配置芯片实例的初始化：依次对每片芯片加载配置表中的默认方向、默认输出电平和默认极性反转值，写回芯片寄存器并使芯片进入就绪状态。

**功能约束**

- **范围边界**：仅初始化当前核已配置的芯片实例；RESET 引脚的硬件复位操作不属于本模块软件责任（由硬件电路或上层复位管理模块控制）。
- **前置条件**：底层 I2C 驱动已完成初始化；配置表已通过集成工具生成并链接。
- **触发条件**：上层调用 Init 接口。
- **输入**：当前核配置表（含芯片数量、I2C 地址、默认方向表、默认输出表、默认极性表）。
- **输出**：各芯片 Configuration/Output/Polarity 寄存器写入对应默认值；芯片进入可操作状态。
- **异常处理**：任一芯片 I2C 写入失败时，应记录故障并返回初始化失败状态；已成功初始化的芯片状态应标记为非就绪，等待重试或故障恢复。
- **验收准则**：初始化完成后，读取各芯片 Configuration/Output/Polarity 寄存器应与配置表默认值一致；注入 I2C 通信故障时，模块应返回初始化失败且不影响已初始化其他芯片的寄存器实际值（寄存器由硬件保持）。

---

#### SRS-GPNCA95YY-FUNC-0002 GPIO 方向配置

`功能需求` `ASIL-D` `Test / UT` `Draft` `来源: 芯片手册-6.5.6 Configuration Registers；原始需求-运行时配置方向`

`Gp_NCA95yy` 模块应支持对指定 GPIO 引脚进行方向配置：向 Configuration 寄存器对应 bit 写入 1 将引脚配置为输入（高阻态），写入 0 将引脚配置为输出。

**功能约束**

- **范围边界**：是否支持运行时动态修改方向的策略由项目确认；若项目禁止运行时修改，则方向配置仅在 Init 阶段生效。
- **前置条件**：芯片已完成初始化；目标引脚已配置。
- **触发条件**：项目允许运行时修改方向时，上层调用方向配置接口并传入有效参数。
- **输入**：信号 Id（解析出 chip/port/pin）、目标方向（输入/输出）。
- **输出**：目标引脚 Configuration 寄存器对应 bit 更新；不影响同 port 其他 bit 的方向配置。
- **异常处理**：Id 非法、芯片未初始化、I2C 写入失败时应返回错误，且不修改任何寄存器状态。
- **验收准则**：对有效输入，读回 Configuration 寄存器确认目标 bit 更新正确且其他 bit 不变；非法输入不产生寄存器写入。

---

#### SRS-GPNCA95YY-FUNC-0003 GPIO 输入读取

`功能需求` `ASIL-D` `Test / UT` `Ready` `来源: 芯片手册-6.5.3 Input Port Registers；原始需求-引脚输入读取`

`Gp_NCA95yy` 模块应支持读取指定 GPIO 引脚的输入状态：通过 I2C 读取对应 Input Port 寄存器，依据 Polarity Inversion 配置对该 bit 做可选的逻辑反转后，返回引脚逻辑状态。

**功能约束**

- **范围边界**：读取 Input Port 寄存器始终反映引脚实际电平，与引脚配置为输入或输出无关。极性反转仅影响软件返回结果，不改变硬件寄存器值。
- **前置条件**：芯片已完成初始化。
- **触发条件**：上层调用输入读取接口并传入有效信号 Id。
- **输入**：信号 Id（解析出 chip/port/pin）。
- **输出**：目标引脚的当前逻辑状态（0 或 1），已应用极性反转。
- **异常处理**：Id 非法、芯片未初始化、I2C 读取失败时应返回错误，输出参数不被修改。
- **验收准则**：模拟不同 Input Port 寄存器值和极性配置组合，验证接口返回正确的反转/非反转结果；非法 Id 和通信故障返回错误。

---

#### SRS-GPNCA95YY-FUNC-0004 GPIO 输出写入

`功能需求` `ASIL-D` `Test / UT/IT` `Draft` `来源: 芯片手册-6.5.4 Output Port Registers；原始需求-引脚输出写入`

`Gp_NCA95yy` 模块应支持设置指定 GPIO 引脚的输出电平：通过 I2C 先读取当前 Output Port 寄存器值，修改目标 bit 后整体写回（读改写），保证同 port 其他 bit 的输出状态不被破坏。

**功能约束**

- **范围边界**：仅对已配置为输出的引脚生效；对配置为输入的引脚，Output Port 寄存器写入不影响引脚电平，但寄存器值会被更新。
- **前置条件**：芯片已完成初始化；目标引脚已配置为输出。
- **触发条件**：上层调用输出写入接口并传入有效信号 Id 和目标电平。
- **输入**：信号 Id（解析出 chip/port/pin）、目标输出电平（0 或 1）。
- **输出**：目标引脚 Output Port 寄存器对应 bit 更新为目标值；同 port 其他 bit 不变。
- **异常处理**：Id 非法、芯片未初始化、I2C 读取或写入失败时应返回错误，Output Port 寄存器保持写入前状态。
- **验收准则**：连续对同一 port 不同 pin 执行输出写入，验证各 pin 输出互不干扰；注入 I2C 写入故障时寄存器值不变。

---

#### SRS-GPNCA95YY-FUNC-0005 输入极性反转配置

`功能需求` `ASIL-D` `Test / UT` `Draft` `来源: 芯片手册-6.5.5 Polarity Inversion Registers；原始需求-极性反转配置`

`Gp_NCA95yy` 模块应支持配置指定 GPIO 引脚的输入极性反转：向 Polarity Inversion 寄存器对应 bit 写入 1 启用反转（输入读取时逻辑取反），写入 0 保持原始极性。

**功能约束**

- **范围边界**：极性反转仅影响 Input Port 读取的软件返回结果，不影响 Output Port 行为；是否支持运行时修改极性由项目确认。
- **前置条件**：芯片已完成初始化。
- **触发条件**：初始化加载默认极性配置；若项目允许运行时修改，上层调用极性配置接口。
- **输入**：信号 Id（解析出 chip/port/pin）、反转使能（0/1）。
- **输出**：Polarity Inversion 寄存器对应 bit 更新；后续 Input Port 读取对该 bit 按配置进行反转/不反转。
- **异常处理**：Id 非法、芯片未初始化、I2C 写入失败时应返回错误且不修改寄存器。
- **验收准则**：配置反转后验证输入读取结果逻辑取反；配置回原始极性后恢复；非法输入不产生寄存器变更。

---

#### SRS-GPNCA95YY-FUNC-0006 中断检测与响应

`功能需求` `ASIL-D` `Test / IT` `Draft` `来源: 芯片手册-6.2.3 Interrupt Output；原始需求-中断检测和响应`

`Gp_NCA95yy` 模块应在 MainFunction 中周期性检测 INT 引脚状态。当检测到 INT 有效（LOW）时，应通过读取 Input Port 寄存器识别发生变化的输入引脚，并向上层报告中断事件。中断在对应 Input Port 寄存器被读取后由芯片硬件自动清除。

**功能约束**

- **范围边界**：INT 引脚为开漏输出，需外部上拉电阻；软件不控制 INT 清除（由芯片硬件在读 Input Port 时自动清除）。每个 8-bit port 的中断独立清除——Port 0 的读操作不清除 Port 1 的中断。
- **前置条件**：芯片已完成初始化；INT 引脚已正确连接到 MCU GPIO。
- **触发条件**：任一配置为输入的引脚电平发生变化（上升沿或下降沿）。
- **输入**：INT 引脚 GPIO 输入状态；Input Port 寄存器值。
- **输出**：中断事件通知（含 chip/port/pin 和变化状态）；更新内部输入状态缓存。
- **异常处理**：无法确认中断源（I2C 读取 Input Port 失败）时，应记录通信故障并保持中断 pending 状态待下次周期重试。
- **验收准则**：模拟输入引脚电平变化后，INT 有效且 MainFunction 正确识别变化引脚；读取 Input Port 后确认 INT 清除；模拟两个 port 同时变化时，读 Port 0 不误清除 Port 1 的中断。

---

#### SRS-GPNCA95YY-FUNC-0007 芯片复位处理

`功能需求` `ASIL-D` `Test / IT` `Draft` `来源: 芯片手册-6.2.2 RESET Input；芯片手册-6.3.1 POR`

`Gp_NCA95yy` 模块应识别芯片复位事件（包括硬件 RESET 引脚复位和上电 POR 复位），在复位发生后能够将芯片寄存器恢复至配置表默认值，使芯片重新进入可操作状态。

**功能约束**

- **范围边界**：RESET 引脚的低有效硬件复位由外部硬件电路触发，软件不主动控制 RESET 引脚（除非项目明确将 RESET 引脚归属本驱动）。POR 复位在 VDD 上电或 VDD 降至 0.2 V 以下超过 50 us 后重新上电时由芯片硬件自动执行。复位后所有寄存器恢复默认值（Input=0xFF, Output=0xFF, Polarity=0x00, Config=0xFF），软件需重新初始化。
- **前置条件**：芯片硬件复位已完成（RESET 引脚恢复高电平或 VDD 达到 V_POR 以上）。
- **触发条件**：检测到芯片寄存器值与软件缓存状态不一致，或收到上层复位恢复请求。
- **输入**：复位恢复信号或状态不一致检测结果。
- **输出**：芯片寄存器重新写入配置表默认值；软件内部状态恢复为就绪。
- **异常处理**：复位恢复过程中 I2C 写入失败时应重试或标记芯片不可用。
- **验收准则**：模拟复位事件后触发恢复流程，验证芯片寄存器恢复至配置默认值；恢复期间通信失败时模块应正确标记故障状态。

---

#### SRS-GPNCA95YY-FUNC-0008 MainFunction 周期处理

`功能需求` `ASIL-D` `Test / UT` `Draft` `来源: AURIX2G 规范-1.2 MainFunction 接口规则；芯片手册-6.2.3 Interrupt`

`Gp_NCA95yy` 模块应提供 MainFunction 周期性驱动函数，在每个调用周期内执行：INT 引脚状态采样、中断状态评估、pending 输入变化识别与上报。

**功能约束**

- **范围边界**：MainFunction 调用周期由项目根据系统时序要求配置；MainFunction 不执行 Output/Configuration/Polarity 的主动刷新（这些由相应的 Set/Write 接口在调用时同步完成）。
- **前置条件**：芯片已完成初始化。
- **触发条件**：上层周期性调用 MainFunction。
- **输入**：INT 引脚 GPIO 状态；当前内部输入缓存。
- **输出**：更新后的输入状态缓存；中断事件通知（如有）。
- **异常处理**：MainFunction 内部不得阻塞或无限等待；I2C 通信失败时应在当次周期记录故障并返回，不中断后续周期调度。
- **验收准则**：通过调整 MainFunction 调用周期和输入变化时机验证：变化发生后首个 MainFunction 周期内应检测到 INT 有效；无变化时 MainFunction 应快速返回不产生误报。

---

### 5.2 接口需求

#### SRS-GPNCA95YY-IF-0001 Init 接口

`接口需求` `ASIL-D` `Test / UT/IT` `Draft` `来源: AURIX2G 规范-1.1 接口分类法则；原始需求-Init`

`Gp_NCA95yy` 模块应提供 `Gp_NCA95yy_Init(void)` 接口，完成当前核所有已配置芯片实例的初始化。

**接口约束**

- **输入**：无（从配置表读取芯片数量、I2C 地址、默认方向/输出/极性）。
- **输出**：无返回值（void）。操作必然成功完成或通过内部故障标记记录。
- **前置条件**：底层 I2C 驱动已完成初始化；配置表有效。
- **异常处理**：芯片 I2C 通信失败时应记录故障。配置表为空（芯片数量为 0）时视为合法场景，直接返回。
- **验收准则**：正常初始化后验证各芯片寄存器值与配置表一致；配置表为空时正常返回不报错；I2C 故障时记录故障。

---

#### SRS-GPNCA95YY-IF-0002 MainFunction 接口

`接口需求` `ASIL-D` `Test / UT` `Draft` `来源: AURIX2G 规范-1.2 MainFunction 接口规则；芯片手册-6.2.3`

`Gp_NCA95yy` 模块应提供 `Gp_NCA95yy_MainFunction(void)` 周期性驱动接口，执行 INT 引脚状态采样和中断响应处理。

**接口约束**

- **输入**：无。
- **输出**：无返回值（void）。
- **前置条件**：至少一个芯片实例已完成初始化。
- **异常处理**：所有芯片未初始化时直接返回不执行任何操作；I2C 通信失败时记录故障。
- **验收准则**：中断触发后 MainFunction 正确识别并报告；无芯片初始化时直接返回。

---

#### SRS-GPNCA95YY-IF-0003 GPIO 输入读取接口

`接口需求` `ASIL-D` `Test / UT` `Ready` `来源: 芯片手册-6.5.3 Input Port Registers；原始需求-GetGpInSig`

`Gp_NCA95yy` 模块应提供 `Gp_NCA95yy_GetGpInSig(uint16 Id_u16, uint8* State_pu8)` 接口，解析信号 Id 后通过 I2C 读取对应 Input Port 寄存器，应用极性反转后返回该引脚的逻辑状态。

**接口约束**

- **输入**：`Id_u16` — 信号标识，编码 Core/Chip/Port/Pin 信息；`State_pu8` — 输出参数指针。
- **输出**：`Std_ReturnType` — E_OK 表示读取成功，E_NOT_OK 表示失败。
- **有效输入范围**：Id 对应的 chip/port/pin 必须在配置范围内。
- **失败后置条件**：返回 E_NOT_OK 时 `*State_pu8` 不被修改。
- **验收准则**：验证各 chip/port/pin 组合的正确读取结果；验证极性反转配置生效；非法 Id 返回 E_NOT_OK 且不修改输出参数。

---

#### SRS-GPNCA95YY-IF-0004 GPIO 输出写入接口

`接口需求` `ASIL-D` `Test / UT` `Draft` `来源: 芯片手册-6.5.4 Output Port Registers；原始需求-SetGpOutSig`

`Gp_NCA95yy` 模块应提供 `Gp_NCA95yy_SetGpOutSig(uint16 Id_u16, uint8 State_u8)` 接口，解析信号 Id 后通过读改写方式设置目标引脚的输出电平，保证同 port 其他 bit 不受影响。

**接口约束**

- **输入**：`Id_u16` — 信号标识；`State_u8` — 目标输出电平（0 或 1）。
- **输出**：`Std_ReturnType` — E_OK 表示写入成功，E_NOT_OK 表示失败。
- **有效输入范围**：Id 对应的 chip/port/pin 必须在配置范围内；State 仅接受 0 或 1。
- **失败后置条件**：返回 E_NOT_OK 时 Output Port 寄存器保持写入前状态不变。
- **验收准则**：连续对同 port 不同 pin 写入，验证互不干扰；非法 Id 或 State 返回 E_NOT_OK 且寄存器不变。

---

#### SRS-GPNCA95YY-IF-0005 故障诊断信息读取接口

`接口需求` `ASIL-D` `Test / IT` `Draft` `来源: AURIX2G 规范-8.8 IoExtDev 接口；芯片手册-6.2.3 INT；原始需求-GetDevFaultSig`

`Gp_NCA95yy` 模块应提供 `Gp_NCA95yy_GetDevFaultSig(uint16 Id_u16, uint32* Fault_pu32)` 接口，返回指定芯片实例的当前故障诊断信息，包括 I2C 通信错误、中断异常状态和初始化失败标志。

**接口约束**

- **输入**：`Id_u16` — 信号标识（解析出 chip）；`Fault_pu32` — 输出参数指针（uint32 位掩码）。
- **输出**：`Std_ReturnType` — E_OK 表示读取成功，E_NOT_OK 表示失败。
- **故障位定义**（待项目确认完整编码）：
  - Bit 0: I2C 通信错误
  - Bit 1: 芯片未初始化
  - Bit 2: 初始化失败
  - Bit 3: 中断异常（INT 持续有效超时）
  - Bit 4-31: 保留
- **失败后置条件**：返回 E_NOT_OK 时 `*Fault_pu32` 不被修改。
- **验收准则**：通过故障注入验证各故障位正确置位和清除；故障恢复后对应 bit 清零。

---

#### SRS-GPNCA95YY-IF-0006 DET 错误检测

`接口需求` `ASIL-D` `Test / UT` `Ready` `来源: 原始需求-所有接口必须支持DET错误检测`

`Gp_NCA95yy` 模块的所有对外接口应实现 DET (Development Error Tracer) 错误检测：当接口被调用时传入非法参数（Id 越界、空指针、State 非法值等），应通过 DET 机制报告开发错误并返回 E_NOT_OK。

**接口约束**

- **输入**：所有对外接口的输入参数。
- **输出**：DET 报告（ReportError）；Std_ReturnType 返回 E_NOT_OK。
- **检测项**（适用于所有接口）：
  - 空指针检测：输出指针参数为 NULL
  - Id 越界检测：Id 解析出的 chip/port/pin 超出配置范围
  - 未初始化检测：芯片实例未完成初始化
  - 参数范围检测：State 值非 0/1（SetGpOutSig）
- **验收准则**：对各接口注入非法参数，验证 DET 报告触发且接口返回 E_NOT_OK；合法参数不触发 DET。

---

### 5.3 配置需求

#### SRS-GPNCA95YY-CFG-0001 I2C 设备地址配置

`配置需求` `ASIL-D` `Review/Test / Review` `Draft` `来源: 芯片手册-6.5.1 Device Address；原始需求-I2C设备地址可配置`

`Gp_NCA95yy` 模块应支持对每片芯片实例配置其 I2C 设备地址。设备地址由芯片硬件地址引脚 A1/A0 决定，软件配置的地址必须与实际硬件连线一致。

**配置约束**

- **配置项**：每芯片 I2C 7-bit 设备地址。
- **有效范围**：`0x74` (A1=0,A0=0), `0x75` (A1=0,A0=1), `0x76` (A1=1,A0=0), `0x77` (A1=1,A0=1)。
- **默认值**：待项目确认（通常为 0x74）。
- **配置依赖**：必须与硬件 A0/A1 引脚连接一致；同一 I2C 总线上不同芯片必须分配不同地址。
- **无效值处理**：地址不在有效枚举范围内时，配置验证阶段应拒绝并报错。
- **验收准则**：配置为各有效地址后，验证 I2C 通信正常（芯片正确响应地址字节）；配置无效地址时配置检查报错。

---

#### SRS-GPNCA95YY-CFG-0002 芯片实例数量配置

`配置需求` `ASIL-D` `Review / Review` `Draft` `来源: 原始需求-每核芯片实例数量可配置`

`Gp_NCA95yy` 模块应支持配置当前核管理的芯片实例数量（0-4 片），当实例数量为 0 时模块不执行任何芯片操作。

**配置约束**

- **配置项**：`MultiChipNum_u8` — 当前核芯片实例数量。
- **有效范围**：`0..4`。
- **默认值**：待项目确认。
- **配置依赖**：每芯片需独立配置 I2C 地址、默认方向和默认输出。
- **无效值处理**：超出 0..4 范围时配置验证阶段拒绝并报错。
- **验收准则**：配置为 0 时所有接口不执行芯片访问；配置为 1-4 时正确初始化对应数量的芯片。

---

#### SRS-GPNCA95YY-CFG-0003 GPIO 默认方向配置

`配置需求` `ASIL-D` `Review / Review` `Draft` `来源: 芯片手册-6.5.6 Configuration Registers；原始需求-默认GPIO方向可配置`

`Gp_NCA95yy` 模块应支持对每片芯片的每个 GPIO 引脚配置上电初始化后的默认方向（输入或输出）。

**配置约束**

- **配置项**：每芯片 Port 0 (8 bit) 和 Port 1 (8 bit) 的默认方向位图。
- **有效范围**：每个 bit 为 0（输出）或 1（输入）。
- **默认值**：待项目确认（芯片硬件默认 0xFF，全部为输入）。
- **配置依赖**：默认输出电平配置应与方向配置一致（配置为输出的引脚需定义默认输出电平）。
- **无效值处理**：无（任意 8-bit 位图均合法）。
- **验收准则**：Init 后验证芯片 Configuration 寄存器与配置表一致。

---

#### SRS-GPNCA95YY-CFG-0004 GPIO 默认输出电平配置

`配置需求` `ASIL-D` `Review / Review` `Draft` `来源: 芯片手册-6.5.4 Output Port Registers；原始需求-默认输出电平可配置`

`Gp_NCA95yy` 模块应支持对每片芯片的每个 GPIO 引脚配置上电初始化后的默认输出电平。

**配置约束**

- **配置项**：每芯片 Port 0 (8 bit) 和 Port 1 (8 bit) 的默认输出电平位图。
- **有效范围**：每个 bit 为 0（低电平）或 1（高电平）。
- **默认值**：待项目确认（芯片硬件默认 0xFF）。
- **配置依赖**：仅对配置为输出的引脚有意义；配置为输入的引脚忽略此值。
- **无效值处理**：无（任意 8-bit 位图均合法）。
- **验收准则**：Init 后验证芯片 Output Port 寄存器与配置表一致。

---

#### SRS-GPNCA95YY-CFG-0005 中断使能与去抖配置

`配置需求` `ASIL-D` `Review / Review` `Draft` `来源: 原始需求-中断使能和去抖时间可配置`

`Gp_NCA95yy` 模块应支持配置中断检测的使能状态和去抖参数。当某芯片中断被禁用时，MainFunction 不检测该芯片的 INT 引脚。

**配置约束**

- **配置项**：
  - 中断使能开关（每芯片，Enable/Disable）
  - 去抖时间（单位：MainFunction 调用次数或毫秒，待项目确认）
- **有效范围**：去抖阈值 >= 1（待项目确认上限）。
- **默认值**：中断使能 = Enable；去抖阈值 = 待项目确认。
- **配置依赖**：中断使能依赖 INT 引脚已连接到 MCU GPIO。
- **无效值处理**：去抖阈值为 0 或超出范围时配置验证阶段拒绝。
- **验收准则**：禁用中断时，引脚变化不产生中断事件；配置去抖阈值后，电平变化持续时间小于阈值时不触发中断。

---

### 5.4 诊断需求

#### SRS-GPNCA95YY-DIAG-0001 I2C 通信故障检测

`诊断需求` `ASIL-D` `Test / UT` `Ready` `来源: 芯片手册-6.4 I2C Interface；AURIX2G 规范-6.3 SPI 通信错误检测(类比I2C)`

`Gp_NCA95yy` 模块应在每次 I2C 读写操作后检测通信是否成功。当 I2C 从设备无应答 (NACK)、总线仲裁丢失或超时时，应标记对应芯片的 I2C 通信错误故障位。

**诊断约束**

- **观测方式**：通过 `GetDevFaultSig` 接口读取 I2C 通信错误位 (Bit 0)。
- **故障触发条件**：I2C 发送地址字节后收到 NACK；I2C 数据字节后收到 NACK；总线超时。
- **故障清除条件**：后续 I2C 通信成功（连续成功次数达到项目定义阈值后清除）。
- **验收准则**：注入 I2C NACK/超时故障后，`GetDevFaultSig` 返回对应故障位=1；故障恢复后故障位清零。

---

#### SRS-GPNCA95YY-DIAG-0002 未初始化访问检测

`诊断需求` `ASIL-D` `Test / UT` `Ready` `来源: AURIX2G 规范-6.2 诊断错误码设计`

`Gp_NCA95yy` 模块应在除 Init 外的所有对外接口中检测芯片实例是否已完成初始化。对未初始化实例的访问应通过 DET 报告并返回 E_NOT_OK。

**诊断约束**

- **观测方式**：DET ReportError + Std_ReturnType 返回 E_NOT_OK。
- **故障触发条件**：接口被调用时目标芯片实例未完成初始化（从未调用过 Init 或 Init 失败后未恢复）。
- **验收准则**：对未初始化芯片调用 GetGpInSig/SetGpOutSig/GetDevFaultSig，验证返回 E_NOT_OK 且触发 DET；Init 后调用正常。

---

#### SRS-GPNCA95YY-DIAG-0003 中断异常监控

`诊断需求` `ASIL-D` `Test / IT` `Draft` `来源: 芯片手册-6.2.3 Interrupt Output`

`Gp_NCA95yy` 模块应在 MainFunction 中监控 INT 引脚状态。当 INT 持续有效（LOW）超过配置的去抖时间且读取 Input Port 后仍未清除时，应标记中断异常故障。

**诊断约束**

- **观测方式**：通过 `GetDevFaultSig` 接口读取中断异常位 (Bit 3)。
- **故障触发条件**：INT 持续有效超过去抖时间 + 读取 Input Port 后未清除。
- **故障清除条件**：INT 恢复无效（HIGH）且 Input Port 读取值稳定。
- **验收准则**：模拟持续 INT 有效且 Input Port 未变化场景，验证中断异常故障置位；恢复正常后故障位清零。

---

#### SRS-GPNCA95YY-DIAG-0004 参数有效性检查

`诊断需求` `ASIL-D` `Test / UT` `Ready` `来源: 原始需求-所有外部接口需进行参数有效性检查`

`Gp_NCA95yy` 模块的所有对外接口应在执行功能操作前完成输入参数的有效性检查，非法参数应拒绝执行并通过 DET 报告。

**诊断约束**

- **观测方式**：DET ReportError + Std_ReturnType 返回 E_NOT_OK。
- **检查项**：
  - Id 越界或非法（chip/port/pin 超出配置范围）
  - 空指针（输出参数为 NULL）
  - 参数值越界（State 非 0/1）
  - 方向不匹配（对配置为输入的引脚执行输出写入时的处理策略由项目确认）
- **验收准则**：逐项注入非法参数，验证接口拒绝执行并触发 DET；合法参数正常执行。

---

## 6 非功能需求

### 6.1 时序需求

#### SRS-GPNCA95YY-TIM-0001 I2C 总线时序约束

`时序需求` `ASIL-D` `Analysis/Test / IT` `Draft` `来源: 芯片手册-5.2 Dynamic Characteristics`

`Gp_NCA95yy` 模块的 I2C 通信应符合 NCA9539-Q1 Fast-mode (400 kHz) 时序约束，具体参数由底层 I2C 驱动保证。模块级需确保：

**时序约束**

- **SCL 时钟频率**：<= 400 kHz (Fast-mode)。
- **总线空闲时间 (t_BUF)**：>= 1.3 us。
- **数据建立时间 (t_SU;DAT)**：>= 100 ns。
- **数据保持时间 (t_HD;DAT)**：>= 0 ns。
- **验收准则**：通过 I2C 总线时序分析或集成测试确认通信波形满足所有 Fast-mode 时序参数。

---

#### SRS-GPNCA95YY-TIM-0002 复位恢复时序

`时序需求` `ASIL-D` `Analysis/Test / IT` `Draft` `来源: 芯片手册-5.2 Dynamic Characteristics；芯片手册-6.2.2`

`Gp_NCA95yy` 模块在芯片复位（RESET 引脚或 POR）后，应满足以下时序约束：

**时序约束**

- **RESET 最小脉宽 (t_w(rst))**：>= 6 ns（硬件保证）。
- **RESET 恢复时间 (t_rec(rst))**：>= 200 ns — 在 RESET 恢复高电平后，软件至少等待 200 ns 才能发起 I2C 通信。
- **复位完成时间 (t_rst)**：>= 400 ns — 从 RESET 有效到芯片寄存器恢复默认值的最长时间。
- **POR 复位条件**：VDD 需降至 0.2 V 以下并保持至少 50 us 才能触发内部 POR 复位。
- **责任方**：t_w(rst) 由硬件保证；t_rec(rst) 和 t_rst 由软件在复位恢复流程中保证。
- **验收准则**：复位后验证等待时间满足 t_rec(rst) 和 t_rst 后才发起 I2C 通信；通信正常。

---

#### SRS-GPNCA95YY-TIM-0003 中断响应时序

`时序需求` `ASIL-D` `Analysis/Test / IT` `Draft` `来源: 芯片手册-5.2 Dynamic Characteristics`

`Gp_NCA95yy` 模块应满足以下中断相关时序约束：

**时序约束**

- **INT 有效时间 (t_v(INT_N))**：从输入引脚电平变化到 INT 有效的最大延迟为 4 us（芯片硬件保证）。
- **INT 复位时间 (t_rst(INT_N))**：从 SCL 第 9 个时钟下降沿（ACK）到 INT 恢复无效的最大延迟为 4 us。
- **验收准则**：通过集成测试验证中断响应时间满足项目实时性要求；t_v(INT_N) 和 t_rst(INT_N) 由芯片硬件保证，软件仅需在 MainFunction 周期内及时采样。

---

#### SRS-GPNCA95YY-TIM-0004 MainFunction 调用周期

`时序需求` `ASIL-D` `Analysis / Review` `Draft` `来源: AURIX2G 规范-7.2 MainFunction 周期约束`

`Gp_NCA95yy` 模块的 MainFunction 调用周期应由项目根据系统输入响应时间要求配置，建议周期为 1 ms - 10 ms。

**时序约束**

- **调用周期**：待项目确认（建议 1-10 ms），通过配置项设定。
- **执行时间约束**：MainFunction 单次执行时间应小于调用周期的 50%，确保不阻塞同任务其他模块。
- **验收准则**：通过 Worst-Case Execution Time 分析和运行时测量，验证 MainFunction 执行时间满足约束。

---

### 6.2 安全等级需求

#### SRS-GPNCA95YY-SAFE-0001 安全等级要求

`安全需求` `ASIL-D` `Review / Review` `Ready` `来源: 原始需求-ASIL-D`

`Gp_NCA95yy` 模块应按 ASIL-D 安全等级进行开发，所有需求、设计、实现和测试活动应符合 ISO 26262-6 对 ASIL-D 软件组件的要求。

**约束定义**

- **适用范围**：本模块所有功能和接口。
- **验收准则**：通过功能安全审计和评估确认 ASIL-D 开发活动完整。

---

### 6.3 编码规范需求

#### SRS-GPNCA95YY-CODE-0001 编码规范符合性

`编码需求` `ASIL-D` `Inspection/Analysis / Review` `Ready` `来源: 原始需求-满足MISRA-C编码规范`

`Gp_NCA95yy` 模块的软件实现应遵循项目指定的编码规范（含 MISRA-C:2012），并通过静态分析工具验证。

**约束定义**

- **适用范围**：本模块所有 C 源码和头文件。
- **验收准则**：通过 MISRA-C 静态分析检查，所有违规项有记录和偏差说明。

---

### 6.4 资源消耗需求

#### SRS-GPNCA95YY-RES-0001 资源消耗约束

`资源需求` `ASIL-D` `Analysis / Review` `Draft` `来源: 原始需求-ROM/RAM资源消耗需评估记录`

`Gp_NCA95yy` 模块的 ROM、RAM 和栈资源消耗应在设计阶段评估，在集成阶段从构建产物（linker map）中实测记录，结果提交项目评审。

**约束定义**

- **资源类型**：ROM（代码段 + 常量段）、RAM（全局/静态变量）、Stack（最坏情况调用栈）。
- **预算**：待项目确认。
- **缩放规则**：RAM 消耗与芯片实例数量成正比（每实例需独立运行时数据）；ROM 消耗相对固定。
- **验收准则**：提供基于 linker map 的资源测量报告和 stack usage 分析报告。

---

## 7 需求来源

| 来源类别 | 来源名称 | 与本文档关系 | 状态 |
| --- | --- | --- | --- |
| 芯片手册 | NCA9539-Q1 Datasheet Rev1.0 (Novosense) | 芯片能力、引脚、寄存器、时序和电气约束来源 | 已接入 |
| 原始需求 | RAWREQ-GPNCA95YY-001 | 模块名称、接口列表、安全等级、编码规范来源 | 已接入 |
| 平台规范 | AURIX2G 平台规范经验库 | 接口命名、MainFunction 判定、状态机、配置模式来源 | 已接入 |

---

## 附录A 需求清单

| 需求ID | 类别 | 需求名称 | 验证方式 | 验证阶段 | 状态 |
| --- | --- | --- | --- | --- | --- |
| SRS-GPNCA95YY-FUNC-0001 | 功能需求 | 驱动初始化 | Test | UT/IT | Draft |
| SRS-GPNCA95YY-FUNC-0002 | 功能需求 | GPIO 方向配置 | Test | UT | Draft |
| SRS-GPNCA95YY-FUNC-0003 | 功能需求 | GPIO 输入读取 | Test | UT | Ready |
| SRS-GPNCA95YY-FUNC-0004 | 功能需求 | GPIO 输出写入 | Test | UT/IT | Draft |
| SRS-GPNCA95YY-FUNC-0005 | 功能需求 | 输入极性反转配置 | Test | UT | Draft |
| SRS-GPNCA95YY-FUNC-0006 | 功能需求 | 中断检测与响应 | Test | IT | Draft |
| SRS-GPNCA95YY-FUNC-0007 | 功能需求 | 芯片复位处理 | Test | IT | Draft |
| SRS-GPNCA95YY-FUNC-0008 | 功能需求 | MainFunction 周期处理 | Test | UT | Draft |
| SRS-GPNCA95YY-IF-0001 | 接口需求 | Init 接口 | Test | UT/IT | Draft |
| SRS-GPNCA95YY-IF-0002 | 接口需求 | MainFunction 接口 | Test | UT | Draft |
| SRS-GPNCA95YY-IF-0003 | 接口需求 | GPIO 输入读取接口 | Test | UT | Ready |
| SRS-GPNCA95YY-IF-0004 | 接口需求 | GPIO 输出写入接口 | Test | UT | Draft |
| SRS-GPNCA95YY-IF-0005 | 接口需求 | 故障诊断信息读取接口 | Test | IT | Draft |
| SRS-GPNCA95YY-IF-0006 | 接口需求 | DET 错误检测 | Test | UT | Ready |
| SRS-GPNCA95YY-CFG-0001 | 配置需求 | I2C 设备地址配置 | Review/Test | Review | Draft |
| SRS-GPNCA95YY-CFG-0002 | 配置需求 | 芯片实例数量配置 | Review | Review | Draft |
| SRS-GPNCA95YY-CFG-0003 | 配置需求 | GPIO 默认方向配置 | Review | Review | Draft |
| SRS-GPNCA95YY-CFG-0004 | 配置需求 | GPIO 默认输出电平配置 | Review | Review | Draft |
| SRS-GPNCA95YY-CFG-0005 | 配置需求 | 中断使能与去抖配置 | Review | Review | Draft |
| SRS-GPNCA95YY-DIAG-0001 | 诊断需求 | I2C 通信故障检测 | Test | UT | Ready |
| SRS-GPNCA95YY-DIAG-0002 | 诊断需求 | 未初始化访问检测 | Test | UT | Ready |
| SRS-GPNCA95YY-DIAG-0003 | 诊断需求 | 中断异常监控 | Test | IT | Draft |
| SRS-GPNCA95YY-DIAG-0004 | 诊断需求 | 参数有效性检查 | Test | UT | Ready |
| SRS-GPNCA95YY-TIM-0001 | 时序需求 | I2C 总线时序约束 | Analysis/Test | IT | Draft |
| SRS-GPNCA95YY-TIM-0002 | 时序需求 | 复位恢复时序 | Analysis/Test | IT | Draft |
| SRS-GPNCA95YY-TIM-0003 | 时序需求 | 中断响应时序 | Analysis/Test | IT | Draft |
| SRS-GPNCA95YY-TIM-0004 | 时序需求 | MainFunction 调用周期 | Analysis | Review | Draft |
| SRS-GPNCA95YY-SAFE-0001 | 安全需求 | 安全等级要求 | Review | Review | Ready |
| SRS-GPNCA95YY-CODE-0001 | 编码需求 | 编码规范符合性 | Inspection/Analysis | Review | Ready |
| SRS-GPNCA95YY-RES-0001 | 资源需求 | 资源消耗约束 | Analysis | Review | Draft |

---

## 附录B 支持和相关性文件

| 序号 | 文件名称 | 文件编号/版本 | 来源 | 与本文档关系 |
| --- | --- | --- | --- | --- |
| 1 | NCA9539-Q1 Datasheet | Rev1.0 (2023/1/5) | Novosense | 芯片能力、引脚、寄存器、时序和电气约束来源 |
| 2 | AURIX2G 平台规范经验库 | - | FC Stack 项目 | 接口命名、MainFunction 判定、状态机、配置模式来源 |
| 3 | 项目开发规范 | 待填写 | 项目输入 | 编码、资源和过程约束来源 |
| 4 | 项目硬件原理图 | 待填写 | 硬件团队 | 引脚连接、I2C 总线拓扑、地址分配 |
| 5 | 项目配置表 | 待填写 | 项目配置 | 默认方向、默认输出、实例数量、I2C 地址 |
