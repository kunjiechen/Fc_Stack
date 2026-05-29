# Trace_Gp_NCA9539_软件需求规范

## 追溯矩阵

| 字段 | 值 |
|------|-----|
| 追溯对象 | [Gp_NCA9539] 软件需求规范 v0.1.0 |
| 生成日期 | 2026-05-28 |
| 生成工具 | FC Requirement Workbench |

---

## 1. Source → Requirement 追溯

### 1.1 芯片手册章节 → 需求映射

| 芯片手册章节 | 来源内容 | 映射需求ID | 映射类型 |
|-------------|---------|-----------|---------|
| Product Overview | 16-bit I2C GPIO expander 概述 | FUNC-0001, FUNC-0002 | 功能概述→多需求 |
| Pin Configuration (Table 1-1) | 引脚定义：INT\, A1, RESET\, P00~P07, P10~P17, A0, SCL, SDA, VDD, VSS | FUNC-0001, INTF-0001~0006, CFG-0001 | 引脚→接口需求 |
| 6.2.1 I/O port | 输入/输出模式 FET 行为 | INTF-0001, INTF-0002, INTF-0003 | 芯片能力→接口需求 |
| 6.2.2 RESET\ input | RESET\ 引脚复位行为 | FUNC-0001, TIM-0001, TIM-0002 | 复位→功能+时序需求 |
| 6.2.3 Interrupt Output | INT\ 中断行为、清除机制 | INTF-0006, DIAG-0003, TIM-0004 | 中断→接口+诊断+时序 |
| 6.3.1 Power-On Reset | POR 行为、V_POR 阈值 | FUNC-0001 | POR→功能需求 |
| 6.4.1 I2C Interface | I2C 接口概述 | INTF-0005 | I2C→接口需求 |
| 6.4.2 Start/Stop Conditions | I2C 起始/停止条件 | INTF-0005 | I2C→接口需求 |
| 6.4.3 Bit Transfer | I2C 位传输 | INTF-0005 | I2C→接口需求 |
| 6.4.5 Acknowledge | I2C ACK/NACK | DIAG-0002 | ACK→诊断需求 |
| 6.5.1 Device Address | 器件地址字节结构、地址表 | FUNC-0002, CFG-0001 | 地址→功能+配置需求 |
| 6.5.2 Command Byte | 命令字节与控制寄存器 | INTF-0005 | 命令字节→接口需求 |
| 6.5.3 Input Port Registers | 输入端口寄存器(0x00,0x01) | INTF-0002 | 寄存器→接口需求 |
| 6.5.4 Output Port Registers | 输出端口寄存器(0x02,0x03) | INTF-0001 | 寄存器→接口需求 |
| 6.5.5 Polarity Inversion Registers | 极性反转寄存器(0x04,0x05) | INTF-0004 | 寄存器→接口需求 |
| 6.5.6 Configuration Registers | 方向配置寄存器(0x06,0x07) | INTF-0003, CFG-0003 | 寄存器→接口+配置需求 |
| 6.6.1 Writing to Port Registers | 写端口寄存器时序 | INTF-0001, INTF-0005, TIM-0003 | 写操作→接口+时序需求 |
| 6.6.2 Reading Port Registers | 读端口寄存器时序 | INTF-0002, INTF-0005 | 读操作→接口需求 |
| 5.2 Dynamic Characteristics | I2C 时序参数表 | TIM-0001~0004, CFG-0002 | 时序→时序+配置需求 |

### 1.2 项目需求 → 需求映射

| 项目需求 | 映射需求ID | 映射类型 |
|---------|-----------|---------|
| FC名称: Gp_NCA9539 | 全部需求（模块命名空间） | 身份约束 |
| 安全级别: ASIL-B | SAFE-0001, SAFE-0002, DIAG-0001, CODE-0001, COMP-0001 | 安全等级→多需求 |
| DET 开发错误检测 | DIAG-0001 | 安全→诊断需求 |
| MISRA C:2012 | CODE-0001 | 编码规范→编码需求 |

---

## 2. Requirement → Verification Intent 追溯

| 需求ID | 验证方式 | 验证阶段 | 验证意图描述 | 对应测试域 |
|--------|---------|---------|-------------|-----------|
| SRS-Gp_NCA9539-FUNC-0001 | Test | UT | 验证上电/复位后初始化流程正确：I2C 通信可达、寄存器默认值符合预期、目标配置写入成功 | Init |
| SRS-Gp_NCA9539-FUNC-0002 | Test | UT | 验证 2+ 实例独立管理：各实例操作互不干扰 | MultiInstance |
| SRS-Gp_NCA9539-INTF-0001 | Test | UT | 验证 GPIO 输出控制：写入 Output 寄存器后引脚电平和回读值一致 | GpioOutput |
| SRS-Gp_NCA9539-INTF-0002 | Test | UT | 验证 GPIO 输入读取：读取值与引脚实际电平一致（含极性反转） | GpioInput |
| SRS-Gp_NCA9539-INTF-0003 | Test | UT | 验证方向配置：写入 Configuration 寄存器后回读一致，引脚行为符合方向设定 | GpioDir |
| SRS-Gp_NCA9539-INTF-0004 | Test | UT | 验证极性反转：配置反转后 Input Port 读值与实际电平相反 | Polarity |
| SRS-Gp_NCA9539-INTF-0005 | Test | UT | 验证 I2C 读写序列正确：写入后读回一致；异常场景返回 E_NOT_OK | I2cRw |
| SRS-Gp_NCA9539-INTF-0006 | Test | UT | 验证中断检测：输入变化触发 INT\，读端口后中断清除 | Interrupt |
| SRS-Gp_NCA9539-CFG-0001 | Review | Review | 审核配置项定义完整、取值范围合理 | Configuration |
| SRS-Gp_NCA9539-CFG-0002 | Review | Review | 审核 I2C 速率配置参数与硬件匹配 | Configuration |
| SRS-Gp_NCA9539-CFG-0003 | Test | UT | 验证初始化后 Configuration 寄存器与目标配置一致 | Init |
| SRS-Gp_NCA9539-DIAG-0001 | Test | UT | 验证 DET：非法参数触发 DET 报告且接口返回 E_NOT_OK | Det |
| SRS-Gp_NCA9539-DIAG-0002 | Test | UT | 验证 I2C NACK 检测：通信故障时返回 E_NOT_OK 且记录故障 | Fault |
| SRS-Gp_NCA9539-DIAG-0003 | Test | UT | 验证中断状态不丢失：快速连续变化后中断记录完整 | Interrupt |
| SRS-Gp_NCA9539-TIM-0001 | Analysis | UT | 示波器测量 RESET\ 释放后 SCL 第一个时钟边沿延迟 >= 200ns | Timing |
| SRS-Gp_NCA9539-TIM-0002 | Analysis | UT | 示波器测量 RESET\ 低电平持续时间 >= 6ns | Timing |
| SRS-Gp_NCA9539-TIM-0003 | Analysis | UT | 测量 Output 写操作后端口输出稳定时间 <= 300ns | Timing |
| SRS-Gp_NCA9539-TIM-0004 | Analysis | UT | 测量 INT\ 有效后到读操作完成的时间特性 | Timing |
| SRS-Gp_NCA9539-SAFE-0001 | Review | Review | 安全分析确认 ASIL-B 等级覆盖 | Safety |
| SRS-Gp_NCA9539-SAFE-0002 | Test | UT | 验证 Configuration 寄存器回读校验和故障恢复 | Safety |
| SRS-Gp_NCA9539-CODE-0001 | Inspection | Review | 静态分析工具确认 MISRA 合规 | Coding |
| SRS-Gp_NCA9539-RES-0001 | Analysis | Review | link map 确认资源消耗 | Resource |
| SRS-Gp_NCA9539-COMP-0001 | Review | Review | 追溯矩阵确认每条 Ready 需求有对应测试 | Process |

---

## 3. Raw Requirement Coverage（原始需求覆盖）

| 原始需求项 | 覆盖需求ID | 覆盖率 |
|-----------|-----------|--------|
| GPIO 扩展（16-bit） | FUNC-0001, FUNC-0002, INTF-0001, INTF-0002, INTF-0003, CFG-0003 | 100% |
| I2C 接口通信 | INTF-0005, CFG-0002, DIAG-0002 | 100% |
| 中断和诊断 | INTF-0006, DIAG-0003, TIM-0004 | 100% |
| 复位和默认状态 | FUNC-0001, TIM-0001, TIM-0002 | 100% |
| 极性反转 | INTF-0004 | 100% |
| 多器件寻址 | FUNC-0002, CFG-0001 | 100% |
| ASIL-B 安全 | SAFE-0001, SAFE-0002, DIAG-0001, COMP-0001 | 100% |
| 编码规范 | CODE-0001 | 100% |
| 资源约束 | RES-0001 | 100% |

**原始需求覆盖率：9/9 项覆盖，覆盖率 100%。**

---

## 4. ASPICE Evidence Summary

| ASPICE 过程 | 实践 | 证据 | 状态 |
|------------|------|------|------|
| SWE.1 软件需求分析 | 需求文档编写 | [Gp_NCA9539] 软件需求规范 v0.1.0 | Available |
| SWE.1 软件需求分析 | 需求与来源可追溯 | 本追溯矩阵 §1 Source→Requirement | Available |
| SWE.1 软件需求分析 | 需求评审 | Review_Gp_NCA9539_软件需求规范 | Available |
| SWE.1 软件需求分析 | 需求检查 | Check_Gp_NCA9539_软件需求规范 | Available |
| SWE.4 软件单元验证 | 需求到验证意图可追溯 | 本追溯矩阵 §2 Requirement→Verification | Available |
| SWE.5 软件集成验证 | 需求到验证方法 | SRS 中每条需求的验证方式字段 | Available |
| SWE.6 软件合格性测试 | 需求覆盖分析 | 本追溯矩阵 §3 Raw Requirement Coverage | Available |
| SUP.9 问题解决管理 | 问题闭环 | Check 文档 §4 问题闭环表 | Available |

---

## 5. 变更影响分析

| 变更来源 | 受影响需求 | 影响评估 |
|---------|-----------|---------|
| 芯片实例数量变更 | FUNC-0002, CFG-0001 | 配置值变更，接口和功能逻辑不变 |
| I2C 速率变更 | CFG-0002, 时序需求 | 仅配置变更，接口不变 |
| 引脚分配变更 | INTF-0001~0006 的引脚映射 | 需求条目不变，仅架构/详细设计中的引脚映射变更 |
| 安全等级升级（ASIL-B→C/D） | SAFE-0001, SAFE-0002 | 安全需求需补充更多安全机制 |
| 芯片型号变更 | 全部需求 | 需要重新分析芯片手册差异 |

---

*本追溯矩阵由 FC Requirement Workbench 自动生成，跟随 SRS 版本同步更新。*
