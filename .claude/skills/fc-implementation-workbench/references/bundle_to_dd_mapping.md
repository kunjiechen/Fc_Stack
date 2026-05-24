# Bundle To Detailed Design Mapping

## 1. 目的

本文件定义结构化 bundle 中的字段，应该如何映射到详细设计正文。

目标是避免：

- 数据有了，但正文不知道怎么落位
- 同一个字段在不同文档里落到不同章节
- 渲染器只会平铺字段，不能生成设计表达

## 2. 映射原则

### 2.1 文档不是 source of truth

bundle 才是中间真相层，markdown 是渲染结果。

### 2.2 字段分两类

- 直接呈现型字段
  - 在正文里有明确位置
- 控制生成型字段
  - 不一定直接出现在正文中，但决定章节内容、粒度、语气、取舍

### 2.3 正文不展示内部生成对象

以下字段可以强烈影响正文，但不应直接渲染其内部名字：

- `grounding_modules`
- `grounding_patterns`
- `grounding_rejections`
- `conf_evidence`

它们的作用是控制正文，不是进入正文。

### 2.4 章节优先级

同一个字段可能影响多个章节，但必须有主落点和次落点。

## 3. 顶层字段映射

### 3.1 `module`

- 主落点:
  - `1. FC概述`
  - 文档元信息
- 控制作用:
  - 所有接口名、内部接口名、文件名命名空间

### 3.2 `grounding_modules`

- 直接落点:
  - 无
- 控制作用:
  - 决定层级判断
  - 决定实现风格
  - 决定功能设计和依赖接口设计的叙述侧重点

### 3.3 `grounding_patterns`

- 直接落点:
  - 无
- 次级影响章节:
  - `4. 功能设计`
  - `6. 单核/多核框架设计`
  - `11. 状态机设计`
  - `14. 运行时变量设计`
  - `16. MemMap设计`

### 3.4 `grounding_rejections`

- 直接落点:
  - 无
- 控制作用:
  - 决定正文里哪些实现模式不应出现

### 3.5 `conf_evidence`

- 直接落点:
  - 无
- 控制作用:
  - 决定 cfg/callout 章节的配置边界和依赖边界表达

### 3.6 `assumptions`

- 默认不直接渲染为“假设”章节
- 控制作用:
  - 参与判断单核/多核
  - 参与判断状态机是否弱化
  - 参与判断哪些内容属于真实待确认项

规则：

- 如果条目本质是实现方案，则应回流到 `1`、`4`、`6`、`11` 等设计章节
- 不再单列“待确认项”主章节
- 少量未确认内容应回流到配置、框架或覆盖表备注

### 3.7 `risks`

- 默认不单独渲染风险章节
- 控制作用:
  - 对覆盖表备注、实现限制要求提供补充说明

## 4. Requirement 字段映射

### 4.1 `requirements[*].id`

- 默认不在每段正文中密集展示
- 主作用:
  - trace 控制
  - 覆盖表
  - 校验

### 4.2 `requirements[*].status`

- `confirmed`
  - 不需要特别强调
- `pending_confirm`
  - 主落点:
    - `15. 配置宏参设计`
    - `18. 架构与详细设计覆盖表`
- `derived`
  - 主落点:
    - 对应设计章节中的简短说明

### 4.3 `decision`

- 主落点:
  - `4. 功能设计`
  - `15. 配置宏参设计`
  - `18. 架构与详细设计覆盖表`

### 4.4 `decision_reason`

- 主落点:
  - 紧跟 `decision`

### 4.5 `impacts`

- 默认不需要逐条渲染
- 主作用:
  - 控制哪些章节必须补说明

## 5. Architecture 字段映射

### 5.1 `architecture.external_interfaces`

- 主落点:
  - `7. 外部接口设计`
- 次落点:
  - `18. 架构与详细设计覆盖表`

formal external interface 必须一一渲染。

### 5.2 `architecture.dependency_interfaces`

- 主落点:
  - `9. 依赖接口与Callout设计`
- 次落点:
  - `18. 架构与详细设计覆盖表`

formal dependency interface 必须一一渲染。

### 5.3 `architecture.config_items`

- 主落点:
  - `15. 配置宏参设计`
- 次落点:
  - `18. 架构与详细设计覆盖表`

规则：

- `formal`
  - 作为当前版本确认配置输出
- `reserved`
  - 说明存在但当前不开放
- `pending_confirm`
  - 必须进入 `15. 配置宏参设计` 的备注或说明
- `conditional`
  - 只有 architecture 明确冻结时才允许写入正文

## 6. Detailed Design 字段映射

### 6.1 `detailed_design.external_interfaces`

- 主落点:
  - `7. 外部接口设计`
- 每项至少展开：
  - 接口表
  - 子功能拆分
  - 执行步骤
  - 参与内部接口
  - 需要时流程图

### 6.2 `detailed_design.internal_interfaces`

- 主落点:
  - `8. 内部接口设计`

规则：

- 先总表
- 再按关键内部接口展开小节
- 小节形式尽量接近外部接口

### 6.3 `detailed_design.dependency_interfaces`

- 主落点:
  - `9. 依赖接口与Callout设计`

### 6.4 `relationship_links`

- 默认不直接原样渲染成字段列表
- 主要用于：
  - 决定 external interface 的参与内部接口表
  - 决定 internal interface 的调用方/依赖方
  - 决定 dependency interface 的关联接口表
  - 决定覆盖表中的承接关系

规则：

- 未定义 relationship object 不得进入主接口表和主执行步骤
- 未定义对象只能进入待修正文档说明

## 7. Pattern 到章节的重点映射

### 7.1 `per_core_runtime_container`

- 强化章节:
  - `4. 功能设计`
  - `6. 单核/多核框架设计`
  - `14. 运行时变量设计`
  - `16. MemMap设计`

### 7.2 `dependency_interface_shape`

- 强化章节:
  - `4. 功能设计`
  - `9. 依赖接口与Callout设计`

### 7.3 `chip_mainfunction_pattern`

- 强化章节:
  - `4. 功能设计`
  - `7. 外部接口设计` 中 `MainFunction`
  - `8. 内部接口设计`

### 7.4 `runtime_capability_reserved_in_config`

- 强化章节:
  - `15. 配置宏参设计`
  - `18. 架构与详细设计覆盖表`

### 7.5 `conditional_external_interfaces`

- 直接落点:
  - 无
- 控制作用:
  - 防止正文错误生成未冻结 external interface

## 8. 冲突优先级

渲染时应遵循：

1. architecture freeze
2. detailed_design bundle
3. project constraints and explicit pending items
4. assumptions 中的明确部署结论
5. grounding patterns

也就是说：

- 对单核/多核的最终判断，已确认项目约束优先级高于 grounding pattern
- 对正文是否展示某项，规范边界优先级高于生成便利性
