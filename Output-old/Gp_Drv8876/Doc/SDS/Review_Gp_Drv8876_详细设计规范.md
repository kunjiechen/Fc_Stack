# Review_Gp_Drv8876_详细设计规范

**详细设计评审记录**

## 评审信息

| 属性 | 内容 |
| --- | --- |
| 被评审文档 | `Gp_Drv8876_模块详细设计规范.md` V4 |
| 评审日期 | TBD |
| 评审人 | TBD |
| 评审依据 | `implementation-review-checklist.md` |

---

## 1. 评审结论

| 项目 | 结论 |
| --- | --- |
| 是否允许进入编码 | **待评审决定** — formal 设计项已完备，pending-confirm 项需项目确认 |
| 阻断项 | 0 |
| 重要遗漏 | 0 |
| 待确认项 | 13（R1-R13，含设计增量溯源项 R9-R11 及故障处理策略项 R12-R13） |

---

## 2. 风险关闭记录

| 索引 | 风险项 | 状态 | 关闭条件 | 关闭日期 | 评审人 |
| --- | --- | --- | --- | --- | --- |
| R1 | 默认安全状态 | 待评审 | 项目确认默认模式 | TBD | TBD |
| R2 | PMODE/IMODE 控制方式 | 待评审 | 确认 DIO/硬件固定 | TBD | TBD |
| R3 | 独立半桥启用 | 待评审 | 确认是否编译 | TBD | TBD |
| R4 | PWM 参数单位与范围 | 待评审 | 项目提供单位/范围 | TBD | TBD |
| R5 | 电流反馈形态 | 待评审 | 确认原始值/mA | TBD | TBD |
| R6 | nFAULT 故障位定义 | 待评审 | 提供 bit 定义 | TBD | TBD |
| R7 | Delay Callout 必要性 | 待评审 | 确认调度周期 | TBD | TBD |
| R8 | 去抖阈值 | 待评审 | 确认去抖次数 | TBD | TBD |
| R9 | nFAULT 故障连续确认策略 | 待评审 | 确认连续确认次数阈值（默认 3）；不采纳则故障判定退化为单次采样。关联设计增量：`FaultConfirmCnt_u8`, `FaultConfirmThreshold_u8`, `CFG_FAULT_CONFIRM_THRESHOLD` | TBD | TBD |
| R10 | nFAULT 故障自恢复策略 | 待评审 | 确认是否使能自恢复及恢复次数阈值（默认 3）；不使能则故障锁存直至 Init 清除。关联设计增量：`FaultRecoveryCnt_u8`, `FaultRecoveryThreshold_u8`, `CFG_FAULT_SELF_RECOVERY_ENABLE`, `CFG_FAULT_RECOVERY_THRESHOLD` | TBD | TBD |
| R11 | nFAULT 故障锁存标志 | 待评审 | 确认锁存标志是否需要（自恢复未使能时保持故障状态）。关联设计增量：`FaultLatched_b` | TBD | TBD |
| R12 | 驱动逻辑故障响应 | 待评审 | DIO/ADC Callout 失败时降级策略确认 | TBD | TBD |
| R13 | 配置错误实例隔离 | 待评审 | 确认单实例配置错误是否影响其他实例 | TBD | TBD |

---

## 3. 设计亮点

- 8 个外部 API 均具子功能拆分、执行步骤、调用关系表和流程图，无一缩减。
- 9 个内部函数全部按外部接口格式逐一完整展开（原型表+子功能拆分+执行步骤+调用关系表+流程图）。
- MainFunction 调用关系表同时列出依赖接口和内部函数，正确反映外部 API 直调依赖接口的灵活调用链。
- 多核框架含框架说明、核模型、任务模型、同步点，运行时数据完全隔离。
- nSLEEP 时序状态机（5 状态，芯片硬件状态机方案），含设计选型说明。
- 故障处理覆盖芯片故障和驱动逻辑故障，每项明确确认策略、恢复策略、锁存语义和清除方式。
- 故障自恢复可配置（CFG_FAULT_SELF_RECOVERY_ENABLE），支持连续多次确认/恢复计数。
- 运行参数和配置参数按变量清单+类型布局双维度设计，字段名携带类型后缀且含字段类型列。
- V4 新增设计增量溯源：运行变量/配置类型/运行参数类型均标注设计依据（architecture/design-addition (Rx)），design-addition 项强制关联 §17 评审项并列出关联设计增量对象，形成"标注→评审项→关闭"闭环。
