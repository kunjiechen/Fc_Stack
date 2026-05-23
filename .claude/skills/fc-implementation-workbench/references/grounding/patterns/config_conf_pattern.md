# Config And Conf Pattern

## Baseline

This codebase uses a clear split between source FC implementation and `Conf_*` assets under:

`/Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G/Conf`

Confirmed examples:

- `Conf_Gp_WkUpSrcP`
- `Conf_Gp_06_Adc3ph`
- `Conf_Gp_IoMcu*`

## Rules

- Treat `CfgData` and `Conf_*` as first-class design evidence.
- Document configuration mapping explicitly.
- Prefer naming and struct-shape descriptions that are compatible with generated configuration assets.
