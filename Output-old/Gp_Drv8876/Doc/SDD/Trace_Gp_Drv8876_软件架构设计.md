# Trace_Gp_Drv8876_软件架构设计

## 追溯元信息

- **上游文档**: `Gp_Drv8876_软件需求规范.md` (SRS V1 Draft)
- **下游架构**: `Gp_Drv8876_软件架构设计.md` (V1 Draft)
- **追溯方向**: SRS → Architecture
- **生成日期**: 2026-05-27

---

## SRS → Architecture 追溯矩阵

| SRS Requirement ID | SRS 摘要 | 架构覆盖对象 | 架构落点 | 覆盖状态 | 设计决策 | 关闭条件 |
| --- | --- | --- | --- | --- | --- | --- |
| SRS-GPDRV8876-FUNC-0001 | 初始化默认状态控制 | `Gp_Drv8876_Init` + per-instance default mode config | §3.1 外部接口; §5 运行时策略; per-instance config table | Covered | Init 将各实例 nSLEEP/EN/PH 置为配置默认值；默认值通过配置表承载 | 默认值由项目确认 (R4) |
| SRS-GPDRV8876-FUNC-0002 | Sleep/Active 模式切换 | `Gp_Drv8876_SetDevModeOutSig` + MainFunction 时序管理 | §3.2, §3.8 外部接口; §5 nSLEEP timing SM | Covered | 异步模式：Set 缓存请求，MainFunction 管理 nSLEEP + tSLEEP/tWAKE | MainFunction 策略确认 (R2) |
| SRS-GPDRV8876-FUNC-0003 | H 桥输出状态控制 | `Gp_Drv8876_SetHbOutSig` + MainFunction 真值表映射 | §3.4 外部接口; §5 buffered request container | Covered | 异步模式：Set 校验并缓存；MainFunction 按 PMODE 查真值表输出 EN/PH | 控制模式范围确认 (R1) |
| SRS-GPDRV8876-FUNC-0004 | 独立半桥输出控制 | `Gp_Drv8876_SetHalfBridgeOutSig` | §3.5 外部接口; `GP_DRV8876_CFG_HALF_BRIDGE_ENABLE` | Pending Confirmation | 条件编译，待项目确认是否启用 | 独立半桥模式确认 (R3) |
| SRS-GPDRV8876-FUNC-0005 | 模式锁存处理 | MainFunction 锁存序列 | §3.8 MainFunction; §8.2 CalloutWrDioCh (PMODE/IMODE) | Covered | nSLEEP Low → 改 PMODE/IMODE → 等待 → nSLEEP High → tWAKE → 允许输出 | PMODE/IMODE 可控性确认 (R1) |
| SRS-GPDRV8876-INTF-0001 | 初始化接口 | `Gp_Drv8876_Init(void)` | §3.1 外部接口 | Covered | void Init(void)，加载当前核配置，幂等设计 | 无 |
| SRS-GPDRV8876-INTF-0002 | 芯片模式设置接口 | `Gp_Drv8876_SetDevModeOutSig(uint16, uint8)` | §3.2 外部接口 | Covered | 异步缓冲语义，返回 Std_ReturnType | 无 |
| SRS-GPDRV8876-INTF-0003 | 芯片模式读取接口 | `Gp_Drv8876_GetDevModeInSig(uint16, uint8*)` | §3.3 外部接口 | Covered | 同步读取软件缓冲模式，Reentrant | 无 |
| SRS-GPDRV8876-INTF-0004 | H 桥输出设置接口 | `Gp_Drv8876_SetHbOutSig(uint16, uint8, uint32, uint32)` | §3.4 外部接口 | Covered | 异步缓冲语义；Period/Duty 单位由配置表定义 | PWM 单位确认 (R7) |
| SRS-GPDRV8876-INTF-0005 | 半桥输出设置接口 | `Gp_Drv8876_SetHalfBridgeOutSig(uint16, uint8, uint8)` | §3.5 外部接口 | Pending Confirmation | 条件接口；项目不启用则移除或固定返回 E_NOT_OK | 独立半桥模式确认 (R3) |
| SRS-GPDRV8876-INTF-0006 | 故障读取接口 | `Gp_Drv8876_GetDevFaultSig(uint16, uint32*)` | §3.6 外部接口 | Covered | 同步读取 MainFunction 更新的故障位掩码，Reentrant | 故障位定义确认 (R6) |
| SRS-GPDRV8876-INTF-0007 | 电流反馈读取接口 | `Gp_Drv8876_GetCurrentRaw(uint16, uint16*)` | §3.7 外部接口 | Covered | 同步读取 MainFunction 更新的 ADC 原始值 | 换算策略确认 (R5) |
| SRS-GPDRV8876-CFG-0001 | 实例与信号映射配置 | Per-core SigMapping table + Core ID check | §4 配置宏; §8.1 CalloutGetCoreId | Covered | uint16 Id → Core/Chip/Channel/Hardware resource; 跨核拒绝 | 无 |
| SRS-GPDRV8876-CFG-0002 | 控制模式配置 | PMODE enum in config container | Per-instance config in `Gp_Drv8876_Cfg.c` | Covered | PH/EN、PWM、独立半桥三选一 | 无 |
| SRS-GPDRV8876-CFG-0003 | 电流调节模式配置 | IMODE enum in config container | Per-instance config in `Gp_Drv8876_Cfg.c` | Covered | 四电平选择；决定诊断边界 | 无 |
| SRS-GPDRV8876-CFG-0004 | PWM 参数配置 | PWM resource binding + range in config table | Per-instance config in `Gp_Drv8876_Cfg.c` | Covered | 周期/占空比范围、空闲状态由配置表承载 | PWM 单位确认 (R7) |
| SRS-GPDRV8876-CFG-0005 | 电流反馈配置 | ADC channel + RIPROPI + AIPROPI + VREF in config table | Per-instance config in `Gp_Drv8876_Cfg.c` | Covered | 配置参数支持原始 ADC 读取和后续换算 | 无 |
| SRS-GPDRV8876-DIAG-0001 | 开发错误检测 | `GP_DRV8876_CFG_DEV_ERROR_DETECT` + 接口层校验 | §4 配置宏; §5 DET error record | Covered | DET 开关 + 运行时 DET 记录 | 无 |
| SRS-GPDRV8876-DIAG-0002 | nFAULT 低有效语义 | `Gp_Drv8876_GetDevFaultSig` + MainFunction 采样 + CalloutReadDioCh | §3.6, §3.8 外部接口; §8.3 依赖接口 | Covered | nFAULT 低→故障位有效；Callout 内处理电平反转 | 无 |
| SRS-GPDRV8876-DIAG-0003 | 逐周期电流斩波指示边界 | Fault status bit + IMODE context in MainFunction | §3.8 MainFunction; §5 fault status bitmask | Covered | MainFunction 根据 IMODE + 当前输出状态区分/聚合 | 故障位定义确认 (R6) |
| SRS-GPDRV8876-DIAG-0004 | 过流响应软件边界 | nFAULT 读取 + IMODE 配置责任边界 | §3.6; §8.3 CalloutReadDioCh | Covered | 架构明确软件仅读取上报，OCP 保护由芯片/IMODE 决定 | 无 |
| SRS-GPDRV8876-TIM-0001 | Sleep 等待时间 | MainFunction + CalloutDelayUs | §3.8 MainFunction; §8.6 CalloutDelayUs | Covered | nSLEEP Low 后等待 ≥1ms (tSLEEP) | Delay Callout 策略确认 (R8) |
| SRS-GPDRV8876-TIM-0002 | Active 唤醒等待时间 | MainFunction + CalloutDelayUs | §3.8 MainFunction; §8.6 CalloutDelayUs | Covered | nSLEEP High 后等待 ≥1ms (tWAKE) 才允许输出 | Delay Callout 策略确认 (R8) |
| SRS-GPDRV8876-TIM-0003 | PWM 频率边界 | 配置表 PWM range + 接口校验 | §3.4; per-instance config range | Covered | 频率 ≤100kHz 由配置约束和接口校验保证 | 无 |
| SRS-GPDRV8876-SAFE-0001 | QM 安全等级 | 架构 QM 标识 | §1 FC总结介绍 | Covered | 不分配 ASIL 目标 | 无 |
| SRS-GPDRV8876-SAFE-0002 | 输出误动作防护 | 接口前置条件检查 + 状态机 guard | §3 外部接口约束; §5 per-instance state machine | Covered | 未初始化/无效ID/唤醒未完成/Sleep 状态拒绝输出 | 无 |
| SRS-GPDRV8876-CODE-0001 | 编码规范符合性 | 命名/文件结构/MemMap 符合项目规则 | 全局命名与文件结构 | Covered | Gp_Drv8876 前缀；宏全大写；文件族符合 project-style-rules | 无 |
| SRS-GPDRV8876-RES-0001 | MCU 资源占用约束 | Per-instance config resource binding | Per-instance config in `Gp_Drv8876_Cfg.c` | Covered | 每实例 DIO/PWM/ADC 资源在配置表声明 | 无 |
| SRS-GPDRV8876-COMP-0001 | 需求追溯完整性 | 本追溯矩阵 + 架构 §2 需求覆盖表 | 本文档 | Covered | 每条 SRS → Architecture 可追溯 | 无 |
| (新增) | 周期调度 | `Gp_Drv8876_MainFunction` | §3.8 外部接口 | Covered | 新增周期性处理函数，SRS R6 标记为待确认 | MainFunction 策略确认 (R2) |

---

## 覆盖统计

- **总 SRS 需求数**: 28
- **Covered**: 24
- **Partially Covered**: 0
- **Pending Confirmation**: 4 (FUNC-0004, INTF-0005, R2 MainFunction strategy, R5 current-conversion API form)
- **未覆盖**: 0

---

## 设计决策记录

| 决策ID | 决策描述 | 依据 | 影响范围 |
| --- | --- | --- | --- |
| D1 | 采用异步请求-周期处理模式（MainFunction） | SRS R6; demo Gp_DRV887x_DIO 模式; tSLEEP/tWAKE 需要时间管理 | 外部接口 Set 为缓冲语义；MainFunction 为唯一硬件写入点 |
| D2 | 使用 Callout 抽象所有硬件访问 | AURIX2G source grounding §4; interface-selection rules | DIO/PWM/ADC/GetCoreId/Delay 共 6 个 Callout |
| D3 | 不生成 FC_Reg.h | DRV8876 无 SPI/I2C/寄存器接口 | 文件列表不含 Reg.h |
| D4 | 不生成 FC_Cali.c | 时序和阈值参数属于项目配置而非标定流程 | 标定参数表标记 Empty |
| D5 | 独立半桥接口条件编译 | SRS FUNC-0004 标记 Open Issue | 由 GP_DRV8876_CFG_HALF_BRIDGE_ENABLE 控制 |
| D6 | 多核按 Core ID 隔离 | SRS CFG-0001 跨核映射约束; source grounding §5 | 每核独立运行时容器和配置表 |
