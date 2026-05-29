# Check_Gp_NCA9539_软件需求规范

## 需求检查清单

| 字段 | 值 |
|------|-----|
| 检查对象 | [Gp_NCA9539] 软件需求规范 v0.1.0 |
| 检查日期 | 2026-05-28 |
| 检查人 | FC Requirement Workbench (自动检查) |
| 检查类型 | 自动化需求质量检查 |
| 发布包完整性 | 7/7 文件已生成 |

---

## 1. 需求条目检查明细

### 1.1 字段完整性检查

| 需求ID | 标题 | 描述 | 来源 | ASIL | 验证方式 | 状态 | 结果 |
|--------|------|------|------|------|---------|------|------|
| SRS-Gp_NCA9539-FUNC-0001 | 模块初始化与复位恢复 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-FUNC-0002 | 多实例管理 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-INTF-0001 | GPIO 输出控制接口 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-INTF-0002 | GPIO 输入读取接口 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-INTF-0003 | GPIO 方向配置接口 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-INTF-0004 | 极性反转配置接口 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-INTF-0005 | I2C 寄存器读写接口 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-INTF-0006 | 中断状态读取接口 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-CFG-0001 | 实例数量与 I2C 地址配置 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-CFG-0002 | I2C 通信速率配置 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-CFG-0003 | 上电默认引脚方向配置 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-DIAG-0001 | DET 错误报告 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-DIAG-0002 | I2C 通信故障诊断 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-DIAG-0003 | 中断状态丢失诊断 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-TIM-0001 | 复位释放后初始化等待时间 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-TIM-0002 | RESET\ 脉冲宽度控制 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-TIM-0003 | 输出端口稳定时间 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-TIM-0004 | 中断响应时间约束 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-SAFE-0001 | 功能安全等级约束 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-SAFE-0002 | 寄存器和配置校验 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-CODE-0001 | MISRA C 编码规范 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-RES-0001 | ROM/RAM/Stack 资源消耗约束 | Y | Y | Y | Y | Y | PASS |
| SRS-Gp_NCA9539-COMP-0001 | 需求与测试追溯 | Y | Y | Y | Y | Y | PASS |

### 1.2 模糊词检查

| 需求ID | 模糊词检查结果 |
|--------|---------------|
| SRS-Gp_NCA9539-FUNC-0001 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-FUNC-0002 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-INTF-0001 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-INTF-0002 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-INTF-0003 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-INTF-0004 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-INTF-0005 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-INTF-0006 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-CFG-0001 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-CFG-0002 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-CFG-0003 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-DIAG-0001 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-DIAG-0002 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-DIAG-0003 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-TIM-0001~0004 | PASS — 数值和单位完整 |
| SRS-Gp_NCA9539-SAFE-0001~0002 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-CODE-0001 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-RES-0001 | PASS — 无模糊词 |
| SRS-Gp_NCA9539-COMP-0001 | PASS — 无模糊词 |

### 1.3 来源证据检查

| 需求ID | 来源证据 | 证据强度 | 结果 |
|--------|---------|---------|------|
| SRS-Gp_NCA9539-FUNC-0001 | Datasheet-POR; Datasheet-RESET pin | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-FUNC-0002 | Datasheet-A0/A1 addressing | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-INTF-0001 | Datasheet-Output/Config Registers | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-INTF-0002 | Datasheet-Input Port Registers | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-INTF-0003 | Datasheet-Config Registers; I/O port | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-INTF-0004 | Datasheet-Polarity Inversion Registers | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-INTF-0005 | Datasheet-I2C Interface; Bus Transactions | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-INTF-0006 | Datasheet-INT output; Interrupt | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-CFG-0001 | Datasheet-A0/A1; Device Address | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-CFG-0002 | Datasheet-Dynamic Characteristics | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-CFG-0003 | Datasheet-POR; Configuration Registers | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-DIAG-0001 | 项目需求-ASIL-B; Datasheet-I2C Interface | L1/L3 | PASS |
| SRS-Gp_NCA9539-DIAG-0002 | Datasheet-I2C Interface; Acknowledge | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-DIAG-0003 | Datasheet-INT output; Interrupt clearing | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-TIM-0001 | Datasheet-t_rec(rst); t_rst | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-TIM-0002 | Datasheet-t_w(rst) | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-TIM-0003 | Datasheet-t_v(Q) | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-TIM-0004 | Datasheet-t_v(INT_N); t_rst(INT_N) | L3 (Datasheet) | PASS |
| SRS-Gp_NCA9539-SAFE-0001 | 项目需求-安全等级 | L1 (项目需求) | PASS |
| SRS-Gp_NCA9539-SAFE-0002 | 项目需求-ASIL-B; Datasheet-Register Maps | L1/L3 | PASS |
| SRS-Gp_NCA9539-CODE-0001 | 项目需求-编码规范 | L1 (项目需求) | PASS |
| SRS-Gp_NCA9539-RES-0001 | 项目需求-资源约束 | L1 (项目需求) | PASS |
| SRS-Gp_NCA9539-COMP-0001 | 项目需求-追溯要求 | L1 (项目需求) | PASS |

---

## 2. 分类覆盖检查

| 类别 | 预期条目数 | 实际条目数 | 结果 |
|------|-----------|-----------|------|
| 功能需求 | >=2 | 2 | PASS |
| 接口需求 | >=5 | 6 | PASS |
| 配置需求 | >=2 | 3 | PASS |
| 诊断需求 | >=2 | 3 | PASS |
| 时序需求 | >=3 | 4 | PASS |
| 安全等级需求 | >=1 | 2 | PASS |
| 编码规范需求 | >=1 | 1 | PASS |
| 资源消耗需求 | >=1 | 1 | PASS |
| 过程质量需求 | >=1 | 1 | PASS |
| **合计** | — | **23** | — |

---

## 3. 芯片手册覆盖率

| 芯片手册关键功能 | 对应 SRS 需求 | 覆盖 |
|----------------|-------------|------|
| 16-bit GPIO 扩展 | FUNC-0001, FUNC-0002, INTF-0001, INTF-0002 | Y |
| 输入端口读取 | INTF-0002 | Y |
| 输出端口控制 | INTF-0001 | Y |
| 方向配置 | INTF-0003, CFG-0003 | Y |
| 极性反转 | INTF-0004 | Y |
| I2C 通信 | INTF-0005, CFG-0002 | Y |
| 器件地址 (A0/A1) | FUNC-0002, CFG-0001 | Y |
| 中断 (INT\) | INTF-0006, DIAG-0003, TIM-0004 | Y |
| 硬件复位 (RESET\) | FUNC-0001, TIM-0001, TIM-0002 | Y |
| 上电复位 | FUNC-0001 | Y |
| 时序参数 | TIM-0001~0004 | Y |
| 待机模式 | — (芯片硬件自动) | N/A |
| 噪声滤波器 | — (芯片硬件，软件不可控) | N/A |
| ESD 保护 | — (芯片硬件特性，非软件需求) | N/A |

---

## 4. 问题闭环表

| 问题ID | 问题描述 | 严重度 | 影响范围 | 建议处理 | 状态 |
|--------|---------|--------|---------|---------|------|
| ISSUE-01 | 所有 23 条需求状态为 Draft，需项目评审确认后升级为 Ready | 中 | 全部需求 | 完成 R1~R7 评审后逐条确认 | 开放 |
| ISSUE-02 | 实例数量未明确（R1），影响 CFG-0001 的具体配置值 | 高 | CFG-0001, FUNC-0002 | 获取硬件设计文档确认 | 开放 |
| ISSUE-03 | 中断处理策略未定（R2），影响 INTF-0006 的架构设计 | 中 | INTF-0006, DIAG-0003 | 架构设计阶段确认 | 开放 |
| ISSUE-04 | RESET\ 和 INT\ 引脚分配未明确（R5, R6） | 中 | TIM-0001, TIM-0002, INTF-0006 | 获取 MCU 引脚分配表 | 开放 |

---

## 5. 发布包完整性检查

| 产物 | 路径 | 状态 |
|------|------|------|
| SRS 文档 | Output/Gp_NCA9539/Doc/SRS/[Gp_NCA9539] 软件需求规范.md | 已生成 |
| Review 评审记录 | Output/Gp_NCA9539/Doc/SRS/Review_Gp_NCA9539_软件需求规范.md | 已生成 |
| Check 检查清单 | Output/Gp_NCA9539/Doc/SRS/Check_Gp_NCA9539_软件需求规范.md | 已生成 |
| Trace 追溯矩阵 | Output/Gp_NCA9539/Doc/SRS/Trace_Gp_NCA9539_软件需求规范.md | 已生成 |
| 芯片架构输入 | Output/Gp_NCA9539/Doc/ChipViews/Gp_NCA9539_芯片架构输入.md | 已生成 |
| 芯片详细设计输入 | Output/Gp_NCA9539/Doc/ChipViews/Gp_NCA9539_芯片详细设计输入.md | 已生成 |

**发布包完整性：7/7 文件已生成。**

---

## 6. 发布判定

| 检查类别 | 结果 |
|----------|------|
| 文件完整性 | PASS |
| 需求字段完整性 | PASS (23/23) |
| 模糊词检查 | PASS |
| 来源证据检查 | PASS (23/23) |
| 分类覆盖 | PASS |
| 芯片手册覆盖 | PASS |

**发布判定：条件通过 — 所有自动化检查通过，但需完成 R1~R7 人工评审后方可正式发布。**
