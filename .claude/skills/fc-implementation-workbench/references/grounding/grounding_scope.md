# Grounding 范围

## 目标

在不把整套参考工程仓库直接塞进 skill 的前提下，构建一套可复用的 FC 详细设计 grounding 基线。

这套基线主要支持：

- 基于真实项目的接口形态收敛
- 依赖接口选择
- 运行时容器与多核模式选择
- 配置与 `Conf_*` 追溯
- 面向 IoExtDev 类 FC 的详细设计风格归一化

## 参考模块

本 skill 当前冻结使用以下工程资产：

1. `Gp_WkUpSrcP`
   Code: `src/FcStackBase/AURIX2G/BswSys_Gp/Gp_WkUpSrcP`
   Conf: `src/FcStackBase/AURIX2G/Conf/Conf_BswSys_Gp/Conf_Gp_WkUpSrcP`

2. `Gp_06_Adc3ph`
   Code: `src/FcStackBase/AURIX2G/Cdd/Gp_06_Adc3ph`
   Conf: `src/FcStackBase/AURIX2G/Conf/Conf_Cdd/Conf_Gp_06_Adc3ph`

3. `Gp_TPT1145`
   Code: `src/FcStackBase/AURIX2G/IoExtDev/IoExtDev/Gp_TPT1145`
   Conf: `src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TPT1145`

4. `Gp_TLE92104`
   Code: `src/FcStackBase/AURIX2G/IoExtDev/IoExtDev/Gp_TLE92104`
   Conf: `src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TLE92104`

5. `Gp_DRV8889`
   Code: `src/FcStackBase/AURIX2G/IoExtDev/IoExtDev/Gp_DRV8889`
   Conf: `src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_DRV8889`

6. `IoMcu` family
   Code: `src/FcStackBase/AURIX2G/IoMcu`
   Conf:
   - `src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuAdc`
   - `src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuDio`
   - `src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuIcu`
   - `src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuPwm`

## 基线分工

- `Gp_TPT1145`, `Gp_TLE92104`, `Gp_DRV8889`
  Primary IoExtDev grounding set for external-interface shape, dependency interfaces, chip runtime patterns, and internal-function granularity.

- `IoMcu`
  Primary dependency-interface and lower-layer adaptation grounding set for `Callout*`, `CfgData`, `MemMap`, and per-core configuration/runtime patterns.

- `Gp_WkUpSrcP`, `Gp_06_Adc3ph`
  Secondary cross-domain style set for lightweight FC structure, signal mapping, and non-IoExtDev FC normalization.

## 使用规则

- 不要把整套参考仓库直接注入 skill 主体。
- grounding 以精选模块事实和模式摘要为主。
- `Conf_*` 资产是配置命名和映射规则的一等证据。
- 目标模块属于 IoExtDev 时，优先看 IoExtDev 三件套，再用 `IoMcu` 解决平台依赖风格问题。
- 当前证据源优先使用解压后的 `Conf_IoExtDev/Conf_IoExtDev/*` 目录，而不是历史压缩包路径。

## 证据深度要求

- Each primary IoExtDev grounding module should expose:
  - code path
  - conf path
  - exported APIs
  - callout family
  - runtime pattern
  - config container symbols
  - key feature switches
  - at least one concrete `Conf_*` evidence note

## 后续维护建议

- 后续如有新目标模块，可继续为 IoExtDev 三件套补充更多 `Cfg`、`CfgData` 和 `Callout` 符号证据。
