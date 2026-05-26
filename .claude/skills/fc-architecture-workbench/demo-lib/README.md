# Demo 架构摘要库

## 作用

本目录保存从历史 demo 源码与配置样本中提炼出的架构摘要。

原始 demo 源码库已经收敛成“每个 FC 一份 Markdown 摘要”的形式。后续做架构参考时，优先读取这些摘要，而不是再回到大体量源码目录。

## 目录结构

- `summaries/`
  每个保留 FC 样本各一份摘要
- `MODULE_INDEX.md`
  用于快速选择最接近样本的索引

## 当前保留模块

| 模块 | 所属层 | 摘要文件 |
| --- | --- | --- |
| `Gp_IoMcuAdc` | `IoMcu` 资源层 | `summaries/Gp_IoMcuAdc.md` |
| `Gp_IoMcuDio` | `IoMcu` 资源层 | `summaries/Gp_IoMcuDio.md` |
| `Gp_IoSigAdc` | `IoSigSrv` 信号服务层 | `summaries/Gp_IoSigAdc.md` |
| `Gp_DRV887x_DIO` | `IoExtDev` 外设设备层 | `summaries/Gp_DRV887x_DIO.md` |
| `Gp_Mux` | `IoExtDev` 外设设备层 | `summaries/Gp_Mux.md` |
| `Gp_TLE92104` | `IoExtDev` 外设设备层 | `summaries/Gp_TLE92104.md` |
| `Gp_RstM` | `BswSys_Gp` 系统层 | `summaries/Gp_RstM.md` |
| `Gp_SysState` | `BswSys_Gp` 系统层 | `summaries/Gp_SysState.md` |
| `Gp_TimeRecord` | `Cdd` 功能构件层 | `summaries/Gp_TimeRecord.md` |
| `Gp_CpuLoadMonitor` | `RtMon` 运行时监控层 | `summaries/Gp_CpuLoadMonitor.md` |

## 使用建议

1. 先读 `MODULE_INDEX.md`，选出最接近的样本
2. 除非目标横跨多个模式，否则只读一个摘要文件
3. 摘要只能作为架构风格证据，不能当成强制模板
4. 用户需求和当前项目约束永远优先于历史摘要
5. 任何配置宏、依赖接口或文件结构在提升为正式输出前，都要重新做必要性检查
