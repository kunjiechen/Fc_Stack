# AURIX2G 在线源码 grounding 基线

## 作用

本文记录从在线工程树中提炼出的、带真实源码依据的架构事实。

当前基线对应的工程根为：

`src/FcStackBase/AURIX2G`

当架构生成或评审需要真实工程证据，而不是只依赖历史摘要、demo 说明或通用 FC 规则时，再使用本文件。

这不是完整源码清单，而是一份长期保留的架构 grounding 摘要，重点覆盖：

- 文件族职责
- 配置与载体拆分
- Callout 用法
- MemMap 风格
- 多核处理方式
- DET / 运行时状态风格
- 在线模块族模式

## 1. 在线工程分层事实

在线源码树不是平铺结构，而是按架构域族组织，例如：

- `IoExtDev/IoExtDev`
- `IoMcu`
- `Cdd`
- `BswSys_Gp`
- `Bsw_Gp`
- `RtMon`
- `SafeTpack`
- `Mcal_Aurix2G_Gp`

这意味着在做架构生成时，不能把所有 FC 当成同一类模块处理。
FC 分层和依赖策略必须结合模块族显式判断。

已观察到的例子：

- `IoExtDev/IoExtDev/Gp_TLE92104`
- `IoMcu/Gp_IoMcuDio`
- `Cdd/Gp_06_Adc3ph`
- `BswSys_Gp/Gp_WkUpSrcP`

## 2. 源码与配置拆分是客观存在的

在线工程对以下目录有明确拆分：

- module source directory
- configuration directory
- integration MemMap directory

常见模式：

- 模块源码目录通常包含：
  - `FC.c`
  - `FC.h`
  - `FC_Types.h`
- 配置目录通常包含：
  - `FC_Cfg.h`
  - `FC_Cfg.c`
  - `FC_CfgData.h`
  - `FC_Callout.h`
  - `FC_Callout.c`
  - sometimes `FC_Cali.c`
  - for register-driven drivers, sometimes `FC_Reg.h`
- 集成侧 MemMap 目录通常包含：
  - `FC_MemMap.h`

示例：

- `Gp_TLE92104`
  - source in `IoExtDev/IoExtDev/Gp_TLE92104`
  - config in `Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TLE92104`
  - MemMap in `Conf/Conf_Intg/MemLayout/MemMap/Gp_TLE92104_MemMap.h`
- `Gp_IoMcuDio`
  - source in `IoMcu/Gp_IoMcuDio`
  - config in `Conf/Conf_IoMcu/Conf_Gp_IoMcuDio`
  - MemMap in `Conf/Conf_Intg/MemLayout/MemMap/Gp_IoMcuDio_MemMap.h`
- `Gp_06_Adc3ph`
  - source in `Cdd/Gp_06_Adc3ph`
  - config in `Conf/Conf_Cdd/Conf_Gp_06_Adc3ph`
  - MemMap in `Conf/Conf_Intg/MemLayout/MemMap/Gp_06_Adc3ph_MemMap.h`
- `Gp_WkUpSrcP`
  - source in `BswSys_Gp/Gp_WkUpSrcP`
  - config in `Conf/Conf_BswSys_Gp/Conf_Gp_WkUpSrcP`
  - MemMap in `Conf/Conf_Intg/MemLayout/MemMap/Gp_WkUpSrcP_MemMap.h`

Architecture generation should therefore avoid the false assumption that all carriers live beside the module `.c` file.

## 3. File Family Responsibilities

Observed file-family responsibilities are consistent enough to treat as grounding:

- `FC.h`
  - external API contract
  - function-level sync/reentrancy/parameter comments
  - `FC_Cfg.h` inclusion
  - register-header inclusion when required
  - `CODE_START/STOP` around public prototypes
- `FC_Types.h`
  - internal/public type system
  - config-aware type definitions
  - often includes `FC_Cfg.h`
- `FC_Cfg.h`
  - compile-time feature switches
  - core enable switches
  - count/size macros
  - hardware mapping macros
  - dependency binding macros
- `FC_CfgData.h`
  - `extern const` config containers
  - often placed in global or per-core const MemMap sections
- `FC_Callout.h/.c`
  - project adaptation boundary
  - hardware/platform/helper bridging
- `FC_Cali.c`
  - optional calibration carrier, not universal
- `FC_Reg.h`
  - required when the FC owns register constants, command bytes, masks, or chip-level register naming
- `FC_MemMap.h`
  - section-carrier file generated/integrated at project level, not necessarily located beside source

## 4. Callout Is A First-Class Architecture Mechanism

Callout is not an exception pattern in this project.
It is a normal architecture mechanism across multiple families.

Observed live examples:

- `Gp_TLE92104` uses callouts for:
  - `GetCoreId`
  - delay
  - SPI sync transmit
  - digital output control
  - PWM output setting
- `Gp_IoMcuDio` uses callouts for:
  - `GetCoreId`
  - module init
  - direction set
  - input level read
  - output level write
- `Gp_06_Adc3ph` uses callouts for:
  - `GetCoreId`
  - delay
  - trigger enable
  - oversampling-related adaptation
- `Gp_WkUpSrcP` uses callout revision hooks for wakeup-source data handling

Architecture implication:

- dependency interface generation should not avoid callout by default
- callout should be selected when project adaptation, platform variation, or hardware binding is expected
- a generated file list should include both `FC_Callout.h` and `FC_Callout.c` whenever callout dependency exists

## 5. Multi-Core Is A Real Architectural Constraint

Multi-core handling is a real live-project fact, not a speculative future option.

Observed patterns:

- core enable macros in `FC_Cfg.h`
- per-core counts such as chip count or signal count
- `CalloutGetCoreId`
- per-core runtime buffers
- per-core const sections
- per-core clear-data sections

Examples:

- `Gp_TLE92104_Cfg.h` explicitly enables or disables cores and defines per-core chip/signal counts
- `Gp_IoMcuDio` keeps DET runtime buffers for multiple cores
- `Gp_06_Adc3ph` and `Gp_TLE92104` both call `CalloutGetCoreId`

Architecture implication:

- do not default to single-core wording unless requirement and grounding both justify it
- runtime state, config containers, and MemMap must be checked for per-core ownership
- if a module uses current-core wording or core-index selection, architecture should export that boundary explicitly

## 6. MemMap Style Is Explicit And Granular

The live project uses explicit per-module MemMap carriers with detailed section variants.

Observed section families include:

- `CODE`
- `CLEAR_FAR_DATA_ALIGN4_COREx`
- `CONST_FAR_DATA_ALIGN4_COREx`
- `CONST_FAR_DATA_ALIGN4_GLOBAL`
- `CONST_FAR_DATA_ALIGN4_CALI_COREx`

Observed style:

- module-specific start/stop macros
- per-core RAM sections
- per-core CONST sections
- optional global CONST sections
- optional calibration CONST sections

Example:

- `Gp_TLE92104_MemMap.h` contains:
  - `GP_TLE92104_CODE_START/STOP`
  - `GP_TLE92104_CLEAR_FAR_DATA_ALIGN4_COREx_START/STOP`
  - `GP_TLE92104_CONST_FAR_DATA_ALIGN4_COREx_START/STOP`
  - `GP_TLE92104_CONST_FAR_DATA_ALIGN4_CALI_COREx_START/STOP`

Architecture implication:

- MemMap generation must not collapse all data into one generic RAM/CONST pair
- calibration, global const, and per-core data should be treated as separate decisions
- `FC_MemMap.h` should be treated as a real architecture carrier, not a cosmetic appendix

## 7. DET Is Typically Runtime-Aware, Not Purely Formal

DET in the live project is not only a macro switch.
It can have real runtime storage and interface/error-state behavior.

Observed examples:

- `Gp_IoMcuDio`
  - `GP_IOMCUDIO_DEV_ERROR_DETECT`
  - per-core DET runtime buffers
  - DET newest-error overwrite policy
- `Gp_WkUpSrcP`
  - `GP_WKUPSRCP_CFG_DET_ENABLE`
- `Gp_06_Adc3ph`
  - `GP_06_ADC3PH_CFG_DET_ENABLE`
- `Gp_TLE92104`
  - `GP_TLE92104_DET_EN`

Architecture implication:

- DET should not always be modeled as a single feature macro only
- some FCs may need runtime DET bookkeeping as part of runtime-state design
- validator rules should allow DET-related runtime-state objects when evidence supports them

## 8. Register-Driven External Device FCs Need Reg Carrier

For external-device drivers with explicit register/protocol ownership, `FC_Reg.h` is real and should not be omitted.

Observed example:

- `Gp_TLE92104.h` includes:
  - `Gp_TLE92104_Cfg.h`
  - `Gp_TLE92104_Reg.h`

Architecture implication:

- if a driver owns register command words, bit masks, mode values, or protocol frame constants, add `FC_Reg.h`
- do not force such constants into `Cfg.h` or prose-only sections

## 9. External API Style Observed In Live FCs

Observed public API patterns include:

- `Init`
- `MainFunction`
- state/signal getters
- signal setters
- fault/diagnostic getters

Observed examples:

- `Gp_TLE92104`
  - `Init`
  - `MainFunction`
  - `SetHbOutSig`
  - `GetDevModeInSig`
  - `SetDevModeOutSig`
  - `GetDevFaultSig`
  - `GetHBVOUT`
- `Gp_IoMcuDio`
  - `SetDioSigDir`
  - `GetDioSigLvlIn`
  - `SetDioSigLvlOut`
- `Gp_WkUpSrcP`
  - `GetWkUpSts`
- `Gp_06_Adc3ph`
  - signal/raw-input getter style

Architecture implication:

- interface naming should stay close to real FC semantic naming instead of forcing one universal naming formula
- getter/setter granularity is domain-specific and must reflect module family

## 10. Configuration Content Is Richer Than Simple Feature Switches

Live `Cfg.h` files are not just feature toggles.
They often include:

- core enable strategy
- total counts and per-core counts
- dependency/hardware mapping macros
- timing constants
- behavioral switches
- diagnostic switches
- chip/signal ID mapping constants

Example:

- `Gp_TLE92104_Cfg.h` contains:
  - core enable switches
  - per-core chip/signal counts
  - total counts
  - chip init retry count
  - watchdog switch
  - fault-clear switches
  - EN/SPI/PWM hardware mapping macros
  - timing constants
  - direction semantic constants
  - upper-layer signal mapping constants

Architecture implication:

- config classification must distinguish:
  - feature macro
  - count/size macro
  - behavior-selection macro
  - timing/retry macro
  - hardware mapping macro
  - ID mapping macro
- some config items belong in `Cfg.h` rather than `Cfg.c`

## 11. Architecture Generation Rules Strengthened By Live Source

The live source confirms the following architecture-generation positions:

- configuration carriers are separate from source carriers
- callout is a standard dependency boundary
- register-based drivers need `Reg.h`
- multi-core must be modeled explicitly when grounding supports it
- MemMap is per-module and often per-core
- DET may have runtime-state consequences
- file list generation should reflect both module and config/integration carriers

## 11A. IoMcu Family Pattern

Observed live sample:

- `IoMcu/Gp_IoMcuDio`

Observed characteristics:

- external APIs are synchronous signal access APIs:
  - `Init`
  - `SetDioSigDir`
  - `GetDioSigLvlIn`
  - `SetDioSigLvlOut`
- there is no default `MainFunction` scheduling contract in the observed live header
- dependency adaptation is still callout-based, but the shape is MCU/DIO oriented instead of external-device register read/write oriented
- `Cfg.h` is rich in:
  - core enable switches
  - signal ID mapping macros
  - dependency selection macro style such as `SPEC_DEP_IF`
  - DET switch
- DET has runtime consequences and multi-core ownership is explicit
- `Reg.h` is not the default carrier for this family

Architecture implication:

- do not force IoExt-style `I2cRead/I2cWrite` dependency interfaces onto IoMcu family modules
- prefer synchronous API and route-mapping wording over periodic polling wording
- freeze dependency selection and signal-ID mapping as first-class configuration concerns
- keep `Callout.h/.c`, but do not require `Reg.h` by default

## 11B. Cdd Family Pattern

Observed live sample:

- `Cdd/Gp_06_Adc3ph`

Observed characteristics:

- external APIs are conversion/raw-signal oriented and do not imply a universal `MainFunction`
- dependency adaptation uses callout for:
  - current-core selection
  - delay
  - trigger-related adaptation
- `Cfg.h` includes strategy-heavy configuration content:
  - DET enable
  - OSP enable
  - group/motor/per-core counts
  - pre/post delay
  - sample strategy
  - validity strategy
  - invalid fill strategy
- MemMap may include `CODE_RAM_COPY` in addition to normal code/data sections
- configuration may include hardware-framework headers, but that does not mean architecture should add a generic `Reg.h` carrier by default

Architecture implication:

- allow Cdd modules to have no `MainFunction` when the live pattern is conversion-driven
- treat strategy macros as first-class architecture objects instead of reducing them to generic feature toggles
- keep `CODE RAM COPY` as an explicit MemMap decision when latency-sensitive code exists
- do not clone IoExt dependency or file-carrier expectations into Cdd by default

## 11C. BswSys_Gp Family Pattern

Observed live sample:

- `BswSys_Gp/Gp_WkUpSrcP`

Observed characteristics:

- external APIs are system-status oriented:
  - `Init`
  - `GetWkUpSts`
- header comments describe asynchronous behavior even though the getter itself is a direct query-style interface
- dependency adaptation is not register access or MCAL port access; instead it uses callout revise hooks such as `CalloutWkSrcDataRevise`
- `Cfg.h` is rich in:
  - DET switch
  - data revise switch
  - wakeup signal count
  - many signal-ID mapping macros
  - dependency-module includes such as IO signal and SCR support headers
- runtime design is global wakeup-status oriented rather than per-core hardware-routing oriented
- configuration family includes a real `Cali.c` carrier in addition to `Cfg.c`, `CfgData.h`, `Callout.h/.c`, and `MemMap.h`

Architecture implication:

- do not force hardware-driver dependency style onto BswSys_Gp family modules
- treat revise hooks, signal-count macros, and signal-ID mapping as first-class architecture decisions
- allow global runtime caches and calibration carriers when the live pattern supports them
- keep `Callout.h/.c`, but do not require `Reg.h` or `MainFunction` by default

## 12. How To Use This Grounding

Use this grounding note when:

- requirement wording is ambiguous but a live AURIX2G pattern exists
- deciding whether `Callout.h/.c` is justified
- deciding whether `Reg.h` is required
- deciding whether the architecture should expose per-core runtime/config boundaries
- deciding how many file carriers should be listed
- deciding whether DET remains macro-only or needs runtime-state mention
- deciding whether MemMap should be global, per-core, calibration-aware, or mixed

Do not use this note to blindly clone one module.
Use it to constrain architecture decisions with real project evidence.
