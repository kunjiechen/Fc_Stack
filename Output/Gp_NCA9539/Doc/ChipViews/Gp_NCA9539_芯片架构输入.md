# Gp_NCA9539 芯片架构输入

> 本文档从芯片手册提取，服务于架构生成阶段。只描述"芯片提供了什么资源，资源长什么样"，不做分类、分组、归并等架构决策。

## A1. 模块身份

| 字段 | 值 |
|------|-----|
| 芯片型号 | NCA9539-Q1 |
| 制造商 | Novosense |
| 数据手册版本 | Rev 1.0 |
| 功能一句话 | 16-bit I2C-bus I/O port with interrupt and reset |
| 通信接口类型 | I2C |
| 通信接口最大速率 | 400 kHz (Fast-mode) |
| 功能安全等级 | 手册未说明 |

## A2. 引脚清单

| 引脚名 | 方向(Mcu视角) | 功能 | 有效电平 | 内部上下拉 | 是否必须连接 |
|--------|--------------|------|---------|-----------|-------------|
| INT\ | Output | Interrupt open-drain output. Connect to VDD through a pull-up resistor | Low有效 | 内部Pull-up | 按需 |
| A1 | Power | Address input 1. Connect directly to VDD or ground | — | 手册未说明 | 必须 |
| RESET\ | Input | Active-low reset input. Connect to VDD through a pull-up resistor | Low有效 | 内部Pull-up | 必须 |
| P00 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P01 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P02 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P03 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P04 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P05 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P06 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P07 | Bidir | Port 0 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| VSS | Power | Ground | — | 手册未说明 | 必须 |
| P10 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P11 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P12 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P13 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P14 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P15 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P16 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| P17 | Bidir | Port 1 input/output. At power-on, the port is configured as an input | — | 手册未说明 | 按需 |
| A0 | Power | Address input 0. Connect directly to VDD or ground | — | 手册未说明 | 必须 |
| SCL | Input | Serial clock bus. Connect to VDD through a pull-up resistor | — | 内部Pull-up | 必须 |
| SDA | Bidir | Serial data bus. Connect to VDD through a pull-up resistor | — | 内部Pull-up | 必须 |
| VDD | Power | Supply voltage | — | 手册未说明 | 必须 |

## A3. 工作模式

<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的模式定义表格。请从手册中提取工作模式信息。 -->

## A4. 寄存器空间概览

| 寄存器名 | 地址 | 位宽 | 访问属性 | 功能分类 | 一句话功能 |
|----------|------|------|---------|---------|-----------|
| Input port register pair 0 | 0x00 | 8 | R/W | 数据 | Input port register pair |
| Input port register pair 1 | 0x01 | 8 | R/W | 数据 | Input port register pair |
| Output port registers 0 | 0x02 | 8 | R/W | 数据 | Output port registers |
| Output port registers 1 | 0x03 | 8 | R/W | 数据 | Output port registers |
| Polarity inversion registers 0 | 0x04 | 8 | R/W | 配置 | Polarity inversion registers |
| Polarity inversion registers 1 | 0x05 | 8 | R/W | 配置 | Polarity inversion registers |
| Configuration registers 0 | 0x06 | 8 | R/W | 配置 | Configuration registers |
| Configuration registers 1 | 0x07 | 8 | R/W | 配置 | Configuration registers |

### 寄存器分类统计表

| 功能分类 | 寄存器数量 | 寄存器列表 |
|----------|-----------|-----------|
| 数据 | 4 | Input port register pair 0, Input port register pair 1, Output port registers 0, Output port registers 1 |
| 配置 | 4 | Polarity inversion registers 0, Polarity inversion registers 1, Configuration registers 0, Configuration registers 1 |

## A5. 通信帧协议

| 字段 | 值 |
|------|-----|
| 帧位宽 | 8 bit |
| 命令结构 | 器件地址(7bit) + R/W(1bit) + 命令字节(8bit) |
| 响应结构 | ACK后紧跟数据字节(8bit)，MSB优先 |
| 地址空间范围 | 手册未说明 |
| Burst Read | 手册未说明 |
| Burst Write | 手册未说明 |
| CRC | 无 |
| 帧间最小间隔 | 手册未说明 |
| device_address | 6.5.1. Device Address ..... 16 |

## A6. 中断资源

<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的中断定义表格 -->

## A7. 时钟与复位

| 字段 | 值 |
|------|-----|
| 时钟源 | I2C总线时钟(SCL)，由主控提供 |
| 复位源列表 | POR (内部上电复位) |
| 各复位源影响范围 | 全量复位：所有寄存器恢复默认值，状态机初始化 |
| 复位后默认模式 | 手册未说明 |
| 复位恢复时间 | 手册未说明 |
