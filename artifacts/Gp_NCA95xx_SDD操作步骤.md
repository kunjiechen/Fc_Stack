# Gp_NCA95xx 架构操作步骤

## 1. 说明

本文档描述 `Gp_NCA95xx_软件架构设计.md` V1 Draft 的使用方式，包括如何评审、如何基于架构推进详细设计和编码实现，以及后续阶段的衔接。

## 2. 当前状态

- 架构版本: V1
- 架构状态: Draft
- 待评审项: R1-R7 + R-OTHER

## 3. 操作流程

### 步骤 1：架构评审

**目标**: 完成风险表评审，将架构状态从 Draft 推进到 Released。

**操作方式 A**（推荐）：直接编辑 `Gp_NCA95xx_软件架构设计.md` 第 10 章风险表。

1. 打开 `artifacts/Gp_NCA95xx_软件架构设计.md`
2. 找到第 10 章「架构风险与待确认」
3. 逐项评审 R1-R7，将 `状态` 改为 `已评审` 或 `待修改`
4. 在 `备注` 列填写确认意见或修改要求
5. 评审 R-OTHER 并填写

**操作方式 B**：在当前聊天窗口回复。

示例回复格式：
```
R1、R2、R3 已评审
R4 待修改，备注：不需要运行时方向变更，保持 STD_OFF
R5 待修改，备注：恢复后重新回写所有配置寄存器
R-OTHER 已评审，备注：无其他建议
```

**发布条件**: 所有 R1-R7 和 R-OTHER 均为 `已评审` 状态。

**发布操作**: 联系架构工程师将状态从 `Draft` 改为 `Released`（不升级版本号，保持 V1）。

### 步骤 2：详细设计

**前置条件**: 架构状态为 `Released`。

**输入**: `Gp_NCA95xx_软件架构设计.md` V1 Released + `Gp_NCA95xx_软件需求规范.md`

**详细设计应覆盖**:
- 每个外部接口的内部实现流程（伪代码/活动图）
- 状态机完整跳转逻辑和边界条件
- 每核运行态容器的结构体定义（C 代码级）
- I2C 寄存器读写序列（含错误处理路径）
- DET 检查点的具体实现
- 回读校验的完整 retry 流程
- 配置数据结构的 C 定义
- Callout stub 的默认实现骨架
- 单元测试用例设计

### 步骤 3：编码实现

**前置条件**: 详细设计完成 + 架构 Released。

**输入**: 详细设计文档 + 架构文档

**按以下顺序创建文件**:

1. `Gp_NCA95xx_Reg.h` — 寄存器地址和位定义（纯常量，无依赖）
2. `Gp_NCA95xx_Cfg.h` — 配置宏参（依赖 Std_Types.h 和 Reg.h）
3. `Gp_NCA95xx_Types.h` — 类型和枚举定义（依赖 Cfg.h）
4. `Gp_NCA95xx_CfgData.h` — 配置数据声明（依赖 Types.h）
5. `Gp_NCA95xx_Callout.h` — Callout 原型（依赖 Types.h）
6. `Gp_NCA95xx.h` — 外部接口声明（依赖 CfgData.h）
7. `Gp_NCA95xx_MemMap.h` — MemMap 段宏
8. `Gp_NCA95xx_Cfg.c` — 配置数据定义（依赖 CfgData.h + MemMap.h）
9. `Gp_NCA95xx.c` — 主体实现（依赖 .h + Callout.h + MemMap.h）
10. `Gp_NCA95xx_Callout.c` — Callout stub（依赖 Callout.h + MemMap.h）

### 步骤 4：单元测试

**前置条件**: 编码实现完成。

**针对每个外部接口编写 UT**:
- Init: 正常初始化 / 多芯片 / 部分失败 / I2C NACK
- MainFunction: INT 触发刷新 / 全量轮询降级 / 状态跳转 / 故障累计
- GetGpioInSig: 正常读取 / 无效 Id / NULL 指针 / 极性反相 / 芯片 Fault
- SetGpioOutSig: 正常设置 / 无效 Id / 非法 State / 引脚为输入 / I2C 失败
- GetDevFaultSig: 正常读取 / 无效 Id / NULL 指针 / 故障位掩码
- GetDevModeInSig: 正常读取 / 各状态值验证
- ResetChip（条件）: 正常复位 / RESET 未归属

**DET 专项测试**: 为 DIAG-0002 的每项 DET 检测编写独立用例。

### 步骤 5：集成测试

**前置条件**: 单元测试完成。

**IT 覆盖**:
- 真实 I2C 通信和多芯片并行初始化
- I2C 故障注入 → Fault 状态切换验证
- RESET 引脚时序测量（示波器）
- INT 响应端到端延迟测量
- 输出回读校验的故障注入验证
- 安全状态行为验证（Fault 下不再执行输出操作）

### 步骤 6：资源验证

**前置条件**: 集成编译通过。

- 从 link map 提取实际 ROM/RAM 消耗
- 与 RES-0001 预算对比（ROM < 2 KB, RAM < 256 B + N×64 B）
- 测量 MainFunction 中 I2C 操作总时序
- 更新架构风险 R7 状态

## 4. 架构更新规则

| 场景 | 动作 |
| --- | --- |
| 架构 Draft + 评审修改建议 | 更新架构文档，保持 V1 Draft |
| 架构 Draft + 全部已评审 | 发布为 V1 Released |
| 架构 V1 Released + 新需求文档 | 升级为 V2 Draft，重新评审 |
| 架构 Released + 无新需求 | 不升级版本，仅作勘误 |

## 5. 配套文档索引

| 文档 | 用途 | 路径 |
| --- | --- | --- |
| 架构文档 | 核心架构定义 | `artifacts/Gp_NCA95xx_软件架构设计.md` |
| 输入资料索引 | 架构输入溯源 | `artifacts/Gp_NCA95xx_架构输入索引.md` |
| 需求追溯矩阵 | 双向追溯 | `artifacts/Gp_NCA95xx_需求架构追溯.md` |
| 架构自检清单 | 质量门禁 | `artifacts/Gp_NCA95xx_SDD检查清单.md` |
| 架构评审记录 | 评审指导 | `artifacts/Gp_NCA95xx_架构评审记录.md` |
| 操作步骤 | 本文档 | `artifacts/Gp_NCA95xx_SDD操作步骤.md` |
| 基线总结 | 架构基线概要 | `artifacts/Gp_NCA95xx_SDD基线总结.md` |
| 软件需求规范 | 上游输入 | `artifacts/Gp_NCA95xx_软件需求规范.md` |
