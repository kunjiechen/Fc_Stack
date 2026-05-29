# Check_Gp_NCA9539_软件架构设计

**架构检查清单与 Gate 结果**

项目编号/Project number: Gp_NCA9539
架构版本: V1
架构状态: Draft
检查日期: 2026-05-28

---

## 1. 元数据检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-001 | 架构版本格式为整数大版本（V1/V2/V3） | Pass | V1 |
| CK-002 | 架构状态有效（Draft/Released） | Pass | Draft |
| CK-003 | 生成时间已填写 | Pass | 2026-05-28 |
| CK-004 | FC 名称正确保留原始格式 | Pass | Gp_NCA9539，含下划线，未 CamelCase 化 |
| CK-005 | AUTOSAR 架构层级已填写 | Pass | IoExtDev |
| CK-006 | 文档修订记录已填写 | Pass | V1 初版生成记录 |
| CK-007 | 文档开头和结尾均包含架构元信息 | Pass | §1 和附录均含元信息 |

---

## 2. 外部接口检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-010 | Init 接口已包含 | Pass | §3.1 `Gp_NCA9539_Init` |
| CK-011 | 函数名前缀保留 FC/驱动名称 | Pass | 所有接口使用 `Gp_NCA9539_` 前缀 |
| CK-012 | 每个外部接口使用独立小表 | Pass | §3.1~3.7 每接口独立小表 |
| CK-013 | 接口原型使用完整 C 声明 | Pass | 含 Std_ReturnType、参数类型、指针标识 |
| CK-014 | 参数使用指针形式（非数组声明式） | Pass | 无 `[]` 声明式参数 |
| CK-015 | Description 使用英文 | Pass | 所有接口 Description 为英文 |
| CK-016 | Sync/Async、Reentrancy、Return Value 已填写 | Pass | 所有字段均已填写 |
| CK-017 | 故障/诊断状态接口已包含 | Pass | §3.7 `Gp_NCA9539_GetFaultStatus` |
| CK-018 | 命名语义化（非通用名） | Pass | SetOutputLevel/GetInputLevel/SetDirection 等语义化命名 |
| CK-019 | 无对外全局变量暴露 | Pass | §5 全局变量声明为 Empty |
| CK-020 | MainFunction 判定已记录 | Pass | §1 架构设计思路 + assumptions: MainFunction_Required=false |

---

## 3. 配置宏参检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-030 | 宏标识符全大写 | Pass | 所有宏使用 `GP_NCA9539_CFG_` 前缀 + ALL_CAPS |
| CK-031 | DET 宏已生成（ASIL-B/D SRS 含诊断需求） | Pass | `GP_NCA9539_CFG_DEV_ERROR_DETECT`，默认 `STD_ON` |
| CK-032 | Version 宏已生成 | Pass | `GP_NCA9539_CFG_SW_MAJOR/MINOR_VERSION` |
| CK-033 | 无"为每个外部接口生成开关宏"的过度配置 | Pass | 仅 6 个宏，无接口级开关 |
| CK-034 | macro_type 取值有效 | Pass | Feature Enable / Development Error Detect / Vendor Version Release / Count Size / Behavior Selection |
| CK-035 | 配置宏参有 Evidence 和 Usage Location | Pass | 每项均关联 SRS 需求 ID 或项目约束 |
| CK-036 | 无 per-core enable 宏（CORE0~COREx）暴露 | Pass | per-core 细节未列入配置宏参表 |
| CK-037 | 无硬件绑定明细暴露 | Pass | I2C 地址、GPIO 引脚映射等硬件绑定归入 Cfg.c 配置表 |

---

## 4. 依赖接口检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-040 | I2C 读写 Callout 已包含 | Pass | §8.1 `CalloutI2cWrite`, §8.2 `CalloutI2cRead` |
| CK-041 | RESET\ 引脚控制 Callout 已包含 | Pass | §8.3 `CalloutDioWrite` |
| CK-042 | INT\ 引脚读取 Callout 已包含 | Pass | §8.4 `CalloutDioRead` |
| CK-043 | Callout 原型使用指针形参（非数组声明式） | Pass | 全部使用 `uint8*` 指针，无 `[]` 写法 |
| CK-044 | I2C Callout 使用 `uint8*` 数据指针 + `uint16 Size_u16` | Pass | 符合 byte-oriented I2C 规范 |
| CK-045 | 每个依赖接口使用独立小表 | Pass | §8.1~8.5 每 Callout 独立小表 |
| CK-046 | Implemented By 字段已填写 | Pass | Project Adaptation |
| CK-047 | Evidence 关联芯片架构视图或 SRS | Pass | SRS 需求 ID + Datasheet 章节 |
| CK-048 | 不在依赖接口中暴露裸 MCAL API | Pass | 全部通过 Callout 抽象 |
| CK-049 | Callout.h 和 Callout.c 已列入文件清单 | Pass | §9 均标记为 Required |
| CK-050 | Description 使用英文 | Pass | 所有 Callout Description 为英文 |

---

## 5. 运行态策略检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-060 | 状态机覆盖 SRS 模式需求 | Pass | UNINIT→NORMAL→RESET_RECOVERY 对应 SRS FUNC-0001 状态 |
| CK-061 | 运行时状态有 memory_section 归属 | Pass | 全部归入 CLEAR_FAR_DATA per core |
| CK-062 | 实例状态、数据缓存、故障记录均已覆盖 | Pass | 8 个运行时状态域完整 |
| CK-063 | DET 有运行时 bookkeeping | Pass | Per-core DET buffer（conditional on DET enable） |
| CK-064 | 中断状态有 bookkeeping 防止丢失 | Pass | Per-instance interrupt pending flags |
| CK-065 | Concurrency strategy 已定义 | Pass | Per-core ownership |

---

## 6. MemMap 检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-070 | CODE 段已定义 | Pass | `GP_NCA9539_CODE_START/STOP` |
| CK-071 | RUNTIME RAM (per core) 段已定义 | Pass | `GP_NCA9539_CLEAR_FAR_DATA_ALIGN4_COREx_START/STOP` |
| CK-072 | CONST (global) 段已定义 | Pass | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_GLOBAL_START/STOP` |
| CK-073 | CONST (per core) 段已定义 | Pass | `GP_NCA9539_CONST_FAR_DATA_ALIGN4_COREx_START/STOP` |
| CK-074 | REG CONST 段独立列出（I2C 寄存器外设） | Pass | 独立行，共享 GLOBAL CONST 宏 |
| CK-075 | CALIB 段已定义（条件/预留） | Pass | 预留，当前为空 |
| CK-076 | start/stop 宏配对 | Pass | 所有段均有配对 START/STOP 宏 |
| CK-077 | FC_MemMap.h 已列入文件清单 | Pass | §9.1 Required |

---

## 7. 文件清单检查

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-080 | FC.c 已列入 | Pass | Required |
| CK-081 | FC.h 已列入 | Pass | Required |
| CK-082 | FC_Types.h 已列入 | Pass | Required |
| CK-083 | FC_Cfg.h 已列入 | Pass | Required |
| CK-084 | FC_Cfg.c 已列入 | Pass | Required |
| CK-085 | FC_CfgData.h 已列入 | Pass | Required |
| CK-086 | FC_Reg.h 已列入（I2C 寄存器外设） | Pass | Required |
| CK-087 | FC_Callout.h 已列入（存在 Callout 依赖） | Pass | Required |
| CK-088 | FC_Callout.c 已列入（存在 Callout 依赖） | Pass | Required |
| CK-089 | FC_MemMap.h 已列入 | Pass | Required |
| CK-090 | FC_MemMap.h 在所有 section-managed 文件的包含关系中体现 | Pass | §9.2 文件关系表 |
| CK-091 | Std_Types.h 列为外部依赖（非本 FC 创建） | Pass | §9.2 |

---

## 8. 交叉校验（芯片架构视图 → 架构输出）

| # | 检查项 | 结果 | 证据/说明 |
| --- | --- | --- | --- |
| CK-100 | A2 "必须连接"引脚均有 Callout/配置覆盖 | Pass | RESET\ → DioWrite Callout; SCL/SDA → I2C Callout; A0/A1 → Cfg.c 配置表; VDD/VSS 不适用; SDA/SCL/INT/RESET 外部上拉约束已记录 |
| CK-101 | A3 硬件模式全集 → SRS/架构状态机覆盖 | Pass | Operating(正常运行)→NORMAL; Reset→RESET_RECOVERY; Standby→架构未涉及（芯片自动行为，无需软件介入），已在 Notes 中标注 |
| CK-102 | A4 R/W 寄存器 → 架构写路径覆盖 | Pass | Output Port 0/1 → SetOutputLevel; Configuration 0/1 → SetDirection; Polarity Inversion 0/1 → SetPolarityInversion; Input Port 0/1 → GetInputLevel (Read-only) |
| CK-103 | A6 中断源 → Callout/查询 API 覆盖 | Pass | INT\ → DioRead Callout + GetInterruptStatus API; read-clear 机制已记录 |
| CK-104 | A5 burst 行为 → Callout 约束记录 | Pass | Burst read/write 交替行为写入 CalloutI2cRead/CalloutI2cWrite Description |

---

## 9. Gate 结果汇总

| Gate | 检查项数 | Pass | Fail | Skip | 结果 |
| --- | --- | --- | --- | --- | --- |
| 元数据 | 7 | 7 | 0 | 0 | Pass |
| 外部接口 | 11 | 11 | 0 | 0 | Pass |
| 配置宏参 | 8 | 8 | 0 | 0 | Pass |
| 依赖接口 | 11 | 11 | 0 | 0 | Pass |
| 运行态策略 | 6 | 6 | 0 | 0 | Pass |
| MemMap | 8 | 8 | 0 | 0 | Pass |
| 文件清单 | 12 | 12 | 0 | 0 | Pass |
| 交叉校验 | 5 | 5 | 0 | 0 | Pass |
| **总计** | **68** | **68** | **0** | **0** | **Pass** |

---

## 10. 主要问题

无。所有检查项均通过。

---

## 11. 下一步动作

1. 完成架构评审（见 `Review_Gp_NCA9539_软件架构设计.md`）
2. 关闭 §10 风险表中 R1~R9 及 R-OTHER
3. 所有风险项关闭后，架构状态由 V1 Draft 升级为 V1 Released
4. Released 后可进入 SDD（详细设计）阶段
