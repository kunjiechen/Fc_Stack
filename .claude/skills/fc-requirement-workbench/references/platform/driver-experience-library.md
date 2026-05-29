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
