# Grounding Scope

## Objective

Build a reusable grounding baseline for FC detailed-design generation without embedding the full reference engineering repository into the skill.

This baseline is intended to support:

- real-project interface shaping
- dependency interface selection
- runtime container and multi-core pattern selection
- configuration and `Conf_*` traceability
- detailed-design style normalization for IoExtDev-oriented FCs

## Reference Modules

The grounding baseline for this skill is frozen to the following engineering assets:

1. `Gp_WkUpSrcP`
   Code: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/BswSys_Gp/Gp_WkUpSrcP`
   Conf: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_BswSys_Gp/Conf_Gp_WkUpSrcP`

2. `Gp_06_Adc3ph`
   Code: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Cdd/Gp_06_Adc3ph`
   Conf: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_Cdd/Conf_Gp_06_Adc3ph`

3. `Gp_TPT1145`
   Code: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/IoExtDev/IoExtDev/Gp_TPT1145`
   Conf: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TPT1145`

4. `Gp_TLE92104`
   Code: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/IoExtDev/IoExtDev/Gp_TLE92104`
   Conf: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_TLE92104`

5. `Gp_DRV8889`
   Code: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/IoExtDev/IoExtDev/Gp_DRV8889`
   Conf: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoExtDev/Conf_IoExtDev/Conf_Gp_DRV8889`

6. `IoMcu` family
   Code: `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/IoMcu`
   Conf:
   - `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuAdc`
   - `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuDio`
   - `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuIcu`
   - `/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf/Conf_IoMcu/Conf_Gp_IoMcuPwm`

## Baseline Roles

- `Gp_TPT1145`, `Gp_TLE92104`, `Gp_DRV8889`
  Primary IoExtDev grounding set for external-interface shape, dependency interfaces, chip runtime patterns, and internal-function granularity.

- `IoMcu`
  Primary dependency-interface and lower-layer adaptation grounding set for `Callout*`, `CfgData`, `MemMap`, and per-core configuration/runtime patterns.

- `Gp_WkUpSrcP`, `Gp_06_Adc3ph`
  Secondary cross-domain style set for lightweight FC structure, signal mapping, and non-IoExtDev FC normalization.

## Working Rules

- Do not inject whole reference repositories into the skill body.
- Use curated module facts and pattern summaries as grounding context.
- Treat `Conf_*` assets as first-class evidence for configuration naming and mapping rules.
- When a target module is IoExtDev, prefer the IoExtDev trio first, then use `IoMcu` to resolve dependency and platform style questions.
- Prefer decompressed `Conf_IoExtDev/Conf_IoExtDev/*` directories as the current evidence source instead of archived zip paths.

## Evidence Depth Requirement

- Each primary IoExtDev grounding module should expose:
  - code path
  - conf path
  - exported APIs
  - callout family
  - runtime pattern
  - config container symbols
  - key feature switches
  - at least one concrete `Conf_*` evidence note

## Immediate Follow-up

- Continue expanding `facts.yaml` for the IoExtDev trio with more extracted `Cfg`, `CfgData`, and `Callout` symbols as needed by future targets.
