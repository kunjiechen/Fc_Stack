# Check_Gp_Drv8876_详细设计规范

**详细设计检查清单**

## 检查信息

| 属性 | 内容 |
| --- | --- |
| 被检查文档 | `Gp_Drv8876_模块详细设计规范.md` V4 |
| 检查日期 | 2026-05-27 |
| 检查依据 | `implementation-review-checklist.md` |

---

## 检查结果总表

| # | 检查类别 | 结果 | 证据/备注 |
| --- | --- | --- | --- |
| 1 | FC Identity And Scope | pass | §1：名称 Gp_Drv8876、层级 IoExtDev、职责、运行模型、多核均显式声明 |
| 2 | File Family Review | pass | §4：9 个文件完整，含 Callout.h/.c、MemMap.h、CfgData.h、Cfg.c |
| 3 | External API Review | pass | §6.1：8 个 API 均有 prototype 表、子功能拆分、执行步骤、调用关系、流程图 |
| 4 | Dependency API And Callout Review | pass | §6.3：6 个 Callout 均有 prototype、关联接口表、执行步骤、流程图 |
| 5 | Subfunction Decomposition Review | pass | 每个外部 API 均有子功能拆分表，MainFunction 拆分为 5 个子功能 |
| 6 | Single-Core / Multi-Core Review | pass | §5 "多核框架设计"：核模型、任务模型、同步点均明确 |
| 7 | State Machine Review | pass | §7：nSLEEP 时序状态机 5 状态，含设计选型说明（芯片硬件状态机方案）、状态定义、切换表、主流程图 |
| 8 | Internal Function Review | pass | §6.2：9 个内部函数全部按外部接口格式逐一展开，含原型表、子功能拆分、执行步骤、调用关系表、流程图 |
| 9 | DET Review | pass | §8：6 个检查点，含触发条件、记录方式、返回策略、适用 API |
| 10 | Fault Handling Review | pass | §9：故障分类（芯片/驱动逻辑）+确认策略（单次/连续多次）+恢复策略（不可恢复/连续多次自恢复）+锁存清除+自恢复配置+运行参数；4 个故障项含 15 列完整属性 |
| 11 | 运行参数设计 Review | pass | §10：10.1 运行变量（7 个，含故障计数器，字段名带类型后缀）+10.2 运行参数类型（含字段类型列） |
| 12 | 配置参数设计 Review | pass | §11：11.1 配置宏参（10 个，含故障自恢复/确认/恢复阈值）+11.2 配置类型（含字段类型列和类型后缀命名，Source 列标注 architecture/design-addition） |
| 13 | Design-Addition Provenance Review | pass | §10.1/§10.2.1/§11.1/§11.2.1 均有 设计依据 列；所有 design-addition 项均标注 (Rx) 格式；§17 含 关联设计增量 列且 R9-R11 逐项列出关联对象；无裸 design-addition 标签 |
| 14 | MemMap / NoClear Review | pass | §12：4 个段，CODE/CLEAR/CONST per-core/CONST global |
| 15 | Flowchart Review | pass | 25 个流程图（8 个外部 API + 9 个内部函数 + 6 个 Callout + 状态机 + 故障确认状态机），节点均以步骤描述呈现 |
| 16 | Coding-Readiness Review | pass | 开发者可直接建文件骨架、stub API、声明运行时数组、定义状态机、实现故障确认/恢复逻辑 |

---

## 详细检查记录

### 1. FC Identity And Scope — pass

- FC 名称：`Gp_Drv8876` ✓
- 软件层级：`IoExtDev` ✓
- 核心职责：中文完整段落 ✓
- 运行模型：异步请求-周期处理（混合）✓
- 单核/多核：多核 ✓

### 2. File Family Review — pass

- 必需文件 9 个均列出 ✓
- `Callout.h/.c` 存在（硬件适配需抽象）✓
- `CfgData.h` + `Cfg.c` 存在（配置类型需实例化）✓
- `MemMap.h` 存在 ✓

### 3. External API Review — pass

- 8 个 API 均有完整 prototype 表 ✓
- sync/async 和 reentrancy 标注 ✓
- return value 语义清晰 ✓
- 每个 API 均有子功能拆分表 ✓
- 每个 API 均有执行步骤有序列表 ✓
- 每个 API 均有调用关系表（类别支持 内部函数/依赖接口）✓
- 每个 API 均有流程图 ✓

### 4. Dependency API And Callout Review — pass

- 6 个 Callout 均有 prototype 表 ✓
- 每个 Callout 均标注 implemented by ✓
- 每个 Callout 均有关联接口表（调用方+类别+场景）✓
- 每个 Callout 均有执行步骤和流程图 ✓
- 延迟 Callout（CalloutDelayUs）已生成 ✓

### 5. Subfunction Decomposition Review — pass

- 子功能步骤反映实际实现顺序 ✓
- cfg/runtime/DET/fault/callout 逻辑位置明确 ✓
- 调用关系表体现实际调用链 ✓

### 6. Multi-Core Review — pass

- §5 标题为"多核框架设计"（动态标题规则）✓
- 每核职责、Init 入口、周期任务、运行时数据均明确 ✓
- 同步点表列出所有共享对象 ✓
- 运行时数据完全隔离，跨核共享仅限于 const ✓

### 7. State Machine Review — pass

- nSLEEP 时序状态机：5 状态 ✓
- 设计选型明确（芯片硬件状态机方案）✓
- 状态定义含含义、进入条件、退出条件 ✓
- 切换表含条件函数和动作函数 ✓
- 主流程图完整 ✓

### 8. Internal Function Review — pass

- 9 个内部函数全部按外部接口格式逐一展开 ✓
- 每个函数含：原型表、子功能拆分、执行步骤、调用关系表、流程图 ✓
- 均为 `static` 作用域 ✓
- 每个函数标注触发点和依赖接口（不调用依赖的标注 N/A）✓
- 调用关系表类别列正确区分 依赖接口 / 内部函数 ✓
- 简单函数（CheckInitId、GetRumtime、GetCfgData、CheckInstanceActive）无缩减 ✓

### 9. DET Review — pass

- 6 个检查点覆盖未初始化、无效 ID、空指针、参数非法、PWM 非法、配置不可用 ✓
- 记录方式明确（DET 上报或内部标志）✓
- 返回策略明确（E_NOT_OK）✓
- 与 Fault 明确分离 ✓

### 10. Fault Handling Review — pass

- 故障分类：芯片故障（nFAULT）+ 驱动逻辑故障（DIO/ADC/Callout/配置错误）✓
- 确认策略：单次确认 / 连续多次，各有策略说明表 ✓
- 恢复策略：不可恢复 / 连续多次自恢复，自恢复含配置宏参 ✓
- 锁存与清除：明确 Init 清除为唯一方式，标注无故障清除接口约束 ✓
- 自恢复配置：FAULT_SELF_RECOVERY_ENABLE + CONFIRM_THRESHOLD + RECOVERY_THRESHOLD ✓
- 故障项设计表含 15 列完整属性 ✓
- 故障相关运行参数 4 个（确认计数器、恢复计数器、位掩码、锁存标志）✓

### 11. 运行参数设计 Review — pass

- 10.1 运行变量表含变量名、类别、类型、Core、读写方、生命周期、MemMap、NoClear ✓
- 变量名携带类型后缀（_b/_u8/_u32 等）✓
- 新增 4 个故障相关变量（FaultConfirmCnt_u8 / FaultRecoveryCnt_u8 / FaultBitmask_u32 / FaultLatched_b）✓
- 10.2 运行参数类型定义：GlobalRuntimeType / InstanceRuntimeType / FaultRuntimeType / MonitorRuntimeType ✓
- 10.2.1 含字段类型列（uint8/uint16/uint32/boolean）✓
- 关键字段名含类型后缀，与字段类型列对应 ✓
- 至少一个全局运行参数类型 ✓
- 拆分按语义边界 ✓

### 12. 配置参数设计 Review — pass

- 11.1 配置宏参：10 个宏，新增故障自恢复/确认/恢复阈值 ✓
- 11.2 配置类型：5 个类型，含字段类型列和类型后缀命名 ✓
- 字段类型列显式标注 C 标准类型（uint8/uint16/uint32/指针类型）✓
- TimingConfigType 新增 FaultConfirmThreshold_u8 和 FaultRecoveryThreshold_u8 ✓
- 配置类型实例化表（Cfg.c 中的 const 对象）✓
- Source 标注（architecture/coding-standard/design-addition (Rx)）✓

### 13. Design-Addition Provenance Review — pass

- §10.1 运行变量表含 设计依据 列，所有行标注 architecture 或 design-addition (Rx) ✓
- §10.2.1 运行参数类型表含 设计依据 列，所有字段标注 architecture 或 design-addition (Rx) ✓
- §11.1 配置宏参表 design-addition 项均使用 design-addition (Rx) 格式 ✓
- §11.2.1 配置类型表含 设计依据 列，所有字段标注 architecture 或 design-addition (Rx) ✓
- §17 风险表含 关联设计增量 列，R9-R11 逐项列出关联对象名 ✓
- 无裸 design-addition（不含 Rx 后缀）标签 ✓
- design-addition 项在 §17 中均有对应风险项解释"为何需要"和"不采纳后果" ✓
- 设计增量与评审项形成"标注→评审项→关闭"闭环 ✓

### 14. MemMap / NoClear Review — pass

- 4 个段定义 ✓
- CODE/CLEAR/CONST per-core/CONST global 划分清晰 ✓
- NoClear 审慎使用：当前无 NoClear 数据 ✓

### 15. Flowchart Review — pass

- 16 个流程图覆盖所有外部 API、关键内部流和 Callout ✓
- 节点标签均为步骤描述 ✓
- 无变量名、数组下标、寄存器名、条件表达式 ✓
- 流程图与步骤表对齐 ✓

### 16. Coding-Readiness Review — pass

- 可立即创建 9 个文件骨架 ✓
- API 可 stub 而不需猜测 ✓
- cfg 对象可直接声明 ✓
- 运行时数组可直接定义 ✓
- 状态机可直接实现 ✓
- 故障处理可直接编码 ✓

---

## 主要问题

无阻断项。13 个 pending-confirm 项均为项目级配置/策略确认（默认状态、PWM 单位、去抖阈值、故障确认/自恢复/锁存策略、驱动逻辑故障响应等），不影响编码骨架搭建。V4 新增设计增量溯源检查（第 13 项），所有 design-addition 项已严格关联 §17 评审项。

## 下一步动作

1. 项目评审 R1-R13 待确认项（R9-R11 为设计增量溯源项，R12-R13 为故障处理策略项）
2. 确认后更新 §10/§11 中的 pending-confirm 状态为 formal，关闭 §17 对应评审项
3. 编码起步按 §15 推荐顺序执行
