# Gp_NCA95xx 架构基线总结

## 1. 基线信息

| 属性 | 值 |
| --- | --- |
| 模块名 | `Gp_NCA95xx` |
| 架构版本 | V1 |
| 架构状态 | Draft |
| AUTOSAR 层级 | IoExtDev |
| 生成时间 | 2026-05-26 |
| 上游输入 | `Gp_NCA95xx_软件需求规范.md` V0.1.0 |
| ASIL 等级 | ASIL_B |

## 2. 架构概要

### 2.1 外部接口（7 个，含 1 个条件接口）

| 接口 | 状态 |
| --- | --- |
| `Gp_NCA95xx_Init` | Formal |
| `Gp_NCA95xx_MainFunction` | Formal |
| `Gp_NCA95xx_GetGpioInSig` | Formal |
| `Gp_NCA95xx_SetGpioOutSig` | Formal |
| `Gp_NCA95xx_GetDevFaultSig` | Formal |
| `Gp_NCA95xx_GetDevModeInSig` | Formal |
| `Gp_NCA95xx_ResetChip` | Conditional（取决于 RESET 引脚归属） |

### 2.2 配置宏参（6 个）

| 宏 | 状态 |
| --- | --- |
| `GP_NCA95xx_CFG_DEV_ERROR_DETECT` | Formal |
| `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE` | Formal |
| `GP_NCA95xx_CFG_RUNTIME_DIR_CHANGE_ENABLE` | Formal |
| `GP_NCA95xx_CFG_RESET_PIN_OWNED` | Conditional |
| `GP_NCA95xx_CFG_SW_MAJOR_VERSION` | Formal |
| `GP_NCA95xx_CFG_SW_MINOR_VERSION` | Formal |

### 2.3 依赖接口（6 个）

| 接口 | 实现边界 | 状态 |
| --- | --- | --- |
| `Gp_NCA95xx_CalloutI2cWrite` | Project Adaptation（MCAL I2C 绑定） | Formal |
| `Gp_NCA95xx_CalloutI2cRead` | Project Adaptation（MCAL I2C 绑定） | Formal |
| `Gp_NCA95xx_CalloutReadDio` | IoMcu / Project Adaptation | Conditional（取决于 INT 引脚连接） |
| `Gp_NCA95xx_CalloutWriteDio` | IoMcu / Project Adaptation | Conditional（取决于 RESET 引脚归属） |
| `Gp_NCA95xx_CalloutGetCoreId` | MCAL / Platform Adaptation | Formal |
| `Gp_NCA95xx_CalloutDelayUs` | MCAL / Platform Adaptation | Conditional（取决于 RESET 引脚归属） |

### 2.4 文件清单（10 个）

| 文件 | Required/Optional |
| --- | --- |
| `Gp_NCA95xx.c` | Required |
| `Gp_NCA95xx.h` | Required |
| `Gp_NCA95xx_Types.h` | Required |
| `Gp_NCA95xx_Cfg.h` | Required |
| `Gp_NCA95xx_Cfg.c` | Required |
| `Gp_NCA95xx_CfgData.h` | Required |
| `Gp_NCA95xx_Reg.h` | Required |
| `Gp_NCA95xx_Callout.h` | Required |
| `Gp_NCA95xx_Callout.c` | Required |
| `Gp_NCA95xx_MemMap.h` | Required |

### 2.5 MemMap 段（5 段）

| 段 | 用途 | 状态 |
| --- | --- | --- |
| CODE | 外部接口和内部函数代码 | Formal |
| RUNTIME RAM (CLEAR_FAR_DATA_ALIGN4_COREx) | 每核运行态容器 | Formal |
| CONST GLOBAL | 全局共享配置常量 | Formal |
| CONST PER-CORE (COREx) | 每核独立配置表 | Formal |
| CALIB | 标定参数（预留） | Empty |

### 2.6 需求覆盖

| 类别 | 需求数 | 覆盖状态 |
| --- | --- | --- |
| FUNC | 4 | 全部 Covered |
| INTF | 6 | 全部 Covered |
| CFG | 7 | 全部 Covered |
| DIAG | 4 | 全部 Covered |
| TIM | 5 | 全部 Covered |
| SAFE | 3 | 全部 Covered |
| CODE | 3 | 全部 Covered |
| RES | 2 | 全部 Covered |
| COMP | 2 | 全部 Covered |
| **总计** | **35** | **全部 Covered** |

### 2.7 关键待确认项（7 项）

| 索引 | 问题 | 影响范围 |
| --- | --- | --- |
| R1 | INT 引脚归属 | ReadDio callout 状态 |
| R2 | RESET 引脚归属 | ResetChip API + WriteDio/DelayUs callout |
| R3 | 上层通知机制 | 潜在新增回调/Callout |
| R4 | 运行时方向变更 | SetGpioDirSig API 是否编译 |
| R5 | 故障恢复策略 | MainFunction 恢复逻辑细节 |
| R6 | 多核配置归属 | CONST 段 GLOBAL ↔ COREx |
| R7 | 资源预算 | 实现后 link map 验证 |

## 3. 架构设计决策记录

| 决策 | 理由 |
| --- | --- |
| 采用信号 ID (uint16) 解耦模式 | 符合项目 IoExtDev 层规范，ASW 不感知 CoreId/ChipIdx/PinIdx 内部编码。 |
| I2C 通信通过 Callout 抽象 | 不直接依赖 MCAL I2C 驱动，保持集成灵活性；符合 FC 依赖策略。 |
| SetGpioOutSig 采用同步 I2C 写入 | GPIO 输出设置对延迟敏感；MainFunction 的 pending 处理仅用于去抖/合并场景。 |
| 输出回读校验通过配置宏控制 | 内部一致性检查，不影响外部接口；具有项目裁剪价值。 |
| 故障状态通过 GetDevFaultSig 查询 | 符合 IoExtDev 层 GetDevFaultSig 命名规范；不泄露内部实现。 |
| CONST 段区分 GLOBAL 和 PER-CORE | 每核拥有独立芯片实例和配置表，CONST PER-CORE 正确反映多核架构。 |
| RUNTIME RAM 使用 CLEAR_FAR_DATA | 无 warm-reset 保留数据需求；CLEAR 确保启动状态确定性。 |

## 4. 配套工件清单

| 工件 | 路径 |
| --- | --- |
| 架构文档 | `artifacts/Gp_NCA95xx_软件架构设计.md` |
| 输入资料索引 | `artifacts/Gp_NCA95xx_架构输入索引.md` |
| 需求追溯矩阵 | `artifacts/Gp_NCA95xx_需求架构追溯.md` |
| 架构自检清单 | `artifacts/Gp_NCA95xx_SDD检查清单.md` |
| 架构评审记录 | `artifacts/Gp_NCA95xx_架构评审记录.md` |
| 操作步骤 | `artifacts/Gp_NCA95xx_SDD操作步骤.md` |
| 基线总结 | 本文档 |
