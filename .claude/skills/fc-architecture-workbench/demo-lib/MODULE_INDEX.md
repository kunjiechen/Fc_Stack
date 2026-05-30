# Demo Summary Module Index

## Purpose

This index maps each retained FC architecture summary to the architecture point it is best suited to validate.

Use this file before opening any summary, so historical demo knowledge is used intentionally and with minimal context loading.

## Coverage Matrix

| Module | Layer | Sub-type | Summary File | Structured Reference | Main Validation Points | Best-Fit Target Scenario |
| --- | --- | --- | --- | --- | --- | --- |
| `Gp_TLE92104` | `IoExtDev` | **Reg** (SPI) | `summaries/Gp_TLE92104.md` | `summaries/Gp_TLE92104.arch.json` | Complex SPI chip control, register abstraction, mode/fault APIs, background state machine | SPI register-based external chip driver FC |
| `Gp_NCA95xx` | `IoExtDev` | **Reg** (I2C) | — | `summaries/Gp_NCA95xx.arch.json` | I2C register-based GPIO expander, register readback, INT handling | I2C register-based external chip driver FC |
| `Gp_DRV887x_DIO` | `IoExtDev` | **Pin** (DIO) | `summaries/Gp_DRV887x_DIO.md` | `summaries/Gp_DRV887x_DIO.arch.json` | DIO pin-control motor driver, mode control, output request, fault diagnosis | Pin-control external device FC |
| `Gp_Mux` | `IoExtDev` | **Pin** (DIO) | `summaries/Gp_Mux.md` | — | Mapping-heavy multi-channel design, periodic switching, cached reads | Mux/channel-switching FC |
| `Gp_IoMcuDio` | `IoMcu` | — | `summaries/Gp_IoMcuDio.md` | `summaries/Gp_IoMcuDio.arch.json` | Simple IO APIs, direction/input/output split, logical signal ID mapping | MCU DIO peripheral FC |
| `Gp_IoMcuAdc` | `IoMcu` | — | `summaries/Gp_IoMcuAdc.md` | — | ADC resource APIs, raw/diag split, `Cfg/CfgData/Callout` boundary | MCU ADC peripheral FC |
| `Gp_IoSigAdc` | `IoSigSrv` | — | `summaries/Gp_IoSigAdc.md` | — | Signal service abstraction, raw/converted/diag separation | Physical signal service FC |
| `Gp_SysState` | `BswSys_Gp` | — | `summaries/Gp_SysState.md` | `summaries/Gp_SysState.arch.json` | System state machine, revise hooks, Internal.h, recorder buffer, calibration carrier | System state management FC |
| `Gp_RstM` | `BswSys_Gp` | — | `summaries/Gp_RstM.md` | — | Reset reasons, NoClear data, NVM interaction, safe-state callouts | Reset/lifecycle management FC |
| `Gp_TimeRecord` | `Cdd` | — | `summaries/Gp_TimeRecord.md` | — | Lightweight utility FC, small API surface | Time-record/tool FC |
| `Gp_CpuLoadMonitor` | `RtMon` | — | `summaries/Gp_CpuLoadMonitor.md` | — | Multi-core runtime buffers, monitor APIs | CPU load/performance monitor FC |

## Structured Reference Selection by Architecture Family

When generating architecture, load the `.arch.json` file that matches the target family and sub-type:

| Target Family + Sub-type | Load This Reference | Key Patterns To Extract |
|--------------------------|--------------------|------------------------|
| IoExtDev Reg (SPI) | `Gp_TLE92104.arch.json` | SPI Callout, FC_Reg.h Required, REG CONST rendered, MainFunction Required, register readback |
| IoExtDev Reg (I2C) | `Gp_NCA95xx.arch.json` | I2C Callout, FC_Reg.h Required, REG CONST rendered, MainFunction Required |
| IoExtDev Pin (DIO) | `Gp_DRV887x_DIO.arch.json` | DIO Callouts only, NO FC_Reg.h, NO REG CONST, pin mapping in Cfg.c, MainFunction Conditional |
| IoMcu | `Gp_IoMcuDio.arch.json` | Synchronous APIs, no MainFunction default, signal-ID mapping macros, DET bookkeeping |
| BswSys_Gp | `Gp_SysState.arch.json` | Revise hooks, Internal.h, global runtime, Cali.c conditional, signal-count macros |

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
