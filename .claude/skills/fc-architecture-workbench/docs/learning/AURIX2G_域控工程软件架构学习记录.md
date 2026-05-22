# AURIX2G 域控工程软件架构学习记录

## 1. 学习目的

- 对 `AURIX2G` 域控工程的软件架构进行完整学习与沉淀。
- 提取后续即使源码工程被删除，仍值得保留的架构知识、组织方法和接口模式。
- 为后续 FC 类模块优化提供参考基线，但本记录当前不对具体 `DRV8876` 架构做对照分析。

## 2. 学习范围

本次重点学习了以下内容：

说明：

- 以下路径为本次学习时对应的历史源码路径。
- 后续即使原始工程被移动或删除，本记录保留的是架构认知与设计结论，而不是要求这些路径继续存在。

- 启动与引导：
  - `AURIX2G/BootCtrl/Gp_Ssw2G`
  - `AURIX2G/BootM/Gp_BstM`
- ECU 与系统管理：
  - `AURIX2G/Bsw_Gp/Gp_EcuM`
  - `AURIX2G/BswSys_Gp/Gp_SysState`
  - `AURIX2G/BswSys_Gp/Gp_RstM`
  - `AURIX2G/BswSys_Gp/Gp_WkUpSrcM`
  - `AURIX2G/BswSys_Gp/Gp_WkUpSrcP`
- MCU IO 抽象：
  - `AURIX2G/IoMcu/Gp_IoMcuAdc`
  - `AURIX2G/IoMcu/Gp_IoMcuDio`
  - `AURIX2G/IoMcu/Gp_IoMcuPwm`
  - `AURIX2G/IoMcu/Gp_IoMcuIcu`
- 信号服务与外扩器件 FC：
  - `AURIX2G/IoSigSrv/Gp_IoSigAdc`
  - `AURIX2G/IoExtDev/Gp_DRV887x_DIO`
  - `AURIX2G/IoExtDev/Gp_Mux`
  - `AURIX2G/IoExtDev/Gp_TLE92104`
- 功能组件与工具类：
  - `AURIX2G/Cdd/Gp_06_Adc3ph`
  - `AURIX2G/Cdd/Gp_Pwm3hb`
  - `AURIX2G/Cdd/Gp_TimeRecord`
  - `AURIX2G/BswSrv/Gp_Lib`
  - `AURIX2G/BswSrv/Gp_VerM`
- 运行监控与安全：
  - `AURIX2G/RtMon/*`
  - `AURIX2G/SafeTpack/*`
- 配置与集成：
  - `AURIX2G/Conf/*`
  - `AURIX2G/Gp_Build.xml`

## 3. 工程总体分层认识

该工程不是单纯的驱动集合，而是一个完整的平台型域控工程。其总体分层可概括为：

1. 启动层
   - `BootCtrl/Gp_Ssw2G`
   - 负责芯片级上电、核启动、栈/CSA/中断表/Trap 表、Cache、Watchdog 等最底层启动控制。

2. 引导状态管理层
   - `BootM/Gp_BstM`
   - 负责 Boot 状态管理、块有效性检查、跳转条件、外部重编程请求等。

3. ECU 管理与 OS 相关基础层
   - `Bsw_Gp/Gp_EcuM`
   - `Bsw_Gp/Os/*`
   - 负责多核初始化编排、事件同步、基础 OS/Trap/IRQ 配套能力。

4. 系统服务与系统状态层
   - `BswSys_Gp/*`
   - 负责系统状态机、复位、唤醒源、停机/关断等系统级动作。

5. MCU 资源抽象层
   - `IoMcu/*`
   - 面向 ADC/DIO/PWM/ICU 等资源提供 FC 风格封装，而不是直接暴露 MCAL。

6. 信号服务层
   - `IoSigSrv/*`
   - 在 MCU 原始资源之上进一步提供“信号语义”的服务，如 ADC、诊断、物理值换算等。

7. 外扩器件/芯片 FC 层
   - `IoExtDev/*`
   - 将具体外设芯片、桥驱、收发器、多路复用器等抽象成面向上层的业务化驱动 FC。

8. 复杂功能组件层
   - `Cdd/*`
   - 放置具有较强功能语义或特定应用价值的组件，如三相 ADC、三桥 PWM、时间记录等。

9. 运行监控与安全层
   - `RtMon/*`
   - `SafeTpack/*`
   - 前者负责 CPU 负载、栈、CSA、任务时间等监控；后者负责启动测试、运行时测试及安全包管理。

10. 配置与集成层
   - `Conf/*`
   - 将各 FC 的 `Cfg/Callout/MemMap/Linker/MCAL/OS/集成` 配置从实现源码中解耦出来。

## 4. 目录架构特点

从 `Gp_Build.xml` 可见，该工程把各层作为独立 BC 组织：

- `Asw`
- `BootCtrl`
- `BootM`
- `Bsw_Gp`
- `BswMem_Gp`
- `BswSrv`
- `BswSys_Gp`
- `Cdd`
- `Conf`
- `IoExtDev`
- `IoMcu`
- `IoSigSrv`
- `Mcal_Aurix2G`
- `Mcal_Aurix2G_Gp`
- `RtMon`
- `SafeTpack`
- `__FcDevp`

这说明它的工程组织核心不是“按产品功能零散堆代码”，而是“按平台层次与职责域分 BC”。

## 5. 单个 FC 的标准文件族

域控工程中的 FC 文件组织高度稳定，常见组合如下：

- `FC.h`
- `FC.c`
- `FC_Types.h`
- `FC_Cfg.h`
- `FC_Cfg.c`
- `FC_CfgData.h`
- `FC_Callout.h`
- `FC_Callout.c`
- `FC_MemMap.h`
- 可选：
  - `FC_Cali.c`
  - `FC_Reg.h`
  - `FC_Internal.h`

这个模式在 `Gp_DRV887x_DIO`、`Gp_Mux`、`Gp_IoMcuAdc`、`Gp_IoSigAdc`、`Gp_TLE92104` 等模块中都很稳定。

## 6. 头文件职责划分规律

### 6.1 `FC.h`

主要承载：

- 对外接口原型
- 接口同步/异步/可重入说明
- `Init`
- `MainFunction`
- 语义化 `Set...OutSig`
- 语义化 `Get...InSig` / `Get...Diag` / `Get...FaultSig`

结论：

- 工程不鼓励泛接口命名。
- 倾向于“语义化信号接口”。

### 6.2 `FC_Types.h`

主要承载：

- 模块基础宏
- 核 ID / 核数常量
- 枚举与状态量
- 硬件配置结构
- 信号映射结构
- DET/接口检查结构
- 运行态结构
- 多芯片缓冲结构

结论：

- `Types.h` 是模块抽象能力的中心，不只是简单类型定义。

### 6.3 `FC_Cfg.h`

主要承载：

- 最大芯片数/信号数
- `STD_ON / STD_OFF` 类功能开关
- 控制模式开关
- 多核使能
- 每核实例数
- 阈值类宏
- 故障阈值、恢复阈值
- API 对外 ID 宏

结论：

- `Cfg.h` 承担“编译期选择”和“基础项目配置”的角色。

### 6.4 `FC_CfgData.h`

主要承载：

- 配置容器 `extern`
- 信号映射表 `extern`
- 标定区声明
- 配置常量段声明

结论：

- 表驱动入口统一从这里对外暴露。

### 6.5 `FC_Callout.h`

主要承载：

- `GetCoreId`
- `Read/Write DIO`
- `Set PWM`
- `Get ADC Raw`
- `Delay`
- SPI 读写
- 其他板级或平台相关依赖

结论：

- 工程把“平台差异”收敛到 `Callout`，避免 FC 直接理解底层板级细节。

## 7. 核心接口风格

该工程的接口设计非常统一，主要表现为：

- 稳定骨架：
  - `Init`
  - `MainFunction`
- 输出控制类：
  - `SetDevModeOutSig`
  - `SetDrvOutSig`
  - `SetHbOutSig`
- 输入读取类：
  - `GetCurSig`
  - `GetDevFaultSig`
  - `GetAdcSigAdcRaw`
  - `GetAdcSigDiag`

设计思想：

- 上层拿到的是“业务语义接口”，不是硬件寄存器动作。
- `Setter` 多数负责写请求。
- 真正执行通常在 `MainFunction` 中周期推进。
- `Getter` 读取的是当前模块内部的已知状态、缓存值或即时读取结果。

## 8. 多核与多实例组织方式

这是该工程最值得保留的架构特征之一。

### 8.1 固定支持多核

大量模块把核心数量固定抽象为 `0~5` 六个核位：

- `CORE_NUM`
- `CORE0_ID ~ CORE5_ID`
- `CORE0_ENABLE ~ CORE5_ENABLE`

### 8.2 每核独立运行态缓冲

典型做法：

- 每核一个 `IfChk` 缓冲
- 每核一个 `MultiChip` 或 `MultiSignal` 缓冲数组
- 全局一个 `RunTimeType rtCont[]` 容器数组

作用：

- 通过 `CoreId` 快速索引当前核的运行态与配置
- 实现多核隔离
- 减少运行时分支复杂度

### 8.3 `Id -> Core/Chip/Signal` 映射

对外接口大多只暴露一个 `Id_u16`。

内部通过：

- `cfgSigMapping_vcatst`
- `cfgConfigCont_vcatst`

把对外 ID 映射为：

- 所属 core
- 所属 chip
- 所属 channel / signal

优点：

- 上层接口简单
- 内部可灵活扩展多芯片、多桥、多通道

## 9. 运行模型与状态机思想

很多模块不是“调用即执行到底”的同步模型，而是“初始化 + 周期推进 + 状态机”的模式。

典型表现：

- `Gp_DRV887x_DIO`
  - 通过驱动模式、控制模式、诊断状态推进输出行为
- `Gp_TLE92104`
  - 初始化、模式切换、诊断、故障记录在 `MainFunction` 中推进
- `Gp_SysState`
  - 用 `InitMemory`、`Init`、`MainFunction`、`GetState`、`SwitchAction` 组织系统状态机
- `Gp_BstM`
  - 引导状态通过初始化和周期处理管理

结论：

- 域控工程中，`MainFunction` 不是可选配套，而是架构中心。
- 模块内部大量功能依赖后台周期处理，而不是直接在外部接口中完成。

## 10. 配置分层思想

该工程对“配置”和“实现”做了明显切分。

### 10.1 `Cfg.h`

放：

- 开关
- 基础数量
- 选择项
- 阈值常量
- API 对外 ID 宏

### 10.2 `Cfg.c`

放：

- 硬件资源绑定
- 每核硬件配置数组
- 映射表内容
- 项目实例化常量

例如 `Gp_DRV887x_DIO_Cfg.c` 中，已把具体 `ADC/PWM/DIO` 信号 ID、采样电阻、比例系数、控制模式等都实例化到表里。

### 10.3 `Conf/Conf_xxx`

放：

- 模块最终项目配置
- Callout 实现
- MemMap
- 链接文件
- MCAL/OS/集成配置

结论：

- 该工程把“平台能力源码”和“项目落地配置”分成两层维护。
- 这是后续删除 demo 或替换项目配置时仍能保留平台通用性的关键。

## 11. `Conf` 目录的工程意义

`Conf` 目录不是补充内容，而是架构的一半。

从目录上看，几乎每个层级都有独立配置域：

- `Conf_BootCtrl`
- `Conf_BootM`
- `Conf_Bsw_Gp`
- `Conf_BswSys_Gp`
- `Conf_Cdd`
- `Conf_IoExtDev`
- `Conf_IoMcu`
- `Conf_IoSigSrv`
- `Conf_RtMon`
- `Conf_SafeTpack`
- `Conf_Intg`
- `Conf_Mcal_Aurix2G`
- `Conf_Mcal_Aurix2G_Gp`

其中 `Conf_Intg` 进一步承担：

- `Bsw`
- `Mcal`
- `MemLayout`
- `Os`
- `Gp_Intg`
- `Gp_TstInj`

结论：

- 该工程是“平台源码 + 项目配置 + 集成资源”三位一体架构。
- 不能只看 `*.c/*.h`，必须同时看 `Conf`。

## 12. 依赖抽象策略

从 `Gp_IoMcuAdc`、`Gp_IoSigAdc`、`Gp_DRV887x_DIO` 等模块可以总结出明确依赖策略：

### 12.1 能抽成通用资源服务的，先抽成 `IoMcu`

如：

- DIO
- PWM
- ADC
- ICU

### 12.2 能抽成信号服务的，再上提到 `IoSigSrv`

如：

- ADC raw
- ADC 物理值
- ADC 诊断值

### 12.3 特殊平台差异再用 `Callout`

如：

- 特殊读法
- 特殊诊断判断
- 特殊时序处理
- 核 ID 获取

结论：

- 这个工程并不是“所有依赖都直接 callout”。
- 它优先复用标准 FC，再用 `Callout` 补平台差异。

## 13. 诊断与错误处理模式

### 13.1 DET / 接口检查是显式建模的

很多模块定义了：

- `InitStu`
- `ErrStu`
- `IfChkType`

说明：

- 初始化状态
- 参数错误
- 核不一致
- 信号类型不匹配
- 硬件配置错误

都被纳入运行态，而不是零散散落在代码里。

### 13.2 故障处理不是单 bit 记录

以 `Gp_DRV887x_DIO` 为例，诊断数据中通常包含：

- 诊断结果位图
- 故障计数
- 故障恢复计数
- 故障信息数组
- 周期故障标志

结论：

- 成熟 FC 的故障管理是“小状态机 + 计数器 + 位图”的组合。

## 14. 监控与安全的独立层价值

### 14.1 `RtMon`

该层负责运行时健康观测：

- CPU Load
- Stack
- CSA
- Task Time
- Time Calibration

其角色不是业务功能，而是平台稳定性与可观测性。

### 14.2 `SafeTpack`

该层负责安全测试与安全流程：

- 启动测试组
- 运行时测试组
- 测试阶段切换
- 安全监控模块

这说明工程从架构层面已把“安全功能”独立出来，而不是分散到普通 FC 中。

## 15. 启动与引导架构要点

### 15.1 `Gp_Ssw2G`

负责极底层启动相关内容：

- 核数量选择
- 各核启动使能
- Cache/Watchdog/A0A1/A8A9
- CSA/Stack 监控参数
- 链接符号适配
- 多核启动基础

这层是硬件平台带入软件平台的入口。

### 15.2 `Gp_BstM`

负责 Boot 状态管理：

- Boot 初始化
- Boot 周期处理
- Boot 状态设置/读取
- Block 有效性检查
- 地址/块信息查询
- 外部重编程请求

结论：

- 启动与引导在该工程中不是散乱逻辑，而是两层分工：
  - `Ssw` 管芯片级启动
  - `BstM` 管 Boot 业务状态

## 16. 系统管理架构要点

### 16.1 `Gp_EcuM`

负责：

- 各核初始化入口
- 核间事件同步
- 等待单事件/全事件

说明该工程显式支持多核初始化编排。

### 16.2 `Gp_SysState`

负责：

- `InitMemory`
- `Init`
- `MainFunction`
- 状态读取
- 状态记录
- 切换动作执行

说明系统状态机是一个独立 FC，而不是散落在多个业务模块中。

## 17. 从 `AURIX2G` 提炼出的稳定架构规则

以下内容建议作为后续平台或 FC 优化时的长期规则保留：

1. 任何稍复杂 FC 都应采用完整文件族，不建议只有 `h/c` 两个文件。
2. 配置必须与实现分离，且要区分 `Cfg.h`、`CfgData.h`、`Cfg.c`。
3. 上层接口应优先语义化，不建议使用泛化 `Read/Write` 风格命名。
4. 多核场景下，对外 ID 与内部 Core/Chip/Signal 映射必须解耦。
5. `MainFunction` 应作为周期推进中心，而不是可有可无。
6. 运行态、DET、诊断、恢复计数应在 `Types.h` 中显式建模。
7. 硬件资源绑定应尽量下沉到配置表，不写死在主逻辑中。
8. 先复用标准 FC 层，再用 `Callout` 处理特例，不要把所有依赖都做成散乱 callout。
9. `Conf` 目录必须视为正式架构组成部分，而不是附属配置。
10. 安全、监控、系统状态应有独立层次，不应混入普通外设 FC。

## 18. 各模块驱动的架构定义思想提炼

这一节重点不是总结“模块做了什么”，而是总结“这些模块在定义架构时是怎么思考的”。

### 18.1 `IoMcu` 类模块的架构定义思想

代表模块：

- `Gp_IoMcuAdc`
- `Gp_IoMcuDio`
- `Gp_IoMcuPwm`
- `Gp_IoMcuIcu`

核心思想：

- 第一性目标不是直接封装 MCAL API，而是定义“统一资源接口”。
- 资源模块优先抽象成 `Signal Interface`，而不是保留底层寄存器或通道语义。
- 模块外部接口围绕“资源能力”定义，如：
  - ADC raw
  - ADC diag
  - DIO level in/out
  - PWM output
- 接口命名会随着架构版本进化，从粗粒度接口演进到“一个信号可承载多个接口”的细粒度形式。

架构定义启发：

- 当模块本质上是 MCU 资源适配层时，架构重点应放在“统一资源语义”和“可跨芯片复用”，而不是放在业务流程。
- 这类模块对外不应暴露底层驱动细节，应优先定义标准化资源接口族。
- 如果未来要兼容不同 MCU 平台，应在架构阶段预留依赖实现选择，而不是后期再硬改。

### 18.2 `IoSigSrv` 类模块的架构定义思想

代表模块：

- `Gp_IoSigAdc`

核心思想：

- 它不是简单“转调 IoMcu”，而是把资源读数提升为“信号服务”。
- 在这一层开始出现：
  - 物理值换算
  - 有效性/诊断判断
  - 参考电压策略
  - 统一输出格式
- 它允许底层来源多样化：
  - 依赖其他 FC
  - 走 callout
  - 走不可用占位策略

架构定义启发：

- 当底层资源值还不足以直接被业务使用时，应单独定义信号服务层，而不是把换算和诊断散落到各个业务 FC。
- 这一层的架构重点不在硬件控制，而在“信号解释权”和“统一读法”。
- 后续新 FC 若涉及电流、电压、位置、诊断量，优先评估是否先沉淀为 `IoSigSrv` 能力。

### 18.3 `IoExtDev` 芯片 FC 的架构定义思想

代表模块：

- `Gp_DRV887x_DIO`
- `Gp_TLE92104`
- `Gp_Mux`

核心思想：

- 这类模块不是直接暴露芯片引脚，而是定义“芯片能力接口”。
- 它们通常围绕以下对象定义架构：
  - 芯片模式
  - 输出控制
  - 输入结果
  - 故障状态
  - 周期诊断
  - 自动恢复
- 模块内部常见“请求态”和“生效态”分离：
  - 外部接口写请求
  - `MainFunction` 推进状态与诊断
  - `Getter` 返回当前已知状态

架构定义启发：

- 当模块面对的是“具体外扩器件”，架构重点应从“引脚控制”提升到“器件语义控制”。
- 若芯片存在模式切换、诊断、恢复、时序要求，必须在架构中明确 `MainFunction` 和状态机，而不是只列 `Set/Get` 接口。
- 对外接口 ID 应与内部芯片/通道/核映射解耦，这是多实例可扩展的关键。

### 18.4 `BswSys` 系统类模块的架构定义思想

代表模块：

- `Gp_SysState`
- `Gp_RstM`
- `Gp_WkUpSrcM`
- `Gp_WkUpSrcP`
- `Gp_EcuStpShdn`

核心思想：

- 这类模块不是资源驱动，也不是单芯片驱动，而是“系统策略和系统记录”的承载层。
- 对外接口通常围绕：
  - 系统状态读取
  - 状态记录
  - 切换动作
  - Reset 执行
  - Reset 原因读取
  - NoClear 数据保存
- 它们往往需要和启动、安全、NVM、MCU 状态深度协作。

架构定义启发：

- 系统类模块设计时，要先定义系统职责边界，再定义接口。
- 这类模块的重点不是接口数量，而是“系统状态归口”和“跨复位生命周期数据管理”。
- 如果一个功能天然跨越启动、运行、异常恢复阶段，应优先进入系统层，而不是挂在某个普通 FC 下。

### 18.5 `Cdd` 功能组件类模块的架构定义思想

代表模块：

- `Gp_06_Adc3ph`
- `Gp_Pwm3hb`
- `Gp_TimeRecord`

核心思想：

- 这类模块处理的是“特定功能域能力”，不是通用资源，也不是单一系统管理。
- 其架构定义更关注：
  - 功能对象边界
  - 时序要求
  - 应用语义
  - 专用配置结构
- `Gp_TimeRecord` 这类模块甚至会直接对外暴露少量运行态实体，说明其目标是“全局共用工具能力”，不是严格的器件封装。

架构定义启发：

- 当功能已超出标准资源 FC 的语义，但又未上升到系统层时，可以用 `Cdd` 作为承载层。
- `Cdd` 不应成为“杂项代码仓库”，而应面向明确功能域组织。
- 这类模块的架构定义要先回答“它是平台通用能力，还是项目临时功能”，再决定是否进入 `Cdd`。

### 18.6 `RtMon` 监控类模块的架构定义思想

代表模块：

- `Gp_CpuLoadMonitor`
- `Gp_StackMonitor`
- `Gp_CsaMonitor`
- `Gp_TaskTimeMon`
- `Gp_TimeCal`

核心思想：

- 监控模块不是业务参与者，而是“运行状态观测器”。
- 架构设计重点在：
  - 采样对象定义
  - 监控周期定义
  - 运行态记录结构
  - 跨核观测能力
- 这类模块往往与 `Callout`、`CoreId`、时间基准强关联。

架构定义启发：

- 监控类功能不要混入普通业务 FC。
- 一旦功能目标是“测量系统运行行为”，就应独立成监控模块。
- 监控模块应优先设计数据结构和读取方式，再设计告警或诊断扩展。

### 18.7 `SafeTpack` 安全类模块的架构定义思想

代表模块：

- `Gp_TstM`
- `Gp_TstApp`
- `Smc/*`

核心思想：

- 安全类模块的架构关注点不在业务接口，而在“测试阶段、执行组、主核职责、运行阶段切换”。
- 接口体现出明显的安全流程意识：
  - 初始化
  - 启动测试组执行
  - 切换到运行态
  - 运行时测试组执行
  - 测试结果清理

架构定义启发：

- 安全相关能力要按“流程”和“阶段”组织接口，不应只按单个功能点拆碎。
- 如果后续 FC 涉及 ASIL 目标，建议在架构阶段就明确它与安全测试层如何交互。

### 18.8 `BootCtrl / BootM` 的架构定义思想

代表模块：

- `Gp_Ssw2G`
- `Gp_BstM`

核心思想：

- 启动链被分成：
  - 芯片启动控制
  - Boot 状态与块管理
- `Gp_Ssw2G` 负责非常底层的平台进入条件。
- `Gp_BstM` 负责更靠上的引导业务状态和跳转策略。

架构定义启发：

- 启动相关设计应明确区分“硬件启动控制”和“软件引导状态机”。
- 后续若遇到 Boot、FBL、APP 交互，不应把它们混在一个 FC 里处理。

### 18.9 跨模块共通的架构定义方法

从这些模块可以提炼出一套共通方法：

1. 先定义模块在分层中的位置，再定义接口。
2. 先定义对象语义，再定义参数列表。
3. 先定义运行模型是同步直达还是周期推进，再决定 `MainFunction` 是否为核心。
4. 先定义配置边界，再写 `Cfg.h / CfgData.h / Cfg.c`。
5. 先决定哪些能力可复用标准 FC，哪些才需要 `Callout`。
6. 先设计运行态结构，再展开故障、诊断、恢复细节。

## 19. 对后续架构设计的直接思路

后续设计新架构时，可以优先按下面顺序思考：

1. 这个模块属于哪一层：
   - `IoMcu`
   - `IoSigSrv`
   - `IoExtDev`
   - `Cdd`
   - `BswSys`
   - `RtMon`
   - `SafeTpack`
2. 它对外暴露的是资源语义、信号语义、器件语义，还是系统语义。
3. 它是否需要 `MainFunction` 来承载状态推进、诊断和恢复。
4. 它是否需要多核、多实例、多芯片映射。
5. 它的依赖应落在标准 FC、配置表还是 `Callout`。
6. 它的运行态、DET、故障计数、恢复状态是否需要单独建模。

建议直接继承的设计习惯：

- 先做架构定义，再写实现。
- 先做文件族设计，再写接口。
- 先做表驱动和映射设计，再写逻辑。
- 先做层次边界，再做模块复用。

## 20. 对后续 FC 优化最有价值的可迁移点

后续如需优化任意 FC，优先迁移以下能力：

- 固定文件族
- 语义化接口命名
- `Init + MainFunction + Set/Get` 运行模型
- 多核/多实例 `RunTimeType` 容器
- `cfgCont + cfgSigMapping` 表驱动
- `IfChk + ErrStu + InitStu` 防御式接口检查
- `Diag/Fault/Recovery Counter` 运行态建模
- `IoMcu -> IoSigSrv -> IoExtDev/Cdd` 分层依赖路线
- `Conf` 独立项目配置层

## 21. 本次学习结论

`AURIX2G` 域控工程的核心价值，不在于某一个具体 FC 的业务逻辑，而在于它已经形成了一套稳定的平台化软件架构方法：

- 分层清晰
- 配置与实现分离
- 多核多实例友好
- 接口语义稳定
- 周期调度中心明确
- 安全与监控层独立
- 项目配置体系完整

后续即使原始工程或 demo 被删除，上述这些架构方法仍然值得作为平台 FC 设计的长期参考基线。
