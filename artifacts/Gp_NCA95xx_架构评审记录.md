# Gp_NCA95xx 架构评审记录

## 1. 说明

本文档为 `Gp_NCA95xx_软件架构设计.md` V1 Draft 的评审记录与评审指南，供软件架构评审人员和相关工程师使用。评审应聚焦于架构完整性、正确性、安全性和可集成性。

## 2. 评审角色

| 角色 | 评审重点 |
| --- | --- |
| 软件架构工程师 | 接口设计合理性、配置分类正确性、依赖边界清晰性、MemMap 策略正确性 |
| 功能安全工程师 | ASIL_B 安全机制覆盖（输出回读、I2C 故障检测、安全状态定义）、DET 覆盖完整性 |
| 硬件工程师 | INT/RESET 引脚连接确认（R1/R2）、I2C 地址与原理图一致性（CFG-0002） |
| 软件集成工程师 | Callout 实现可行性、I2C/DIO 驱动绑定方式、多核配置数据部署 |
| 软件测试工程师 | 接口可测试性、DET 用例覆盖、故障注入点 |

## 3. 评审维度

### 3.1 外部接口评审

对照 SRS INTF 需求，逐接口确认：

- [ ] `Gp_NCA95xx_Init` — 多芯片实例初始化逻辑、部分失败处理是否符合预期
- [ ] `Gp_NCA95xx_MainFunction` — 周期调度周期、INT 检测/降级策略是否符合预期
- [ ] `Gp_NCA95xx_GetGpioInSig` — 极性与缓存策略是否正确
- [ ] `Gp_NCA95xx_SetGpioOutSig` — 同步写入 vs 异步缓存策略是否正确（当前架构采用同步 I2C 写入）
- [ ] `Gp_NCA95xx_GetDevFaultSig` — 故障位定义是否满足诊断需求
- [ ] `Gp_NCA95xx_GetDevModeInSig` — 状态枚举值是否与 SRS 一致
- [ ] `Gp_NCA95xx_ResetChip`（条件接口）— 是否需要此接口，若需要，时序约束是否满足

### 3.2 配置评审

- [ ] `GP_NCA95xx_CFG_DEV_ERROR_DETECT` 默认 STD_ON 是否合适
- [ ] `GP_NCA95xx_CFG_REG_READBACK_VERIFY_ENABLE` 默认 STD_ON 是否合适（ASIL_B 安全需求）
- [ ] `GP_NCA95xx_CFG_RUNTIME_DIR_CHANGE_ENABLE` 默认 STD_OFF 是否满足项目需求
- [ ] `GP_NCA95xx_CFG_RESET_PIN_OWNED` 默认 STD_OFF — 硬件确认后调整
- [ ] 配置数据表结构（DevAddr、DefaultDir、DefaultOut 等）是否完整

### 3.3 依赖接口评审

- [ ] I2C Write/Read Callout 参数设计是否满足 NCA9539-Q1 的 I2C 访问模式
- [ ] ReadDio Callout 是否需要（取决于 INT 引脚连接，见 R1）
- [ ] WriteDio + DelayUs Callout 是否需要（取决于 RESET 引脚连接，见 R2）
- [ ] GetCoreId Callout 在多核场景下的正确性
- [ ] Callout 实现边界（Project Adaptation / IoMcu / MCAL）是否清晰

### 3.4 安全评审（ASIL_B）

- [ ] 输出回读校验（SAFE-0002）的覆盖范围：配置标记为安全关键的输出引脚范围是否明确
- [ ] 安全状态（SAFE-0003）的 Fault 行为：停止新 I2C 操作 + 保留输出缓存，是否满足安全目标
- [ ] DET 覆盖（DIAG-0002）：所有外部接口的 NULL 指针、无效参数、未初始化访问检测是否完整
- [ ] I2C 通信故障检测（DIAG-0001）：故障确认阈值（3）和恢复阈值（2）是否合适

### 3.5 MemMap 评审

- [ ] RUNTIME RAM 使用 CLEAR_FAR_DATA_ALIGN4_COREx — 每核独立运行态是否符合多核部署方案
- [ ] CONST PER-CORE vs GLOBAL 拆分是否合理 — 取决于多核配置数据是否独立
- [ ] CALIB 段当前为空 — 未来是否需要标定参数

### 3.6 文件结构评审

- [ ] 10 个文件是否完整覆盖 FC 功能
- [ ] `Gp_NCA95xx_Reg.h` 包含的寄存器定义是否完整（Input Port 0/1、Output Port 0/1、Polarity 0/1、Configuration 0/1）
- [ ] `Gp_NCA95xx_Callout.c` stub 框架是否满足集成需求

## 4. 关键风险项评审

| 风险 | 评审问题 | 决策者 |
| --- | --- | --- |
| R1: INT 引脚归属 | INT 是否接入 MCU GPIO？由本驱动采样还是外部 ISR？ | 硬件工程师 + 系统工程师 |
| R2: RESET 引脚归属 | RESET 是否接入 MCU GPIO 且由本驱动控制？ | 硬件工程师 + 系统工程师 |
| R3: 上层通知机制 | 是否需要回调/Callout 通知，还是上层自行轮询 GetGpioInSig？ | 软件架构工程师 |
| R4: 运行时方向变更 | 项目是否需要运行时修改 GPIO 方向？ | 系统工程师 |
| R5: 故障恢复策略 | Fault→Normal 后是否需要重新回写寄存器？ | 软件架构工程师 + 功能安全工程师 |
| R6: 多核配置归属 | 每核独立芯片实例 vs 跨核共享？ | 软件架构工程师 |
| R7: 资源预算 | ROM/RAM 预算确认 | 软件集成工程师 |

## 5. 评审结论模板

```text
评审结论：
- 接口设计：[通过/需修改]，具体意见：___
- 配置设计：[通过/需修改]，具体意见：___
- 依赖设计：[通过/需修改]，具体意见：___
- 安全设计：[通过/需修改]，具体意见：___
- MemMap设计：[通过/需修改]，具体意见：___
- 文件结构：[通过/需修改]，具体意见：___
- 风险项评审：
  R1 [已评审/待修改]，备注：___
  R2 [已评审/待修改]，备注：___
  ...
  R-OTHER，备注：___
```
