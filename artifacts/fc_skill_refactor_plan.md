# FC Skill Refactor Plan

## 1. 目标

本轮的真实改造对象是现有 skill：

- `/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/.claude/skills/fc-implementation-workbench`

本轮不是去修改仓库根目录下其他试验性 skill 目录，而是把当前已有的 `fc-implementation-workbench` 作为主载体，升级成更稳定的 FC 详细设计生成工作流承载体。

长期目标仍然是把能力边界整理为：

1. `fc-requirement-design`
2. `fc-architecture-design`
3. `fc-detailed-design`

但本轮**不做三 skill 并行深改**，而是：

- 以 `fc-implementation-workbench` 为当前实施载体
- 先把“详细设计生成流水线能力”落进去
- 后续再决定是否从该 skill 正式拆分/改名为 `fc-detailed-design`

这样做的原因是，当前若同时改三个 skill，容易让 grounding、schema、validator、规则文件再次分散。

---

## 2. 当前问题

当前混乱主要来自四个方面：

1. 三类 skill 的职责边界没有切开
2. 规则、参考资料、grounding、校验混在一起
3. 生成流程和校验流程没有拆开
4. 真实工程 grounding 还没有沉淀成 skill 内部标准资产

因此，本轮不是简单补 prompt，而是重构 skill 架构。

---

## 3. 目标能力边界

虽然本轮只改 `fc-implementation-workbench`，但它承接的能力边界必须对齐未来的三 skill 体系。

### 3.1 `fc-requirement-design`

职责：

- 原始输入理解
- 需求抽取
- 需求结构化
- 需求 ID / 来源 / 状态 / 约束 / 验收准则整理
- 需求层一致性检查

不负责：

- 冻结 external/dependency interface
- internal interface 拆分
- 详细控制流和运行态设计

### 3.2 `fc-architecture-design`

职责：

- 从需求导出架构设计
- 冻结 external interfaces
- 冻结 dependency interfaces
- 配置宏/配置表边界定义
- 文件列表、MemMap、风险项定义
- formal / reserved / pending_confirm 边界控制

不负责：

- internal interface 设计
- 详细流程图和控制流
- 运行态细节拆分

### 3.3 `fc-detailed-design`

职责：

- 基于 architecture 冻结结果展开详细设计
- internal interface 设计
- external/internal/dependency 关系追踪
- 控制流、状态机、运行态设计
- grounding 选型
- 自动校验
- 详细设计产物稳定性控制

不负责：

- 重新改写需求
- 擅自变更 architecture 冻结接口集合

---

## 4. 本轮实施范围

### 4.1 本轮正式落地重点

本轮正式深改对象只有一个：

- `.claude/skills/fc-implementation-workbench`

但其升级目标是承载 `fc-detailed-design` 这条能力主线。

### 4.2 本轮同步处理，但只作为未来边界参考

- `fc-requirement-design`
- `fc-architecture-design`

本轮只在计划层面保留它们的职责边界，不进入实际重构实施。

---

## 5. `fc-implementation-workbench` 本轮升级目标

把当前 `fc-implementation-workbench` 从“实现设计 workbench”升级为“可承载详细设计流水线能力的稳定 skill”。

本轮目标包括：

1. 保留当前 skill 路径不变
2. skill 内部目录按标准 skill 结构增强
3. grounding 资产沉入该 skill 内部
4. schema 沉入该 skill 内部
5. validator 沉入该 skill 内部
6. `SKILL.md` 重写为“主规则 + 外挂 references”结构
7. 用 `Gp_NCA95yy` 样例验证新结构和校验链

---

## 6. 当前 skill 的目标目录结构

计划结构如下：

```text
.claude/skills/fc-implementation-workbench/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── validate_fc_docs.py
└── references/
    ├── grounding/
    │   ├── index.yaml
    │   ├── grounding_scope.md
    │   ├── modules/
    │   └── patterns/
    ├── schemas/
    │   ├── requirements.schema.json
    │   ├── architecture.schema.json
    │   └── detailed_design.schema.json
    ├── workflow.md
    └── validation_rules.md
```

原则：

- `SKILL.md` 只放核心规则和使用流程
- grounding、schema、pattern、workflow 放 `references/`
- 校验脚本放 `scripts/`
- 尽量复用当前 skill 已有 `references/rules/`、`references/templates/`、`references/semantic-model.md`
- 不再把这些内容散落在 skill 外部目录

---

## 7. Grounding 方案

本轮 grounding 不会把完整工程嵌入 skill。

采用“基线抽取”方式，仅沉淀推荐 FC 的标准化摘要与模式。

### 7.1 Grounding 参考范围

本轮 grounding 基线来自以下推荐 FC：

1. `Gp_WkUpSrcP`
2. `Gp_06_Adc3ph`
3. `Gp_TPT1145`
4. `Gp_TLE92104`
5. `Gp_DRV8889`
6. `IoMcu`

以及对应 `Conf_*` 配置目录。

### 7.2 Grounding 的目标

在详细设计生成前，先回答这些问题：

- 真实工程里 external interface 一般怎么定
- dependency interface 的真实形态是什么
- `CalloutGetCoreId` 是否属于标准模式
- runtime container 是 direct array 还是 per-core container
- DET / fault 设计一般是轻量还是重型
- MemMap / CfgData / Conf 的真实风格是什么

### 7.3 Grounding 产物

当前 skill 内部应沉淀：

- grounding 模块索引
- 每个基线模块的 summary
- 每个基线模块的 facts
- pattern 文档

---

## 8. 结构化 Schema 方案

本轮会在 `fc-implementation-workbench` skill 内定义中间模型 schema。

### 8.1 目标

不要再直接从自然语言一步生成 markdown。

改为：

1. requirement model
2. architecture model
3. detailed design model
4. markdown rendering

### 8.2 本轮 schema 范围

- `requirements.schema.json`
- `architecture.schema.json`
- `detailed_design.schema.json`

### 8.3 作用

即使这次还不做完整自动化生成器，schema 也能先统一数据结构，为后续 requirement/architecture skill 升级做好接口准备。

---

## 9. 自动校验方案 V1

本轮只做最关键的一批硬校验，先解决“生成了但明显不一致”的问题。

### 9.1 校验范围

1. DD external interfaces 是否与 architecture 完全一致
2. DD dependency interfaces 是否与 architecture 完全一致
3. formal dependency interface 是否漏项
4. `关联接口` 字段是否存在
5. 明显的架构/详设接口漂移是否存在

### 9.2 本轮不做

- requirement 全量追溯校验
- config/risk 全量交叉校验
- internal interface 全量语义正确性校验

这些留到后续版本。

---

## 10. `SKILL.md` 重写目标

新版本 `.claude/skills/fc-implementation-workbench/SKILL.md` 只保留四类内容：

1. skill 适用范围
2. 输入输出边界
3. 详细设计生成流程
4. 何时读取哪些 references

不再把全部 grounding、pattern、workflow、校验规则挤在一个文件中。

---

## 11. 本轮执行步骤

### Step 1

盘点当前 `.claude/skills/fc-implementation-workbench` 已有结构与可复用资产。

### Step 2

确认本轮仅以 `fc-implementation-workbench` 为改造载体，不改错目录。

### Step 3

在当前 skill 内增加 `grounding/`、`schemas/`、`scripts/validator` 能力结构。

### Step 4

把当前已整理的 grounding/schema/validator/workflow 内容迁入 `fc-implementation-workbench` skill 内部。

### Step 5

重写当前 skill 的 `SKILL.md`，改成“主规则 + references 导航”的结构。

### Step 6

清理之前落在错误目录或 skill 外的临时内容。

### Step 7

用 `Gp_NCA95yy` 跑一轮 validator 验证新结构。

---

## 12. 本轮交付物

本轮最终交付应包括：

1. `fc-implementation-workbench` 的标准化目录结构
2. grounding 参考资产进入 `.claude/skills/fc-implementation-workbench/references/grounding/`
3. schema 进入 `.claude/skills/fc-implementation-workbench/references/schemas/`
4. validator 进入 `.claude/skills/fc-implementation-workbench/scripts/`
5. 当前 skill 的 `SKILL.md` 重写完成
6. 错误目录下的临时内容清理或迁移完成
7. `Gp_NCA95yy` 样例验证结果

---

## 13. 本轮明确不做的事

为了避免再次失控，本轮明确不做：

- 不同时深改三个 skill 的完整实现
- 不把完整参考工程嵌入 skill
- 不做 requirement/architecture 的重型 validator
- 不做大而全自动生成流水线

---

## 14. 推荐验证目标

本轮验证只要求证明两件事：

1. 当前 `fc-implementation-workbench` skill 结构已经标准化
2. grounding + schema + validator 已经能够支撑 `Gp_NCA95yy` 这类详细设计生成任务

---

## 15. 执行策略总结

本轮不是“三个 skill 一起重写”，也不是去改错目录，而是：

- 先把目标能力边界切清
- 真正落地只改 `.claude/skills/fc-implementation-workbench`
- 把这个 skill 做成标准结构、带 grounding、带 schema、带 validator 的版本
- 后续如果需要，再从这个 skill 正式拆分/演进出 `fc-detailed-design`

后续如果这条链跑通，再把 requirement 和 architecture 两个 skill 按同样方式逐步升级。
