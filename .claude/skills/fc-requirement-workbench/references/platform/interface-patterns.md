# AURIX 2G 平台规范经验库

基于 FcStack AURIX2G 工程（G-Pulse G4 平台）提取的内置规范，用于需求生成时的模式参考和规则校验。

---

## 一、驱动接口模式

### 1.1 接口分类法则

| 类别 | 标识 | 说明 |
|------|------|------|
| `Init` | Init(void) | 初始化当前核的所有芯片/通道，必须在对应 MCAL 驱动 Init 之后调用 |
| `MainFunction` | MainFunction(void) | 周期性驱动函数，负责状态轮询、故障检测、pending 指令执行 |
| `GetDevModeInSig` | GetDevModeInSig(uint16 Id, uint8* DevMode) | 同步读取芯片/信号的实际模式 |
| `SetDevModeOutSig` | SetDevModeOutSig(uint16 Id, uint8 DevMode) | 异步设置芯片的目标模式（异步接口必须配 MainFunction） |
| `GetDevFaultSig` | GetDevFaultSig(uint16 Id, uint32* Fault) | 读取芯片故障信息 |
| `GetDiag` | GetXxxDiag(uint16 Id, uint32* Diag) | 读取诊断/状态数据 |
| `SetOutput` | SetXxxOutSig(uint16 Id, ...) | 设置输出信号参数（异步执行） |
| `GetRaw` | GetXxxXxxRaw(uint16 Id, uint16* Raw) | 读取原始采集值 |

### 1.2 MainFunction 接口规则（修正）

**规则：驱动中存在异步接口（Sync/Async 标注为 Asynchronous 的 Set* 操作或需要周期轮询状态/诊断），就必须提供 MainFunction 接口。**

判断逻辑：
1. 检查 `Sync/Async` 标注：`Asynchronous` → 需要 MainFunction
2. 检查是否有 SPI 通信依赖（寄存器周期性读出）→ 需要 MainFunction
3. 检查是否有周期性诊断/故障检测需求 → 需要 MainFunction
4. 纯 GPIO 控制（如 TJA1043 的 EN/STB 引脚直驱）且无 SPI 状态读回 → 可不需要 MainFunction

**实例对照：**

| 驱动 | 异步接口 | MainFunction | 理由 |
|------|---------|-------------|------|
| Gp_TLE92104 | SetHbOutSig, SetDevModeOutSig | 有 | SPI 控制电机驱动芯片，周期更新输出和模式 |
| Gp_TLF35584 | SetDevSigModeOut | 有 | SPI 读写 PMIC 寄存器，周期检测故障和喂狗 |
| Gp_DRV8889 | SetHbOutSig, SetDevModeOutSig | 有 | SPI 控制步进电机驱动芯片 |
| Gp_TPT1145 | SetOpMode | 有 | SPI CAN FD 收发器，扫描总线唤醒事件 |
| Gp_IoMcuAdc | - | 有 | 周期轮询 ADC 结果寄存器（非直读通道） |
| Gp_TJA1043 | -（EN/STB 直驱） | 无 | 纯 DIO 控制，无 SPI，状态立即生效 |
| Gp_IoMcuPwm | - | 无 | 操作立即下发 MCAL PWM 接口 |
| Gp_IoMcuDio | - | 无 | 操作立即下发 MCAL DIO 接口 |

### 1.3 信号 ID (uint16 Id) 设计规范

每个信号接口使用 `uint16 Id` 定位目标：
- 高位：Core 归属
- 中位：Chip/HW Channel Index
- 低位：Signal/Channel Index

通过 `SigMappingCfgType` 配置结构将 Id 映射到 `MapCoreId + MapChipIdx + MapChlIdx`。

### 1.4 驱动状态机模式

每个外部芯片驱动必须定义：

```
状态枚举：
- Unknown / Uninit  （未初始化）
- Init              （初始化中）
- Normal            （正常运行）
- Standby           （待机）
- Sleep             （睡眠）
- Fault / Failsafe  （故障/安全态）
```

示例（TJA1043）：
```c
Gp_TJA1043_DevMode_Unknown_e  = 0x00U
Gp_TJA1043_DevMode_Init_e     = 0x11U
Gp_TJA1043_DevMode_Normal_e   = 0x21U
Gp_TJA1043_DevMode_Standby_e  = 0x51U
Gp_TJA1043_DevMode_Sleep_e    = 0x61U
Gp_TJA1043_DevMode_Fault_e    = 0x71U
```

**编码规律**：
- `0x?1` = 可运行状态（Normal/Init）
- `0x?1` = 低功耗状态（Standby/Sleep）
- `0x?1` = 异常状态（Fault）
- 高位 = 状态分类，低位 = 子状态

---

## 二、多核与单核需求规范

### 2.1 多核架构

AURIX 2G 支持 6 核（Core0-Core5）：

```
Core ID 定义（所有模块统一）：
GP_xxx_CORE0_ID  = 0U
GP_xxx_CORE1_ID  = 1U
GP_xxx_CORE2_ID  = 2U
GP_xxx_CORE3_ID  = 3U
GP_xxx_CORE4_ID  = 4U
GP_xxx_CORE5_ID  = 5U
```

### 2.2 每核独立数据区

每个核有独立的运行时数据和配置数据区：

```
GP_TJA1043_VAR_CLEAR_UNSPECIFIED_CORE0_DATA   (6 个核各自独立)
GP_TJA1043_CONST_UNSPECIFIED_CORE0_DATA       (6 个核各自独立)
+ 1 个全局共享常量数据区 (GLOBAL_CONST_DATA)
```

**需求规范**：任何声明为 `Reentrancy: Non_Reentrancy` 的函数，当在多核场景使用时，每个核必须拥有独立的数据区和配置区，函数实现必须仅访问当前核的数据。

### 2.3 多核同步机制

**Gp_EcuM 跨核同步接口**：

```c
// 按核号初始化
Gp_EcuM_Core0Init(void);
Gp_EcuM_Core1Init(void);  // 条件编译：GP_ECUM_CORE_NUM_SUM > 1
...
Gp_EcuM_Core5Init(void);  // 条件编译：GP_ECUM_CORE_NUM_SUM > 5

// 跨核事件同步
Gp_EcuM_SetEvent(uint8 CoreId_u8);       // 某核完成，发送事件
Gp_EcuM_WaitSingleEvent(uint8 EventId);  // Master 等待单一事件
Gp_EcuM_WaitAllEvent(uint8 EventNum);    // Master 等待所有事件
```

**同步协议**：Magic 值 `GP_ECUM_SYNC_EVENT_MAGIC = 0x5555AAAAU` 用于验证同步事件的合法性。

### 2.4 主核从核区分

安全相关模块（TstM）有明确的主核约束：

```
Only Master Core shall call:
- Gp_TstM_Init()              // 仅主核初始化
- Gp_TstM_SwitchToRunPhase()  // 仅主核切换运行阶段
- Gp_TstM_ClearRunTimeTestResult()  // 仅主核清除结果

Reentrant by different cores:
- Gp_TstM_ExecStartupTestGroup()   // 各核独立执行
- Gp_TstM_ExecRunTimeTestGroup()   // 各核独立执行
```

### 2.5 中断向量表 - 核分配

```c
// 每核 + 每 VM（虚拟机）组合的中断向量表编号
GP_INTERRUPT_VEC_TABLE_CORE0_VM0 ~ CORE0_VM7  // Core0, VM0-VM7
...
GP_INTERRUPT_VEC_TABLE_CORE5_VM0 ~ CORE5_VM7  // Core5, VM0-VM7

// TOS (Trigger Output Selection) 每核不同
GP_INTERRUPT_TOS_CPU0 = 0U
GP_INTERRUPT_TOS_CPU1 = 2U   // AURIX2G 特殊：跳过了 1
GP_INTERRUPT_TOS_CPU2 = 3U
...
```

### 2.6 单核场景

当 `GP_ECUM_CORE_NUM_SUM = 1U` 时：
- 只有 `Gp_EcuM_Core0Init()` 存在
- 所有跨核同步接口通过条件编译裁剪
- 无需 SetEvent/WaitEvent
- 所有 ISR 绑定到单一向量表

