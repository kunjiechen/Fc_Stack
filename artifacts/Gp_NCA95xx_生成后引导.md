# Post-Generation Guide — Gp_NCA95xx

## 生成结果摘要

- **SRS 文件**：`artifacts/SRS_Gp_NCA95xx.md`
- **需求总数**：36 条
- **当前状态**：全部 `Draft`
- **待补充输入**：[Input_Manifest_Gp_NCA95xx.md](artifacts/Input_Manifest_Gp_NCA95xx.md)
- **开放项**：[Open_Items_Gp_NCA95xx.md](artifacts/Open_Items_Gp_NCA95xx.md)

## 需求分布

| 类别 | 数量 | ID 范围 |
| --- | --- | --- |
| 功能需求（FUNC） | 4 | 0001 - 0004 |
| 接口需求（INTF） | 6 | 0001 - 0006 |
| 配置需求（CFG） | 7 | 0001 - 0007 |
| 诊断需求（DIAG） | 4 | 0001 - 0004 |
| 时序需求（TIM） | 5 | 0001 - 0005 |
| 安全需求（SAFE） | 3 | 0001 - 0003 |
| 编码需求（CODE） | 3 | 0001 - 0003 |
| 资源需求（RES） | 2 | 0001 - 0002 |
| 过程需求（COMP） | 2 | 0001 - 0002 |

## 当前输入完整度：L1

仅有 Datasheet，缺少项目需求文档和原始需求。所有需求条目均为 `Draft` 状态等待项目确认。

## 下一步可执行动作

请选择以下动作之一：

1. **补原始需求** — 提供项目需求文档或口头需求，我帮你整理到 `Original_Requirement_Pack_Gp_NCA95xx.md`
2. **补来源资料** — 提供硬件原理图 / I2C 通道分配 / 引脚连接方案
3. **逐类评审 SRS** — 按 FUNC → INTF → CFG → DIAG → SAFE → TIM → RES → CODE → COMP 的顺序逐类确认
4. **先确认阻断项** — 优先处理 [Open Items](artifacts/Open_Items_Gp_NCA95xx.md) 中的 6 个阻断项
5. **保持 Draft，继续补料** — 当前 SRS 方向正确，等待更多输入后重新生成

## 建议优先级

当前最关键的确认事项（按优先级）：

1. RESET 引脚归属 → 决定是否需要 ResetChip 接口
2. INT 引脚连接方案 → 决定 MainFunction 是中断轮询还是全量轮询
3. 芯片实例数量和 I2C 地址 → 决定配置结构体规模
4. 各 I/O 引脚用途和方向 → 决定默认配置表
5. 安全关键输出列表 → 决定回读校验范围

## 对话框引导

当你说“要调整”时，请指明调整类型：

1. `补原始需求` — 修改或补充升级点/任务目标
2. `补来源资料` — 新增 datasheet 章节、硬件原理图、项目约束
3. `修改需求表达` — 某条需求描述不清、分类错误、字段缺失
4. `转 Open Item` — 当前无法确认，先挂起
