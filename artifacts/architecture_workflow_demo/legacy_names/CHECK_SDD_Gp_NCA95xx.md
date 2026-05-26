# CHECK_SDD_Gp_NCA95xx

- **Module**: `Gp_NCA95xx`
- **Architecture Version**: V1
- **Architecture Status**: Draft

| Gate | Check Item | Result | Evidence | Main Issue | Next Action |
| --- | --- | --- | --- | --- | --- |
| Gate1 | 输入充分性检查 | 不通过 | requirement_input / coverage_result / input index | 未绑定明确 SRS 输入，当前更像 seed-driven draft。 | 补齐 SRS 路径并重新确认输入充分性。 |
| Gate2 | 模块边界与职责检查 | 通过 | external_apis / dependency_apis / file_items / layer | 无 | 进入详细架构设计。 |
| Gate3 | 接口配置运行态完整性检查 | 通过 | external_apis / config_macros / runtime_states / memmap_sections | 无 | 进入追溯和评审。 |
| Gate4 | SRS 到 SDD 追溯检查 | 不通过 | coverage_result / Trace_SRS_SDD | 缺少 coverage_result。 | 先建立 SRS coverage_result。 |
| Gate5 | 风险与评审闭环检查 | 条件通过 | risk_items / release_gate warning-blocking split | 仍有待评审或待修改风险项。 | 在 Review_SDD 中关闭或接受遗留风险。 |
| Gate6 | 实现就绪性检查 | 条件通过 | implementation_constraints / release gate proof | 仍有 release blocker，暂不建议进入 SDS。 | 条件进入 SDS，持续跟踪 blocker。 |
| Gate7 | 架构基线发布检查 | 条件通过 | release_gate / rule_evidence / grounding_evidence | architecture_status 不是 Released; output_mode 不是 Released; 缺少 module-family grounding_evidence | 保持 Draft/Formal Draft，优先清理 pending_confirm/reserved/open risk，补齐 formal 对象证据后再申请 Released。 |
