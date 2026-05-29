# Trace 追溯矩阵 — Gp_Drv8876

## Source -> Requirement Trace Matrix

| Requirement ID | Source | Trace Status |
| --- | --- | --- |
| SRS-GPDRV8876-FUNC-0001 | 原始需求-驱动名称与安全级别；Datasheet-5 引脚功能；Datasheet-7.4 器件功能模式 | Covered |
| SRS-GPDRV8876-FUNC-0002 | Datasheet-7.4.1 活动模式；Datasheet-7.4.2 低功耗睡眠模式；Datasheet-6.5 tWAKE/tSLEEP | Covered |
| SRS-GPDRV8876-FUNC-0003 | Datasheet-7.3.2 控制模式；Datasheet-表3 PH/EN 控制模式；Datasheet-表4 PWM 控制模式 | Covered |
| SRS-GPDRV8876-FUNC-0004 | Datasheet-7.3.2.3 独立半桥控制模式 | Covered |
| SRS-GPDRV8876-FUNC-0005 | Datasheet-7.3.2 控制模式；Datasheet-7.3.3.2 电流调节 | Covered |
| SRS-GPDRV8876-INTF-0001 | 原始需求-驱动名称；AURIX2G 平台规范-Init 接口模式 | Covered |
| SRS-GPDRV8876-INTF-0002 | Datasheet-7.4 器件功能模式；AURIX2G 平台规范-SetDevModeOutSig | Covered |
| SRS-GPDRV8876-INTF-0003 | AURIX2G 平台规范-GetDevModeInSig；Datasheet-7.4 器件功能模式 | Covered |
| SRS-GPDRV8876-INTF-0004 | Datasheet-表3 PH/EN 控制模式；Datasheet-表4 PWM 控制模式；AURIX2G 平台规范-SetOutput | Covered |
| SRS-GPDRV8876-INTF-0005 | Datasheet-表5 独立半桥控制模式；AURIX2G 平台规范-SetOutput | Covered |
| SRS-GPDRV8876-INTF-0006 | Datasheet-5 引脚功能 nFAULT；Datasheet-7.3.4 保护电路；AURIX2G 平台规范-GetDevFaultSig | Covered |
| SRS-GPDRV8876-INTF-0007 | Datasheet-7.3.3.1 电流检测；Datasheet-公式1/2；AURIX2G 平台规范-GetRaw | Covered |
| SRS-GPDRV8876-CFG-0001 | AURIX2G 平台规范-信号 ID 设计规范；Datasheet-5 引脚配置和功能 | Covered |
| SRS-GPDRV8876-CFG-0002 | Datasheet-表2 PMODE 功能；Datasheet-7.3.2 控制模式 | Covered |
| SRS-GPDRV8876-CFG-0003 | Datasheet-表6 IMODE 功能；Datasheet-7.3.3.2 电流调节 | Covered |
| SRS-GPDRV8876-CFG-0004 | Datasheet-6.3 建议运行条件 fPWM；AURIX2G 平台规范-MCU PWM 输出 | Covered |
| SRS-GPDRV8876-CFG-0005 | Datasheet-7.3.3.1 电流检测；Datasheet-公式1/2/3 | Covered |
| SRS-GPDRV8876-DIAG-0001 | AURIX2G 平台规范-诊断错误码设计；SRS 构建规则-DET 要求 | Covered |
| SRS-GPDRV8876-DIAG-0002 | Datasheet-5 引脚功能 nFAULT；Datasheet-7.3.4 保护电路；Datasheet-表7 故障条件汇总 | Covered |
| SRS-GPDRV8876-DIAG-0003 | Datasheet-7.3.3.2.2 逐周期电流斩波；Datasheet-表6 IMODE 功能 | Covered |
| SRS-GPDRV8876-DIAG-0004 | Datasheet-7.3.4.3 OUT 过流保护；Datasheet-表6 IMODE 功能 | Covered |
| SRS-GPDRV8876-TIM-0001 | Datasheet-6.5 tSLEEP | Covered |
| SRS-GPDRV8876-TIM-0002 | Datasheet-6.5 tWAKE | Covered |
| SRS-GPDRV8876-TIM-0003 | Datasheet-6.3 建议运行条件 fPWM | Covered |
| SRS-GPDRV8876-SAFE-0001 | 原始需求-安全级别为QM | Covered |
| SRS-GPDRV8876-SAFE-0002 | Datasheet-保护特性；原始需求-安全级别为QM | Covered |
| SRS-GPDRV8876-CODE-0001 | AURIX2G 平台规范-命名与编码规范；SRS 模板-编码规范要求 | Covered |
| SRS-GPDRV8876-RES-0001 | Datasheet-5 引脚功能；AURIX2G 平台规范-配置需求规范 | Covered |
| SRS-GPDRV8876-COMP-0001 | SRS 模板-可追溯性要求 | Covered |

## Requirement -> Verification Intent Coverage Matrix

| Requirement ID | Verification Method | Verification Stage | Coverage Status | Verification Intent |
| --- | --- | --- | --- | --- |
| SRS-GPDRV8876-FUNC-0001 | Test | UT/IT | covered | 验证初始化后默认状态、无效配置抑制输出。 |
| SRS-GPDRV8876-FUNC-0002 | Test | UT/IT | covered | 验证 nSLEEP Sleep/Active 控制和非法请求保持状态。 |
| SRS-GPDRV8876-FUNC-0003 | Test | UT/IT | covered | 验证 PH/EN 与 PWM 真值表映射。 |
| SRS-GPDRV8876-FUNC-0004 | Test | UT/IT | partial_covered | 待项目确认是否启用独立半桥。 |
| SRS-GPDRV8876-FUNC-0005 | Test | UT/IT | covered | 验证 PMODE/IMODE 重锁存顺序和等待。 |
| SRS-GPDRV8876-INTF-0001 | Test | UT | covered | 验证 Init 接口初始化配置和实例状态。 |
| SRS-GPDRV8876-INTF-0002 | Test | UT/IT | partial_covered | 待项目确认模式枚举值。 |
| SRS-GPDRV8876-INTF-0003 | Test | UT | covered | 验证 GetDevMode 返回软件请求状态。 |
| SRS-GPDRV8876-INTF-0004 | Test | UT/IT | partial_covered | 待项目确认 PWM 参数单位和范围。 |
| SRS-GPDRV8876-INTF-0005 | Test | UT/IT | partial_covered | 待项目确认接口是否交付。 |
| SRS-GPDRV8876-INTF-0006 | Test | UT/IT | covered | 验证 nFAULT 低有效故障读取。 |
| SRS-GPDRV8876-INTF-0007 | Test | UT/IT | partial_covered | 待项目确认返回原始值或换算值。 |
| SRS-GPDRV8876-CFG-0001 | Review/Test | Review/UT | partial_covered | 审查 ID 映射与资源唯一性。 |
| SRS-GPDRV8876-CFG-0002 | Review/Test | Review/UT | covered | 审查 PMODE 枚举和非法配置检测。 |
| SRS-GPDRV8876-CFG-0003 | Review/Test | Review/UT | covered | 审查 IMODE 枚举和非法配置检测。 |
| SRS-GPDRV8876-CFG-0004 | Review/Test | Review/UT | partial_covered | 待项目确认 PWM 单位和边界。 |
| SRS-GPDRV8876-CFG-0005 | Review/Test | Review/UT | partial_covered | 待项目确认电流换算策略。 |
| SRS-GPDRV8876-DIAG-0001 | Test | UT | covered | 验证开发错误检测和错误返回。 |
| SRS-GPDRV8876-DIAG-0002 | Test | UT/IT | covered | 验证 nFAULT 电平到故障位映射。 |
| SRS-GPDRV8876-DIAG-0003 | Review/Test | UT/IT | partial_covered | 待项目确认是否细分电流斩波指示。 |
| SRS-GPDRV8876-DIAG-0004 | Review/Test | UT/IT | covered | 审查软件与芯片 OCP 责任边界。 |
| SRS-GPDRV8876-TIM-0001 | Test | UT/IT | covered | 验证 Sleep 等待 >=1 ms。 |
| SRS-GPDRV8876-TIM-0002 | Test | UT/IT | covered | 验证 Active 唤醒等待 >=1 ms。 |
| SRS-GPDRV8876-TIM-0003 | Review/Test | UT/IT | covered | 验证 PWM 频率 <=100 kHz。 |
| SRS-GPDRV8876-SAFE-0001 | Review | Review | covered | 评审确认 QM 等级。 |
| SRS-GPDRV8876-SAFE-0002 | Review/Test | UT/IT | partial_covered | 通过故障注入覆盖输出误动作防护。 |
| SRS-GPDRV8876-CODE-0001 | Review/Analysis | Review | partial_covered | 待项目确认编码规范和静态检查规则。 |
| SRS-GPDRV8876-RES-0001 | Review/Analysis | Review/IT | partial_covered | 待项目确认资源预算。 |
| SRS-GPDRV8876-COMP-0001 | Review | Review | covered | 审查 Trace 文档完整性。 |

## Raw Requirement Coverage

| Raw Requirement | Covered By | Coverage Status |
| --- | --- | --- |
| 驱动名称：Gp_Drv8876 | SRS-GPDRV8876-INTF-0001；SRS-GPDRV8876-FUNC-0001 | Covered |
| 安全级别为QM | SRS-GPDRV8876-SAFE-0001；SRS-GPDRV8876-SAFE-0002 | Covered |

## ASPICE Evidence Summary

| Evidence Type | File | Status |
| --- | --- | --- |
| SRS | Gp_Drv8876_软件需求规范.md | Draft |
| Review Record | Review_Gp_Drv8876_软件需求规范.md | Generated |
| Check List | Check_Gp_Drv8876_软件需求规范.md | Generated |
| Trace Matrix | Trace_Gp_Drv8876_软件需求规范.md | Generated |

| Lifecycle Status | Count |
| --- | --- |
| Ready | 15 |
| Draft | 12 |
| Open Issue | 2 |
| Total | 29 |
