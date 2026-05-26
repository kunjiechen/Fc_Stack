# Gp_IoMcuDio Grounding Input

## Module Identity
- Module Name: Gp_IoMcuDio
- Layer: IoMcu
- Safety Level: QM
- Project: FcStack

## Overview
Gp_IoMcuDio 是 MCU 层 DIO 信号驱动，封装 MCAL DIO 和 PORT 模块，为上层应用提供统一的数字输入/输出信号访问接口。每个信号通过 uint16 ID 寻址。

## Operating Modes
- Init: 初始化所有已配置 DIO 通道的本地缓冲区
- Normal: 正常读写模式下提供方向配置、输入读取和输出设置

## Interfaces

### Gp_IoMcuDio_Init
- Direction: output
- Description: 初始化函数，对所有已配置 DIO 通道设置初始值。需在 PORT 初始化完成后调用。不允许重入。

### Gp_IoMcuDio_SetDioSigDir
- Direction: output
- Description: 设置指定 DIO 通道的方向（输入/输出）。注意：当前 FC 版本不直接支持方向设置，项目通过 Callout 方式实现。

### Gp_IoMcuDio_GetDioSigLvlIn
- Direction: input
- Description: 通过信号 ID 读取指定 DIO 通道的输入电平。数据来源为 Callout 函数或 MCAL DIO 接口。

### Gp_IoMcuDio_SetDioSigLvlOut
- Direction: output
- Description: 通过信号 ID 设置指定 DIO 通道的输出电平。数据输出方式为 Callout 函数或 MCAL DIO 接口。

## Configuration
- Multi-core enable (GP_IOMCUDIO_CORE0_ENABLE, etc.)
- DET enable (GP_IOMCUDIO_DEV_ERROR_DETECT)
- Per-channel configuration (signal ID mapping, direction, initial level)

## Dependencies
- MCAL DIO
- MCAL PORT
- Gp_IoMcuDio_Callout.h (Callout functions)
- Gp_IoMcuDio_CfgData.h (Configuration data)

## Diagnostics
- DET 错误检测（未初始化访问、非法 ID、空指针）
- 返回 Std_ReturnType (E_OK / E_NOT_OK)
