# Gate 7 SDD 基线发布检查清单

## 1 检查目标

确认 SDD 发布前所有门禁、评审问题、开放项、追溯、交付物和发布条件已闭环，使 SDD 可作为 SDS、Coding、IT 和 ST 的正式输入基线。

## 2 适用阶段

SDD 评审完成后、基线发布前。

## 3 基线发布检查

| 序号 | 检查类别 | 检查项 | 通过标准 | 结果 | 问题记录 |
| --- | --- | --- | --- | --- | --- |
| G7-01 | Gate 汇总 | Gate 1 是否通过 | 架构输入完整性通过或有批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-02 | Gate 汇总 | Gate 2 是否通过 | SRS 覆盖与追溯通过或有批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-03 | Gate 汇总 | Gate 3 是否通过 | 架构内容完整性通过或有批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-04 | Gate 汇总 | Gate 4 是否通过 | 架构技术正确性通过或有批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-05 | Gate 汇总 | Gate 5 是否通过 | 通用化与集成边界通过或有批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-06 | Gate 汇总 | Gate 6 是否通过 | SDS 输入充分性通过或有批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-07 | SDD 文档 | SDD 文档是否完整 | `SDD_[FC_SHORT_NAME].md` 已生成，章节完整，版本和状态明确 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-08 | 追溯矩阵 | SRS-SDD 追溯是否发布 | `Trace_SRS_SDD_[FC_SHORT_NAME].md` 或等效章节已同步 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-09 | 接口输出 | InterfaceSpec 是否发布或并入 SDD | API、参数、返回值、同步/异步和错误处理已归档 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-10 | 时序输出 | TimingSpec 是否发布或并入 SDD | 周期、响应时间、超时、调度模型已归档 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-11 | 状态机输出 | StateMachine 是否发布或并入 SDD | 状态集合、转移表、状态机图和异常路径已归档 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-12 | 安全输出 | SafetyDesign 是否发布或并入 SDD | 安全机制、响应、降级、安全状态和验证入口已归档 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-13 | 架构决策 | 架构决策记录是否归档 | 关键取舍、无来源风险处理、通用化边界和遗留项已记录 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-14 | 操作步骤 | 实际操作步骤是否生成 | `Operation_Steps_SDD_[FC_SHORT_NAME].md` 已生成并同目录归档 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-15 | CHECK 清单 | SDD CHECK 清单是否生成 | `CHECK_SDD_[FC_SHORT_NAME].md` 已汇总 Gate 1 至 Gate 7 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-16 | 输出路径 | 发布文件是否路径一致 | SDD、Trace、Review、Operation Steps、CHECK 等在同一输出路径或索引明确 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-17 | 评审记录 | 评审记录是否完整 | `Review_SDD_[FC_SHORT_NAME].md` 包含问题、结论、责任人、关闭状态 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-18 | 问题闭环 | 评审问题是否关闭 | 所有 Fail 项和评审问题已关闭或批准遗留 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-19 | 开放项 | 开放项是否管理 | Open 项有影响分析、责任人、关闭条件、是否阻塞 SDS 结论 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-20 | 遗留批准 | 遗留风险是否批准 | 未关闭但允许发布的风险有批准人、理由和关闭计划 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-21 | 版本状态 | 文档版本和状态是否明确 | 版本、日期、编制人、评审/批准人、发布状态完整 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-22 | 变更影响 | 若 SRS 有回写问题是否同步 | SRS 问题、需求变更或开放项已同步到相关记录 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-23 | 下游通知 | 是否明确下游使用条件 | SDS 可使用的基线版本、遗留限制和禁止假设项明确 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-24 | 发布结论 | 是否形成发布结论 | 是否允许进入 SDS、限制条件、批准人和日期明确 | [ ] Pass [ ] Fail [ ] N/A | |

## 4 不允许基线发布的情形

存在以下情形时，不允许 SDD 基线发布：

- Gate 1 至 Gate 6 存在未批准 Fail 项。
- 有效 SRS 未覆盖且无 N/A 或开放项说明。
- 高影响开放项影响 SDS 但未关闭或未批准遗留。
- SDD 文档缺少接口、状态、配置、安全或错误处理关键设计。
- 安全相关问题未经过安全评审或批准。
- 操作步骤和 CHECK 清单未生成或未与 SDD 同路径归档。
- 发布版本、评审人、批准人或日期缺失。

## 5 发布包建议清单

| 文件 | 必需性 | 说明 |
| --- | --- | --- |
| `SDD_[FC_SHORT_NAME].md` | 必需 | 软件架构设计规范 |
| `Trace_SRS_SDD_[FC_SHORT_NAME].md` | 必需 | SRS 到 SDD 追溯矩阵 |
| `Review_SDD_[FC_SHORT_NAME].md` | 必需 | SDD 评审记录 |
| `Operation_Steps_SDD_[FC_SHORT_NAME].md` | 必需 | 实际操作步骤记录 |
| `CHECK_SDD_[FC_SHORT_NAME].md` | 必需 | SDD 门禁检查汇总 |
| `Architecture_Input_Index_[FC_SHORT_NAME].md` | 建议 | 架构输入索引 |
| `Architecture_Decision_[FC_SHORT_NAME].md` | 建议 | 架构决策记录 |
| `InterfaceSpec_[FC_SHORT_NAME].md` | 可选 | 若接口内容未完整并入 SDD，则独立输出 |
| `TimingSpec_[FC_SHORT_NAME].md` | 可选 | 若时序内容未完整并入 SDD，则独立输出 |
| `StateMachine_[FC_SHORT_NAME].md` | 可选 | 若状态机内容未完整并入 SDD，则独立输出 |
| `SafetyDesign_[FC_SHORT_NAME].md` | 可选 | 若安全机制内容未完整并入 SDD，则独立输出 |

## 6 Gate 结论

```text
Gate 7 SDD 基线发布：通过 / 不通过 / 有条件通过

Gate 1-6 结论：
未关闭问题：
批准遗留项：
发布包缺失项：
基线版本：
是否允许进入 SDS：是 / 否
评审人：
批准人：
日期：
```
