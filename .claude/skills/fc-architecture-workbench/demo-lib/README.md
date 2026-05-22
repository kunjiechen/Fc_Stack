# Demo Architecture Summaries

## Purpose

This directory keeps architecture summaries distilled from the previous retained demo source/config samples.

The source/config demo library has been replaced by one Markdown summary per FC. Future FC architecture work should read these summaries instead of source code.

## Directory Layout

- `summaries/`
  - one architecture summary file per retained FC sample
- `MODULE_INDEX.md`
  - architecture-point index for selecting the closest summary quickly

## Retained Summary Modules

| Module | Layer | Summary |
| --- | --- | --- |
| `Gp_IoMcuAdc` | `IoMcu` resource layer | `summaries/Gp_IoMcuAdc.md` |
| `Gp_IoMcuDio` | `IoMcu` resource layer | `summaries/Gp_IoMcuDio.md` |
| `Gp_IoSigAdc` | `IoSigSrv` signal service layer | `summaries/Gp_IoSigAdc.md` |
| `Gp_DRV887x_DIO` | `IoExtDev` external device layer | `summaries/Gp_DRV887x_DIO.md` |
| `Gp_Mux` | `IoExtDev` external device layer | `summaries/Gp_Mux.md` |
| `Gp_TLE92104` | `IoExtDev` external device layer | `summaries/Gp_TLE92104.md` |
| `Gp_RstM` | `BswSys_Gp` system layer | `summaries/Gp_RstM.md` |
| `Gp_SysState` | `BswSys_Gp` system layer | `summaries/Gp_SysState.md` |
| `Gp_TimeRecord` | `Cdd` functional component layer | `summaries/Gp_TimeRecord.md` |
| `Gp_CpuLoadMonitor` | `RtMon` runtime monitor layer | `summaries/Gp_CpuLoadMonitor.md` |

## Use Guidance

1. Start with `MODULE_INDEX.md` to select the closest summary.
2. Read only the selected FC summary unless the target architecture spans multiple patterns.
3. Use summaries as architecture-style evidence, not as mandatory implementation templates.
4. Prefer user requirements and current project constraints over historical summary patterns.
5. Re-run configuration macro and dependency-interface necessity checks before promoting any item to formal output.
