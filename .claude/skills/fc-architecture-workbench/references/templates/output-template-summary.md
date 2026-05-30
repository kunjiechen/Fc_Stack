# 《`<FC>` 软件架构设计》

**`<FC>`_软件架构设计**

**`<FC>` Software Architecture Design**

项目编号/Project number: `<FC>`
保密性/Security: 内部

**Document Properties**
Status: **草稿**
架构版本: **V1**
架构状态: **Draft**
Author: FC Architecture Workbench
Created: `<GenerationTime>`

**Approved Versions**

Current Document version **V1** is **Draft**.

**Approved Versions:**

- TBD

**Document Signatures**

| 版本 | 状态 | 审批人 | 日期 | 意见 |
| --- | --- | --- | --- | --- |
| V1 | Draft | TBD | TBD | TBD |

## 适用说明

本文档适用于 `<FC>` 模块的软件架构设计定义。本文档描述模块的外部接口、依赖接口、配置参数、状态机设计、故障设计、全局变量设计、内存分配与文件族设计，不描述详细实现方案、代码细节或测试用例步骤。

---

## 文档修订记录

| 版本 | 日期 | 作者 | 变更说明 | 状态 |
| --- | --- | --- | --- | --- |
| V1 | `<GenerationDate>` | FC Architecture Workbench | `<ChangeSummary>` | Draft |

---

## 目录

- [1 FC总结介绍](#1-fc总结介绍)
- [2 外部接口设计](#2-外部接口设计)
- [3 依赖接口设计](#3-依赖接口设计)
- [4 配置参数设计](#4-配置参数设计)
  - [4.1 配置宏参](#41-配置宏参)
  - [4.2 配置参数](#42-配置参数)
- [5 状态机设计](#5-状态机设计)
  - [5.1 芯片工作模式](#51-芯片工作模式)
  - [5.2 软件状态机](#52-软件状态机)
  - [5.3 状态转换详表](#53-状态转换详表)
- [6 故障设计](#6-故障设计)
  - [6.1 故障分类](#61-故障分类)
  - [6.2 故障策略维度定义](#62-故障策略维度定义)
  - [6.3 故障全链路表](#63-故障全链路表)
- [7 全局变量设计](#7-全局变量设计)
  - [7.1 全局变量](#71-全局变量)
  - [7.2 标定变量](#72-标定变量)
- [8 内存分段设计](#8-内存分段设计)
- [9 驱动文件设计](#9-驱动文件设计)
  - [9.1 文件列表](#91-文件列表)
  - [9.2 文件关系](#92-文件关系)
- [10 架构风险与待确认](#10-架构风险与待确认)
- [附录：架构元信息](#附录架构元信息)

---

## 1. FC总结介绍

- **架构版本**: `V1` / `V2` / `V3`
- **架构状态**: `Draft` / `Released`
- **生成时间**: `<GenerationTime>`
- **变更点总结**: (初版写"初版生成"；升级/更新时用一句话概括主要变化)
- **FC名称**: `<FC>`
- **FC功能介绍**: (中文完整段落；层级名、接口名、架构术语可保留英文)
- **应用场景**: (中文完整段落；层级名、接口名、架构术语可保留英文)
- **架构设计思路**: (中文完整段落；包含 MainFunction 决策及理由、Callout 归并策略、执行模型、关键设计取舍)
- **AUTOSAR架构层级**:
- **当前软件架构所处层级**: (e.g. `IoExtDev`, `IoHwAb`, `Cdd`, `Srv`)

说明：
- 当前软件架构所处层级填写项目的正式层级名，如 `IoExtDev`、`IoHwAb`、`Srv`、`Cdd` 等。
- 若项目已有固定层级归属，直接落正式结论，不展开过程性讨论。
- 版本号仅使用 `V1`、`V2`、`V3` 这种整数大版本，不使用 `V1.0`、`V1.1`。
- 仅需求文档输入时生成 `V1`；正式架构文件 + 需求文档输入时升级到下一大版本；草稿架构更新不升级版本。

---

## 2. 外部接口设计

架构层描述接口契约——做什么、边界在哪里、异常如何处理。所有接口使用统一格式，不展开实现细节。

### 2.x `<FC>_FunctionName`

**原型**: `Std_ReturnType <FC>_FunctionName(...)`

<一句话英文概述，描述该接口的职责和返回值含义>

**同步/异步**: Synchronous  |  **可重入**: Non-reentrant  |  **返回值**: `E_OK` / `E_NOT_OK`

**前置条件**: <初始化依赖、参数范围、状态约束、调用时序>
**异常处理**: <非法输入时的行为——DET 上报策略、失败时的状态保护、回退策略>

> 对于 Init：前置条件中说明"首次调用，不可重复初始化"；异常处理中说明配置校验失败、Callout 缺失等场景的失败保护和状态回退策略。不单独列出步骤表——步骤级展开属于详细设计范畴。

说明：
- 接口原型按项目正式风格展示，写出完整 C 函数原型。函数名前缀保留原始 FC/驱动名称。
- **Init** 和 **MainFunction**（如 Required）必须列入本节。
- Init 用**前置条件**和**异常处理**两个字段把初始化契约说清楚：校验什么、依赖什么、失败时状态如何保护。不需要逐步骤展开。
- MainFunction 在**前置条件**中说明调用周期约束，在描述段中概括周期执行的任务清单（如：状态轮询、故障去抖、模式检测）。
- 对外接口全量列出，不做遗漏。
- 格式为结构化列表（非超宽表）——便于人阅读和机器解析。

---

## 3. 依赖接口设计

依赖接口是 FC 对平台/硬件的需求声明——描述"我需要什么能力"，不描述"怎么实现"。每个依赖接口按类别归并，不逐引脚生成。隐藏依赖（多核→GetCoreId、延时→DelayUs、模拟量→AdcRead）需主动推导列出。

### 3.x `<FC>_CalloutXxx`

**原型**: `Std_ReturnType <FC>_CalloutXxx(uint16 Id_u16, ...)`

<一句话描述——此 Callout 统一了哪些硬件依赖，为何归并为一类>

**实现方**: MCAL / IoMcu / 项目适配层
**约束**: <参数合法性、板级反相归属、调用时序>

说明：
- 本节仅体现依赖接口（Callout 原型），紧接外部接口之后，不与外部接口混排。
- **函数名必须固化**：包含 `<FC>_Callout` 前缀（如 `Gp_TJA1043_CalloutDioWrite`），禁止使用不绑定 FC 的通用名。
- Callout 原型中不允许使用数组形参写法（`TxData_au8[]`），必须使用指针形参。
- `Implemented By` 可为 `MCAL`、`IoMcu`、`IoExtDev`、`Service Layer` 或 `Project Adaptation`。
- 不允许 FC 直接调用裸 MCAL API、直接操作寄存器或直接绑定具体驱动。
- **格式为结构化列表**（非超宽表）——架构关注契约边界，不逐字段罗列详细设计级信息。

---

## 4. 配置参数设计

提取前过滤：芯片自主行为的时间参数不提取。只有软件主动使用、且不同项目可能取不同值的参数才进入配置。

通过过滤后：**宏参体现功能开关，配置参数体现功能的参数**。

### 4.1 配置宏参

功能开关，每条独立展开。

#### `<FC>_CFG_<NAME>`

**类型**: `Feature Enable` / `Development Error Detect` / `Behavior Selection` / `Strategy Selection` / `Dependency Selection` / `Count Size`
**默认值**: `<default>`
**说明**: <一句话>
**来源**: <SRS 需求 ID>

### 4.2 配置参数

以 `<FC>_CfgType` 结构体为索引入口，按资源类别组织成员。声明在 `<FC>_CfgData.h`，定义在 `<FC>_Cfg.c`（CONST 段）。

#### `<FC>_CfgType` 结构体

```c
typedef struct
{
    /* ---- IO资源配置：直接展开，不用数组 ---- */
    uint16 <Pin>_DioId_u16;   // <说明>
    ...

    /* ---- 功能参数 ---- */
    uint16 <Param>_u16;        // <说明>
} <FC>_CfgType;
```

| 成员 | 类型 | 类别 | 说明 |
|------|------|------|------|
| `<Pin>_DioId_u16` | `uint16` | IO资源配置 | <引脚名> DIO 通道 ID |
| `<Param>_u16` | `uint16` | 功能参数 | <用途> |

说明：
- **IO资源配置**直接展开为独立成员（不用数组）。引脚型设备一把只有一个 CfgType。
- **寄存器配置**：寄存器多的建子结构体 `<FC>_RegCfgType`。位域多的寄存器整寄存器配置，不拆 bit。
- **通信配置**：SPI/I2C 设备建子结构体 `<FC>_SpiCfgType` / `<FC>_I2cCfgType`（含通道号、序列号等）。
- 仅当存在对应资源时才按需嵌套子结构体。

---

## 5. 状态机设计

本章定义完整的软件状态机——包含芯片硬件支持的工作模式 + 驱动层为管理这些模式所需的软件状态。是详细设计阶段状态机代码骨架的直接输入。

### 5.1 芯片工作模式

芯片硬件定义的运行模式（从数据手册提取，不做软件加工）。

| 模式名 | 硬件行为 | INH 状态 | 总线状态 | CAN 收发 | 功耗特征 |
| --- | --- | --- | --- | --- | --- |
| Normal | 正常收发，总线偏置 0.5VCC | HIGH | 在线 | 收发使能 | 正常 |
| Listen-only | 仅接收，发送器禁用，总线偏置 0.5VCC | HIGH | 在线 | 仅接收 | 正常 |
| Standby | 低功耗接收器监控总线，总线偏置到地 | HIGH | 在线（仅监控） | 禁用 | 低功耗 |
| Go-to-Sleep | 同 Standby + 发出 sleep 命令 | HIGH | 在线（仅监控） | 禁用 | 低功耗 |
| Sleep | 低功耗接收器，总线偏置到地，INH 浮空 | 浮空 | 在线（仅监控） | 禁用 | 极低功耗 |

### 5.2 软件状态机

驱动层为管理芯片模式引入的软件状态。在芯片工作模式之上增加了软件管控状态（UNINIT、过渡态等），且区分软件主动切换和硬件强制切换两种转换路径。

**5.2.1 状态枚举与编码**

| 状态名 | 编码 | 类型 | 说明 |
| --- | --- | --- | --- |
| UNINIT | 0x00 | 软件状态 | 模块加载后、Init 完成前的初始状态 |
| NORMAL | 0x01 | 芯片模式 | 正常收发模式，对应芯片 Normal |
| LISTEN_ONLY | 0x02 | 芯片模式 | 仅接收模式，对应芯片 Listen-only |
| STANDBY | 0x03 | 芯片模式 | 第一级低功耗，对应芯片 Standby |
| GO_TO_SLEEP | 0x04 | 软件过渡态 | 睡眠前过渡，对应芯片 Go-to-Sleep。th 到期后自动转 SLEEP |
| SLEEP | 0x05 | 芯片模式 | 第二级低功耗，对应芯片 Sleep |

**5.2.2 状态转换图**

```
                         ┌──────────┐
                Init ──→ │  UNINIT  │ (软件状态)
                         └──────────┘
                              │ Init Step6 完成
                              ▼
                   ┌─────────────────────┐
                   │   DEFAULT_MODE      │←──────────────────────┐
                   │ (NORMAL 或 STANDBY) │                       │
                   └──────┬──────────────┘                       │
                          │ SetDevModeOutSig                      │
                          ▼                                       │
          ┌──────────────────────────────────┐                    │
          │  NORMAL ←→ LISTEN_ONLY           │                    │
          │    ↓ SetDevMode(GO_TO_SLEEP)     │                    │
          │    ↓         ↕                   │                    │
          │ STANDBY ←→ GO_TO_SLEEP → SLEEP  │                    │
          └──────────────────────────────────┘                    │
                   │          │          │                        │
                   │ UVBAT    │ UVNOM    │ WAKE                   │
                   ▼          ▼          └────────────────────────┘
               STANDBY      SLEEP      (Wake→Standby→Normal)
              (硬件强制)   (硬件强制)

软件主动切换: SetDevModeOutSig() → CalloutDioWrite 控制 STB_N/EN
硬件强制切换: MainFunction 中 DetectModeChange() 异步检测
过渡态: GO_TO_SLEEP — 保持 th 后芯片硬件自动转入 SLEEP，软件在 MainFunction 中确认
```

**5.2.3 软件状态机变量设计**

状态机相关的运行时变量（定义在 `<FC>.c` 中）：

| 变量 | 类型 | 说明 | 生命周期 |
| --- | --- | --- | --- |
| `ModeState_e` | enum | 当前软件状态（含 UNINIT + 5 个芯片模式 + 过渡态） | Init 置 DEFAULT；SetDevModeOutSig/MainFunction 更新 |
| `RequestedMode_e` | enum | 最近一次 SetDevModeOutSig 请求的目标模式（用于 GO_TO_SLEEP 过渡态校验） | SetDevModeOutSig 写入；MainFunction 确认后清除 |
| `LastModeBeforeSleep_e` | enum | 进入 Sleep 前的模式（用于 UV 恢复后还原） | 进入 Sleep 前锁存；UV 恢复后使用 |

### 5.3 状态转换详表

| 当前状态 | 触发事件 | 目标状态 | 触发源 | 软件动作 | 芯片进入动作 | 时序约束 |
| --- | --- | --- | --- | --- | --- | --- |
| UNINIT | `Init()` Step6 完成 | DEFAULT_MODE | 软件 | 设置 ModeState=DEFAULT；清零故障标志和计数器 | 按 STB_N/EN 进入对应芯片模式 | — |
| NORMAL | `SetDevModeOutSig(LISTEN_ONLY)` | LISTEN_ONLY | 软件 | 查模式真值表 → CalloutDioWrite(STB_N=H, EN=L)；更新 ModeState | 禁用发送器 | 切换后等 ≥8μs 再读 ERR_N |
| LISTEN_ONLY | `SetDevModeOutSig(NORMAL)` | NORMAL | 软件 | CalloutDioWrite(STB_N=H, EN=H)；更新 ModeState | 使能发送器 | 同上 |
| NORMAL | `SetDevModeOutSig(STANDBY)` | STANDBY | 软件 | CalloutDioWrite(STB_N=L, EN=L)；更新 ModeState | 总线偏置到地；仅低功耗接收器 | — |
| STANDBY | `SetDevModeOutSig(NORMAL)` | NORMAL | 软件 | CalloutDioWrite(STB_N=H, EN=H)；更新 ModeState | 总线偏置回 0.5VCC | 切换后等 ≥8μs |
| NORMAL | `SetDevModeOutSig(GO_TO_SLEEP)` | GO_TO_SLEEP | 软件 | 锁存 RequestedMode=SLEEP；CalloutDioWrite(STB_N=L, EN=H)；更新 ModeState=GO_TO_SLEEP；启动 th 计时 | 启动 th 计时器 | th=20~50μs 后芯片自动转 SLEEP |
| GO_TO_SLEEP | MainFunction 检测到 th 到期 + INH=LOW | SLEEP | 硬件→软件确认 | 锁存 LastModeBeforeSleep；更新 ModeState=SLEEP | INH 浮空 | th=20~50μs |
| GO_TO_SLEEP | STB_N/EN 变化或 Wake 置位（th 到期前） | 对应模式 | 硬件 | MainFunction 检测 → 取消 sleep；更新 ModeState | 取消 Sleep 进入 | — |
| NORMAL / LISTEN_ONLY | MainFunction 检测到 INH=LOW + INH 之前为 HIGH（UVNOM 判定） | SLEEP | 硬件→软件确认 | 锁存 LastModeBeforeSleep；记录欠压事件（§6.3）；更新 ModeState=SLEEP | INH 浮空；总线偏置到地 | tdet(uv)=100~350ms |
| 任意 | MainFunction 检测到状态机意外为 STANDBY + VBAT 欠压（UVBAT 判定） | STANDBY | 硬件→软件确认 | 记录 VBAT 欠压事件（§6.3） | 总线脱离（零负载） | — |
| STANDBY / SLEEP | MainFunction 检测到 Wake 标志置位（ERR_N/RXD 为 LOW） | STANDBY | 硬件→软件确认 | 清除 UVNOM 定时器；更新 ModeState=STANDBY；调用 HandleWakeReason 判定唤醒源 | INH 激活 | twake=5~50μs（本地）/ 唤醒模式 0.5~2ms（远程） |
| SLEEP | UVNOM 恢复（INH 重新变 HIGH + VCC/VIO 恢复） | 按 STB_N/EN 恢复 | 硬件→软件确认 | MainFunction 检测 → 查 LastModeBeforeSleep → 重新初始化 → 更新 ModeState | INH 激活 | trec(uv)=1~5ms |
| STANDBY | UVBAT 恢复 | 按 STB_N/EN 恢复 | 硬件→软件确认 | MainFunction 检测 → 确认模式 → 更新 ModeState | 总线重新连接 | — |

说明：
- **触发源**：软件 = API 调用直接控制；硬件→软件确认 = 芯片硬件行为先在 MainFunction 中检测到，软件确认后更新状态变量。
- **软件动作**列是驱动代码执行的操作——这是软件状态机和芯片状态机耦合的关键列。
- **芯片进入动作**列描述芯片硬件行为，软件不可控，仅能观测。

---

## 6. 故障设计

本章定义每条故障的检测→确认→响应→快照→恢复→清除全生命周期。是详细设计阶段 MainFunction 故障处理骨架和故障存储结构的直接输入。

### 6.1 故障分类

| 分类 | 说明 | 示例 |
| --- | --- | --- |
| `hardware_chip` | 芯片硬件检测并上报的故障，通过引脚电平或寄存器标志反映 | UVNOM、UVBAT、过温、TXD 超时、总线短路 |
| `software_state` | 软件运行时状态异常 | 未初始化访问、状态机非法转换 |
| `software_param` | API 调用参数非法 | 空指针、超范围参数、非法模式值 |

### 6.2 故障策略维度定义

每条故障从触发到闭环需定义以下 6 个策略维度。架构层给出策略决策，详细设计层按决策实现具体逻辑。

| 策略维度 | 定义 | 架构层需决策的内容 | 典型选项 |
| --- | --- | --- | --- |
| **确认策略** | 故障触发后，如何判定它是真实故障而非瞬态干扰 | 确认方式 + 阈值 | `芯片自判定` / `连续 2 次 MainFunction` / `连续 3 次 MainFunction` |
| **故障响应** | 确认后立即执行的动作 | 软件动作粒度 | `LogOnly` / `DET+ReturnError` / `DisableTx` / `ForceSleep` |
| **快照策略** | 故障确认时刻锁存哪些运行时数据，用于根因分析 | 锁存数据范围 | `None` / `ModeSnapshot` / `PinLevelSnapshot` / `FullContext`（具体字段待项目确认） |
| **恢复策略** | 故障条件消失后，如何恢复正常运行 | 恢复方式 | `Auto`（芯片自恢复） / `Manual`（软件主动恢复） / `Reset`（需复位） / `Fatal`（不可恢复） |
| **清除策略** | 故障恢复后，如何清除故障标志和快照数据 | 清除条件 | `EnterNormal` / `ReadClear` / `ApiClear` / `PowerOnReset` |
| **影响范围** | 故障存在期间，哪些功能受影响 | 影响的功能域 | `FullChip` / `TxOnly` / `SingleCall` / `BusDisconnect` |

### 6.3 故障全链路表

| 故障名称 | 分类 | 检测机制 | 确认策略 | 故障响应 | 快照策略 | 恢复策略 | 清除策略 | 影响范围 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UVNOM | hardware_chip | VCC/VIO 欠压 > tdet(uv) → 芯片进 Sleep，INH 浮空。MainFunction 中 DetectModeChange 检测 INH=LOW + 状态机变化 | 连续 2 次 MainFunction 确认 | 记录欠压事件；DET 上报；锁存 LastModeBeforeSleep | ModeSnapshot（锁存当前模式） | Auto（VCC+VIO 恢复 > trec(uv) 后芯片自动退出） | PowerOnReset（重新初始化） | FullChip |
| UVBAT | hardware_chip | VBAT < Vuvd(VBAT) → 芯片进 Standby，总线脱离。MainFunction 中 DetectModeChange 检测 | 连续 2 次 MainFunction 确认 | 记录 VBAT 欠压事件 | ModeSnapshot | Auto（VBAT 恢复后芯片自动恢复） | Auto（VBAT 恢复自动清除） | BusDisconnect |
| TXD 超时 | hardware_chip | TXD 持续显性 > tto(dom)TXD → 芯片禁用发送器。MainFunction 在 Listen-only 模式通过 PollErrN 读 Local failure | 芯片自判定 | 记录本地故障；DET 上报 | None | Auto（MCU 释放 TXD 后芯片自动恢复） | EnterNormal | TxOnly |
| 过温 | hardware_chip | 结温 > Tj(sd) → 芯片禁用发送器。MainFunction 中 PollErrN 读 Local failure | 芯片自判定 | 记录过温事件；DET 上报 | FullContext（故障计数+模式） | Auto（降温后芯片自动恢复） | Auto（降温自动清除） | TxOnly |
| 总线短路 | hardware_chip | 4 对 TXD 显隐边沿内检测 CANH/CANL 短路 → Bus failure 标志置位。Normal 模式通过 PollErrN 读取 | 芯片自判定 | 记录总线故障；DET 上报 | None | Manual（重新进入 Normal 重试） | EnterNormal 或 PowerOnReset | TxOnly |
| 未初始化访问 | software_state | 各 API 入口检查初始化标志 | 单次触发即确认 | DET 上报；返回 E_NOT_OK | FullContext（调用 API ID + 参数） | Manual（调用 Init 后恢复） | ApiClear（Init 成功后清除） | SingleCall |
| 非法参数 | software_param | 各 API 入口检查参数范围/指针非空 | 单次触发即确认 | DET 上报；返回 E_NOT_OK | FullContext（非法参数值 + API ID） | Manual（调用方修正参数） | Auto（仅当次返回错误） | SingleCall |
| 非法状态转换 | software_state | SetDevModeOutSig 检查目标模式是否在 §5.3 合法转换集合中 | 单次触发即确认 | DET 上报；返回 E_NOT_OK | FullContext（请求模式+当前模式） | Manual（调用方传入合法模式） | Auto（仅当次返回错误） | SingleCall |

说明：
- **确认策略**：芯片硬件自判定故障无需软件去抖。仅外部信号读取类故障（INH 判断欠压）需多次确认防瞬态。
- **快照策略**：`None`=芯片行为确定，快照无额外诊断价值。`FullContext`=锁存数据辅助根因分析，具体字段由项目诊断需求确认。
- ASIL-D 要求硬件故障+软件故障全覆盖。

---

## 7. 全局变量设计

本章定义模块对外暴露的全局变量和标定可调参数。运行时状态变量（ModeState、FaultFlags 等）在 §5 状态机和 §6 故障设计章节中直接定义，不在此处重复汇总。

### 7.1 全局变量

| 变量 | 状态 | 说明 |
| --- | --- | --- |
| `Empty` | `Empty` | 架构不允许对外提供全局变量输出。所有外部访问通过 §2 的函数接口。 |


### 7.2 标定变量

| 变量 | 类型 | 默认值 | 说明 | 状态 |
| --- | --- | --- | --- | --- |
| `Empty` | `N/A` | `N/A` | 当前无确认的标定变量。阈值和时序参数均归类为编译期配置（§4），不属于标定流程可调参数。 | `Empty` |

说明：
- 标定变量仅在项目明确需要标定工具链时填充，IoExtDev 族默认 Empty。
- 若项目后续引入标定需求（如可调故障阈值、可调去抖次数），在此节增加对应变量并标注 `Conditional`。

---

## 8. 内存分段设计

| Memory Section | Target Content | Start Macro | Stop Macro | Used Files | Notes |
| --- | --- | --- | --- | --- | --- |
| CODE | All external API implementations and internal static helper functions. | `FC_CODE_START` | `FC_CODE_STOP` | `<FC>.c`, `<FC>_Callout.c` | Standard CODE section. |
| RUNTIME RAM | Runtime state variables defined in §5/§6: state machine, fault flags, debounce counters, DET buffer, snapshot storage. | `FC_CLEAR_FAR_DATA_ALIGN4_START` | `FC_CLEAR_FAR_DATA_ALIGN4_STOP` | `<FC>.c` | Default `CLEAR_FAR_DATA`. Single-core: global（不标注核号）。Multi-core: per-core with `COREx` notation. |
| CONST (global shared) | Configuration data shared across cores: mode truth tables, default values. | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_START` | `FC_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP` | `<FC>_Cfg.c`, `<FC>_CfgData.h` | Shared config constants. |
| CONST (per core) | Per-core configuration tables: pin mapping tables, per-core instance configuration. | `FC_CONST_FAR_DATA_ALIGN4_COREx_START` | `FC_CONST_FAR_DATA_ALIGN4_COREx_STOP` | `<FC>_Cfg.c`, `<FC>_CfgData.h` | Each core has its own config data region. |
| CALIB | Calibration variables (§7.3). | `FC_CONST_FAR_DATA_ALIGN4_CALI_START` | `FC_CONST_FAR_DATA_ALIGN4_CALI_STOP` | `<FC>_Cali.c` / `<FC>_CfgData.h` | Only rendered when §7.3 is not Empty. |

说明：
- `CONST` 不能默认只给 GLOBAL；必须同时包含 GLOBAL 和 per-core。
- 仅当 FC 控制 SPI/I2C/寄存器型外设时，才增加 `REG CONST` 行。引脚直连型设备不渲染。
- 仅当 §7.3 非空时，才渲染 `CALIB` 行。
- RUNTIME RAM 段承载 §5/§6 中的运行时状态变量（ModeState、FaultFlags 等）。单核使用 global 段（不标注具体核号），多核使用 COREx 模式。

---

## 9. 驱动文件设计

### 9.1 文件列表

| File | Required/Optional | Responsibility | Key Content |
| --- | --- | --- | --- |
| `<FC>.c` | Required | Driver implementation file. | External API implementations (§2), runtime state variables (§5, §6). |
| `<FC>.h` | Required | External interface header file. | External API prototypes, `CODE_START/STOP` section macros. |
| `<FC>_Types.h` | Required | Type definitions header file. | State enums (§5.2), fault flag bit definitions (§6.3), variable struct types (§5, §6), pin index enums, config container structs. |
| `<FC>_Cfg.h` | Required | Configuration macro header file. | Feature switches, behavior selection macros (§4.1). Includes `Std_Types.h`. |
| `<FC>_Cfg.c` | Required | Configuration data implementation file. | Pin mapping tables (§4.2), mode control truth tables, per-core config tables. |
| `<FC>_CfgData.h` | Required | Configuration data declaration header file. | `extern` declarations for config tables and containers. |
| `<FC>_Callout.h` | Conditional | Platform adaptation interface header file. | Callout prototypes (§3). Required when Callout dependencies exist. |
| `<FC>_Callout.c` | Conditional | Platform adaptation implementation file. | Callout integration stubs. Required when Callout dependencies exist. |
| `<FC>_MemMap.h` | Required | Memory section mapping header file. | MemMap macro definitions (§8). |

### 9.2 文件关系

| File | Direct Dependency | Relationship Description |
| --- | --- | --- |
| `<FC>_Cfg.h` | `Std_Types.h` (external) | References `Std_ReturnType`, `uint8/uint16/uint32`, `boolean`, `STD_ON/STD_OFF`. |
| `<FC>_Types.h` | `<FC>_Cfg.h` | Type definitions depend on configuration macros. |
| `<FC>_Callout.h` | `<FC>_Types.h` | Callout prototypes reference FC public types. |
| `<FC>_CfgData.h` | `<FC>_Types.h` | Config data declarations reference types (pin index enum, config struct). |
| `<FC>.h` | `<FC>_Types.h` | External API header uses FC types in prototypes. |
| `<FC>.c` | `<FC>.h` | Implements external APIs. |
| `<FC>.c` | `<FC>_Callout.h` | Calls hardware and platform callouts (§3). |
| `<FC>.c` | `<FC>_MemMap.h` | Places code and runtime data into memory sections (§8). |
| `<FC>_Cfg.c` | `<FC>_CfgData.h` | Defines config tables. |
| `<FC>_Cfg.c` | `<FC>_MemMap.h` | Places config const data into memory sections. |
| `<FC>_Callout.c` | `<FC>_Callout.h` | Implements callout stubs. |
| `<FC>_Callout.c` | `<FC>_MemMap.h` | Places callout adaptation code into memory sections. |
| `<FC>_MemMap.h` | All FC-created section-managed files | Included at section boundaries. |

说明：
- 仅当 FC 控制 SPI/I2C/寄存器型外设时，才渲染 `<FC>_Reg.h` 行。引脚直连型不渲染。
- 若 FC 存在 Callout 依赖，必须同时列出 `<FC>_Callout.h` 与 `<FC>_Callout.c`。

---

## 10. 架构风险与待确认

填写说明：
- 可以直接修改下表的 `状态` 和 `备注`，也可以在当前窗口直接回复。
- `状态` 只允许填写：`待评审`、`已评审`、`待修改`。

| 索引 | 问题项 | 问题/风险 | 影响 | 建议动作 | 备注 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Pending item | 中文描述风险或待确认问题。 | 中文描述影响范围。 | 中文描述建议动作。 | 用户填写。 | `待评审` |
| R-OTHER | 其他 | 用户补充的其他建议或风险。 | 用户填写。 | 用户填写。 | 无其他建议。 | `待评审` |

说明：
- 每条风险项必须有稳定索引。必须保留 `R-OTHER` / `其他` 行。
- 若任一真实风险项仍为 `待评审` 或 `待修改`，架构状态必须保持 `Draft`。
- 所有真实风险项均为 `已评审` 后，才允许从 `Draft` 发布为 `Released`。

---

## 附录：架构元信息

- **架构版本**: `V1` / `V2` / `V3`
- **架构状态**: `Draft` / `Released`
- **生成时间**: `<GenerationTime>`
- **生成/修订说明**:
- **版本策略**: 仅正式架构文件 + 需求文档触发大版本升级。
- **发布条件**: 所有真实风险项均为 `已评审`。
- **变更点总结【简洁版】**:
  - 初版生成 / 草稿更新 / 正式版本升级。
  - 外部接口、依赖接口、配置、状态机、故障设计、全局变量、MemMap、文件结构或风险状态变化。

---

## 下一步：评审与发布引导

当前架构状态为 **V1 Draft**。请通过以下方式完成评审：

- **推荐评审方式 1**：直接修改第 10 章风险表中的 `状态` 和 `备注` 列。
- **推荐评审方式 2**：在当前窗口回复，例如 `R1、R2 已评审；R4 待修改，备注：按 xxx 方案调整`。
- 如果所有风险项均认可，可回复：**`全部已评审，R-OTHER 无其他建议，直接发布`**。
- 修改完成后仍保持 `V1 Draft`，直到所有真实风险项均为 `已评审` 后发布为 **V1 Released**。
- 草稿评审发布不升级版本；只有正式架构文件 + 新需求文档才升级到下一大版本。
