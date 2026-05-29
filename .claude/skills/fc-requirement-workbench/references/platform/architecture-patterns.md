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

