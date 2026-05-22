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

---

## 三、配置需求规范

### 3.1 配置三件套

每个模块的配置由三个文件组成：

| 文件 | 命名 | 内容 |
|------|------|------|
| CfgData.h | `Gp_xxx_CfgData.h` | 集成生成的配置数据（从 Conf/ 目录经过工具链生成） |
| Cfg.h | `Gp_xxx_Cfg.h` | 预编译配置常量和开关 |
| MemMap.h | `Gp_xxx_MemMap.h` | 内存分区映射（CODE/DATA/CONST 段分配） |

### 3.2 配置容器分级

```
GlobalCfg                   ← 驱动全局配置
├── HWCfg_cptst             ← 硬件通道配置指针
│   ├── DevId_te           ← 芯片型号（支持同驱动多型号）
│   ├── EN_u16 / STB_u16   ← 芯片控制引脚（DIO Channel ID）
│   └── ...
├── MultiChipNum_u8         ← 每核管理的芯片数量
└── ChipCfg[0..N]           ← 每芯片配置
    ├── SpiChnId            ← SPI 通道索引
    ├── SpiSeqId            ← SPI 序列索引
    ├── PwmChnId[3]         ← PWM 通道索引
    └── EnChnId             ← 使能引脚 DIO Channel
```

### 3.3 预编译配置开关

```c
GP_xxx_SPEC_MCUIF         // MCU 接口选择：IFXMCAL / 未定义
GP_xxx_DRIVER_USED_FOR    // 驱动用途：BOOT / APP
GP_xxx_SETDAC_ENABLE      // 功能开关：DAC 功能启用
GP_xxx_GETCOUNT_ENABLE    // 功能开关：计数读取功能启用
GP_IRQ_CFG_DEVICE_SEL     // 设备选择：AURIX2G / AURIX3G
GP_IRQ_CFG_KEYWORD_SEL    // 编译器选择：COMPILER_DEFAULT / MANUAL_WRITE
GP_IRQ_CFG_PROJ_SEL       // 项目类型：HV（Hypervisor）/ NO_HV
GP_ECUM_CORE_NUM_SUM      // 核数：1-6
GP_ECUM_CSRM_SUPPORT      // CSRM 支持开关
GP_RSTM_PROJ_TYPE_SEL     // 项目类型：APP / BOOT / APP_NO_BOOT
```

### 3.4 信号映射配置

```c
typedef struct Gp_xxx_SigMapCfg {
    uint32 MapCoreId_u32;     // 信号归属核
    uint8  MapChipIdx_u8;     // 信号归属芯片索引
    uint8  MapChlIdx_u8;      // 信号归属通道索引（如半桥/PWM 索引）
} Gp_xxx_SigMapCfgType;
```

此结构用于将上层 uint16 Id 映射为硬件通道。ASW 通过 Id 与硬件解耦。

### 3.5 多芯片实例配置

```c
typedef struct Gp_xxx_GlobalCfg {
    const Gp_xxx_HWCHCfgType *HWCfg_cptst;  // 硬件配置数组
    uint8 MultiChipNum_u8;                   // 芯片数量（支持 0-5 个独立芯片）
} Gp_xxx_GlobalCfgType;
```

---

## 四、安全需求规范

### 4.1 SafeTpack 安全包分层

```
TstM  (Test Manager)     ← 测试调度与生命周期管理
├── TstHnd (Test Handler) ← 单个测试的执行框架
│   └── TstLib/*          ← 具体测试库实现
│       ├── Gp_Lbist          （Logic BIST）
│       ├── Gp_Monbist        （Memory On-Line BIST）
│       ├── Gp_VmtMbist       （VMT MBIST）
│       ├── Gp_SfrTst         （特殊功能寄存器测试）
│       ├── Gp_RegMon         （寄存器监控）
│       ├── Gp_StmMon         （系统定时器监控）
│       ├── Gp_SmuAliveAlm    （SMU 存活告警）
│       ├── Gp_FwCheck        （固件完整性检查）
│       ├── Gp_ConvctrlTst    （转换器控制测试）
│       ├── Gp_DtsTst         （DTS 测试）
│       └── Gp_PflsIntegCheck （PFlash 完整性检查）
├── TstApp (Test Application) ← 应用层测试接口
└── Smc   (Safety Monitor Control)
    ├── Gp_ClkMonitor     （时钟监控）
    ├── Gp_VolMonitor     （电压监控）
    ├── Gp_DtsMonitor     （温度监控）
    ├── Gp_Ap             （应用监控）
    ├── Gp_RamSpr         （RAM 特殊保护）
    └── Gp_EndInitLib     （初始化结束保护）
```

### 4.2 安全测试生命周期

```
开机 PreRun 测试阶段：
  Gp_TstM_Init() → Gp_TstM_ExecStartupTestGroup(0, N) → Gp_TstM_SwitchToRunPhase()

运行阶段：
  Gp_TstM_ExecRunTimeTestGroup(0, M)  ← 周期性调用
  Gp_TstM_ClearRunTimeTestResult()    ← 按需清除
```

**关键约束**：
- PreRun 测试失败 → 系统不进 RunPhase，安全状态
- Runtime 测试失败 → 记录故障，可能触发安全状态
- 仅 Master Core 管理生命周期切换

### 4.3 WDG 看门狗模式

TLF35584 PMIC 支持 5 种看门狗组合：

```c
GP_TLF35584_FWD_SPI             // 仅功能狗 + SPI 喂狗
GP_TLF35584_FWD_WWD_SPI         // 功能狗 + 窗口狗 + SPI 喂狗
GP_TLF35584_WWD_WDI             // 窗口狗 + WDI 引脚喂狗
GP_TLF35584_WWD_SPI             // 窗口狗 + SPI 喂狗
GP_TLF35584_FWD_SPI_WWD_WDI     // 功能狗(SPI) + 窗口狗(WDI)
```

窗口狗时序参数：
```
Closed Window: 20ms / 30ms / 40ms / 100ms
Open Window:   20ms / 30ms / 40ms / 100ms
时间基准: 0.1ms / 1ms
```

### 4.4 故障处理规范

**故障去抖（Fault Debounce）**：
```c
typedef struct {
    uint32 FaultHistoryCnt_u32;  // 故障持续时间累计
    uint8  ReadFaultCnt_u8;      // 连续读到故障的次数
    uint8  FaultThreshold_u8;    // 故障确认阈值
} Gp_TLF35584_FaultDebonceDataType;
```

**故障分类**：
```c
GP_TLF35584_SPI_ERR              // 位0：SPI通信错误
GP_TLF35584_POWN_OFF_ERR         // 位1：掉电错误
GP_TLF35584_INIT_ERR             // 位2：初始化错误
GP_TLF35584_SYSTEM_ERR           // 位3：系统错误
GP_TLF35584_WAKE_UP_SOURCE_ERR   // 位4：唤醒源错误
GP_TLF35584_PROTECT_REG_ERR      // 位5：保护寄存器错误
GP_TLF35584_PORST_FAIL_ERROR     // 位6：上电复位失败
```

**安全状态分级（RstM）**：
```
GP_RSTM_SAFE_STATE_FLAG_FALSE        // 无安全状态
GP_RSTM_SAFE_STATE_FLAG_TRUE_L1      // 一级安全状态（可恢复）
GP_RSTM_SAFE_STATE_FLAG_TRUE_L2      // 二级安全状态（需复位）
```

### 4.5 复位管理（Gp_RstM）

```c
// 复位执行
Gp_RstM_PerformReset(RstId, CoreId, RstType);

// 获取上次复位类型
Gp_RstM_GetLastRstTypeInfo(RstTypePlt, RstTypeMcal, RstId, RstCoreId);

// 获取错误复位总次数
Gp_RstM_GetErrRstTotalCount();

// 获取安全状态标志
Gp_RstM_GetSafeStateInfo();

// NoClear 数据跨复位保存
Gp_RstM_NoClearDataRecord(DataId, DataLen, Data);    // 记录
Gp_RstM_GetNoClearDataAddr(DataId, &Addr);            // 读取
Gp_RstM_NoClearDataSaveToNvm();                       // 保存到 NVM
```

---

## 五、状态管理需求规范

### 5.1 系统状态机（Gp_SysState）

```c
// 初始化
Gp_SysState_InitMemory();      // 必须先调用，初始化内部变量
Gp_SysState_Init();            // 初始化并记录 BOOT 阶段

// 周期状态切换
Gp_SysState_MainFunction();    // 系统主状态机切换

// 状态获取
Gp_SysState_GetState();        // 返回 Gp_SysState_StateType

// 状态记录
Gp_SysState_RecordState(PhaseAndState); // 记录当前阶段和状态

// 状态切换动作
Gp_SysState_SwitchAction(Switch);       // 执行特定切换路径
```

### 5.2 ECU 启停状态机（Gp_EcuStpShdn）

```
状态：
- UNDEF         （未定义）
- NORM          （正常运行）
- SAFE          （安全状态）
- TRYPWRSHDN    （尝试下电关闭）

接口：
- Gp_EcuStpShdn_Startup()              // 启动流程（多核时序、PreRun 测试、MCAL 初始化、SBC 自检）
- Gp_EcuStpShdn_Mainfunction()         // 周期运行（MCU 运行时测试）
- Gp_EcuStpShdn_SetSafeSta()           // 设置安全状态
- Gp_EcuStpShdn_SetTryPwrShdnSta()     // 设置尝试下电
- Gp_EcuStpShdn_GetSta()               // 获取当前状态
- Gp_EcuStpShdn_PwrOff()               // 执行下电
```

### 5.3 芯片设备状态（通用模式）

所有外部芯片驱动遵循统一的状态定义：

| 状态值 | 含义 | 典型场景 |
|--------|------|---------|
| `0x00` | Unknown | 未初始化/异常 |
| `0x11` | Init | 初始化完成但未运行 |
| `0x21` | Normal | 正常运行 |
| `0x51` | Standby | 低功耗待机（可快速恢复） |
| `0x61` | Sleep | 睡眠（需唤醒流程） |
| `0x71` | Fault / Failsafe | 故障保护状态 |

---

## 六、诊断需求规范

### 6.1 诊断接口模式

**三级诊断层次**：

```
Level 1 - 芯片级故障诊断（外部芯片）
  GetDevFaultSig()      → uint32 位掩码，每位对应一种故障

Level 2 - 信号级诊断（MCU 外设）
  GetXxxSigDiag()       → uint32，包含信号有效性和硬件状态

Level 3 - 系统级诊断（BswSys/RtMon）
  StackMonitor / CpuLoad / CsaMonitor → 运行时健康监控
```

### 6.2 诊断错误码设计

模块级错误码使用位掩码设计（每类错误占不同位）：

```c
// TJA1043
GP_TJA1043_IF_NO_ERR            = 0x00U  // 无错误
GP_TJA1043_IF_UNINITED          = 0x01U  // 未初始化
GP_TJA1043_IF_INVALID_ARG       = 0x02U  // 参数无效
GP_TJA1043_IF_INCONSISTENT_CORE = 0x04U  // 核归属不一致
GP_TJA1043_IF_HWCFGERR_CORE     = 0x10U  // 硬件配置错误
```

**规范**：
- 错误码=0 表示无错误
- 每位代表一个故障维度
- 支持多错误同时标记（位或运算）

### 6.3 SPI 通信错误检测

所有依赖 SPI 的外部芯片驱动必须包含：
```c
GP_xxx_SPI_ERR  // SPI 发送/接收错误标记
```

### 6.4 运行时监控（RtMon）

```
Stack Monitor:   栈使用率监控（调试/测试用，不建议生产 APP 使用）
CpuLoad Monitor: CPU 负载监控
Csa Monitor:     Context Save Area 监控
TaskTime Monitor:任务执行时间监控
TimeCal:         时间标定/同步
```

---

## 七、时序需求规范

### 7.1 初始化时序

```
启动顺序（由 Gp_EcuStpShdn_Startup 编排）：
1. MCU_Init (MCAL)
2. SafeTpack PreRun Test  → 检查通过
3. Gp_RstM_Init → 获取上次复位信息
4. MCAL 各模块 Init
5. SBC BIST (Gp_TLF35584_Bist)
6. 各 CDD 模块 Init
7. OS 启动
8. Gp_SysState_Init
9. 应用 Init
```

### 7.2 MainFunction 周期约束

```
ADC MainFunction:    按配置周期轮询 ADC 结果寄存器
                    每个通道独立可配轮询次数
                    
PMIC MainFunction:   建议周期 ≤ 10ms
                    看门狗服务、故障检测、状态比对

电机驱动 MainFunction: 取决于 PWM 更新频率要求
                      建议周期 ≤ PWM 周期的 2 倍

CAN 收发器 MainFunction: 建议周期 1-5ms
                        处理模式切换、唤醒扫描
```

### 7.3 ADC 轮询机制

```
可配参数：每通道独立轮询计数
"every channel which is not configured as directly read has a polling count
which is increased by MainFunction periodically, when it reach the count maximum,
it will be cleared, then read ADC raw and diagnostic data."

直接读取通道（Directly Read Channel）：
- MainFunction 不轮询此通道
- 由应用层调用 GetAdcSigAdcRaw 时立即读取
- 适用于"等待并检查"场景
```

### 7.4 看门狗时间约束

```
FWD (功能狗) 窗口: 40ms / 60ms / 80ms / 160ms
WWD (窗口狗) 闭窗: 20ms / 30ms / 40ms / 100ms
WWD (窗口狗) 开窗: 20ms / 30ms / 40ms / 100ms
时间基准选择: 0.1ms 或 1ms
```

---

## 八、驱动类型经验库（需求生成参考）

### 8.1 CAN/LIN 收发器驱动

**参考**：Gp_TJA1043, Gp_TPT1145

**必须接口**：
- Init(void)
- MainFunction(void) ← 仅当有 SPI（TPT1145 有，TJA1043 无）
- SetOpMode / SetDevModeOutSig → 设置工作模式
- GetOpMode / GetDevModeInSig → 获取当前模式
- GetBusWuReason → 读取总线唤醒原因
- CheckWakeupFlag → 检查唤醒标志
- SetWakeupMode → 配置唤醒源使能/禁止
- GetTrcvSystemData / GetDevFaultSig → 读取诊断/状态

**配置项**：
- 芯片型号（支持同驱动多型号）
- EN/STB 引脚 DIO Channel
- SPI 通道/序列（TPT1145）
- 唤醒引脚配置
- PN（Partial Networking）配置

### 8.2 多路电机/电磁阀驱动

**参考**：Gp_TLE92104 (4路半桥), Gp_DRV8889 (步进电机)

**必须接口**：
- Init(void)
- MainFunction(void) ← 必须有（异步 SPI 控制）
- SetHbOutSig → 设置半桥输出（周期/占空比/方向）
- SetDevModeOutSig → 设置芯片模式（异步）
- GetDevModeInSig → 获取芯片模式
- GetDevFaultSig → 获取故障信息

**配置项**：
- SPI 通道/序列
- PWM 通道索引（每个半桥）
- 使能引脚 DIO Channel
- 寄存器预配置值（GENCTRL1/2, VDS1/2, HBMODE, PWMSET 等）
- 时序参数（TDON_OFF1/2/3 死区时间）

### 8.3 PMIC/SBC 电源管理

**参考**：Gp_TLF35584

**必须接口**（最复杂）：
- Init(void)
- MainFunction(void) ← 必须有（周期 SP I状态监测 + 看门狗服务）
- GetDevSigModeIn → 读取当前 PMIC 状态
- SetDevSigModeOut → 设置 PMIC 目标状态
- GetDevSigDiag → 读取所有诊断状态
- Bist → 开机自检（FWD/WWD/ABIST/ERR PIN BIST）
- SetDevMpsMode → 设置测试/正常模式
- SetWkUpTimer → 设置唤醒定时器
- SetWdgTriggerCondition → 配置看门狗触发条件
- GetSystemUnusualReason → 获取系统异常原因

**配置项**：
- 看门狗模式（5 种组合可选）
- 窗口狗闭合/打开时间
- 功能狗窗口时间
- 看门狗时间基准（0.1ms / 1ms）
- EMC 频率扩展（0%-6%）
- 初始化寄存器值（DEVCFG/SYSPCFG/WDCFG/FWDCFG/WWDCFG 等）
- MPS 默认模式
- 唤醒定时器配置
- 故障去抖阈值

**状态机**：
```
Init → Normal → Standby → Wake → PORST
       ↓                    ↑
      Fault 诊断监控 ←──────┘
```

### 8.4 MCU ADC 信号采集

**参考**：Gp_IoMcuAdc

**必须接口**：
- Init(void) ← 启动硬件转换
- MainFunction(void) ← 周期轮询结果
- GetAdcSigAdcRaw(uint16 Id, uint16* Raw) ← 获取原始值
- GetAdcSigDiag(uint16 Id, uint32* Diag) ← 获取诊断
- (*) Callout 函数支持自定义处理

**配置项**：
- 通道列表（每通道独立周期、分辨率）
- 直接读取 vs 周期轮询
- 多路复用器支持（最多 8 个 Mux 芯片，每芯片 8 通道）
- 跨平台支持（AURIX2G/3G, TRAVEO2G, STELLAR PX）

### 8.5 MCU PWM 输出

**参考**：Gp_IoMcuPwm

**必须接口**：
- Init(void) ← 设置 PWM 空闲状态
- SetEcuPwmOutSigPedAndDuty(uint16 Id, uint32 Period, uint32 Duty) ← 设置周期和占空比
- GetEcuPwmOutSigDiag(uint16 Id, uint32* Diag) ← 获取诊断
- (*) Callout 函数支持自定义处理

**配置项**：
- PWM 通道列表
- 空闲状态电平
- 时间单位（us/ns，跨平台可配）
- 周期/占空比有效性检查范围

### 8.6 MCU DIO 数字输入输出

**参考**：Gp_IoMcuDio

**必须接口**：
- Init(void)
- Set/Get 操作（同步，无需 MainFunction）
- GetDiag

### 8.7 MCU ICU 输入捕获

**参考**：Gp_IoMcuIcu

**必须接口**：
- Init(void)
- MainFunction 或中断回调 ← 取决于实现
- 捕获模式（边沿/周期/占空比）

### 8.8 I2C GPIO 扩展器驱动

**参考**：Gp_NCA9539

**层级**：IoExtDev

**必须接口（基准 4-6 个）**：
- Init(void) — 初始化当前核所有芯片实例，加载配置表，回写默认方向/输出/极性
- MainFunction(void) ← 仅当存在中断轮询或异步操作时必需
- GetXxxInSig(uint16 Id, ...) — 通过 uint16 Id 解析 chip/port/pin，返回 GPIO 输入状态
- SetXxxOutSig(uint16 Id, ...) — 通过 uint16 Id 解析 chip/port/pin，设置 GPIO 输出电平
- GetDevFaultSig(uint16 Id, uint32* Fault) — 读取芯片故障/诊断信息

**可选接口**：
- ResetChip ← 仅当 RESET 引脚归属本驱动
- SetXxxDirSig ← 仅当项目允许运行时方向变更
- SetXxxPolSig ← 仅当项目使用极性反转

**配置项**：
- I2C 设备地址（A0/A1 硬件决定，支持 4 片同总线）
- 每核芯片实例数量（0-4）
- 每芯片默认方向表、默认输出电平、默认极性
- I2C 通道与速率
- 中断使能与去抖配置

**命名关键约束**：
- 故障诊断接口必须使用 `GetDevFaultSig`，**不得**使用 `GetDiag`（`GetDiag` 是 IoMcu 层信号级诊断接口名）
- 输入/输出接口使用语义命名（`GetXxxInSig` / `SetXxxOutSig`），不按寄存器名命名（如 `ReadInputPort`）

---

## 九、命名与编码规范

### 9.1 文件命名

```
Gp_{Module}.h              公开 API 声明
Gp_{Module}_Types.h        类型、枚举、宏、配置结构体
Gp_{Module}_Cfg.h          预编译配置常量
Gp_{Module}_CfgData.h      集成配置数据
Gp_{Module}_MemMap.h       内存分区映射
Gp_{Module}_Reg.h          寄存器定义（仅 SPI 芯片）
Gp_{Module}.c              主实现
Gp_{Module}_Internal.h     内部函数和数据
Gp_{Module}_Callout.h      用户回调函数
```

### 9.2 函数签名规范

```
返回类型:
- void             操作必然成功（Init/MainFunction）
- Std_ReturnType   操作可能失败（E_OK / E_NOT_OK）
- 状态类型          状态查询（Gp_SysState_StateType）

参数命名:
- Id_u16           uint16 信号 ID
- DevMode_pu8      uint8* 输出参数，指针（p）+ 数据类型（u8）
- DevMode_u8       uint8  输入参数，值类型（u8）
- Fault_pu32       uint32* 输出参数，32位故障码
- ChipIdx_u8       uint8  芯片索引
- SpiChnId_u8      uint8  SPI 通道

命名后缀:
- _t     typedef 类型
- _e     enum 值（TDE 标记）
- _u8    8bit 无符号变量
- _pu8   8bit 无符号指针
- _ptst  结构体指针
- _cptst 指向 const 的结构体指针
- _catst const 数组的指针
- _vatst 可变数组的指针
```

### 9.3 注解标记规范

```c
/*$TDE-B$*/  typedef enum 开始
/*$TDE-E$*/  typedef enum 结束
/*$TDST-B$*/ typedef struct 开始
/*$TDST-E$*/ typedef struct 结束
/*$TDB-B$*/  typedef 普通类型 开始
/*$TDB-E$*/  typedef 普通类型 结束
```

---

## 十、需求校验检查清单（基于经验库）

### 10.1 接口完整性检查

- [ ] 有异步 Set 接口 → 必须有 MainFunction
- [ ] 外部 SPI 芯片 → 必须有 SPI 错误诊断
- [ ] 多核系统 → 函数标注 Non_Reentrancy + 每核独立数据区
- [ ] 状态管理 → 必须有 GetDevMode + SetDevMode
- [ ] 故障诊断 → 必须有 GetDevFault/GetDiag 接口
- [ ] 唤醒功能 → 必须有 GetWuReason + SetWakeupMode

### 10.2 配置完整性检查

- [ ] 每个芯片 → 有 ChipCfg 结构（SPI/PWM/EN 通道索引）
- [ ] 每个信号 → 有 SigMapCfg 映射（CoreId + ChipIdx + ChlIdx）
- [ ] 全局配置 → GlobalCfg 包含所有子配置指针
- [ ] 多核场景 → 每核有独立配置段
- [ ] 预编译开关 → 所有可选功能可通过宏配置

### 10.3 多核一致性检查

- [ ] Core ID 定义：0-5，跨度统一
- [ ] 同步机制：SetEvent/WaitEvent 配对
- [ ] 主核职责：安全生命周期管理、全局资源初始化
- [ ] 从核职责：局部外设初始化、任务执行

### 10.4 安全一致性检查

- [ ] PreRun Test → SwitchToRunPhase 流程完整
- [ ] 看门狗配置 → 模式-窗口-喂狗方式一致
- [ ] 故障恢复 → 去抖+恢复策略
- [ ] 安全状态 → L1/L2 分级 + NoClear 数据保存
- [ ] 复位管理 → 复位类型记录 + 安全状态判断
