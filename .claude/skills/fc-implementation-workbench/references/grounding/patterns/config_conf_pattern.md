# 配置与 Conf 模式

## 基线

该代码体系对 FC 源码实现和 `Conf_*` 配置资产有清晰拆分，配置根目录位于：

`src/FcStackBase/AURIX2G/Conf`

已确认的例子：

- `Conf_Gp_WkUpSrcP`
- `Conf_Gp_06_Adc3ph`
- `Conf_Gp_IoMcu*`

## 规则

- 把 `CfgData` 和 `Conf_*` 视为一等设计证据。
- 配置映射关系需要显式写清楚。
- 命名和结构体形态优先兼容已生成的配置资产。
