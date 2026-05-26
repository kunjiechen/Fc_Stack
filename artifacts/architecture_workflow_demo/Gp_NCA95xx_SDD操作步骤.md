# Gp_NCA95xx SDD操作步骤

- **Module**: `Gp_NCA95xx`
- **Document File**: `Gp_NCA95xx_SDD操作步骤.md`
- **Freeze Bundle**: `.claude/skills/fc-architecture-workbench/demo-lib/summaries/Gp_NCA95xx.arch.json`
- **Architecture Version**: V1

## 1. 本次执行步骤

1. 收集架构输入并建立 `Gp_NCA95xx_架构输入索引.md`。
2. 基于 architecture seed 构建 freeze bundle，冻结正式对象、保留对象和待确认对象。
3. 渲染正式架构文档 `Gp_NCA95xx_软件架构设计.md`，并同步生成 `Gp_NCA95xx_需求架构追溯.md`。
4. 运行 release gate 评估，确认 pending_confirm、reserved、risk 和 rule_evidence 完整性。
5. 输出 `Gp_NCA95xx_SDD检查清单.md`、`Gp_NCA95xx_架构评审记录.md`、`Gp_NCA95xx_SDD基线总结.md`，用于人工评审和阶段归档。

## 2. 本次关键判断

- 覆盖条目数: 0
- 风险条目数: 2
- Release Ready: No
- 推荐下一步: 保持 Draft/Formal Draft，优先清理 pending_confirm/reserved/open risk，补齐 formal 对象证据后再申请 Released。

## 3. 本次建议动作

- 优先处理: architecture_status 不是 Released
- 优先处理: output_mode 不是 Released
- 优先处理: 缺少 module-family grounding_evidence
