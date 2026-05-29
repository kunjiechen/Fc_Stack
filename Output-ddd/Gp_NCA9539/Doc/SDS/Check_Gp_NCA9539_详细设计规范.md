# 《Gp_NCA9539 详细设计检查清单》

**Check_Gp_NCA9539_详细设计规范**

项目编号/Project number: Gp_NCA9539
保密性/Security: 内部

**Document Properties**
Status: **草稿**
检查版本: **V1**
Author: FC Implementation Workbench
Created: 2026-05-28

---

## 1. 检查范围

本清单基于 `implementation-rules.md` §17（Mandatory Validation Questions）和 `detailed_design_quality_contract.md` 建立，对 `Gp_NCA9539_模块详细设计规范.md` V1 进行逐项检查。

---

## 2. 编码就绪检查（Mandatory Validation Questions）

| # | 检查项 | 结果 | 证据 | 备注 |
| --- | --- | --- | --- | --- |
| 1 | 开发者能否直接从此输出创建文件骨架？ | **通过** | §4 文件列表设计：12 个文件，每个标注 Required/Optional | 文件关系在 §4.2 中明确 |
| 2 | 配置参数和运行参数能否不重新设计直接实现？ | **通过** | §11 配置参数设计：12 宏参 + 4 配置类型；§10 运行参数设计：12 变量 + 4 运行参数类型 | 双维度完整，类型带字段描述 |
| 3 | 外部 API 与依赖 API 是否清晰分离？ | **通过** | §6.1 外部接口 7 个，§6.3 依赖接口/Callout 6 个 | 接口分层独立描述 |
| 4 | 内部函数职责是否足够清晰以支持分解？ | **通过** | §6.2 内部接口：8 个内部函数，每个含 prototype / 子功能分解 / 执行步骤 / 调用关系 / 流程图 | full-per-function 规则全面遵守 |
| 5 | 状态机逻辑是否足够显式以支持编码？ | **通过** | §7 状态机：3 状态 + 5 转换 + 转换表 + 主流程图 | 含条件函数和动作函数 |
| 6 | DET 和 Fault 处理是否有意区分？ | **通过** | §8 DET：6 个检查点（API 滥用）vs §9 Fault：3 个故障项（运行时异常） | 边界清晰，无交叉 |
| 7 | 多核存在时 per-core 所有权和同步点是否明确？ | **通过（单核）** | §5 单核框架设计：单核部署，per-core 结构预留，CalloutGetCoreId 标记 Conditional | 单核纯度规则已遵守 |
| 8 | pending confirmations 是否与已确认事实隔离？ | **通过** | DET 缓冲类型标记 pending-confirm；CalloutGetCoreId 标记 Conditional；风险表 R7/R9/R12 追踪 | 不确定项不混入 formal 区域 |
| 9 | MainFunction 是否有理由或显式拒绝？ | **通过** | §1 FC概述：运行模型为纯同步事件驱动，无周期采样/去抖/状态机推进需求 | 拒绝理由完整 |
| 10 | 每个 Callout、Cfg.c、NoClear 决策是否有可见理由？ | **通过** | Callout: 6 个均标注 Implemented By 和 Evidence；Cfg.c: §11.2.2 配置实例化；NoClear: 未使用（无 reset continuity 需求） | 设计决策均可追溯 |

---

## 3. 章节完整性检查

| 章节 | 要求 | 结果 | 备注 |
| --- | --- | --- | --- |
| §1 FC概述 | 功能介绍、层级、实现方案、运行模型、单核/多核 | **通过** | 含 MainFunction 判定理由 |
| §2 设计输入 | 输入类别、文档/来源、版本/日期、用途 | **通过** | 覆盖 SRS/SDD/芯片约束/平台规则/编码规范 |
| §3 功能设计 | 功能方案说明、核心设计决策 | **通过** | 6 项核心决策 + 子功能交互图 |
| §4 文件列表设计 | 文件列表、文件关系 | **通过** | 12 文件 + 15 条文件关系 |
| §5 单核框架设计 | 单核框架说明、per-core 预留策略 | **通过** | 单核纯度约束已遵守 |
| §6 接口设计 | 外部接口 + 内部接口 + 依赖接口/Callout | **通过** | 7 外部 + 8 内部 + 6 Callout，全部 full-per-function |
| §7 状态机设计 | 选型说明、状态定义、切换表、流程图 | **通过** | 3 状态 + 5 转换 + D2 交叉校验 |
| §8 DET设计 | 检查点、触发条件、记录方式、返回策略 | **通过** | 6 个检查点 |
| §9 故障处理设计 | 确认策略、恢复策略、锁存/清除、故障项表 | **通过** | 3 个故障项 + D3 交叉校验 |
| §10 运行参数设计 | 运行变量表 + 运行参数类型 | **通过** | 12 变量 + 4 类型，字段均有描述 |
| §11 配置参数设计 | 配置宏参 + 配置类型 + 配置实例化 | **通过** | 12 宏参 + 4 配置类型 + 1 const 实例 |
| §12 MemMap设计 | Memory Section 表 | **通过** | 7 个段 |
| §13 编码起步建议 | 推荐实现顺序 | **通过** | 7 步顺序 + 首次创建/实现/配置/运行时/验证说明 |
| §14 风险与待确认项 | 风险索引、问题、影响、建议、状态 | **通过** | 12 条风险 + R-OTHER |
| §15 伴生评审与追溯产物 | 产物文件名和用途 | **通过** | Review/Check/Trace 三个产物 |

---

## 4. 质量合同逐项检查

| # | 质量要求 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 可实现 — 不猜文件布局 | **通过** | §4 文件列表明确定义 12 个文件及关系 |
| 2 | 可实现 — 不猜接口组织 | **通过** | §6.1 外部接口原型、§6.3 依赖接口原型均完整 |
| 3 | 可实现 — 不猜配置参数位置 | **通过** | §11 宏参 + 类型 + 实例化三层次明确 |
| 4 | 可实现 — 不猜运行时变量位置 | **通过** | §10 变量表明确所属 Core + MemMap 放置 |
| 5 | 可实现 — 不猜 Fault/DET 边界 | **通过** | §8 DET (API 滥用) vs §9 Fault (运行时异常) 严格区分 |
| 6 | 可实现 — 不猜 MemMap 布局 | **通过** | §12 7 段完整 |
| 7 | 可追踪 — 设计对象回到上游 | **通过** | 宏参/类型字段/运行变量/故障项均标注 source/设计依据 |
| 8 | 粒度合适 — 不过轻 | **通过** | 所有接口有执行步骤、调用关系、流程图 |
| 9 | 粒度合适 — 不过重 | **通过** | 流程图中无变量名/数组下标/寄存器名/伪代码 |
| 10 | 一致性 — 不漂移 | **通过** | 7 外部接口与 SDD 3.1-3.7 一致；6 配置宏参与 SDD §4 一致（+6 design-addition） |
| 11 | 无内部生成痕迹 | **通过** | 正文中无 grounding 基线名单、Conf_* 证据条目、bundle 字段名 |
| 12 | 待确认信息不单列主章节 | **通过** | 待确认内容出现在 §5 框架设计 (Conditional)、§10/§11 (pending-confirm)、§14 风险表 |
| 13 | 面向项目风格 | **通过** | IoExtDev 族 Grounding 风格（Gp_TPT1145/Gp_TLE92104/Gp_DRV8889）驱动 |

---

## 5. 交叉校验检查

| # | 校验项 | 校验逻辑 | 结果 |
| --- | --- | --- | --- |
| D1-CROSS | R/W 寄存器 → 写路径覆盖 | 每个 R/W 寄存器（Output Port 0/1、Polarity 0/1、Configuration 0/1）是否有对应的写 API 或步骤 | **通过** — SetOutputLevel / SetPolarityInversion / SetDirection / Init 覆盖 6 个 R/W 寄存器 |
| D1-SIDE | 读副作用 → 运行态处理 | Input Port 读清除 INT\ 是否有运行态标志/计数器 | **通过** — IntPort0Pending_b / IntPort1Pending_b 在 GetInterruptStatus/GetInputLevel 中维护 |
| D2-CROSS | 状态转换全集 → 状态机覆盖 | D2 每行转换是否在 §7 有对应条目 | **通过** — POR→正常运行（Init 成功）、正常运行→复位（RESET\ 或 NACK≥阈值）、正常运行→待机（驱动透明） |
| D3-CROSS | 故障全集 → Fault 表覆盖 | D3 每个故障源是否在 §9 有对应条目 | **通过** — 3 个故障源全部覆盖（中断事件重分类为正常通知） |
| D4-CROSS | 带 min/max 的时序参数 → 配置宏 | 每个有 min 或 max 的时序参数是否生成对应宏 | **通过** — t_rec(rst) → T_REC_RST_MIN_NS, t_w(rst) → T_W_RST_MIN_NS, t_v(Q) → T_V_Q_MAX_NS |
| D5-CROSS | 初始化步骤 → Init() 步骤覆盖 | D5 每个初始化操作是否体现（含等待和重试） | **通过** — Init 执行步骤含 I2C 可达性验证、寄存器默认值校验、配置写入、回读验证 |
| D7-CROSS | 器件地址/命令字节 → 配置常量 | 地址表和命令字节是否有对应的 Reg.h 常量或 Cfg.h 宏 | **通过** — FC_Reg.h 含寄存器地址 0x00~0x07 和 I2C 基地址 0x74 |

---

## 6. 设计增量溯源检查

| # | 设计增量 | 来源标注 | 风险项引用 | 风险表条目 | 结果 |
| --- | --- | --- | --- | --- | --- |
| 1 | `GP_NCA9539_CFG_MAX_I2C_RETRY_COUNT` | design-addition (R1) | R1 | "I2C 重试次数" in §14 | **通过** |
| 2 | `GP_NCA9539_CFG_T_REC_RST_MIN_NS` | design-addition (R2) | R2 | "RESET\ 恢复等待" in §14 | **通过** |
| 3 | `GP_NCA9539_CFG_T_W_RST_MIN_NS` | design-addition (R3) | R3 | "RESET\ 脉冲宽度" in §14 | **通过** |
| 4 | `GP_NCA9539_CFG_T_V_Q_MAX_NS` | design-addition (R4) | R4 | "输出稳定等待" in §14 | **通过** |
| 5 | `GP_NCA9539_CFG_FAULT_SELF_RECOVERY_ENABLE` | design-addition (R5) | R5 | "故障自恢复" in §14 | **通过** |
| 6 | `Gp_NCA9539_CalloutDelayUs` | design-addition (R6) | R6 | "延时 Callout" in §14 | **通过** |
| 7 | `Gp_NCA9539_DetBufferType` / `DetBuffer_ast` | design-addition (R7) | R7 | "DET 缓冲类型" in §14 | **通过** |
| 8 | `GP_NCA9539_CFG_I2C_NACK_CONSECUTIVE_LIMIT` / `I2cNackConsecutiveCnt_au8` | design-addition (R8) | R8 | "连续 NACK 跳转阈值" in §14 | **通过** |

---

## 7. 主要问题

无阻断性问题。12 项风险均为待评审状态，待项目确认后关闭。

---

## 8. 下一步动作

1. 项目方逐项评审 R1-R12 风险项，更新 §14 风险表状态
2. 确认单核/多核部署策略，决定 per-core 基础设施保留或简化
3. 确认中断处理策略（轮询/ISR），决定 CODE RAM COPY 段激活
4. 确认是否需要 Deinit/Reinit 接口
5. 确认运行期间寄存器回读策略，决定是否需要 MainFunction
6. 全部风险项评审关闭后，详细设计状态可升级为 Released
