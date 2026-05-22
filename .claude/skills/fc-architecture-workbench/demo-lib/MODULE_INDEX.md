# Demo Summary Module Index

## Purpose

This index maps each retained FC architecture summary to the architecture point it is best suited to validate.

Use this file before opening any summary, so historical demo knowledge is used intentionally and with minimal context loading.

## Coverage Matrix

| Module | Layer | Summary File | Main Validation Points | Best-Fit Target Scenario |
| --- | --- | --- | --- | --- |
| `Gp_IoMcuAdc` | `IoMcu` resource layer | `summaries/Gp_IoMcuAdc.md` | ADC resource APIs, `Init/MainFunction`, raw/diag split, `Cfg/CfgData/Callout` boundary | MCU ADC resource FC |
| `Gp_IoMcuDio` | `IoMcu` resource layer | `summaries/Gp_IoMcuDio.md` | Simple IO APIs, direction/input/output split, logical signal ID mapping | DIO/IO control FC |
| `Gp_IoSigAdc` | `IoSigSrv` signal service layer | `summaries/Gp_IoSigAdc.md` | Signal service abstraction, raw/converted/diag separation, calibration/conversion handling | Physical signal service FC |
| `Gp_DRV887x_DIO` | `IoExtDev` external device layer | `summaries/Gp_DRV887x_DIO.md` | Mode control, output request, current readback, fault diagnosis, multi-core/multi-instance runtime | H-bridge or motor-driver chip FC |
| `Gp_Mux` | `IoExtDev` external device layer | `summaries/Gp_Mux.md` | Mapping-heavy multi-channel design, periodic switching, cached reads, minimal external APIs | Mux/channel-switching FC |
| `Gp_TLE92104` | `IoExtDev` external device layer | `summaries/Gp_TLE92104.md` | Complex SPI chip control, register abstraction, mode/fault APIs, background state machine | SPI external chip driver FC |
| `Gp_RstM` | `BswSys_Gp` system layer | `summaries/Gp_RstM.md` | Reset reasons, NoClear data, NVM interaction, safe-state callouts | Reset/lifecycle management FC |
| `Gp_SysState` | `BswSys_Gp` system layer | `summaries/Gp_SysState.md` | System state machine, `Internal.h`, external/internal state separation, recorder buffer | System state management FC |
| `Gp_TimeRecord` | `Cdd` functional component layer | `summaries/Gp_TimeRecord.md` | Lightweight utility FC, small API surface, optional observation callout | Time-record/tool FC |
| `Gp_CpuLoadMonitor` | `RtMon` runtime monitor layer | `summaries/Gp_CpuLoadMonitor.md` | Multi-core runtime buffers, monitor APIs, observation ownership | CPU load/performance monitor FC |

## Recommended Selection Strategy

- Resource wrapper: start with `Gp_IoMcuAdc` or `Gp_IoMcuDio`.
- Signal/service abstraction: start with `Gp_IoSigAdc`.
- External chip driver: start with `Gp_DRV887x_DIO`, `Gp_TLE92104`, or `Gp_Mux`.
- System-level module: start with `Gp_RstM` or `Gp_SysState`.
- Monitor/observer: start with `Gp_CpuLoadMonitor`.
- Lightweight utility: start with `Gp_TimeRecord`.

## Use Notes

- Do not treat any single summary as the mandatory final form.
- Read one closest summary first; read additional summaries only when the target FC crosses patterns.
- Summary files replace the previous retained source/config samples.
- Always apply current requirements, project constraints, and formal macro/dependency necessity checks before producing final architecture.
