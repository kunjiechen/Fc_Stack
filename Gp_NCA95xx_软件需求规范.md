# 《Gp_NCA95xx 软件需求规范》

**Gp_NCA95xx_需求规范**

**Gp_NCA95xx_Requirements Specification**

项目编号/Project number: Gp_NCA95xx
保密性/Security: 内部

**Document Properties**
Status:**草稿**
版本:**0.1.0**
Author: FC Requirement Workbench
Created: 2026-05-22 10:00

**Approved Versions**
Current Document version **0.1.0** is **TBD**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| 0.1.0 | 草稿 | TBD | TBD | TBD |

## 适用说明

本文档适用于 `Gp_NCA95xx` 项目中 `Gp_NCA95xx` I2C GPIO 扩展驱动的软件需求定义。本文档仅描述软件应满足的需求，不描述详细设计方案、代码实现方案或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| 0.1.0 | 2026-05-22 | FC Requirement Workbench | 基于 NCA9539-Q1 Datasheet Rev1.0 初始生成 Planned SRS 草稿 | 草稿 |

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

本文档定义 `Gp_NCA95xx` 模块的软件需求，明确模块在 `Gp_NCA95xx` 项目中的功能边界、对外接口、状态行为、配置约束、诊断状态、时序要求、非功能约束和验证要求。

本文档作为 `Gp_NCA95xx` 模块软件架构设计、详细设计、编码实现、单元测试、集成测试和系统测试的上游输入。所有正式需求均应具备需求 ID、来源、约束、验收准则和验证方式。

---

## 2 适用范围

本文档适用于 `Gp_NCA95xx` 项目中 `Gp_NCA95xx` 模块的软件开发、评审、集成、测试和交付活动。

### 2.1 适用对象

- 软件需求工程师
- 软件架构和详细设计工程师
- 软件开发工程师
- 软件测试工程师
- 功能安全工程师
- 项目质量和配置管理人员

### 2.2 范围内

本文档覆盖：

- Gp_NCA95xx 驱动的初始化、MainFunction 周期处理和状态管理。
- 16-bit GPIO 输入采样与输出控制（Pin 级与 Port 级）。
- GPIO 方向配置（输入/输出）与极性反转配置。
- I2C 总线寄存器访问（器件地址、命令字节、读写序列）。
- 中断（INT）信号检测、清除与异常响应。
- 硬件复位（RESET）与上电复位（POR）后的重新初始化。
- I2C 通信故障检测与诊断。
- ASIL-C 安全等级下的配置完整性校验、实例间免于干扰和故障上报。
- 时序约束（I2C 速率、复位时序、中断响应时序）。
- 资源消耗的评估与记录。

### 2.3 范围外

本文档不覆盖：

- I2C 总线控制器的底层驱动实现（依赖 MCAL I2C 驱动）。
- 具体 GPIO 引脚的外围电路设计（上拉/下拉电阻选值、LED 驱动电流限额等硬件约束由硬件设计保证）。
- 中断控制器（ICU）的底层配置和 ISR 路由（依赖 MCAL ICU 驱动或 OS ISR 配置）。
- ACPI 电源管理策略、按键消抖算法、传感器融合算法等应用层逻辑。
- 芯片封装、焊接工艺、EMC/ESD 硬件防护、RoHS 合规。
- DEM/DET 完整故障存储与上报策略（仅定义本驱动的故障检测和上报接口）。

---

## 3 定义和缩写

### 3.1 定义

| 术语 | 定义 |
| --- | --- |
| GPIO 扩展 | 通过 I2C 总线扩展 MCU 的通用输入输出引脚数量。 |
| Port | 8-bit 一组 GPIO 引脚的逻辑分组，NCA9539-Q1 包含 Port 0（P00-P07）和 Port 1（P10-P17）。 |
| Pin | 单个 GPIO 引脚，可独立配置方向和极性。 |
| 输入采样 | 通过 I2C 读取 Input Port Register 获取引脚逻辑电平。 |
| 输出控制 | 通过 I2C 写入 Output Port Register 控制引脚输出电平。 |
| 极性反转 | 通过 Polarity Inversion Register 将输入采样结果取反后上报。 |
| 中断 | INT 引脚被芯片拉低，表示至少一个输入引脚状态发生变化。 |
| 上电复位（POR） | VDD 上电后内部自动复位，寄存器恢复默认值。 |

### 3.2 缩写

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| GPIO | General Purpose Input/Output | 通用输入输出 |
| I2C | Inter-Integrated Circuit | 集成电路间总线 |
| SCL | Serial Clock Line | 串行时钟线 |
| SDA | Serial Data Line | 串行数据线 |
| INT | Interrupt | 中断输出 |
| POR | Power-On Reset | 上电复位 |
| ASIL | Automotive Safety Integrity Level | 汽车安全完整性等级 |
| MCAL | Microcontroller Abstraction Layer | 微控制器抽象层 |
| DIO | Digital Input/Output | 数字输入输出 |
| ICU | Input Capture Unit | 输入捕获单元 |
| DEM | Diagnostic Event Manager | 诊断事件管理器 |
| DET | Development Error Tracer | 开发错误追踪 |
| ACK | Acknowledge | 应答 |
| NACK | Not Acknowledge | 不应答 |
| MSB | Most Significant Bit | 最高有效位 |
| LSB | Least Significant Bit | 最低有效位 |

---

## 4 概述

### 4.1 外设芯片介绍

NCA9539-Q1 是一款通过 AEC-Q100 Grade 1 认证的 16-bit I2C GPIO 扩展芯片，工作电压 1.65 V 至 3.6 V，支持最高 400 kHz Fast-mode I2C 总线。

芯片具备以下与软件需求相关的能力：

- 16 个 GPIO 引脚（P00-P07 组成 Port 0，P10-P17 组成 Port 1），每个引脚可独立配置为输入或输出。
- 通过 I2C 总线访问 8 个内部寄存器：Input Port 0/1、Output Port 0/1、Polarity Inversion 0/1、Configuration 0/1。
- 上电后所有引脚默认为输入模式，Output Port Register 默认值为 0xFF，Polarity Inversion Register 默认值为 0x00，Configuration Register 默认值为 0xFF。
- 开漏低有效中断输出（INT），任一路输入引脚状态变化时触发，读取对应 Port 寄存器后自动清除。
- 硬件低有效复位输入（RESET），复位后所有寄存器恢复默认值。
- 内部上电复位（POR），VDD 达到 V_POR 后自动释放复位。
- 两个硬件地址引脚（A0, A1），支持最多 4 片器件共用同一 I2C 总线。

**边界约束**：

- 芯片本身不支持内部上拉/下拉电阻；输入引脚的外部偏置由硬件电路保证。
- 芯片的 I2C 地址由硬件引脚 A0/A1 的物理连接决定，软件不可运行时动态修改。
- I/O 引脚对 VDD 和 VSS 均通过 ESD 保护二极管连接；施加高于 VDD 的电压可能导致通过保护二极管向 VDD 注入电流。

**待定项**：

- 项目实际使用的 GPIO 引脚数量和功能分配待硬件设计确认。
- 每核管理的芯片实例数量待项目配置确认。
- I2C 总线与 MCU 的物理连接（I2C 模块编号、引脚映射）待硬件原理图确认。
- INT 引脚连接的 MCU GPIO/ICU 通道待硬件原理图确认。
- RESET 引脚是否由本驱动控制或由其他模块（如 SBC/PMIC）管理待架构确认。

### 4.2 驱动功能介绍

`Gp_NCA95xx` 驱动应实现以下软件功能：

- 初始化当前核所有已配置的 NCA9539-Q1 芯片实例，包括 I2C 地址验证、寄存器初始配置和初始状态建立。
- 提供周期 MainFunction，负责输入端口轮询采样、中断状态检测和 pending 输出指令执行。
- 提供 Pin 级和 Port 级 GPIO 输入读取接口，返回经极性反转处理后的逻辑电平。
- 提供 Pin 级和 Port 级 GPIO 输出写入接口，通过 I2C 总线将输出值写入芯片 Output Port Register。
- 提供 GPIO 方向配置和极性反转配置的运行时管理（若项目允许运行时变更）。
- 检测和上报 I2C 通信故障（NACK、超时）、寄存器配置不一致、未初始化访问等异常。
- 在 ASIL-C 安全等级下，提供配置完整性校验、输出回读验证和实例间免于干扰保证。

**边界约束**：

- 本驱动不实现 I2C 总线控制器的底层时序和电气驱动；I2C 读写操作依赖 MCAL I2C 驱动提供的接口。
- 本驱动不实现中断服务例程（ISR）；INT 引脚信号由 MCAL DIO/ICU 或 OS ISR 捕获后，通过回调或事件触发本驱动的中断处理。
- 本驱动的 MainFunction 周期由上层调度（如 BswM 或 OS Task）保证；驱动仅规定最大允许周期。

**待定项**：

- 是否支持运行时方向变更或极性变更，待项目策略确认。
- 是否支持 Pin 级独立 API（如 `ReadPin`、`WritePin`），还是仅提供 Port 级 API，待架构确认。
- 中断处理方式（轮询 INT 引脚状态 vs ICU 中断触发 MainFunction 唤醒），待架构和硬件确认。

### 4.3 外设引脚介绍

| 引脚 | 芯片侧方向 | Pin 口功能 |
| --- | --- | --- |
| P00-P07 | 可配置 I/O | Port 0 GPIO 引脚；上电默认为输入；方向由 Configuration Port 0 Register 控制 |
| P10-P17 | 可配置 I/O | Port 1 GPIO 引脚；上电默认为输入；方向由 Configuration Port 1 Register 控制 |
| SCL | 输入 | I2C 串行时钟线；需外部上拉至 VDD |
| SDA | 双向开漏 | I2C 串行数据线；需外部上拉至 VDD |
| INT | 输出（开漏低有效） | 中断输出；输入状态变化时拉低；需外部上拉至 VDD |
| RESET | 输入（低有效） | 硬件复位输入；需外部上拉至 VDD（若不使用） |
| A0 | 输入 | I2C 地址选择位 0；接 VDD 或 VSS 确定器件地址 |
| A1 | 输入 | I2C 地址选择位 1；接 VDD 或 VSS 确定器件地址 |
| VDD | 供电 | 电源正极，1.65 V 至 3.6 V |
| VSS | 供电 | 电源地 |

### 4.4 状态机介绍

NCA9539-Q1 芯片本身无复杂工作模式状态机（不区分 Normal/Standby/Sleep 等工作模式），其行为主要由寄存器配置决定。驱动的软件状态机定义如下：

| 状态 | 说明 | 进入条件 | 退出条件 |
| --- | --- | --- | --- |
| UNINIT | 驱动未初始化；所有实例不可用 | 系统启动或驱动模块复位后 | Init 调用成功完成 |
| INIT | 驱动初始化中；正在配置芯片寄存器 | Init 调用开始执行 | 所有已配置实例初始化完成或任一实例初始化失败 |
| NORMAL | 驱动正常运行；可响应读写请求和中断 | 所有实例初始化成功 | 发生不可恢复故障或收到复位请求 |
| FAULT | 驱动检测到故障；部分或全部实例不可用 | I2C 通信故障、配置校验失败等 | 故障清除并重新初始化完成 |

```
UNINIT ──Init()──> INIT ──所有实例OK──> NORMAL
  ^                 │                      │
  │                 │ 任一实例失败          │ 故障检测
  │                 v                      v
  └────────────── FAULT <──────────────────┘
                     │
                     │ 重新 Init()
                     v
                   INIT
```

### 4.5 通信参数

I2C 总线支持以下速率模式：

- Standard-mode：0 kHz 至 100 kHz
- Fast-mode：0 kHz 至 400 kHz

**器件寻址**：

NCA9539-Q1 的 7-bit I2C 器件地址由固定部分（`11101`）和硬件可编程部分（A1, A0）组成：

| A1 | A0 | 7-bit 地址（Hex） | 8-bit 写地址 | 8-bit 读地址 |
| --- | --- | --- | --- | --- |
| L | L | 0x74 | 0xE8 | 0xE9 |
| L | H | 0x75 | 0xEA | 0xEB |
| H | L | 0x76 | 0xEC | 0xED |
| H | H | 0x77 | 0xEE | 0xEF |

器件内部寄存器通过命令字节（Command Byte）寻址。命令字节在器件地址确认后由 Master 发送，高 5 位固定为 `00000`，低 3 位（B2, B1, B0）选择目标寄存器。

| B2 | B1 | B0 | 命令字节 | 寄存器 | 访问类型 | 上电默认值 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0x00 | Input Port 0 | 只读 | 0xFF |
| 0 | 0 | 1 | 0x01 | Input Port 1 | 只读 | 0xFF |
| 0 | 1 | 0 | 0x02 | Output Port 0 | 读/写 | 0xFF |
| 0 | 1 | 1 | 0x03 | Output Port 1 | 读/写 | 0xFF |
| 1 | 0 | 0 | 0x04 | Polarity Inversion Port 0 | 读/写 | 0x00 |
| 1 | 0 | 1 | 0x05 | Polarity Inversion Port 1 | 读/写 | 0x00 |
| 1 | 1 | 0 | 0x06 | Configuration Port 0 | 读/写 | 0xFF |
| 1 | 1 | 1 | 0x07 | Configuration Port 1 | 读/写 | 0xFF |

I2C 时序参数（Fast-mode）：

| 参数 | 符号 | 条件 | 最小值 | 最大值 | 单位 |
| --- | --- | --- | --- | --- | --- |
| SCL 时钟频率 | f_SCL | Fast-mode | 0 | 400 | kHz |
| 总线空闲时间 | t_BUF | Fast-mode | 1.3 | - | us |
| 重复 START 保持时间 | t_HD;STA | Fast-mode | 0.6 | - | us |
| SCL 低电平周期 | t_LOW | Fast-mode | 1.3 | - | us |
| SCL 高电平周期 | t_HIGH | Fast-mode | 0.6 | - | us |
| 数据建立时间 | t_SU;DAT | Fast-mode | 100 | - | ns |
| 数据保持时间 | t_HD;DAT | Fast-mode | 0 | - | ns |
| 数据有效时间 | t_VD;DAT | Fast-mode | - | 50 | ns |
| 数据有效应答时间 | t_VD;ACK | Fast-mode | 0.1 | 0.9 | us |
| SDA/SCL 上升时间 | t_r | Fast-mode | 20+0.1Cb | 300 | ns |
| SDA/SCL 下降时间 | t_f | Fast-mode | 20+0.1Cb | 300 | ns |
| 复位脉冲宽度 | t_w(rst) | - | 6 | - | ns |
| 复位恢复时间 | t_rec(rst) | - | 200 | - | ns |
| 复位时间 | t_rst | - | 400 | - | ns |
| INT 有效时间 | t_v(INT_N) | - | - | 4 | us |
| INT 复位时间 | t_rst(INT_N) | - | - | 4 | us |

注：Cb 为 I2C 总线单线总电容（单位 pF）。I2C 时序由 MCAL I2C 驱动保证；本驱动不直接控制 SCL/SDA 时序。

---

## 5 功能需求

本章描述模块必须实现的功能行为，包括模式与状态、接口、配置、诊断和错误处理。

### 5.1 模式需求

#### SRS-Gp_NCA95xx-FUNC-0001 驱动状态机管理

`功能需求` `ASIL-C` `Test / UT/IT` `Draft` `来源: Datasheet-6.3 Device Functional Modes; Datasheet-6.4 Programming; 项目-ASIL Safety Level`

Gp_NCA95xx 模块应在每个核上维护独立的驱动状态机，支持 UNINIT、INIT、NORMAL、FAULT 四种状态之间的受控转换。

**功能约束**

- **范围边界**：仅覆盖驱动软件状态；芯片内部上电复位和硬件复位由硬件保证，驱动负责复位后的重新初始化。
- **前置条件**：驱动模块已加载；配置数据可用；依赖的 MCAL I2C 驱动已初始化。
- **触发条件**：Init 调用触发 UNINIT→INIT；初始化完成触发 INIT→NORMAL；故障检测触发 NORMAL→FAULT；重新初始化触发 FAULT→INIT。
- **输入**：初始化请求、配置数据、I2C 读写结果、故障检测结果。
- **输出**：当前驱动状态；各芯片实例的可用性标记。
- **异常处理**：任一芯片实例初始化失败时，应记录该实例为不可用并报告故障，但不阻止其他实例正常工作（若架构允许部分实例运行）。
- **验收准则**：状态转换路径符合状态图定义；不存在未定义的转换路径；多核场景下各核状态独立。

---

#### SRS-Gp_NCA95xx-FUNC-0002 MainFunction 周期处理

`功能需求` `ASIL-C` `Test / UT/IT` `Draft` `来源: aurix2g-normative-patterns-1.2 MainFunction Interface Rules; Datasheet-6.5 Register Maps; Datasheet-6.2.3 Interrupt Output`

Gp_NCA95xx 模块应在 MainFunction 中周期执行输入端口采样、中断状态检测和 pending 输出指令下发。

**功能约束**

- **范围边界**：MainFunction 的执行周期由上层调度保证；驱动仅规定最大允许周期。中断检测的具体方式（轮询 INT 引脚或响应 ICU 事件）取决于项目配置。
- **前置条件**：驱动处于 NORMAL 状态；至少一个芯片实例已配置并初始化成功。
- **触发条件**：上层调度周期调用 MainFunction。
- **输入**：中断标志（来自 ISR/回调或 INT 引脚轮询结果）、pending 输出指令队列、输入采样周期计数器。
- **输出**：采样到的输入端口值更新至内部缓存；pending 输出指令通过 I2C 写入芯片；中断事件上报。
- **异常处理**：I2C 通信失败时，应记录故障并保持上一次有效输入/输出值不变；连续通信失败次数超过阈值时应将对应实例标记为 FAULT。
- **验收准则**：MainFunction 执行周期不超过项目规定的最大值；输入采样值在芯片输入变化后的 t_v(INT_N)（最大 4 us）加上 I2C 读取时间内更新至内部缓存。

---

### 5.2 接口需求

#### SRS-Gp_NCA95xx-INTF-0001 初始化接口

`接口需求` `ASIL-C` `Test / UT` `Draft` `来源: aurix2g-normative-patterns-1.1 Interface Classification; Datasheet-6.3 Device Functional Modes`

Gp_NCA95xx 模块应提供 `Gp_NCA95xx_Init(void)` 接口，完成当前核所有已配置芯片实例的初始化。

**接口约束**

- **范围边界**：Init 必须在对应 MCAL I2C 驱动 Init 之后调用。Init 仅初始化当前核的实例；多核场景下各核独立调用。
- **前置条件**：MCAL I2C 驱动已初始化；配置数据已加载且校验通过；当前核具备访问权限。
- **触发条件**：系统启动流程或故障恢复流程中调用。
- **输入**：无显式参数；内部读取当前核的配置数据（GlobalCfg）。
- **输出**：无返回值；初始化结果反映在各实例的内部状态中。
- **接口契约**：对每个已配置芯片实例，依次执行：I2C 器件地址探测（可选）→ 写入 Configuration Register 设定方向 → 写入 Output Register 设定默认输出值 → 写入 Polarity Inversion Register 设定极性 → 读取 Input Register 建立初始采样值 → 标记实例为可用。
- **异常处理**：器件地址无应答时，标记该实例为不可用；寄存器写入后回读校验失败时，重试一次（可配置次数），仍失败则标记该实例为不可用并上报故障。
- **验收准则**：Init 返回后，所有硬件和配置正常的实例应处于 NORMAL 态可用状态；配置或硬件异常的实例应被标记为不可用。

---

#### SRS-Gp_NCA95xx-INTF-0002 MainFunction 接口

`接口需求` `ASIL-C` `Test / UT` `Draft` `来源: aurix2g-normative-patterns-1.2 MainFunction Interface Rules`

Gp_NCA95xx 模块应提供 `Gp_NCA95xx_MainFunction(void)` 接口，供上层调度周期调用以执行驱动周期任务。

**接口约束**

- **范围边界**：由于驱动存在异步输出操作（SetOutput 可能通过 pending 机制延迟下发）和 I2C 周期输入采样需求，必须提供 MainFunction 接口。
- **前置条件**：驱动处于 NORMAL 状态。
- **触发条件**：上层调度周期调用。
- **输入**：无显式参数。
- **输出**：无返回值；内部更新输入采样缓存、执行 pending 输出指令、处理中断事件。
- **接口契约**：MainFunction 应为 Non_Reentrancy；多核场景下各核独立调用各自的 MainFunction，访问各自的数据区。
- **异常处理**：MainFunction 内发生的 I2C 通信故障应通过内部故障记录机制上报，不通过返回值直接返回。
- **验收准则**：MainFunction 单次执行时间不超过项目规定的上限；多核并行调用不产生数据竞争。

---

#### SRS-Gp_NCA95xx-INTF-0003 GPIO 输入读取接口

`接口需求` `ASIL-C` `Test / UT` `Draft` `来源: Datasheet-6.5.3 Input Port Registers; Datasheet-6.2.1 I/O Port`

Gp_NCA95xx 模块应提供 GPIO 输入读取接口，支持通过 I2C 读取芯片 Input Port Register 并返回经极性反转处理后的引脚逻辑电平。

**接口约束**

- **范围边界**：接口可设计为 Port 级（`GetInputPort`）和/或 Pin 级（`GetInputPin`），具体粒度待架构确认。极性反转由驱动按 Polarity Inversion Register 配置自动处理。
- **前置条件**：驱动处于 NORMAL 状态；目标实例已初始化且可用；实例 ID 有效。
- **触发条件**：上层调用输入读取接口。
- **输入**：实例 ID（uint16 Id）；若为 Pin 级接口则还包括 Pin 编号或掩码。
- **输出**：经极性反转处理后的输入值（Port 级返回 8-bit，Pin 级返回 0/1）；接口返回状态（E_OK 或 E_NOT_OK）。
- **接口契约**：读取操作通过 I2C 读取 Input Port Register 实现；读取前无需发送命令字节（若上一条命令已指向 Input Port Register）或需发送命令字节（若上一条命令指向其他寄存器）。
- **异常处理**：实例 ID 无效、实例未初始化或不可用时，返回 E_NOT_OK 且输出指针内容不变。I2C 读取 NACK 时，返回 E_NOT_OK 并保持上一次有效输入值不变，同时上报 I2C 通信故障。
- **验收准则**：正常读取返回的输入值与芯片引脚实际逻辑电平一致（考虑极性反转）；异常情况不返回过期或虚假数据。

---

#### SRS-Gp_NCA95xx-INTF-0004 GPIO 输出写入接口

`接口需求` `ASIL-C` `Test / UT` `Draft` `来源: Datasheet-6.5.4 Output Port Registers; Datasheet-6.6.1 Writing to Port Registers`

Gp_NCA95xx 模块应提供 GPIO 输出写入接口，支持通过 I2C 将输出值写入芯片 Output Port Register。

**接口约束**

- **范围边界**：接口可设计为 Port 级（`SetOutputPort`）和/或 Pin 级（`SetOutputPin`）。仅当对应引脚已配置为输出时，写入值才会在引脚上生效。驱动应维护内部输出缓存，对于未配置为输出的位，写入值仅更新缓存而不下发到芯片。
- **前置条件**：驱动处于 NORMAL 状态；目标实例已初始化且可用；实例 ID 有效；目标引脚已配置为输出方向。
- **触发条件**：上层调用输出写入接口。
- **输入**：实例 ID（uint16 Id）；输出值（Port 级为 8-bit，Pin 级包含 Pin 编号和 0/1 值）。
- **输出**：接口返回状态（E_OK 或 E_NOT_OK）；芯片 Output Port Register 被更新。
- **接口契约**：输出操作可通过 I2C 立即写入对应 Output Port Register，或写入内部 pending 缓存后由 MainFunction 统一下发（取决于是否为异步设计）。
- **异常处理**：实例 ID 无效、实例未初始化或不可用时，返回 E_NOT_OK 且不执行任何 I2C 操作。I2C 写入 NACK 时，返回 E_NOT_OK，保持输出缓存不变，并上报 I2C 通信故障。若接口采用异步模式而 pending 队列已满，应返回 E_NOT_OK。
- **验收准则**：正常写入后芯片对应引脚输出电平与写入值一致；写入失败后芯片引脚状态不变。

---

#### SRS-Gp_NCA95xx-INTF-0005 中断状态获取接口

`接口需求` `ASIL-C` `Test / UT` `Draft` `来源: Datasheet-6.2.3 Interrupt Output; Datasheet-6.6.2 Reading Port Registers`

Gp_NCA95xx 模块应提供中断状态获取接口，支持上层查询中断触发原因和清除中断状态。

**接口约束**

- **范围边界**：中断状态获取接口返回自上次读取以来发生输入变化的 Port 和 Pin 信息。中断清除由读取 Input Port Register 的 I2C 操作自动完成（芯片行为），驱动负责封装该行为。
- **前置条件**：驱动处于 NORMAL 状态；目标实例已初始化且可用；INT 引脚已正确连接并配置。
- **触发条件**：上层主动查询或中断触发后调用。
- **输入**：实例 ID（uint16 Id）。
- **输出**：中断状态字（标明哪些引脚发生了输入变化）；接口返回状态（E_OK 或 E_NOT_OK）。
- **接口契约**：中断检测基于 Input Port Register 变化比对。驱动应在内部维护上一次读取的 Input Port Register 值，在 MainFunction 或中断处理中比对变化并记录中断事件。
- **异常处理**：实例 ID 无效、实例未初始化或不可用时，返回 E_NOT_OK。I2C 读取失败时，中断状态字保持上一次有效值，并上报通信故障。
- **验收准则**：中断发生后，接口能正确返回发生变化的 Port 和 Pin 信息；读取操作完成后中断状态被正确清除。

---

#### SRS-Gp_NCA95xx-INTF-0006 驱动复位接口

`接口需求` `ASIL-C` `Test / UT` `Draft` `来源: Datasheet-6.2.2 RESET Input; Datasheet-6.3.1 Power-On Reset`

Gp_NCA95xx 模块应提供复位接口，支持对指定芯片实例执行硬件复位和/或软件重新初始化。

**接口约束**

- **范围边界**：若 RESET 引脚由本驱动控制，复位操作应拉低 RESET 引脚至少 t_w(rst)（≥ 6 ns），然后拉高并等待 t_rst（≥ 400 ns）后重新执行初始化。若 RESET 引脚由其他模块管理，复位接口仅执行软件层面的重新初始化（恢复默认寄存器值）。
- **前置条件**：驱动已初始化；目标实例已配置。
- **触发条件**：上层请求复位或故障恢复流程触发。
- **输入**：实例 ID（uint16 Id）。
- **输出**：接口返回状态（E_OK 或 E_NOT_OK）；目标实例寄存器恢复默认值并重新初始化。
- **异常处理**：实例 ID 无效时，返回 E_NOT_OK。RESET 引脚控制失败（若适用）时，上报故障。
- **验收准则**：复位后目标实例寄存器值恢复为 Datasheet 规定的上电默认值；复位后实例可用于正常读写操作。

---

### 5.3 配置需求

#### SRS-Gp_NCA95xx-CFG-0001 I2C 器件地址配置

`配置需求` `ASIL-C` `Review / Test` `Draft` `来源: Datasheet-6.5.1 Device Address; Datasheet-6.5.2 Control Register and Command Byte`

Gp_NCA95xx 模块应在配置数据中为每个芯片实例维护其 I2C 器件地址。

**配置约束**

- **范围边界**：I2C 器件地址的 7-bit 值由硬件引脚 A0/A1 的物理连接决定，软件不可运行时修改。软件仅读取配置中的地址值用于 I2C 通信。
- **有效范围**：7-bit 地址为 0x74、0x75、0x76、0x77 之一；8-bit 写地址为 0xE8-0xEE（偶数），8-bit 读地址为 0xE9-0xEF（奇数）。
- **默认值**：无默认值；必须由项目配置明确指定。
- **配置依赖**：同一 I2C 总线上不可存在地址相同的两个 NCA9539-Q1 器件。
- **异常处理**：配置的器件地址不在有效范围内时，应在配置校验阶段拒绝并上报配置错误。I2C 通信时若器件地址无应答，应上报通信故障。
- **验收准则**：配置的地址值正确映射到 Datasheet 规定的地址表；地址冲突能被配置校验检测。

---

#### SRS-Gp_NCA95xx-CFG-0002 GPIO 方向配置

`配置需求` `ASIL-C` `Review / Test` `Draft` `来源: Datasheet-6.5.6 Configuration Registers; Datasheet-6.2.1 I/O Port`

Gp_NCA95xx 模块应在配置数据中为每个芯片实例的每个 Port 维护 GPIO 方向配置（输入/输出），并支持运行时方向变更（若项目允许）。

**配置约束**

- **范围边界**：方向配置对应 Configuration Register（0x06 为 Port 0, 0x07 为 Port 1）。Bit=1 表示输入，Bit=0 表示输出。上电默认所有引脚为输入。运行时方向变更策略待项目确认。
- **有效范围**：8-bit 位掩码（每 bit 对应一个 Pin）；Bit=1=输入，Bit=0=输出。
- **默认值**：0xFF（所有引脚为输入），与芯片上电默认一致。
- **配置依赖**：方向配置影响 Output Register 写入行为和引脚的电气特性。将输入引脚改为输出时，Output Register 对应位的值会立即驱动到引脚上。
- **异常处理**：配置值写入后应回读校验；回读不一致时重试一次，仍失败则报告配置故障。
- **验收准则**：配置写入后回读值与写入值一致；方向配置生效后引脚行为符合预期。

---

#### SRS-Gp_NCA95xx-CFG-0003 GPIO 极性反转配置

`配置需求` `ASIL-C` `Review / Test` `Draft` `来源: Datasheet-6.5.5 Polarity Inversion Registers`

Gp_NCA95xx 模块应在配置数据中为每个芯片实例的每个 Port 维护极性反转配置，并支持运行时变更（若项目允许）。

**配置约束**

- **范围边界**：极性反转配置对应 Polarity Inversion Register（0x04 为 Port 0, 0x05 为 Port 1）。Bit=1 表示对应引脚输入值取反，Bit=0 表示保留原值。上电默认所有位为 0（不反转）。
- **有效范围**：8-bit 位掩码（每 bit 对应一个 Pin）；Bit=1=反转，Bit=0=不反转。
- **默认值**：0x00（不反转），与芯片上电默认一致。
- **配置依赖**：极性反转仅影响输入读取结果，不影响输出行为。
- **异常处理**：配置值写入后应回读校验；回读不一致时重试一次，仍失败则报告配置故障。
- **验收准则**：极性反转配置生效后，输入读取接口返回的值在对应位与芯片实际电平相反。

---

#### SRS-Gp_NCA95xx-CFG-0004 默认输出值配置

`配置需求` `ASIL-C` `Review / Test` `Draft` `来源: Datasheet-6.5.4 Output Port Registers`

Gp_NCA95xx 模块应在配置数据中为每个芯片实例维护上电初始化后的默认输出值。

**配置约束**

- **范围边界**：默认输出值在 Init 阶段写入 Output Port Register。上电时芯片 Output Port Register 默认为 0xFF。
- **有效范围**：8-bit 位掩码（Port 0 和 Port 1 各自独立）。
- **默认值**：0xFF，与芯片上电默认一致。
- **配置依赖**：仅配置为输出方向的引脚，其默认输出值才在引脚上生效。
- **异常处理**：默认输出值写入后应回读校验；写入失败时报告配置故障。
- **验收准则**：Init 完成后，输出引脚的电平与配置的默认输出值一致。

---

#### SRS-Gp_NCA95xx-CFG-0005 多实例与多核配置

`配置需求` `ASIL-C` `Review / Test` `Draft` `来源: aurix2g-normative-patterns-3 Configuration Requirements; Datasheet-6.5.1 Device Address`

Gp_NCA95xx 模块应在配置数据中维护实例数量、每核管理的芯片索引和信号映射关系。

**配置约束**

- **范围边界**：最多支持 4 片 NCA9539-Q1 共用同一 I2C 总线（由 A0/A1 地址限制）。多核场景下，每核有独立的配置数据区。信号 ID（uint16 Id）通过 SigMappingCfg 映射到（CoreId, ChipIdx, PinMask）。
- **有效范围**：实例数量 1..4；CoreId 0..5；ChipIdx 0..3。
- **默认值**：无默认值；必须由项目配置明确指定。
- **配置依赖**：实例数量受硬件 A0/A1 地址限制和 I2C 总线负载限制。
- **异常处理**：配置的实例数量为 0 或超过硬件上限时，应在配置校验阶段拒绝。同一 I2C 总线上出现地址冲突时，应在配置校验阶段报告错误。芯片索引越界时，Init 阶段拒绝初始化。
- **验收准则**：配置校验能检测实例数量/地址冲突/ChipIdx 越界等异常；多核场景下各核配置数据相互独立。

---

### 5.4 诊断需求

#### SRS-Gp_NCA95xx-DIAG-0001 I2C 通信故障检测

`诊断需求` `ASIL-C` `Test / UT/IT` `Draft` `来源: Datasheet-6.4.5 Acknowledge; 项目-ASIL Safety Level`

Gp_NCA95xx 模块应在每次 I2C 读写操作中检测通信故障（NACK、超时、总线仲裁丢失），并向上层上报。

**诊断约束**

- **范围边界**：I2C 通信故障的具体检测机制（NACK、超时、仲裁丢失）由 MCAL I2C 驱动提供；本驱动负责解释故障状态、记录故障计数和上报。
- **适用状态**：NORMAL、INIT。
- **故障触发**：MCAL I2C 驱动返回非 E_OK 状态；或连续 NACK 次数超过阈值；或 I2C 操作超时。
- **故障处理**：记录故障类型和故障计数；返回 E_NOT_OK 给调用者；通过 GetFault 接口（待定义）向上层提供故障状态字。
- **故障清除**：通信恢复正常后，连续成功通信次数达到恢复阈值时清除通信故障标记。
- **验收准则**：模拟 I2C NACK 和超时场景时驱动能正确检测并上报故障；故障恢复后状态正确清除。

---

#### SRS-Gp_NCA95xx-DIAG-0002 寄存器回读校验

`诊断需求` `ASIL-C` `Test / UT` `Draft` `来源: Datasheet-6.5 Register Maps; 项目-ASIL Safety Level`

Gp_NCA95xx 模块应在写入 Configuration Register、Polarity Inversion Register 和 Output Register 后执行回读校验，确保写入值与芯片寄存器实际值一致。

**诊断约束**

- **范围边界**：回读校验适用于所有写操作涉及的寄存器。Input Register 为只读，不执行回读校验。回读校验仅验证写入值与回读值一致，不验证引脚实际电平（引脚电平验证属于硬件测试范围）。
- **适用状态**：NORMAL、INIT（初始化过程中的寄存器写入也需校验）。
- **故障触发**：写入值 I2C Write 成功后，I2C Read 读取到的寄存器值与写入值不一致。
- **故障处理**：立即重试一次（写入+回读）；重试仍不一致时，标记对应实例为 FAULT，记录寄存器地址、期望值和实际值，上报故障。
- **故障清除**：重新初始化该实例并通过回读校验。
- **验收准则**：寄存器写入后回读值与写入值一致；模拟回读不一致场景时驱动正确检测并上报故障。

---

#### SRS-Gp_NCA95xx-DIAG-0003 未初始化访问检测

`诊断需求` `ASIL-C` `Test / UT` `Draft` `来源: aurix2g-normative-patterns-6 Diagnostic Requirements`

Gp_NCA95xx 模块应在所有功能接口中检测驱动初始化状态，拒绝未初始化或故障状态下的接口调用。

**诊断约束**

- **范围边界**：适用于除 Init 之外的所有接口。检测内容包括：驱动整体是否已初始化、目标实例是否已初始化且可用。
- **适用状态**：UNINIT、INIT、FAULT 状态下拒绝功能调用。
- **故障触发**：在驱动状态不为 NORMAL 或目标实例不可用时调用功能接口。
- **故障处理**：返回 E_NOT_OK；通过 DET（若启用）上报开发错误。
- **验收准则**：UNINIT 状态下调用任何功能接口（除 Init）均返回 E_NOT_OK；FAULT 状态下同。

---

#### SRS-Gp_NCA95xx-DIAG-0004 中断异常监控

`诊断需求` `ASIL-C` `Test / UT` `Draft` `来源: Datasheet-6.2.3 Interrupt Output; 项目-ASIL Safety Level`

Gp_NCA95xx 模块应监控中断信号的合理性，检测中断持续拉低（stuck low）等异常。

**诊断约束**

- **范围边界**：中断异常监控应在 MainFunction 中执行。中断持续拉低超过可配置的最大允许时间（如 100 ms）时，视为中断异常。
- **适用状态**：NORMAL。
- **故障触发**：INT 引脚持续低电平超过最大允许时间；或连续多次读取 Input Register 未能清除 INT 低电平。
- **故障处理**：标记对应实例中断通路异常；上报故障；继续按周期读取 Input Register 以获取输入状态。
- **验收准则**：模拟 INT 持续拉低场景时驱动能正确检测并上报；正常中断触发/清除场景下不产生误报。

---

## 6 非功能需求

### 6.1 时序需求

#### SRS-Gp_NCA95xx-TIM-0001 I2C 总线时序合规

`时序需求` `ASIL-C` `Analysis / Test` `Ready` `来源: Datasheet-5.2 Dynamic Characteristics; Datasheet-6.4.1 I2C Interface`

Gp_NCA95xx 模块所依赖的 I2C 总线通信应符合 NCA9539-Q1 Datasheet 规定的 Fast-mode（最高 400 kHz）时序参数。

**时序约束**

- **范围边界**：I2C 时序由 MCAL I2C 驱动保证，本驱动不直接控制 SCL/SDA 时序。本需求的验证方式为 Analysis（审查 MCAL I2C 配置与 Datasheet 时序参数的符合性）。
- **关键参数**：SCL 频率 ≤ 400 kHz；t_LOW ≥ 1.3 us；t_HIGH ≥ 0.6 us；t_SU;DAT ≥ 100 ns；t_BUF ≥ 1.3 us。
- **验收准则**：MCAL I2C 驱动配置的时序参数均在 Datasheet 规定范围内；集成测试中 I2C 通信误码率为 0。

---

#### SRS-Gp_NCA95xx-TIM-0002 复位时序合规

`时序需求` `ASIL-C` `Analysis / Test` `Draft` `来源: Datasheet-5.2 Dynamic Characteristics; Datasheet-6.2.2 RESET Input`

Gp_NCA95xx 模块在执行硬件复位时应满足 Datasheet 规定的 RESET 时序要求。

**时序约束**

- **范围边界**：若 RESET 引脚由本驱动控制，本需求适用。若 RESET 由其他模块管理，改为约束约束或标记为 NotApplicable。
- **关键参数**：复位脉冲宽度 t_w(rst) ≥ 6 ns；复位恢复时间 t_rec(rst) ≥ 200 ns；复位时间 t_rst ≥ 400 ns。
- **验收准则**：硬件复位后芯片寄存器恢复为 Datasheet 规定的上电默认值；复位后芯片在 t_rst 时间内完成初始化并响应 I2C 通信。

---

#### SRS-Gp_NCA95xx-TIM-0003 MainFunction 最大周期约束

`时序需求` `ASIL-C` `Analysis / Review` `Draft` `来源: aurix2g-normative-patterns-7 Timing Requirements; 项目-架构`

Gp_NCA95xx 模块的 MainFunction 调用周期应由项目架构根据 GPIO 输入采样实时性要求和输出响应延迟要求定义，并在配置中固化。

**时序约束**

- **范围边界**：MainFunction 的周期取决于项目对 GPIO 输入变化的响应时间要求和输出延迟容忍度。典型值建议 ≤ 5 ms（类比 CAN 收发器 MainFunction 周期）。
- **验收准则**：MainFunction 被上层调度以不超过配置值的固定周期调用；MainFunction 单次执行的最坏情况执行时间（WCET）不超过配置周期的 50%。

---

### 6.2 安全等级需求

#### SRS-Gp_NCA95xx-SAFE-0001 ASIL-C 安全完整性

`安全需求` `ASIL-C` `Review / Analysis` `Draft` `来源: 项目-ASIL Safety Level`

Gp_NCA95xx 模块的开发、验证和集成应满足 ISO 26262 ASIL-C 等级要求。

**安全约束**

- **范围边界**：本需求定义驱动模块的整体安全等级。各子需求的 ASIL 等级可在此基础上根据安全分析结果进行分解和降级。
- **要求**：驱动应实现配置完整性校验、I2C 通信故障检测、寄存器回读验证；应检测并上报故障；应支持多实例间的免于干扰。
- **安全目标**：GPIO 输出控制的非预期翻转（unintended toggle）不得导致违背整车安全目标。
- **验收准则**：安全分析（FMEA/FTA）确认驱动故障模式均有检测和响应机制；安全用例测试覆盖所有已识别的故障模式。

---

#### SRS-Gp_NCA95xx-SAFE-0002 配置完整性校验

`安全需求` `ASIL-C` `Review / Analysis` `Draft` `来源: 项目-ASIL Safety Level; aurix2g-normative-patterns-4 Safety Requirements`

Gp_NCA95xx 模块应在 Init 阶段对配置数据的完整性进行校验。

**安全约束**

- **范围边界**：配置完整性校验包括：配置数据结构版本检查、CRC 校验、实例数量与硬件地址的合法性检查、配置数据指针非空检查。
- **验收准则**：配置数据被篡改或损坏时，Init 阶段应检测到并拒绝初始化，上报配置故障；正常配置数据通过校验。

---

#### SRS-Gp_NCA95xx-SAFE-0003 实例间免于干扰

`安全需求` `ASIL-C` `Review / Analysis` `Draft` `来源: 项目-ASIL Safety Level; aurix2g-normative-patterns-4 Safety Requirements`

Gp_NCA95xx 模块应保证同一核上管理的多个 NCA9539-Q1 芯片实例之间不存在互相干扰。

**安全约束**

- **范围边界**：免于干扰要求包括：一个实例的 I2C 通信故障不影响其他实例的正常读写；一个实例的寄存器写入不会误写到另一个实例（由器件地址区分，硬件保证）；驱动内部数据结构的实例数据区相互隔离。
- **验收准则**：故障注入测试验证单实例故障不影响其他实例的功能和性能；代码审查确认实例数据区无交叉访问。

---

### 6.3 编码规范需求

#### SRS-Gp_NCA95xx-CODE-0001 编码标准合规

`编码需求` `ASIL-C` `Inspection / Analysis` `Draft` `来源: 项目-编码规范; aurix2g-normative-patterns-9 Naming and Coding Standards`

Gp_NCA95xx 模块的代码应符合项目编码规范和命名约定。

**编码约束**

- **范围边界**：文件命名遵循 `Gp_NCA95xx.h`、`Gp_NCA95xx_Types.h`、`Gp_NCA95xx_Cfg.h`、`Gp_NCA95xx_CfgData.h`、`Gp_NCA95xx_MemMap.h`、`Gp_NCA95xx.c` 等约定。函数命名遵循 `Gp_NCA95xx_` 前缀。
- **MISRA 合规**：代码应符合 MISRA C:2012 要求；偏差须记录和审批。
- **验收准则**：静态分析工具报告无未豁免的 MISRA 违规；代码走查确认命名符合约定。

---

### 6.4 资源消耗需求

#### SRS-Gp_NCA95xx-RES-0001 资源消耗评估与记录

`资源需求` `ASIL-C` `Analysis` `Draft` `来源: 项目-资源预算; construction-rules-6 Resource Requirements`

Gp_NCA95xx 模块应在构建后评估并记录 ROM、RAM、栈使用量和 CPU 负载，供项目资源预算审查。

**资源约束**

- **资源类型**：ROM（代码段 + 常量段）、RAM（每核全局变量 + 每实例数据）、栈（最坏情况调用深度）、CPU 负载（MainFunction WCET × 调用频率）。
- **约束**：ROM/RAM/栈的实际消耗不得超过项目分配的预算。若项目预算未定，本需求仅要求评估和记录实际消耗值，不设定具体阈值。
- **验收准则**：从链接映射文件（map file）提取 ROM/RAM 实际消耗数据；从 WCET 分析或实测获取 CPU 负载数据；数据记录在资源消耗报告中。

---

### 6.5 可追溯性需求

#### SRS-Gp_NCA95xx-COMP-0001 需求追溯完整性

`可追溯性需求` `ASIL-C` `Review` `Draft` `来源: 项目-ASPICE; rule-engine-Trace Rules`

Gp_NCA95xx 模块的每条需求应具备上游来源和下游验证意图的可追溯链路。

**追溯约束**

- **范围边界**：上游追溯到 Datasheet 章节或项目需求条目；下游追溯到验证用例或验证方法。追溯链路在需求管理工具或追溯矩阵中维护。
- **验收准则**：所有 Ready 需求均有至少一条上游来源记录和至少一条验证意图记录；追溯矩阵无悬挂链接。

---

## 7 需求来源

| 来源类别 | 来源名称 | 与本文档关系 | 状态 |
| --- | --- | --- | --- |
| Datasheet | NCA9539-Q1 Datasheet Rev1.0 EN | 芯片能力和约束的主要来源 | 已引用 |
| 项目需求 | ASIL-C 安全等级要求 | 安全需求等级来源 | 已应用 |
| 项目需求 | 驱动命名 Gp_NCA95xx | 模块命名来源 | 已应用 |
| 平台规范 | AURIX 2G 平台驱动接口规范（aurix2g-normative-patterns.md） | 接口模式、配置规范、安全规范参考 | 已引用 |
| 待补充 | 项目 GPIO 引脚分配表 | 配置需求的具体引脚号和方向配置 | 缺失（Open Issue） |
| 待补充 | 硬件原理图（I2C 总线连接、INT/RESET 引脚连接） | Pin 所有权和中断处理方式确认 | 缺失（Open Issue） |
| 待补充 | 项目 I2C 总线速率和时序配置 | 时序需求的具体参数 | 缺失（Open Issue） |
| 待补充 | 项目 ROM/RAM/栈预算 | 资源需求的具体阈值 | 缺失（Open Issue） |

---

## 附录A 需求清单

| 需求ID | 类别 | 需求名称 | 验证方式 | 验证阶段 | 状态 |
| --- | --- | --- | --- | --- | --- |
| SRS-Gp_NCA95xx-FUNC-0001 | 功能需求 | 驱动状态机管理 | Test | UT/IT | Draft |
| SRS-Gp_NCA95xx-FUNC-0002 | 功能需求 | MainFunction 周期处理 | Test | UT/IT | Draft |
| SRS-Gp_NCA95xx-INTF-0001 | 接口需求 | 初始化接口 | Test | UT | Draft |
| SRS-Gp_NCA95xx-INTF-0002 | 接口需求 | MainFunction 接口 | Test | UT | Draft |
| SRS-Gp_NCA95xx-INTF-0003 | 接口需求 | GPIO 输入读取接口 | Test | UT | Draft |
| SRS-Gp_NCA95xx-INTF-0004 | 接口需求 | GPIO 输出写入接口 | Test | UT | Draft |
| SRS-Gp_NCA95xx-INTF-0005 | 接口需求 | 中断状态获取接口 | Test | UT | Draft |
| SRS-Gp_NCA95xx-INTF-0006 | 接口需求 | 驱动复位接口 | Test | UT | Draft |
| SRS-Gp_NCA95xx-CFG-0001 | 配置需求 | I2C 器件地址配置 | Review / Test | Review/UT | Draft |
| SRS-Gp_NCA95xx-CFG-0002 | 配置需求 | GPIO 方向配置 | Review / Test | Review/UT | Draft |
| SRS-Gp_NCA95xx-CFG-0003 | 配置需求 | GPIO 极性反转配置 | Review / Test | Review/UT | Draft |
| SRS-Gp_NCA95xx-CFG-0004 | 配置需求 | 默认输出值配置 | Review / Test | Review/UT | Draft |
| SRS-Gp_NCA95xx-CFG-0005 | 配置需求 | 多实例与多核配置 | Review / Test | Review/UT | Draft |
| SRS-Gp_NCA95xx-DIAG-0001 | 诊断需求 | I2C 通信故障检测 | Test | UT/IT | Draft |
| SRS-Gp_NCA95xx-DIAG-0002 | 诊断需求 | 寄存器回读校验 | Test | UT | Draft |
| SRS-Gp_NCA95xx-DIAG-0003 | 诊断需求 | 未初始化访问检测 | Test | UT | Draft |
| SRS-Gp_NCA95xx-DIAG-0004 | 诊断需求 | 中断异常监控 | Test | UT | Draft |
| SRS-Gp_NCA95xx-TIM-0001 | 时序需求 | I2C 总线时序合规 | Analysis / Test | Analysis/IT | Ready |
| SRS-Gp_NCA95xx-TIM-0002 | 时序需求 | 复位时序合规 | Analysis / Test | Analysis/UT | Draft |
| SRS-Gp_NCA95xx-TIM-0003 | 时序需求 | MainFunction 最大周期约束 | Analysis / Review | Analysis/Review | Draft |
| SRS-Gp_NCA95xx-SAFE-0001 | 安全需求 | ASIL-C 安全完整性 | Review / Analysis | Review/Analysis | Draft |
| SRS-Gp_NCA95xx-SAFE-0002 | 安全需求 | 配置完整性校验 | Review / Analysis | Review/Analysis | Draft |
| SRS-Gp_NCA95xx-SAFE-0003 | 安全需求 | 实例间免于干扰 | Review / Analysis | Review/Analysis | Draft |
| SRS-Gp_NCA95xx-CODE-0001 | 编码需求 | 编码标准合规 | Inspection / Analysis | Inspection/Analysis | Draft |
| SRS-Gp_NCA95xx-RES-0001 | 资源需求 | 资源消耗评估与记录 | Analysis | Analysis | Draft |
| SRS-Gp_NCA95xx-COMP-0001 | 可追溯性需求 | 需求追溯完整性 | Review | Review | Draft |

---

## 附录B 支持和相关性文件

| 序号 | 文件名称 | 文件编号/版本 | 来源 | 与本文档关系 |
| --- | --- | --- | --- | --- |
| 1 | NCA9539-Q1 Datasheet | Rev1.0 EN / 2023-01-05 | Novosense | 芯片能力和约束的原始来源 |
| 2 | AURIX 2G 平台规范经验库 | aurix2g-normative-patterns.md | FC Platform | 驱动接口模式、配置规范、安全规范参考 |
| 3 | SRS 输出模板 | srs-output-template.md | FC Requirement Workbench | SRS 文档结构参考 |
| 4 | SRS 编写标准 | authoring-standard.md | FC Requirement Workbench | 需求编写质量规范 |
| 5 | 需求构建规则 | construction-rules.md | FC Requirement Workbench | 需求字段完整性和状态判定 |
| 6 | 需求校准规则 | calibration-rules.md | FC Requirement Workbench | 写法偏好和颗粒度校准 |
| 7 | 项目 GPIO 引脚分配表 | TBD | 项目硬件设计 | GPIO 引脚号和功能分配（待补充） |
| 8 | 项目硬件原理图 | TBD | 项目硬件设计 | I2C/INT/RESET 引脚连接确认（待补充） |

---

## **重要声明**

本文档基于 NCA9539-Q1 Datasheet Rev1.0 EN 和 AURIX 2G 平台规范自动生成，当前状态为草稿（Draft）。以下信息需要项目补充后需求方可提升为 Ready：

1. GPIO 引脚分配表和功能定义（硬件设计）。
2. I2C 总线编号、SDA/SCL 引脚映射（硬件原理图）。
3. INT 引脚连接的 MCU GPIO/ICU 通道及其中断处理方式（硬件+架构）。
4. RESET 引脚的控制归属（硬件+架构）。
5. 运行时方向变更和极性变更策略（架构）。
6. API 粒度确认：Pin 级 vs Port 级接口（架构）。
7. MainFunction 调度周期（架构）。
8. ROM/RAM/栈预算（项目）。
9. I2C 总线速率和上拉电阻值（硬件）。

本文档中的 Datasheet-only 信息默认标记为 Draft；只有经项目补充确认后的需求方可提升为 Ready。
