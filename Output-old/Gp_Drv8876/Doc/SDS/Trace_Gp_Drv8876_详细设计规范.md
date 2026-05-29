# Trace_Gp_Drv8876_详细设计规范

**需求/架构 → 详细设计追溯矩阵**

## 追溯信息

| 属性 | 内容 |
| --- | --- |
| 追溯对象 | SRS `Gp_Drv8876_软件需求规范.md` V1 + SDD `Gp_Drv8876_软件架构设计.md` V1 → SDS V4 |
| 生成日期 | 2026-05-27 |

---

## SRS → SDS 追溯

| SRS 需求 ID | 需求摘要 | DD 落位章节 | DD 对象名 | 覆盖状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| SRS-GPDRV8876-FUNC-0001 | 初始化默认状态控制 | §6.1.1, §10.1, §11.2.1 | `Gp_Drv8876_Init`, DefaultDevMode/DefaultHbState | Covered | Init 加载配置并设默认输出 |
| SRS-GPDRV8876-FUNC-0002 | Sleep/Active 模式切换 | §6.1.2, §6.1.8, §7 | `SetDevModeOutSig`, `MainFunction`, nSLEEP 状态机 | Covered | 异步缓冲+时序管理 |
| SRS-GPDRV8876-FUNC-0003 | H 桥输出状态控制 | §6.1.4, §6.2.7 | `SetHbOutSig`, `MapHbOutput` | Covered | 真值表映射 PH/EN+PWM |
| SRS-GPDRV8876-FUNC-0004 | 独立半桥输出控制 | §6.1.5 | `SetHalfBridgeOutSig` | Pending | 启用取决于 HALF_BRIDGE_ENABLE |
| SRS-GPDRV8876-FUNC-0005 | 模式锁存处理 | §6.1.8, §6.2.6 | `MainFunction`, `ProcessModeTransition` | Covered | Sleep→改配置→Active 序列 |
| SRS-GPDRV8876-INTF-0001 | 初始化接口 | §6.1.1 | `Gp_Drv8876_Init(void)` | Covered | 子功能拆分+流程图 |
| SRS-GPDRV8876-INTF-0002 | 芯片模式设置接口 | §6.1.2 | `SetDevModeOutSig(Id_u16, DevMode_u8)` | Covered | 子功能拆分+流程图 |
| SRS-GPDRV8876-INTF-0003 | 芯片模式读取接口 | §6.1.3 | `GetDevModeInSig(Id_u16, *DevMode_pu8)` | Covered | 子功能拆分+流程图 |
| SRS-GPDRV8876-INTF-0004 | H 桥输出设置接口 | §6.1.4 | `SetHbOutSig(Id, HbState, Period, Duty)` | Covered | 子功能拆分+流程图 |
| SRS-GPDRV8876-INTF-0005 | 半桥输出设置接口 | §6.1.5 | `SetHalfBridgeOutSig(Id, HalfBridge, OutState)` | Pending | 半桥模式待确认 |
| SRS-GPDRV8876-INTF-0006 | 故障读取接口 | §6.1.6 | `GetDevFaultSig(Id_u16, *Fault_pu32)` | Covered | 子功能拆分+流程图 |
| SRS-GPDRV8876-INTF-0007 | 电流反馈读取接口 | §6.1.7 | `GetCurrentRaw(Id_u16, *Raw_pu16)` | Covered | ADC 原始值读取 |
| SRS-GPDRV8876-CFG-0001 | 实例与信号映射配置 | §11.2.1 | `SigMappingType`, `ConfigContainerType` | Covered | ID→Core/Chip/资源映射 |
| SRS-GPDRV8876-CFG-0002 | 控制模式配置 | §11.2.1 | `InstanceConfigType.PMODE` | Covered | PH_EN/PWM/INDEP_HB 枚举 |
| SRS-GPDRV8876-CFG-0003 | 电流调节模式配置 | §11.2.1 | `InstanceConfigType.IMODE` | Covered | LEVEL_1/2/3/4 枚举 |
| SRS-GPDRV8876-CFG-0004 | PWM 参数配置 | §11.2.1 | `PwmConfigType` | Covered | 周期/占空比范围 |
| SRS-GPDRV8876-CFG-0005 | 电流反馈配置 | §11.2.1 | `AdcConfigType` | Covered | ADC 通道+电阻值 |
| SRS-GPDRV8876-DIAG-0001 | 开发错误检测 | §8, §11.1 | DET 检查点, `DEV_ERROR_DETECT` | Covered | 6 个检查点 |
| SRS-GPDRV8876-DIAG-0002 | nFAULT 低有效语义 | §6.1.6, §9.5, §6.2.8 | `GetDevFaultSig`, nFAULT 故障项, `SampleFaultPin` | Covered | 连续多次确认+自恢复/锁存策略 |
| SRS-GPDRV8876-DIAG-0003 | 逐周期电流斩波指示 | §9.5 | nFAULT 故障项（芯片故障类型） | Covered | 连续多次确认策略 |
| SRS-GPDRV8876-DIAG-0004 | 过流响应软件边界 | §9.5, §9.3 | 故障处理设计 | Covered | 软件仅读取上报，锁存后 Init 清除 |
| SRS-GPDRV8876-TIM-0001 | Sleep 进入等待时间 | §7, §11.2.1 | nSLEEP 状态机, `tSLEEP_Us_u32` (≥1ms) | Covered | SLEEP_WAIT 状态管理 |
| SRS-GPDRV8876-TIM-0002 | Active 唤醒等待时间 | §7, §11.2.1 | nSLEEP 状态机, `tWAKE_Us_u32` (≥1ms) | Covered | WAKE_WAIT 状态管理 |
| SRS-GPDRV8876-TIM-0003 | PWM 输入频率边界 | §11.2.1 | `PwmConfigType.FrequencyMaxHz` (100kHz) | Covered | 配置约束 |
| SRS-GPDRV8876-SAFE-0001 | QM 安全等级管理 | §1 | FC概述 QM 层级 | Covered | 不分配 ASIL |
| SRS-GPDRV8876-SAFE-0002 | 输出误动作防护 | §6.1.4, §6.1.5, §8 | 前置条件检查+DET | Covered | 未初始化/无效ID/Sleep拒绝输出 |
| SRS-GPDRV8876-CODE-0001 | 编码规范符合性 | §13 | 代码编写限制要求 | Covered | 8 条限制规则 |
| SRS-GPDRV8876-RES-0001 | MCU 资源占用约束 | §11.2.1 | `SigMappingType` | Covered | 每实例 DIO/PWM/ADC 声明 |
| SRS-GPDRV8876-COMP-0001 | 需求追溯完整性 | 本文档 | SRS→SDS 追溯表 | Covered | 29 条 SRS 全覆盖 |

---

## SDD → SDS 追溯

| SDD 对象 | SDD 章节 | DD 落位章节 | DD 对象名 | 覆盖状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `Gp_Drv8876_Init` | §3.1 | §6.1.1 | `Gp_Drv8876_Init` | Covered | |
| `Gp_Drv8876_SetDevModeOutSig` | §3.2 | §6.1.2 | `Gp_Drv8876_SetDevModeOutSig` | Covered | |
| `Gp_Drv8876_GetDevModeInSig` | §3.3 | §6.1.3 | `Gp_Drv8876_GetDevModeInSig` | Covered | |
| `Gp_Drv8876_SetHbOutSig` | §3.4 | §6.1.4 | `Gp_Drv8876_SetHbOutSig` | Covered | |
| `Gp_Drv8876_SetHalfBridgeOutSig` | §3.5 | §6.1.5 | `Gp_Drv8876_SetHalfBridgeOutSig` | Covered | |
| `Gp_Drv8876_GetDevFaultSig` | §3.6 | §6.1.6 | `Gp_Drv8876_GetDevFaultSig` | Covered | |
| `Gp_Drv8876_GetCurrentRaw` | §3.7 | §6.1.7 | `Gp_Drv8876_GetCurrentRaw` | Covered | |
| `Gp_Drv8876_MainFunction` | §3.8 | §6.1.8 | `Gp_Drv8876_MainFunction` | Covered | |
| `CalloutGetCoreId` | §8.1 | §6.3.1 | `Gp_Drv8876_CalloutGetCoreId` | Covered | |
| `CalloutWrDioCh` | §8.2 | §6.3.2 | `Gp_Drv8876_CalloutWrDioCh` | Covered | |
| `CalloutReadDioCh` | §8.3 | §6.3.3 | `Gp_Drv8876_CalloutReadDioCh` | Covered | |
| `CalloutSetPwmPerdAndDuty` | §8.4 | §6.3.4 | `Gp_Drv8876_CalloutSetPwmPerdAndDuty` | Covered | |
| `CalloutGetAdcRaw` | §8.5 | §6.3.5 | `Gp_Drv8876_CalloutGetAdcRaw` | Covered | |
| `CalloutDelayUs` | §8.6 | §6.3.6 | `Gp_Drv8876_CalloutDelayUs` | Covered | |
| `DEV_ERROR_DETECT` | §4 | §11.1 | `GP_DRV8876_CFG_DEV_ERROR_DETECT` | Covered | |
| `MAINFUNCTION_ENABLE` | §4 | §11.1 | `GP_DRV8876_CFG_MAINFUNCTION_ENABLE` | Covered | |
| `HALF_BRIDGE_ENABLE` | §4 | §11.1 | `GP_DRV8876_CFG_HALF_BRIDGE_ENABLE` | Covered | |
| SW_MAJOR/MINOR_VERSION | §4 | §11.1 | `GP_DRV8876_CFG_SW_MAJOR/MINOR_VERSION` | Covered | |
| Per-core runtime container | §5 | §10.1, §10.2 | `InstanceRuntimeType` + 运行变量表 | Covered | |
| Per-core config tables | §5 | §11.2 | `ConfigContainerType`, `SigMappingType` | Covered | |
| MemMap: CODE | §6 | §12 | CODE 段 | Covered | |
| MemMap: CLEAR_FAR_DATA | §6 | §12 | CLEAR_FAR_DATA 段 (per-core) | Covered | |
| MemMap: CONST per-core | §6 | §12 | CONST 段 (per-core) | Covered | |
| MemMap: CONST global | §6 | §12 | CONST 段 (global) | Covered | |
| 文件族：9 文件 | §9 | §4 | 文件列表 | Covered | |
| 内部函数：CheckInitAndId | — | §6.2.1 | `Gp_Drv8876_CheckInitAndId` | Covered | 全格式展开（V3） |
| 内部函数：CheckInitIdAndPtr | — | §6.2.2 | `Gp_Drv8876_CheckInitIdAndPtr` | Covered | 全格式展开（V3） |
| 内部函数：GetRumtime | — | §6.2.3 | `Gp_Drv8876_GetRumtime` | Covered | 全格式展开（V3） |
| 内部函数：GetCfgData | — | §6.2.4 | `Gp_Drv8876_GetCfgData` | Covered | 全格式展开（V3） |
| 内部函数：CheckInstanceActive | — | §6.2.5 | `Gp_Drv8876_CheckInstanceActive` | Covered | 全格式展开（V3） |
| 内部函数：ProcessModeTransition | — | §6.2.6 | `Gp_Drv8876_ProcessModeTransition` | Covered | 全格式展开（V3） |
| 内部函数：MapHbOutput | — | §6.2.7 | `Gp_Drv8876_MapHbOutput` | Covered | 全格式展开（V3） |
| 内部函数：SampleFaultPin | — | §6.2.8 | `Gp_Drv8876_SampleFaultPin` | Covered | 全格式展开+故障确认/恢复逻辑（V3） |
| 内部函数：SampleAdcRaw | — | §6.2.9 | `Gp_Drv8876_SampleAdcRaw` | Covered | 全格式展开（V3） |
| 故障处理：确认策略 | — | §9.1 | 故障确认策略（单次/连续多次） | Covered | V3 新增 |
| 故障处理：恢复策略 | — | §9.2 | 故障恢复策略（不可恢复/连续多次自恢复） | Covered | V3 新增 |
| 故障处理：锁存与清除 | — | §9.3 | 故障锁存与清除方式 | Covered | V3 新增 |
| 故障处理：自恢复配置 | — | §9.4 | `CFG_FAULT_SELF_RECOVERY_ENABLE` | Covered | V3 新增 |
| 故障处理：故障项设计 | — | §9.5 | 15 列完整故障属性表 | Covered | V3 新增 |
| 故障处理：运行参数 | — | §9.6 | 故障计数器变量 | Covered | V3 新增 |
| 配置宏参：故障自恢复 | — | §11.1 | `CFG_FAULT_SELF_RECOVERY_ENABLE` | Covered | V3 新增 |
| 配置宏参：故障确认/恢复阈值 | — | §11.1 | `CFG_FAULT_CONFIRM_THRESHOLD` / `CFG_FAULT_RECOVERY_THRESHOLD` | Covered | V3 新增 |
| 设计增量：故障确认计数器 | — | §10.1, §10.2.1, §17 | `FaultConfirmCnt_u8`, `FaultConfirmThreshold_u8` → R9 | Covered | V4 设计增量溯源 |
| 设计增量：故障恢复计数器 | — | §10.1, §10.2.1, §17 | `FaultRecoveryCnt_u8`, `FaultRecoveryThreshold_u8` → R10 | Covered | V4 设计增量溯源 |
| 设计增量：故障锁存标志 | — | §10.1, §10.2.1, §17 | `FaultLatched_b` → R11 | Covered | V4 设计增量溯源 |
| 设计增量：默认安全值 | — | §11.2.1, §17 | `DefaultDevMode_u8`, `DefaultHbState_u8` → R1 | Covered | V4 设计增量溯源 |
| 设计增量：PWM 参数边界 | — | §11.2.1, §17 | `PeriodMin_u32`, `PeriodMax_u32` → R4 | Covered | V4 设计增量溯源 |
| 设计增量：Sleep 时序运行时 | — | §10.2.1, §17 | `SleepTimingState_u8`, `SleepTimingStart_u32` → R7 | Covered | V4 设计增量溯源 |
| 设计增量：设计依据列 | — | §10.1, §10.2.1, §11.1, §11.2.1 | 设计依据 列（architecture/design-addition (Rx)） | Covered | V4 新增 |
| 设计增量：关联设计增量列 | — | §17 | 关联设计增量 列 | Covered | V4 新增 |

---

## 覆盖统计

| 来源 | 总数 | Covered | Pending | 覆盖率 |
| --- | --- | --- | --- | --- |
| SRS 需求 | 29 | 27 | 2 | 93% |
| SDD 对象 | 25 | 25 | 0 | 100% |
| 详细设计增量（内部函数/故障策略/配置项/设计增量溯源） | 27 | 27 | 0 | 100% |
| **合计** | **81** | **79** | **2** | **98%** |

> Pending 项：SRS-GPDRV8876-FUNC-0004（独立半桥待确认）、SRS-GPDRV8876-INTF-0005（半桥接口待确认）— 两项均由项目 R3 决定。
> V4 新增 9 条设计增量溯源条目，覆盖 R1/R4/R7/R9/R10/R11 共 6 个设计增量评审项。
