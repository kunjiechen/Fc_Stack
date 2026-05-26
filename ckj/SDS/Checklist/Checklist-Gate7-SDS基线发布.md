# Gate 7 SDS基线发布检查清单

## 1 检查目标

确认 SDS 评审、问题闭环、过程记录、追溯矩阵和发布结论完整，满足基线化并进入 Coding 的条件。

## 2 适用阶段

SDS 技术检查和 CodingReady 检查通过后、正式基线发布前。

## 3 基线发布检查

| 序号 | 检查对象 | 检查项 | 通过标准 | 结果 | 问题记录 |
| --- | --- | --- | --- | --- | --- |
| G7-01 | SDS 文档 | 是否形成正式评审版本 | SDS 状态为 Review/Ready/Baselined 的受控版本 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-02 | DataDict | 是否形成正式数据字典 | DataDict 与 SDS 版本一致，内容完整可用 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-03 | 追溯矩阵 | 是否完成 SDD → SDS 追溯 | 关键 SDD 设计项均可追溯到 SDS | [ ] Pass [ ] Fail [ ] N/A | |
| G7-04 | Code 入口 | 是否完成 SDS → Code 入口 | 每个关键 SDS ID 均有代码对象入口 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-05 | UT 入口 | 是否完成 SDS → UT 入口 | 每个关键 SDS 项均有 UT 入口或覆盖说明 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-06 | Operation Steps | 是否生成实际操作步骤 | `Operation_Steps_SDS_[FC].md` 已生成并可复现过程 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-07 | CHECK 清单 | 是否生成 SDS CHECK 清单 | `CHECK_SDS_[FC].md` 已生成且覆盖 Gate 1~Gate 7 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-08 | Review 记录 | 是否形成评审记录 | `Review_SDS_[FC].md` 已记录结论、问题和遗留风险 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-09 | 问题闭环 | 阻塞问题是否关闭 | 所有 Blocker 已关闭；遗留风险已批准 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-10 | 开放项 | Open 项是否已评估影响 | 每个 Open 项已说明是否阻塞 Coding 和关闭条件 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-11 | 输出归档 | 输出物是否同路径归档 | SDS、DataDict、Trace、Review、Operation Steps、CHECK 清单归档一致 | [ ] Pass [ ] Fail [ ] N/A | |
| G7-12 | 发布结论 | 是否给出明确结论 | 已明确是否允许进入 Coding、批准人和日期 | [ ] Pass [ ] Fail [ ] N/A | |

## 4 不通过处理

| 问题类型 | 处理要求 |
| --- | --- |
| 过程记录缺失 | 补齐 Operation Steps、CHECK 或 Review 记录 |
| 追溯缺失 | 补齐 Trace 和下游入口 |
| 阻塞问题未关 | 不得基线发布，先关闭或批准遗留 |
| 输出散落 | 统一归档到 SDS 输出路径 |

## 5 Gate 结论

```text
Gate 7 SDS基线发布：通过 / 不通过 / 有条件通过

阻塞问题：
批准遗留项：
基线版本：
是否允许进入Coding：是 / 否
批准人：
日期：
```
