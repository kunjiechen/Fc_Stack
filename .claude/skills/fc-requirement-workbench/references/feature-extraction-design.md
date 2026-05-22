# Feature Extraction Design for SRS Generation

本文件定义 SRS 生成前的芯片信息特征提取方案。它不是最终 SRS 模板，而是用于把 Datasheet、项目需求、源码、配置和测试材料转换成可审查、可组合、可追溯的中间特征模型。

核心目标：

- 正确读取芯片信息，而不是简单摘录文档句子。
- 多视角并行提取，避免只从单一功能块视角理解芯片。
- 详细提取子功能，支撑后续功能需求、接口需求、配置需求、状态需求、诊断需求、时序需求和非功能需求生成。
- 明确哪些内容能生成需求，哪些只能进入概述、约束、缺口或 Open Issue。
- 为后续驱动设计讨论提供基础数据，但不直接生成架构或代码。

## 1. 总体原则

1. Datasheet 事实不等于软件需求。
2. 特征提取先于需求生成。
3. 并行提取的是视角和证据，最终需求必须经过聚合、责任判断和缺口分析。
4. 每个特征必须保留来源、证据、软件责任、可生成需求判断和缺失输入。
5. 对每个重要功能，除提取事实外，还必须输出功能总结和应用方案。
6. 当基础数据不足时，不允许静默补全；必须输出 `Open Issue` 或 `Needs Review`。

## 2. 输入来源

| 输入来源 | 主要用途 | 典型内容 |
| --- | --- | --- |
| Datasheet | 建立芯片能力和约束 | 功能列表、Pin、寄存器、状态、时序、电气参数 |
| 项目需求文档 | 确认项目支持范围 | 需要支持的功能、不支持项、接口期望、安全等级 |
| 源码 | 校准现有命名和实现事实 | API、枚举、结构体、错误码、状态变量 |
| 配置文件 | 固化项目实例和默认值 | 实例数量、Pin 映射、默认方向、地址、开关 |
| 测试材料 | 提取验证意图 | 测试项、预期结果、边界条件、覆盖缺口 |
| 历史 SRS | 校准写法和颗粒度 | 需求表达、Ready/Draft 判断、章节组织 |

## 3. 多视角并行提取器

提取器应按视角拆分。各提取器可以逻辑并行执行，也可以在实现初期顺序执行，但输出必须保持独立来源和独立判断。

| 提取器 | 读取重点 | 输出特征 | 后续用途 |
| --- | --- | --- | --- |
| `identity_extractor` | 标题、首页、General Description | 芯片型号、类别、厂商、用途 | SRS 概述、适用范围 |
| `capability_extractor` | Feature list、General Description | 芯片能力、功能边界 | 概述、功能候选 |
| `pin_extractor` | Pin table、Pin description | Pin 分组、方向、极性、所有权候选 | 接口、资源、配置 |
| `interface_extractor` | I2C/SPI/CAN/LIN 协议、读写流程 | 通信协议、地址、读写序列、错误响应 | 接口需求 |
| `register_extractor` | Register map、address table | 寄存器组、地址、访问属性、默认值 | 功能、配置、接口 |
| `bitfield_extractor` | Bit description、field table | bit 语义、有效值、默认值、保留位 | 子功能、配置、边界 |
| `state_extractor` | POR、Reset、Operating mode、State diagram | 芯片状态、驱动状态候选、状态转换 | 状态需求、初始化 |
| `diagnostic_extractor` | INT、ERR、fault、status、flag | 诊断信号、错误状态、清除条件 | 诊断需求 |
| `timing_extractor` | Timing table、AC/DC characteristics | 时序值、触发条件、单位、上下限 | 时序需求、验证 |
| `electrical_extractor` | Electrical characteristics | 电压、电流、IO 驱动、上拉、功耗 | 资源约束、非功能 |
| `constraint_extractor` | Note、Caution、Reserved、Unsupported | 禁止项、限制输入、保留地址、未定义行为 | 边界、异常、Open Issue |
| `project_mapping_extractor` | 项目需求、配置、源码、测试 | 项目实际使用范围、API、默认策略 | Ready 需求判断 |

## 4. 后处理器

| 后处理器 | 作用 |
| --- | --- |
| `feature_aggregator` | 把散点证据合并成可用特征组，例如 P00-P17 + Register 0-7 合成 GPIO 控制能力 |
| `cross_view_validator` | 用多视角证据交叉校验，例如 Feature list、Pin table、Register map 是否互相支持 |
| `responsibility_classifier` | 判断软件责任：软件动作、软件约束、硬件能力、项目排除、不适用、待确认 |
| `subfunction_analyzer` | 对每个能力继续拆解子功能，输出功能总结和应用方案 |
| `gap_analyzer` | 输出缺失项目输入，例如 API 命名、默认配置、错误处理、验证方式 |
| `requirement_candidate_mapper` | 将特征映射到候选需求类别，但不直接确认 Ready |

## 5. 特征类别

| 特征类别 | 必须提取内容 | 典型问题 |
| --- | --- | --- |
| 芯片身份特征 | 型号、器件类型、用途、接口类型、通道数量 | 型号和封装是否影响软件 |
| 能力特征 | 芯片支持的功能、功能边界、组合能力 | Datasheet 支持是否等于项目支持 |
| Pin 特征 | 名称、方向、极性、端口分组、软件关系 | Pin 是否由软件控制或采样 |
| 接口协议特征 | 总线类型、地址、读写流程、返回/错误语义 | 项目 API 是否封装该协议 |
| 寄存器特征 | 地址、名称、访问属性、默认值、用途 | 是否需要驱动读写和缓存 |
| Bitfield 特征 | bit 含义、有效值、默认值、保留位 | 是否存在非法值或保留位处理 |
| 子功能特征 | 输入、输出、配置、状态、错误、时序 | 能否形成可验证需求 |
| 状态特征 | POR、Reset、Ready、Error、状态转换 | 芯片状态和驱动状态是否混淆 |
| 诊断特征 | 中断、错误标志、状态位、清除机制 | 是否有软件可观测路径 |
| 时序特征 | 最小/最大值、单位、触发条件、测量点 | 是否可测、是否需软件等待 |
| 电气/资源特征 | 电压、电流、IO、功耗、上拉、频率 | 是否只是硬件约束 |
| 限制/禁止特征 | Reserved、unsupported、invalid、caution | 软件是否需要拒绝 |
| 项目映射特征 | 使用范围、默认策略、接口命名、ASIL、验证方式 | 能否从候选变成 Ready |

## 6. 子功能详细提取模型

每个能力特征必须进一步拆解子功能。子功能不是实现设计，而是 SRS 生成所需的行为单元。

每个子功能至少包含：

| 字段 | 说明 |
| --- | --- |
| Subfunction Name | 子功能名称 |
| Functional Summary | 该子功能做什么，解决什么问题 |
| Trigger / Entry | 触发条件或调用入口 |
| Inputs | 输入参数、配置项、Pin、寄存器、状态 |
| Outputs | 输出结果、返回值、寄存器变化、状态变化 |
| Preconditions | 前置条件 |
| Postconditions | 后置条件 |
| Error / Boundary | 错误、非法输入、禁止值、边界 |
| Timing | 相关时序值 |
| Related Pins | 相关 Pin |
| Related Registers | 相关寄存器 |
| Application Scheme | 项目中可能如何使用该子功能 |
| Candidate Requirement Types | 功能、接口、配置、状态、诊断、时序、非功能 |
| Missing Inputs | 缺失的项目输入 |
| Can Generate Requirement | Yes / Needs Review / No |

## 7. 应用方案输出要求

对每个重要特征或子功能，必须输出 `Application Scheme`。该字段用于说明它在驱动需求中可能如何落地，但不得直接承诺项目一定支持。

应用方案应覆盖：

- 软件是否需要提供 API。
- 是否需要初始化配置。
- 是否需要运行时配置。
- 是否需要缓存或读回确认。
- 是否需要错误处理。
- 是否需要测试验证。
- 是否依赖硬件连接或项目配置。

示例：

```markdown
Application Scheme:
The driver may expose pin-level and port-level APIs to read input state and write output state through the I2C register map. Project configuration must confirm which GPIO pins are used, their default direction, default output level, and whether runtime direction changes are allowed.
```

## 8. 聚合规则

特征聚合必须减少 Datasheet 摘抄式噪声。

推荐聚合：

| 原始提取 | 聚合结果 |
| --- | --- |
| P00-P07, P10-P17 | 16-bit GPIO Port Capability |
| SCL, SDA, I2C address, read/write sequence | I2C Control Interface |
| A0, A1, address table | I2C Address Selection |
| Register 0/1 | Input Port Register Group |
| Register 2/3 | Output Port Register Group |
| Register 4/5 | Polarity Inversion Register Group |
| Register 6/7 | Configuration Register Group |
| INT pin + input change behavior | Interrupt Signaling |
| RESET pin + POR defaults | Reset and Default State |
| Timing table rows | Timing Constraint Group |
| Reserved bits/registers/addresses | Prohibited or Boundary Group |

禁止直接把每个 GPIO pin、每个 bit、每个时序表行都生成独立需求。只有当项目需求明确要求单独控制或验证时，才允许拆成独立需求。

## 9. 软件责任判断

| 判断值 | 含义 | 需求处理 |
| --- | --- | --- |
| `software_action` | 软件需要主动调用、读写、配置或拒绝 | 可生成候选需求 |
| `software_constraint` | 软件需要遵守约束，但不一定直接控制 | 可生成约束/非功能/接口边界 |
| `hardware_capability` | 芯片能力事实 | 进入概述或候选，默认不 Ready |
| `hardware_constraint` | 电气或硬件限制 | 通常不生成软件需求 |
| `project_exclusion` | 项目明确不支持 | 生成范围边界或拒绝需求 |
| `not_applicable` | 与软件无关 | 不生成需求 |
| `open_issue` | 责任不清 | 输出缺口，等待确认 |

## 10. 可生成需求判断

| 值 | 判定条件 |
| --- | --- |
| `Yes` | 有明确软件动作、来源、输入输出、边界和验证方式 |
| `Needs Review` | Datasheet 支持，但项目责任、接口、默认策略或验证方式不完整 |
| `No` | 纯硬件事实、封装信息、电气绝对值、订购信息、无软件动作 |

Datasheet-only 输入默认不得直接生成 `Ready` 需求，除非该行为明显属于通用驱动职责并且仍标记为候选状态等待项目确认。

## 11. 中间文件结构

中间文件应按“策略、摘要、特征组、子功能、缺口”组织。

```markdown
# Feature Extraction - {MODULE}

## Extraction Strategy

## Cross-view Summary

## Feature Groups

### FEAT-{MODULE}-GPIO-001 16-bit GPIO Port Capability

| 字段 | 内容 |
| --- | --- |
| Feature Category | Capability / GPIO |
| Functional Summary | ... |
| Evidence | ... |
| Related Pins | ... |
| Related Registers | ... |
| Software Responsibility | ... |
| Candidate Requirement Types | ... |
| Application Scheme | ... |
| Missing Inputs | ... |
| Can Generate Requirement | ... |
| Status | ... |

#### Subfunctions

| Subfunction | Summary | Inputs | Outputs | Boundary | Application Scheme | Can Generate Requirement |
| --- | --- | --- | --- | --- | --- | --- |

## Open Issues and Required Inputs
```

## 12. NCA9539 推荐特征组

针对 NCA9539 类 I2C GPIO 扩展芯片，至少应形成以下特征组：

| 特征组 | 子功能 |
| --- | --- |
| Chip Identity | 器件识别、适用场景、能力边界 |
| 16-bit GPIO Port Capability | 输入读取、输出控制、方向配置、端口级访问、Pin 级访问 |
| I2C Control Interface | 地址选择、寄存器读、寄存器写、通信错误处理 |
| Register Map | Input、Output、Polarity、Configuration 寄存器组 |
| Input Port Function | 输入采样、端口读取、Pin 读取、输入变化识别 |
| Output Port Function | 输出写入、默认输出、读回/缓存策略 |
| Polarity Inversion Function | 输入极性配置、默认极性、非法配置处理 |
| Direction Configuration Function | 输入/输出方向配置、默认输入状态、运行时变更策略 |
| Interrupt Signaling | INT 触发条件、有效电平、清除条件、软件响应 |
| Reset and POR Behavior | 上电默认、RESET 输入、复位后重新初始化 |
| Timing Constraints | I2C 频率、reset timing、interrupt timing、读写时序 |
| Electrical and Resource Constraints | 供电、IO 电流、上拉、地址脚、I2C 总线资源 |
| Prohibited / Reserved Behavior | 保留地址、保留 bit、非法寄存器访问、未支持接口 |

## 13. 完整开发支撑边界

该特征模型可支撑：

- 芯片能力理解。
- 驱动功能边界识别。
- SRS 候选需求生成。
- 配置项候选生成。
- 接口候选生成。
- 验证点候选生成。
- 缺口和补料清单生成。

但它不能单独完成完整开发，还需要：

- 项目支持范围。
- API 命名和接口规范。
- 配置规范。
- 硬件原理图或 Pin 使用清单。
- 安全等级。
- 错误处理策略。
- I2C 访问方式和底层依赖。
- 测试策略和验收标准。

## 14. 执行流程

```text
输入 Markdown / 项目材料
  ↓
文档结构解析
  ↓
多视角并行提取
  ├─ identity
  ├─ capability
  ├─ pin
  ├─ interface
  ├─ register
  ├─ bitfield
  ├─ state
  ├─ diagnostic
  ├─ timing
  ├─ electrical
  ├─ constraint
  └─ project_mapping
  ↓
特征聚合
  ↓
子功能分析
  ↓
多视角交叉校验
  ↓
软件责任判断
  ↓
缺口分析
  ↓
特征提取中间文件
  ↓
候选需求生成
  ↓
人工确认 / 补充项目输入
  ↓
正式 SRS Markdown
```

## 15. 质量检查

中间文件生成后必须检查：

- 是否形成特征组，而不是仅有零散摘录。
- 是否详细列出子功能。
- 是否给出每个子功能的应用方案。
- 是否区分芯片能力和软件责任。
- 是否标出缺失项目输入。
- 是否保留来源证据。
- 是否避免把封装、订购、法律声明、电气绝对值直接生成需求。
- 是否避免 Datasheet-only 内容直接变成 Ready 需求。
