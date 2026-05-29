# Gp_NCA9539 芯片详细设计输入

> 本文档从芯片手册提取，服务于详细设计 + 代码生成阶段。在架构视图基础上追加：寄存器行为语义与精确常量、状态转换条件、故障源行为、操作时序参数、初始化约束、数据组装规则、命令/响应编码和跨寄存器关系。不含 `#define` 宏名、C 变量名或代码片段。

## D1. 寄存器完整行为与常量表

> 每条 bit 同时提供行为语义和精确常量。每个寄存器后附寄存器级约束摘要。

<!-- LLM_SUPPLEMENT: 未在数据手册中找到结构化的 bit 段定义表格。请从寄存器说明章节逐寄存器提取 bit 段信息。 -->

## D2. 状态转换条件

<!-- LLM_SUPPLEMENT: 请从芯片手册的模式/状态描述章节提取状态转换条件。 -->

## D3. 故障源行为

<!-- LLM_SUPPLEMENT: 请从芯片手册的诊断/故障/中断章节提取故障源行为。 -->

## D4. 操作时序参数

| 参数符号 | 含义 | 典型值 | 最小值 | 最大值 | 单位 | 用途场景 |
|----------|------|--------|--------|--------|------|---------|
| Input diode clamp voltage | Input diode clamp voltage |  | -1.2 |  | V |  |
| Supply voltage Range | Supply voltage Range |  | 1.65 | 3.6 | V |  |
| Supply current | Supply current | 12.5 |  | 30 | $\mu A$ |  |
| Standby current | Standby current | 0.14 |  | 5 | $\mu A$ |  |
| Power On Reset Voltage, Rising [1] | Power On Reset Voltage, Rising [1] | 1.17 | 0.75 | 1.5 | V |  |
| Power On Reset Voltage, Falling [1] | Power On Reset Voltage, Falling [1] | 1.05 | 0.75 | 1.5 | V |  |
| Input SCL; Input and Output SDA | Input SCL; Input and Output SDA |  |  |  |  |  |
| LOW-level input voltage | LOW-level input voltage |  | -0.5 | $0.3 \cdot V_{DD}$ | V |  |
| HIGH-level input voltage | HIGH-level input voltage |  | $0.7 \cdot V_{DD}$ | 3.6 | V |  |
| LOW-level output current | LOW-level output current |  | 3 |  | mA |  |
| Input leakage current | Input leakage current |  | -1 | 1 | μA |  |
| Input capacitance | Input capacitance | 6 |  | 10 | pF |  |
| I/Os | I/Os |  |  |  |  |  |
| LOW-level input voltage | LOW-level input voltage |  | -0.5 | $0.3 \cdot V_{DD}$ | V |  |
| HIGH-level input voltage | HIGH-level input voltage |  | $0.7 \cdot V_{DD}$ | 3.6 | V |  |
| LOW-level output current | LOW-level output current |  | 8 |  | mA |  |
| HIGH-level output voltage | HIGH-level output voltage |  | 1.2 |  | V |  |
| HIGH-level input leakage current | HIGH-level input leakage current |  |  | 1 | μA |  |
| LOW-level input leakage current | LOW-level input leakage current |  |  | -1 | μA |  |
| Input capacitance | Input capacitance | 3.7 |  | 9.5 | pF |  |
| Output capacitance | Output capacitance | 3.7 |  | 9.5 | pF |  |
| Interrupt INT | Interrupt INT |  |  |  |  |  |
| LOW-level output current | LOW-level output current |  | 3 |  | mA |  |
| Select Inputs A0, A1 | Select Inputs A0, A1 |  |  |  |  |  |
| LOW-level input voltage | LOW-level input voltage |  | -0.5 | 0.3*V DD | V |  |
| HIGH-level input voltage | HIGH-level input voltage |  | 0.7*V DD | 3.6 | V |  |
| Input leakage current | Input leakage current |  | -1 | 1 | μA |  |
| RESET | RESET |  |  |  |  |  |
| Input leakage current | Input leakage current |  | -1 | 1 | μA |  |

## D5. 初始化约束

<!-- LLM_SUPPLEMENT: 请从芯片手册的初始化/上电/POR 章节提取初始化约束。 -->

## D6. 读回数据组装规则

<!-- LLM_SUPPLEMENT: 请从芯片手册的多寄存器数据读取章节提取数据组装规则。 -->

## D7. 命令/响应编码

### 器件地址

| inputs | i <sup>2</sup> c bus slave address |
|----|----|
| A0 |  |
| L | 116(decimal), 74h(hexadecimal) |
| H | 117(decimal), 75h(hexadecimal) |
| L | 118(decimal), 76h(hexadecimal) |
| H | 119(decimal), 77h(hexadecimal) |

### 命令字节

| 命令字节(hex) | 目标寄存器 | 操作 |
|--------------|-----------|------|
|  | B2 |  |
| 00h | 0 |  |
| 01h | 0 |  |
| 02h | 0 |  |
| 03h | 0 |  |
| 04h | 1 |  |
| 05h | 1 |  |
| 06h | 1 |  |
| 07h | 1 |  |


## D8. 跨寄存器关系

<!-- LLM_SUPPLEMENT: 请从芯片手册的 Burst/多字节访问/寄存器更新顺序等章节提取跨寄存器约束。 -->
