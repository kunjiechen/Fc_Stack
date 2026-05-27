# FC软件架构定义

## 文档元信息

- 架构版本: `V1`
- 架构状态: `Draft`
- 输出模式: `Formal Draft`
- 生成时间: 2026-05-26
- 生成/修订说明: 基于 SRS-Gp_NCAxx39 V0.1.0 初始架构生成
- 变更点总结: 初版生成。5 个外部接口、2 个 I2C Callout + 1 个 DIO Callout、7 个必需文件 + 3 个条件文件、CODE / CLEAR_FAR_DATA_COREx / CONST 段布局。

---

## 0. 抽取与判定总览

### 0.1 需求抽取与分类表

| 需求条目 | 抽取点 | 是否外部接口 | 分类 | 暂定落点 | 判定依据 | 备注/待确认 |
| --- | --- | --- | --- | --- | --- | --- |
| SRS-NCAxx39-INTF-0001 | Init 初始化 | 是 | 外部接口 | Gp_NCAxx39.c / Gp_NCAxx39.h | 标准 FC Init 模式 | |
| SRS-NCAxx39-INTF-0002 | MainFunction 周期 | 是 | 外部接口 | Gp_NCAxx39.c / Gp_NCAxx39.h | 存在 I2C 轮询 + INT 采样 + 故障去抖 | |
| SRS-NCAxx39-INTF-0003 | GetGpInSig 输入读取 | 是 | 外部接口 | Gp_NCAxx39.c / Gp_NCAxx39.h | IoExtDev 语义 Getter | |
| SRS-NCAxx39-INTF-0004 | SetGpOutSig 输出设置 | 是 | 外部接口 | Gp_NCAxx39.c / Gp_NCAxx39.h | IoExtDev 语义 Setter | |
| SRS-NCAxx39-INTF-0005 | GetDevFaultSig 故障读取 | 是 | 外部接口 | Gp_NCAxx39.c / Gp_NCAxx39.h | IoExtDev 层芯片级故障查询，命名遵循 aurix2g 规范 | |
| SRS-NCAxx39-CFG-0001 | 实例数量配置 | 否 | 静态配置 | Gp_NCAxx39_Cfg.h | 预编译宏 | |
| SRS-NCAxx39-CFG-0002 | I2C 设备地址配置 | 否 | 静态配置 | Gp_NCAxx39_CfgData.h / Gp_NCAxx39_Cfg.c | 配置表项，非宏参 | |
| SRS-NCAxx39-CFG-0003 | 默认引脚方向标定 | 否 | 静态配置 | Gp_NCAxx39_CfgData.h / Gp_NCAxx39_Cfg.c | 配置表项 | |
| SRS-NCAxx39-CFG-0004 | 默认输出电平标定 | 否 | 静态配置 | Gp_NCAxx39_CfgData.h / Gp_NCAxx39_Cfg.c | 配置表项 | |
| SRS-NCAxx39-CFG-0005 | 默认极性反转标定 | 否 | 静态配置 | Gp_NCAxx39_CfgData.h / Gp_NCAxx39_Cfg.c | 配置表项 | |
| SRS-NCAxx39-CFG-0006 | 信号映射配置 | 否 | 静态配置 | Gp_NCAxx39_CfgData.h / Gp_NCAxx39_Types.h | SigMappingCfgType 结构 | |
| SRS-NCAxx39-CFG-0007 | I2C 通道与速率配置 | 否 | 静态配置 | Gp_NCAxx39_CfgData.h | 配置表项，非宏参 | |
| SRS-NCAxx39-CFG-0008 | DET 开关 | 否 | 静态配置 | Gp_NCAxx39_Cfg.h | 预编译宏 | |
| SRS-NCAxx39-DIAG-0001 | I2C 通信错误检测 | 否 | 动态数据 | Gp_NCAxx39.c 内部变量 | 运行时故障去抖计数器 | |
| SRS-NCAxx39-DIAG-0002 | INT 中断检测 | 否 | 动态数据 + Callout | Gp_NCAxx39.c / Gp_NCAxx39_Callout.h | DIO Callout 依赖 | INT 引脚归属待确认 |
| SRS-NCAxx39-DIAG-0003 | DET 错误检测 | 否 | 运行时逻辑 | Gp_NCAxx39.c 各 API 入口 | 参数校验 + DET 报告 | |
| SRS-NCAxx39-DIAG-0004 | 输出寄存器读回校验 | 否 | 动态数据 | Gp_NCAxx39.c MainFunction 内部 | ASIL_B 安全机制 | |
| SRS-NCAxx39-DIAG-0005 | 配置完整性校验 | 否 | Init 阶段逻辑 | Gp_NCAxx39.c Init 内部 | ASIL_B 安全机制 | |
| SRS-NCAxx39-TIM-0003 | INT 响应时间 | 否 | 时序约束 | 由 MainFunction 调度保证 | 非独立接口 | |

### 0.2 外部接口候选清单

| 候选接口 | 所属模块 | 来源需求 | 接口类型 | 输入参数 | 输出参数 | 置信度 | 是否保留 | 保留原因 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gp_NCAxx39_Init | Gp_NCAxx39 | INTF-0001 | 初始化 | void | void | 高 | 是 | 标准 FC Init |
| Gp_NCAxx39_MainFunction | Gp_NCAxx39 | INTF-0002 | 周期 | void | void | 高 | 是 | I2C 轮询 + INT 采样 + 故障去抖 + 输出读回 |
| Gp_NCAxx39_GetGpInSig | Gp_NCAxx39 | INTF-0003 | 读 | uint16 Id_u16 | uint8* Level_pu8, Std_ReturnType | 高 | 是 | IoExtDev 语义 Getter |
| Gp_NCAxx39_SetGpOutSig | Gp_NCAxx39 | INTF-0004 | 写 | uint16 Id_u16, uint8 Level_u8 | Std_ReturnType | 高 | 是 | IoExtDev 语义 Setter |
| Gp_NCAxx39_GetDevFaultSig | Gp_NCAxx39 | INTF-0005 | 诊断 | uint16 Id_u16 | uint32* Fault_pu32, Std_ReturnType | 高 | 是 | IoExtDev 芯片级故障查询 |

### 0.3 配置宏参清单

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GP_NCAXX39_CFG_DEV_ERROR_DETECT | DET 错误检测全局开关 | Development Error Detect | STD_ON | SRS-NCAxx39-CFG-0008 | Gp_NCAxx39_Cfg.h | Formal |
| GP_NCAXX39_CFG_MULTI_CHIP_NUM | 当前核管理芯片实例数 (0–4) | Count Size | 0 | SRS-NCAxx39-CFG-0001 | Gp_NCAxx39_Cfg.h | Formal |
| GP_NCAXX39_CFG_REG_READBACK_VERIFY_ENABLE | 输出寄存器周期读回校验开关 | Feature Enable | STD_ON | SRS-NCAxx39-DIAG-0004 | Gp_NCAxx39_Cfg.h | Formal |

---

## 1. FC概述

- FC名称: Gp_NCAxx39
- 核心职责: 为 NCA9539-Q1 系列 16-bit I2C GPIO 扩展器提供 IoExtDev 层驱动，管理多芯片实例的 GPIO 方向、输出电平、极性反转和输入读取，并提供芯片级故障诊断
- 功能摘要:
  - 每核多芯片实例管理与标定数据加载
  - I2C 同步读写芯片寄存器（Input/Output/Configuration/Polarity Inversion 四组寄存器对）
  - MainFunction 周期 INT 轮询、I2C 故障检测与去抖、输出寄存器读回校验
  - ASIL_B 安全机制：配置完整性校验、输出读回校验、DET 参数校验、多实例故障隔离
- 运行模型: 同步 Set/Get + 周期 MainFunction
- 目标场景: AURIX2G 平台汽车电子 I2C GPIO 扩展（LED 驱动、按键扫描、传感器使能等）

---

## 2. 设计输入

### 2.1 输入文档

- FC需求: SRS-Gp_NCAxx39 V0.1.0

### 2.2 场景约束

- 平台/芯片: AURIX 2G (TC3xx)
- MCAL/BSW假设: MCAL I2C 驱动已配置；MCAL DIO 驱动可用（INT 引脚采样）；DET 模块可用（DET=STD_ON 时）
- OS假设: 上层周期任务调度 MainFunction
- 多核: 支持 1–6 核，每核独立数据区；不支持跨核共享实例
- 多实例: 每核 0–4 个芯片实例，同 I2C 总线通过设备地址区分
- 其他约束: ASIL_B；I2C 总线速率 400 kHz Fast-mode；芯片默认 POR 状态为全输入、全高电平、无极性反转

---

## 3. 假设与缺失信息

- 假设1: INT 引脚连接至 MCU DIO，归属本模块管理
- 假设2: RESET 引脚由硬件独立管理或上拉至 VDD，不归属本模块控制
- 假设3: I2C Callout 适配层由项目侧实现，本模块仅定义 Callout 契约
- 缺失信息1: INT 引脚 DIO 通道编号及归属确认
- 缺失信息2: I2C 通道索引与总线上其他设备拓扑
- 缺失信息3: 故障去抖阈值与 INT 超时阈值具体数值

### 3.1 需求中的占位项与未决项

- TBD 项: 故障去抖阈值 (FaultThreshold_u8)、INT 超时周期数、ROM/RAM 预算阈值
- 缺失附件: I2C Callout 适配层详细规格
- 未定义信号列表: 无
- 暂定接口区域: 运行时方向变更接口 (SetGpDirSig)、运行时极性变更接口 (SetGpPolSig)、整端口批量读写接口——需求阶段标记为 Open Issue，本版架构不包含

---

## 4. 需求到架构映射

| 需求条目 | 抽取含义 | 分类 | 架构落点 | 判定依据 | 待确认问题 |
| --- | --- | --- | --- | --- | --- |
| SRS-NCAxx39-FUNC-0001 | 设备模式管理 (Unknown/Init/Normal/Fault) | 动态状态 | Gp_NCAxx39.c 内部状态机 | 标准 FC 状态管理 | |
| SRS-NCAxx39-FUNC-0002 | MainFunction 周期处理 | 外部接口 + 内部逻辑 | Gp_NCAxx39_MainFunction | 存在异步轮询需求 | |
| SRS-NCAxx39-INTF-0001 | Init 接口：加载标定、回写寄存器 | 外部接口 | Gp_NCAxx39_Init | 标准 FC Init | |
| SRS-NCAxx39-INTF-0002 | MainFunction 接口定义 | 外部接口 | Gp_NCAxx39_MainFunction | 标准 FC MainFunction | |
| SRS-NCAxx39-INTF-0003 | GetGpInSig：读取输入电平 | 外部接口 | Gp_NCAxx39_GetGpInSig | IoExtDev 语义 | |
| SRS-NCAxx39-INTF-0004 | SetGpOutSig：设置输出电平 | 外部接口 | Gp_NCAxx39_SetGpOutSig | IoExtDev 语义 | |
| SRS-NCAxx39-INTF-0005 | GetDevFaultSig：读取故障掩码 | 外部接口 | Gp_NCAxx39_GetDevFaultSig | IoExtDev 芯片级故障查询 | |
| SRS-NCAxx39-CFG-0001 | 实例数量 0–4 | 配置宏参 | GP_NCAXX39_CFG_MULTI_CHIP_NUM | 预编译常量 | |
| SRS-NCAxx39-CFG-0002 | I2C 设备地址 0x74–0x77 | 配置表 | HWCfg.DevAddr_u8 | 静态配置表项 | |
| SRS-NCAxx39-CFG-0003 | 默认引脚方向标定 | 配置表 | HWCfg.DirPort0_u8 / DirPort1_u8 | 标定数据 | |
| SRS-NCAxx39-CFG-0004 | 默认输出电平标定 | 配置表 | HWCfg.OutPort0_u8 / OutPort1_u8 | 标定数据 | |
| SRS-NCAxx39-CFG-0005 | 默认极性反转标定 | 配置表 | HWCfg.PolPort0_u8 / PolPort1_u8 | 标定数据 | |
| SRS-NCAxx39-CFG-0006 | 信号 ID 映射 (CoreId + ChipIdx + PinIdx) | 配置表 | SigMappingCfgType 数组 | 静态映射表 | |
| SRS-NCAxx39-CFG-0007 | I2C 通道与速率 | 配置表 | HWCfg.I2cChnId_u8 | 静态配置表项 | |
| SRS-NCAxx39-CFG-0008 | DET 开关 | 配置宏参 | GP_NCAXX39_CFG_DEV_ERROR_DETECT | 预编译开关 | |
| SRS-NCAxx39-DIAG-0001 | I2C 通信错误检测与去抖 | 动态数据 + 内部逻辑 | MainFunction 内 Callout 返回值判断 | 运行时故障处理 | 阈值待确认 |
| SRS-NCAxx39-DIAG-0002 | INT 中断检测 | Callout + 内部逻辑 | Gp_NCAxx39_CalloutDioRead | DIO Callout 依赖 | INT 引脚归属待确认 |
| SRS-NCAxx39-DIAG-0003 | DET 参数校验 | 防御层逻辑 | 各外部 API 入口 | DET 标准模式 | |
| SRS-NCAxx39-DIAG-0004 | 输出寄存器读回校验 | MainFunction 内部逻辑 | MainFunction 内 I2C 读回 + 比对 | ASIL_B 安全机制 | |
| SRS-NCAxx39-DIAG-0005 | 配置完整性校验 | Init 内部逻辑 | Init 内 I2C 回读 + 比对 | ASIL_B 安全机制 | |
| SRS-NCAxx39-SAFE-0002 | 多实例故障隔离 | 每实例独立状态 | 运行时数据结构按实例索引 | 独立故障状态 | |

### 4.1 接口覆盖率表

| 需求ID | 功能描述 | 对应接口/配置/运行态 | 覆盖状态 | 备注 |
| --- | --- | --- | --- | --- |
| SRS-NCAxx39-FUNC-0001 | 设备模式管理 | 内部 DevMode 状态机 | 已覆盖 | |
| SRS-NCAxx39-FUNC-0002 | MainFunction 周期处理 | Gp_NCAxx39_MainFunction | 已覆盖 | |
| SRS-NCAxx39-INTF-0001 | Init | Gp_NCAxx39_Init | 已覆盖 | |
| SRS-NCAxx39-INTF-0002 | MainFunction | Gp_NCAxx39_MainFunction | 已覆盖 | |
| SRS-NCAxx39-INTF-0003 | GetGpInSig | Gp_NCAxx39_GetGpInSig | 已覆盖 | |
| SRS-NCAxx39-INTF-0004 | SetGpOutSig | Gp_NCAxx39_SetGpOutSig | 已覆盖 | |
| SRS-NCAxx39-INTF-0005 | GetDevFaultSig | Gp_NCAxx39_GetDevFaultSig | 已覆盖 | |
| SRS-NCAxx39-CFG-0001 | 实例数量 | GP_NCAXX39_CFG_MULTI_CHIP_NUM | 已覆盖 | |
| SRS-NCAxx39-CFG-0002 | I2C 地址 | HWCfg.DevAddr_u8 | 已覆盖 | |
| SRS-NCAxx39-CFG-0003 | 方向标定 | HWCfg.DirPort0_u8 / DirPort1_u8 | 已覆盖 | |
| SRS-NCAxx39-CFG-0004 | 输出电平标定 | HWCfg.OutPort0_u8 / OutPort1_u8 | 已覆盖 | |
| SRS-NCAxx39-CFG-0005 | 极性标定 | HWCfg.PolPort0_u8 / PolPort1_u8 | 已覆盖 | |
| SRS-NCAxx39-CFG-0006 | 信号映射 | SigMappingCfgType | 已覆盖 | |
| SRS-NCAxx39-CFG-0007 | I2C 通道速率 | HWCfg.I2cChnId_u8 | 已覆盖 | |
| SRS-NCAxx39-CFG-0008 | DET 开关 | GP_NCAXX39_CFG_DEV_ERROR_DETECT | 已覆盖 | |
| SRS-NCAxx39-DIAG-0001 | I2C 错误检测 | MainFunction 内部 | 已覆盖 | |
| SRS-NCAxx39-DIAG-0002 | INT 检测 | CalloutDioRead + MainFunction | 已覆盖 | INT 归属待确认 |
| SRS-NCAxx39-DIAG-0003 | DET 检测 | 各 API 入口 | 已覆盖 | |
| SRS-NCAxx39-DIAG-0004 | 输出读回校验 | MainFunction 内部 | 已覆盖 | |
| SRS-NCAxx39-DIAG-0005 | 配置完整性校验 | Init 内部 | 已覆盖 | |
| SRS-NCAxx39-TIM-0001 | I2C 速率 | 由 Callout 适配层保证 | 已覆盖 | |
| SRS-NCAxx39-TIM-0002 | 复位时序 | 不适用（RESET 不归属本模块） | 未覆盖 | RESET 归属待确认 |
| SRS-NCAxx39-TIM-0003 | INT 响应时间 | MainFunction 调度保证 | 已覆盖 | |
| SRS-NCAxx39-SAFE-0001 | ASIL_B | 全接口 | 已覆盖 | |
| SRS-NCAxx39-SAFE-0002 | 故障隔离 | 每实例独立状态 | 已覆盖 | |
| SRS-NCAxx39-CODE-0001 | MISRA | 编码阶段保证 | 已覆盖 | |
| SRS-NCAxx39-CODE-0002 | 命名规范 | 全文件 | 已覆盖 | |
| SRS-NCAxx39-RES-0001 | 资源预算 | 链接映射文件 | 已覆盖 | |

### 4.2 反向追踪表

| 接口名 | 来源需求ID | 来源类型 | 置信度 | 备注 |
| --- | --- | --- | --- | --- |
| Gp_NCAxx39_Init | SRS-NCAxx39-INTF-0001 | 需求 | 高 | 标准 FC Init |
| Gp_NCAxx39_MainFunction | SRS-NCAxx39-INTF-0002 | 需求 | 高 | I2C 轮询 + INT + 故障 + 读回 |
| Gp_NCAxx39_GetGpInSig | SRS-NCAxx39-INTF-0003 | 需求 | 高 | IoExtDev Getter |
| Gp_NCAxx39_SetGpOutSig | SRS-NCAxx39-INTF-0004 | 需求 | 高 | IoExtDev Setter |
| Gp_NCAxx39_GetDevFaultSig | SRS-NCAxx39-INTF-0005 | 需求 | 高 | IoExtDev 芯片故障查询 |
| Gp_NCAxx39_CalloutI2cWrite | SRS-NCAxx39-INTF-0001/0004 | 规则推导 | 高 | I2C 寄存器写入依赖 |
| Gp_NCAxx39_CalloutI2cRead | SRS-NCAxx39-INTF-0003 | 规则推导 | 高 | I2C 寄存器读取依赖 |
| Gp_NCAxx39_CalloutDioRead | SRS-NCAxx39-DIAG-0002 | 规则推导 | 中 | INT 引脚采样；归属待确认 |

---

## 5. 文件列表定义

| 文件名 | 必需/可选 | 职责 | 关键内容 |
| --- | --- | --- | --- |
| `Gp_NCAxx39.c` | Required | FC 主实现 | Init, MainFunction, GetGpInSig, SetGpOutSig, GetDevFaultSig；内部状态机、I2C 读写逻辑、DET 校验、故障去抖、输出读回校验 |
| `Gp_NCAxx39.h` | Required | 对外接口声明 | 5 个外部 API 原型、Sync/Async 标注、Reentrancy 标注 |
| `Gp_NCAxx39_Cfg.c` | Required | 配置常量定义 | GlobalCfg 实例、HWCfg 数组、SigMappingCfg 数组 |
| `Gp_NCAxx39_Cfg.h` | Required | 预编译配置宏 | GP_NCAXX39_CFG_DEV_ERROR_DETECT, GP_NCAXX39_CFG_MULTI_CHIP_NUM, GP_NCAXX39_CFG_REG_READBACK_VERIFY_ENABLE；包含 Gp_NCAxx39_Reg.h |
| `Gp_NCAxx39_CfgData.h` | Required | 配置数据声明 | extern GlobalCfg, HWCfgType, SigMappingCfgType 声明 |
| `Gp_NCAxx39_Types.h` | Required | 类型定义 | DevMode 枚举, FaultStatus 位掩码宏, HWCfgType, SigMappingCfgType, RuntimeDataType |
| `Gp_NCAxx39_MemMap.h` | Required | 内存段宏映射 | CODE / CLEAR_FAR_DATA_COREx / CONST_FAR_DATA_COREx / CONST_FAR_DATA_GLOBAL 段宏 |
| `Gp_NCAxx39_Reg.h` | Conditional | I2C 寄存器常量 | 设备地址基址、8 个寄存器地址、默认值、I2C R/W 位定义；包含 Std_Types.h |
| `Gp_NCAxx39_Callout.h` | Conditional | Callout 原型声明 | CalloutI2cWrite, CalloutI2cRead, CalloutDioRead 原型 |
| `Gp_NCAxx39_Callout.c` | Conditional | Callout 适配实现/桩 | I2C 事务绑定、DIO 读取绑定、板级反相适配 |

### 5.1 文件之间的链接关系

| 文件 | 直接依赖 | 关系说明 |
| --- | --- | --- |
| `Gp_NCAxx39.c` | Gp_NCAxx39.h, Gp_NCAxx39_Types.h, Gp_NCAxx39_Cfg.h, Gp_NCAxx39_CfgData.h, Gp_NCAxx39_Callout.h, Gp_NCAxx39_MemMap.h | 主实现依赖所有类型、配置、Callout 和段宏 |
| `Gp_NCAxx39.h` | Gp_NCAxx39_Types.h | 对外接口可能引用 DevMode 等类型 |
| `Gp_NCAxx39_Cfg.c` | Gp_NCAxx39_Cfg.h, Gp_NCAxx39_CfgData.h, Gp_NCAxx39_Types.h, Gp_NCAxx39_Reg.h, Gp_NCAxx39_MemMap.h | 配置常量定义依赖类型、寄存器常量和段宏 |
| `Gp_NCAxx39_Cfg.h` | Gp_NCAxx39_Reg.h | 配置宏可能引用寄存器地址常量 |
| `Gp_NCAxx39_CfgData.h` | Gp_NCAxx39_Types.h | 配置数据声明引用 HWCfgType 等 |
| `Gp_NCAxx39_Types.h` | Std_Types.h | 基础类型依赖 |
| `Gp_NCAxx39_Reg.h` | Std_Types.h | 寄存器常量文件基础类型依赖 |
| `Gp_NCAxx39_Callout.h` | Gp_NCAxx39_Types.h | Callout 可能引用 FC 类型 |
| `Gp_NCAxx39_Callout.c` | Gp_NCAxx39_Callout.h | Callout 实现包含自身头文件 |

### 5.2 五大类头文件承载关系

| 类别 | 主承载头文件 | 次承载头文件 | 承载说明 |
| --- | --- | --- | --- |
| 对外接口 | `Gp_NCAxx39.h` | `Gp_NCAxx39_Types.h` | 5 个外部 API 原型声明；类型定义承载 DevMode 枚举和 FaultStatus 宏 |
| 配置宏参 | `Gp_NCAxx39_Cfg.h` | `Gp_NCAxx39_CfgData.h`、`Gp_NCAxx39_Types.h` | Cfg.h 承载 DET 开关、实例数、读回校验开关；配置表项下沉到 Cfg.c/CfgData.h |
| 寄存器定义 | `Gp_NCAxx39_Reg.h` | `Gp_NCAxx39_Cfg.h` | Reg.h 承载 I2C 设备地址基址、8 寄存器地址、位定义、POR 默认值；Cfg.h 在需要寄存器符号时包含 Reg.h |
| 标定参数 | `Gp_NCAxx39_CfgData.h` | `Gp_NCAxx39_Types.h` | 方向表、输出电平表、极性表通过 HWCfg 配置表承载 |
| 全局参数 | `Gp_NCAxx39_Types.h` | — | 所有共享类型、枚举、结构体 |
| 内存分配宏 | `Gp_NCAxx39_MemMap.h` | 各文件段边界 include | CODE / CLEAR_FAR_DATA / CONST 段切换 |

### 5.3 可选文件

| 文件名 | 触发条件 | 职责 |
| --- | --- | --- |
| `Gp_NCAxx39_Reg.h` | I2C register-based 外设。 | 承载 NCA9539-Q1 的 I2C 设备地址基址、8 个寄存器地址 (0x00–0x07)、位定义、POR 默认值、R/W 位常量。 |
| `Gp_NCAxx39_Callout.h` | 存在 I2C + DIO Callout 依赖。 | 承载 I2C 读写和 DIO 读取 Callout 原型，定义项目适配契约。 |
| `Gp_NCAxx39_Callout.c` | 存在 Callout 依赖。 | 承载项目侧 I2C 事务绑定、DIO 读取绑定和板级反相适配实现或集成桩。 |

---

## 6. 外部接口定义

### 6.1 Gp_NCAxx39_Init

| 接口名 | 类型 | 用途 | 输入 | 输出 | 返回值 | 时序/模式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gp_NCAxx39_Init | 初始化 | 加载配置表与标定数据，遍历所有已配置芯片实例，通过 I2C Callout 回写方向、输出电平、极性寄存器，执行配置回读校验，将实例模式置为 Init | void | void | void | 同步；启动阶段调用一次 | 每个实例独立初始化；I2C 失败标记 Unknown 并继续其余实例 |

### 6.2 Gp_NCAxx39_MainFunction

| 接口名 | 类型 | 用途 | 输入 | 输出 | 返回值 | 时序/模式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gp_NCAxx39_MainFunction | 周期 | INT 引脚采样、输入端口 I2C 刷新、I2C 故障检测与去抖、输出寄存器读回校验 | void | void | void | 异步周期；上层任务调度 | 仅处理当前核所属 Normal 模式实例 |

### 6.3 Gp_NCAxx39_GetGpInSig

| 接口名 | 类型 | 用途 | 输入 | 输出 | 返回值 | 时序/模式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gp_NCAxx39_GetGpInSig | 读 | 通过 uint16 Id 解析目标芯片实例与引脚，I2C 同步读取 Input Port 寄存器，应用极性反转后返回逻辑电平 | uint16 Id_u16 | uint8* Level_pu8 → 0 或 1 | Std_ReturnType: E_OK / E_NOT_OK | 同步；可在任意任务上下文调用 | DET 校验: Null 指针、无效 Id、未初始化；I2C 失败返回 E_NOT_OK |

### 6.4 Gp_NCAxx39_SetGpOutSig

| 接口名 | 类型 | 用途 | 输入 | 输出 | 返回值 | 时序/模式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gp_NCAxx39_SetGpOutSig | 写 | 通过 uint16 Id 解析目标芯片实例与引脚，I2C 同步写入 Output Port 寄存器，设置输出电平 | uint16 Id_u16, uint8 Level_u8 (0 或 1) | void | Std_ReturnType: E_OK / E_NOT_OK | 同步；可在任意任务上下文调用 | DET 校验: Level 非 0/1、无效 Id、未初始化；I2C 失败返回 E_NOT_OK 且输出不变 |

### 6.5 Gp_NCAxx39_GetDevFaultSig

| 接口名 | 类型 | 用途 | 输入 | 输出 | 返回值 | 时序/模式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gp_NCAxx39_GetDevFaultSig | 诊断 | 通过 uint16 Id 解析目标芯片实例，返回当前故障与诊断状态位掩码 | uint16 Id_u16 | uint32* Fault_pu32 (0 = 无故障) | Std_ReturnType: E_OK / E_NOT_OK | 同步；可在任意任务上下文调用 | 故障位包含: I2C 通信错误、配置校验错误、输出读回不一致、INT 超时；DET 校验: Null 指针、无效 Id、未初始化 |

### 6.6 接口设计规则应用说明

- 对外接口采用函数形式，不定义对外全局变量。
- 函数名前缀保留 `Gp_NCAxx39_`，不做 CamelCase 化。
- Init 和 MainFunction 返回 void（操作必然成功）；Set/Get 类接口返回 Std_ReturnType。
- 所有 Set/Get/GetDevFaultSig 接口实施参数 DET 校验（开关由 GP_NCAXX39_CFG_DEV_ERROR_DETECT 控制）。
- GetGpInSig 为同步接口（直接发起 I2C 读）；SetGpOutSig 为同步接口（直接发起 I2C 写）。
- MainFunction 为周期异步处理接口（INT 轮询 + 故障去抖 + 输出读回校验）。

---

## 7. 外部依赖与Callout定义

| 依赖项 | 依赖用途 | 选用方式 | 暂定接口 | 原因 |
| --- | --- | --- | --- | --- |
| I2C 寄存器写入 | 向芯片寄存器写入配置/输出数据 | Callout | Gp_NCAxx39_CalloutI2cWrite | I2C 事务细节项目相关，FC 不应绑定具体 MCAL I2C API |
| I2C 寄存器读取 | 从芯片寄存器读取输入/配置数据 | Callout | Gp_NCAxx39_CalloutI2cRead | I2C 事务细节项目相关，FC 不应绑定具体 MCAL I2C API |
| DIO 引脚读取 | INT 引脚电平采样 | Callout | Gp_NCAxx39_CalloutDioRead | 板级 DIO 通道映射项目相关 |
| DET 错误报告 | 开发错误检测上报 | 标准接口绑定 | Det_ReportError | 遵循 AUTOSAR DET 标准接口 |

### 7.1 接口统一性判定

- 已统一依赖: DET 错误报告采用标准 AUTOSAR Det_ReportError 接口绑定
- 未统一依赖: I2C 读写、DIO 读取——各自语义不同，不强制统一
- 需要Callout的依赖: I2C Write、I2C Read、DIO Read——均为项目/板级适配
- 判定理由:
  - I2C 读写操作涉及设备地址、寄存器地址、数据缓冲区、长度等参数，且不同 MCAL 实现 API 差异大 → Callout
  - DIO 读取涉及板级通道映射和可能的反相逻辑 → Callout
  - DET 报告遵循 AUTOSAR 标准 Det_ReportError 签名 → 标准接口绑定

### 7.2 Callout接口定义

#### 7.2.1 Gp_NCAxx39_CalloutI2cWrite

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCAxx39_CalloutI2cWrite(uint8 DevAddr_u8, uint8 Reg_u8, const uint8* Data_pu8, uint16 Size_u16)` | Writes `Size_u16` bytes from `Data_pu8` to register `Reg_u8` of I2C device at address `DevAddr_u8`. | Synchronous | Reentrant | E_OK: write completed successfully. E_NOT_OK: I2C transaction failed (NACK, bus error, timeout). | DevAddr_u8 must be a valid 7-bit I2C address (0x74–0x77 for NCA9539-Q1). Reg_u8 must be 0x00–0x07. Data_pu8 must be non-null. Size_u16 must be 1 or 2 (single register or register-pair write). | Project Adaptation | SRS-NCAxx39-INTF-0001, 0004; interface-selection rules §Callout | Formal |

#### 7.2.2 Gp_NCAxx39_CalloutI2cRead

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCAxx39_CalloutI2cRead(uint8 DevAddr_u8, uint8 Reg_u8, uint8* Data_pu8, uint16 Size_u16)` | Reads `Size_u16` bytes from register `Reg_u8` of I2C device at address `DevAddr_u8` into `Data_pu8`. Performs I2C write of command byte followed by repeated START and read. | Synchronous | Reentrant | E_OK: read completed successfully. E_NOT_OK: I2C transaction failed (NACK, bus error, timeout). | DevAddr_u8 must be a valid 7-bit I2C address (0x74–0x77). Reg_u8 must be 0x00–0x07. Data_pu8 must be non-null. Size_u16 must be 1 or 2. | Project Adaptation | SRS-NCAxx39-INTF-0003; interface-selection rules §Callout | Formal |

#### 7.2.3 Gp_NCAxx39_CalloutDioRead

| Interface Prototype | Description | Sync/Async | Reentrancy | Return Value | Basic Constraints | Implemented By | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Std_ReturnType Gp_NCAxx39_CalloutDioRead(uint16 DioChnId_u16, uint8* Level_pu8)` | Reads the logical level of the DIO channel identified by `DioChnId_u16` and writes the result (0 or 1) into `*Level_pu8`. Board-level inversion is handled inside the callout. | Synchronous | Reentrant | E_OK: read completed. E_NOT_OK: DIO channel invalid or read failed. | DioChnId_u16 must map to a configured DIO channel. Level_pu8 must be non-null. | Project Adaptation | SRS-NCAxx39-DIAG-0002; interface-selection rules §Callout | Conditional (INT pin ownership TBD) |

---

## 8. 全局参数定义

本节为空——模块不定义对外全局变量。

### 8.1 内部运行态说明

- 内部状态策略: 每实例维护独立的运行时数据结构，包含 DevMode、FaultStatus、DirCache[2]、OutCache[2]、PolCache[2]、FaultDebounce 计数器。所有内部变量在 Init 中显式初始化，不依赖编译器默认初始化。
- DET/故障状态策略: 故障状态以位掩码维护，包含 I2C 通信错误、配置校验错误、输出读回不一致、INT 超时等位。故障去抖通过连续失败计数器 + 阈值实现。
- 输入/输出缓存策略: OutCache 在 SetGpOutSig 时同步更新（与 I2C 写入原子）；输入读取直接通过 I2C 实时获取（不从缓存返回，保证数据新鲜度）。Init 阶段配置回读值写入 DirCache/PolCache 供后续校验。

---

## 9. 配置宏参定义

### 9.1 基础配置

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GP_NCAXX39_CFG_DEV_ERROR_DETECT | DET 错误检测全局开关 | Development Error Detect | STD_ON | SRS-NCAxx39-CFG-0008 | Gp_NCAxx39_Cfg.h | Formal |

### 9.2 功能相关配置

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GP_NCAXX39_CFG_MULTI_CHIP_NUM | 当前核管理的 NCA9539-Q1 芯片实例数 | Count Size | 0 | SRS-NCAxx39-CFG-0001 | Gp_NCAxx39_Cfg.h | Formal |

### 9.3 功能开关与行为选择

| Macro or Parameter | Purpose | Type | Default Value | Evidence | Usage Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GP_NCAXX39_CFG_REG_READBACK_VERIFY_ENABLE | 输出寄存器周期读回校验开关 | Feature Enable | STD_ON | SRS-NCAxx39-DIAG-0004 | Gp_NCAxx39_Cfg.h | Formal |

### 9.4 配置原则说明

- 不同项目的配置宏参值可以不同。
- Cfg.h 仅保留基础配置、功能开关、行为选择。常规寄存器初始值、时序参数、阈值和重试次数在 Cfg.c/CfgData.h 中以配置表方式组织。
- 宏标识符全大写，FC 名称部分转为大写 (`GP_NCAXX39_`)。
- 已有稳定对外接口承载的基本功能不重复生成功能开关宏。
- 每核实例数、硬件绑定表、阈值和重试次数默认不放入配置宏参清单。
- 项目中无标定流程需求，无标定参数定义。

---

## 10. 内存分配宏定义

| 内存段 | 目标内容 | 进入宏 | 退出宏 | 使用文件 | 备注 |
| --- | --- | --- | --- | --- | --- |
| CODE | 外部 API 和内部函数代码 | GP_NCAXX39_CODE_START | GP_NCAXX39_CODE_STOP | Gp_NCAxx39.c | 标准代码段 |
| CLEAR_FAR_DATA_COREx | 每核运行时变量（实例状态、故障去抖、缓存） | GP_NCAXX39_CLEAR_FAR_DATA_ALIGN4_COREx_START | GP_NCAXX39_CLEAR_FAR_DATA_ALIGN4_COREx_STOP | Gp_NCAxx39.c | per-core 独立数据区；x = 0..5 |
| CONST_FAR_DATA_COREx | 每核配置表（HWCfg 数组、SigMappingCfg） | GP_NCAXX39_CONST_FAR_DATA_ALIGN4_COREx_START | GP_NCAXX39_CONST_FAR_DATA_ALIGN4_COREx_STOP | Gp_NCAxx39_Cfg.c | per-core 独立常量区；x = 0..5 |
| CONST_FAR_DATA_GLOBAL | 全局共享常量 | GP_NCAXX39_CONST_FAR_DATA_ALIGN4_GLOBAL_START | GP_NCAXX39_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP | Gp_NCAxx39_Cfg.c | 全局共享配置（如有） |

### 10.1 MemMap策略

- 代码段规则: 所有函数代码放入 CODE 段，通过 GP_NCAXX39_CODE_START/STOP 界定。
- RAM变量段规则: 每核运行时变量放入独立 CLEAR_FAR_DATA_ALIGN4_COREx 段，保证多核数据隔离。
- ROM/配置/标定段规则: 每核独立配置表放入 CONST_FAR_DATA_ALIGN4_COREx 段；全局共享配置放入 CONST_FAR_DATA_ALIGN4_GLOBAL 段。不使用 NO_CLEAR 段（无暖复位保留需求）。
- 集成重定义预期: 项目集成时可通过 MemMap.h 将段宏重映射至实际链接脚本段名。

### 10.2 段宏使用边界

- 运行态默认使用 CLEAR_FAR_DATA_ALIGN4_COREx，保证每核独立数据区且上电清零。
- 配置常量存在按核归属（HWCfg 数组、SigMappingCfg），使用 CONST_FAR_DATA_ALIGN4_COREx；不使用单一全局 CONST 段。
- 不引入 NO_CLEAR 段（无暖复位数据保留需求）。
- 不引入 NEAR 段（无快速中断执行需求）。

### 10.3 MemMap包含关系

Gp_NCAxx39_MemMap.h 应被以下文件在段边界处包含：
- Gp_NCAxx39.c（CODE、CLEAR_FAR_DATA_COREx）
- Gp_NCAxx39_Cfg.c（CONST_FAR_DATA_COREx、CONST_FAR_DATA_GLOBAL）

---

## 11. 全局标定参数定义

Empty — 项目中无标定流程需求。方向、输出电平、极性反转均通过静态配置表承载。

---

## 12. 命名与符合性检查

### 12.1 命名规则应用

- 文件/模块命名规则: 文件名以 `Gp_NCAxx39` 为前缀，保留原始 FC 命名空间大小写。
- C标识符命名空间规则: 外部 API 和 Callout 函数以 `Gp_NCAxx39_` 为前缀；类型以 `Gp_NCAxx39_` 为前缀 + `Type` 后缀；枚举值以 `Gp_NCAxx39_` 为前缀 + `_e` 后缀。
- FC标识符规则: 保持 `Gp_NCAxx39` 作为顶层命名空间，不自动 CamelCase 化为 `GpNcaxx39`。
- 函数命名规则: `Gp_NCAxx39_[Action][Object]`，如 `Gp_NCAxx39_GetGpInSig`。
- 全局参数命名规则: 不定义对外全局变量。
- 类型命名规则: typedef enum → `Gp_NCAxx39_XxxType`；typedef struct → `Gp_NCAxx39_XxxType`。

### 12.2 符合性观察

- 观察1: 函数名前缀 `Gp_NCAxx39_` 与 aurix2g IoExtDev 命名空间一致。
- 观察2: 配置宏全大写 `GP_NCAXX39_CFG_*` 符合命名规则。
- 观察3: 接口命名使用语义风格 (`GetGpInSig` / `SetGpOutSig` / `GetDevFaultSig`)，符合 IoExtDev 层规范，避免寄存器风格命名 (`ReadInputPort`)。

---

## 13. 风险与待确认问题

### 13.0 架构风险与待确认总表

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | INT 引脚归属 | INT 引脚是否连接至 MCU 且 DIO 通道归属本模块未确认 | CalloutDioRead 接口定义、MainFunction INT 轮询逻辑 | 确认项目硬件原理图中 INT 引脚连接和 DIO 通道分配 | | 待评审 |
| R2 | RESET 引脚归属 | RESET 引脚是否归属本模块控制未确认 | 是否需要 ResetChip 接口和 CalloutDioWrite | 确认硬件设计中 RESET 引脚连接；若不归属本模块则 RESET 由硬件上拉管理 | | 待评审 |
| R3 | I2C Callout 事务粒度 | I2C Callout 接口当前设计为单寄存器读写，上层是否需要寄存器对（Port 0 + Port 1）连续读写以优化通信次数 | CalloutI2cRead/Write 的 Size_u16 参数语义 | 评估是否需要支持 Size_u16=2 的寄存器对读写（当前已设为 1 或 2） | | 待评审 |
| R4 | 故障去抖阈值 | I2C 故障去抖阈值 (FaultThreshold_u8) 和 INT 超时周期数未确定 | MainFunction 故障检测行为 | 根据 MainFunction 调用周期确定合理阈值：建议 I2C 故障阈值 3–5 次，INT 超时 10 个周期 | | 待评审 |
| R5 | 运行时方向变更 | 是否需要运行时动态重配置引脚方向 (SetGpDirSig) 和极性 (SetGpPolSig) | 外部接口数量 | 当前版本仅支持 Init 时标定配置；若项目需要运行时变更则增加接口 | | 待评审 |
| R6 | I2C 总线共享 | 同 I2C 总线是否挂载其他设备 | Callout 实现中的总线互斥策略 | 确认 I2C 总线拓扑；若存在多主或共享场景需增加互斥机制 | | 待评审 |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议。 | 待评审 |

---

### 13.1 接口遗漏风险清单

| 风险项 | 风险等级 | 说明 | 建议动作 |
| --- | --- | --- | --- |
| 缺少 SetGpDirSig | 低 | 若项目需要运行时变更引脚方向，当前架构未包含此接口 | 确认需求后可在下一版本增加 |
| 缺少 SetGpPolSig | 低 | 若项目需要运行时变更极性反转，当前架构未包含此接口 | 确认需求后可在下一版本增加 |
| 缺少整端口批量读写 | 低 | 若上层需要一次 I2C 事务读取/写入整个 8-bit 端口 | 确认需求后可在下一版本增加 |

### 13.2 待确认接口清单

| 接口名 | 来源需求 | 置信度 | 待确认原因 | 建议处理 |
| --- | --- | --- | --- | --- |
| Gp_NCAxx39_CalloutDioRead | SRS-NCAxx39-DIAG-0002 | 中 | INT 引脚 DIO 通道归属未确认 | 确认硬件设计后再定 |
| Gp_NCAxx39_CalloutDioWrite | SRS-NCAxx39-TIM-0002 | 低 | RESET 引脚归属未确认 | 确认硬件设计后再定 |

### 13.3 不建议直接生成的低置信度接口

| 接口名 | 推导依据 | 低置信度原因 | 建议 |
| --- | --- | --- | --- |
| Gp_NCAxx39_ResetChip | SRS-NCAxx39-TIM-0002 | RESET 引脚归属未确认 | 先确认硬件设计，不直接落代码 |

---

## 附录：架构元信息

- 架构版本: `V1`
- 架构状态: `Draft`
- 生成时间: 2026-05-26
- 生成/修订说明: 基于 SRS-Gp_NCAxx39 V0.1.0 初始架构生成。5 个外部接口、2 个 I2C Callout + 1 个 DIO Callout（条件项）、7 个必需文件 + 3 个条件文件、3 个配置宏参、CODE / CLEAR_FAR_DATA_COREx / CONST_FAR_DATA_COREx / CONST_FAR_DATA_GLOBAL 四类内存段。
- 版本策略: 仅正式架构文件 + 需求文档触发大版本升级。
- 发布条件: 所有真实风险项均为 `已评审`。
- 变更点总结:
  - 初版生成 (V1 Draft)
  - 外部接口: Gp_NCAxx39_Init, MainFunction, GetGpInSig, SetGpOutSig, GetDevFaultSig
  - 依赖 Callout: CalloutI2cWrite, CalloutI2cRead, CalloutDioRead (条件)
  - 文件集: 7 必需 + 3 条件 (Reg.h / Callout.h / Callout.c)

---

## 下一步：评审与发布引导

当架构状态为 `Draft` 时必须输出本节：

- 推荐评审方式 1：直接修改风险表中的 `状态` 和 `备注`。
- 推荐评审方式 2：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：故障阈值改为 3`。
- 如果所有风险项均认可，可回复：`全部已评审，R-OTHER 无其他建议，直接发布`。
- 如果某项需要修改，可回复：`R3 待修改，备注：I2C Callout 仅支持 Size=1`。
- 修改完成后仍保持 V1 `Draft`，直到所有真实风险项均为 `已评审` 后发布为 V1 `Released`。
- 草稿评审发布不升级版本。
