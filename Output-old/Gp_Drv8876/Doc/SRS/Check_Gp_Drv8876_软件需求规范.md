# Check 需求检查清单 — Gp_Drv8876

**模块**: Gp_Drv8876  
**文档**: Gp_Drv8876_软件需求规范.md  
**检查时间**: 2026-05-27 13:55  
**状态**: Draft

## 1 检查总览

| 检查域 | 结论 | 说明 |
| --- | --- | --- |
| 文件完整性 | Pass | SRS、Review、Check、Trace 已生成。 |
| 命名规范 | Pass | 正式 SRS 文件名为 `Gp_Drv8876_软件需求规范.md`。 |
| 需求 ID | Pass | 29 条需求 ID 唯一，按类型分组。 |
| 来源追溯 | Pass | 每条需求均有来源标签，Trace 已同步。 |
| 需求类别覆盖 | Pass | 覆盖 FUNC、INTF、CFG、DIAG、TIM、SAFE、CODE、RES、COMP。 |
| 接口定义 | Conditional | 已定义主要接口；半桥、电流换算和 MainFunction 待项目确认。 |
| 配置定义 | Conditional | 已定义实例、PMODE、IMODE、PWM、电流反馈配置；部分默认值待确认。 |
| 诊断定义 | Conditional | 已定义 DET、nFAULT 和 OCP 边界；故障细分待确认。 |
| 时序定义 | Pass | 已定义 tSLEEP、tWAKE 和 PWM 100 kHz 边界。 |
| 非功能需求 | Conditional | QM 已明确；编码规范和资源预算待项目补充。 |

## 2 需求类别明细

| 类别 | 数量 | 检查结论 |
| --- | --- | --- |
| FUNC | 5 | Pass |
| INTF | 7 | Conditional |
| CFG | 5 | Conditional |
| DIAG | 4 | Conditional |
| TIM | 3 | Pass |
| SAFE | 2 | Conditional |
| CODE | 1 | Conditional |
| RES | 1 | Conditional |
| COMP | 1 | Pass |
| Total | 29 | Conditional |

## 3 检查项明细

| 检查ID | 检查项 | 结果 | 说明 |
| --- | --- | --- | --- |
| C1 | 是否包含目的、范围、定义、概述、需求、风险、来源和附录 | Pass | SRS 章节完整。 |
| C2 | 每条需求是否有 ID、类别、安全等级、验证方式、状态和来源 | Pass | 29 条需求均具备状态标签行。 |
| C3 | 是否避免将芯片能力直接写成软件责任 | Pass | 多处以范围边界说明芯片内部保护和硬件能力。 |
| C4 | 是否定义外部接口 | Pass | Init、Set/Get Mode、Set Output、Get Fault、Get CurrentRaw 已定义。 |
| C5 | 接口失败后置条件是否明确 | Pass | 接口需求均说明 E_NOT_OK 或不写输出参数/保持原状态。 |
| C6 | 是否定义配置范围和非法配置处理 | Conditional | PMODE/IMODE 明确；默认状态和 PWM 单位待确认。 |
| C7 | 是否定义诊断读取接口 | Pass | `Gp_Drv8876_GetDevFaultSig` 已定义。 |
| C8 | 是否定义 DET 或等效开发错误检测 | Pass | SRS-GPDRV8876-DIAG-0001 已定义。 |
| C9 | 是否定义时序数值 | Pass | tSLEEP >=1 ms、tWAKE >=1 ms、PWM <=100 kHz。 |
| C10 | 安全等级是否来自原始需求 | Pass | QM 已追溯到用户原始需求。 |
| C11 | 是否存在 Open Issue | Conditional | 2 条需求为 Open Issue，6 个风险项待评审。 |
| C12 | 是否可进入 SDD | Conditional | 可进入草稿设计，基线前需关闭或批准遗留项。 |

## 4 问题闭环表

| 问题ID | 类型 | 描述 | 责任方 | 关闭条件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| CHK-001 | 项目决策 | 初始化默认安全状态未确认。 | 项目/系统工程师 | 明确 Sleep/Coast/Brake 默认值。 | Open |
| CHK-002 | 项目决策 | 支持控制模式和半桥接口范围未确认。 | 项目/软件架构 | 明确支持模式清单。 | Open |
| CHK-003 | 项目决策 | PWM 参数单位和边界未确认。 | 软件架构/集成 | 明确单位、范围、空闲状态。 | Open |
| CHK-004 | 项目决策 | IPROPI 返回原始值或换算值未确认。 | 软件架构/测试 | 明确接口输出单位。 | Open |
| CHK-005 | 项目决策 | nFAULT 故障细分策略未确认。 | 系统/诊断 | 明确故障位掩码定义。 | Open |
| CHK-006 | 架构决策 | 是否需要 MainFunction 未确认。 | 软件架构 | 明确同步或周期调度策略。 | Open |

## 5 发布包完整性

| 文件 | 状态 |
| --- | --- |
| Gp_Drv8876_软件需求规范.md | Present |
| Review_Gp_Drv8876_软件需求规范.md | Present |
| Check_Gp_Drv8876_软件需求规范.md | Present |
| Trace_Gp_Drv8876_软件需求规范.md | Present |

## 6 发布结论

当前需求包结论为 **Conditional**。建议作为 SDD 草稿输入使用；若要发布为需求基线，应先关闭 CHK-001 至 CHK-006，或由项目评审批准遗留。
