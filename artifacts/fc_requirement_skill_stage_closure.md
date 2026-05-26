# FC Requirement Skill 阶段收口基线

## 1. 文档目的

本文档用于对 `fc-requirement-workbench` 当前阶段成果做正式收口，明确：

- 当前阶段已经完成了什么
- 哪些 artifact 可以作为 golden baseline
- 需求 skill 当前的职责边界是什么
- 后续回归应如何执行

本文档只针对需求 skill，不替代架构 skill 或详细设计 skill。

---

## 2. 当前阶段结论

当前阶段已经完成需求 skill 的第一轮工程化收口：

1. `raw input -> requirement bundle -> architecture seed -> test seed -> validation` 主链已跑通
2. raw extraction gate 已建立并完成两轮以上收敛
3. `ready/draft/open_issue` 已不再只是展示字段，而会受到 gate 和质量门禁约束
4. 三个代表性试点已经进入统一 regression pack；其中 2 个达到 `0 warning / 0 error`，1 个保留已知 warning 并纳入 expectation 管理

当前这套 requirement skill 已经不再是“只能生成 SRS 文档”的规则集合，而是具备结构化对象层、门禁、回放和 golden baseline 的独立 skill。

---

## 3. 职责边界

需求 skill 当前的职责定义如下：

- 负责 requirement bundle 生成
- 负责 requirement coverage / source / verification / status 证明
- 负责 architecture seed 和 test seed 输出
- 负责 requirement 级别 gate、promotion、quality contract 和 validation

需求 skill 不负责：

- 直接生成正式架构文档
- 冻结架构接口/文件列表/运行态/MemMap 最终方案
- 替代 `fc-architecture-workbench`

因此：

- `architecture seed` 是架构输入候选，不是正式架构结论
- `test seed` 是测试输入候选，不是正式测试用例集

---

## 4. Golden Baseline

当前阶段确定以下 3 个 regression baseline：

### 4.1 Gp_NCA95yy

输入：

- [Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN.md](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN.md)
- [raw_input_Gp_NCA95yy.txt](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/raw_input_Gp_NCA95yy.txt)

输出：

- [gp_nca95yy_requirement_bundle.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_nca95yy_requirement_bundle.yaml)
- [gp_nca95yy_architecture_seed.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_nca95yy_architecture_seed.yaml)
- [gp_nca95yy_test_seed.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_nca95yy_test_seed.yaml)
- [gp_nca95yy_bundle_validation.json](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_nca95yy_bundle_validation.json)

收口结果：

- validation = `0 warning / 0 error`
- capability promotion 已收口
- coverage gap 已收口

### 4.2 Gp_TLE92104

输入：

- [Gp_TLE92104_grounding_input.md](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/Gp_TLE92104_grounding_input.md)
- [raw_input_Gp_TLE92104.txt](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/raw_input_Gp_TLE92104.txt)

输出：

- [gp_tle92104_requirement_bundle.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_tle92104_requirement_bundle.yaml)
- [gp_tle92104_architecture_seed.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_tle92104_architecture_seed.yaml)
- [gp_tle92104_test_seed.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_tle92104_test_seed.yaml)
- [gp_tle92104_bundle_validation.json](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_tle92104_bundle_validation.json)

收口结果：

- validation = `0 warning / 0 error`
- capability promotion 已收口
- coverage gap 已收口

### 4.3 Gp_IoMcuDio

输入：

- [Gp_IoMcuDio_grounding_input.md](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/Gp_IoMcuDio_grounding_input.md)
- [raw_input_Gp_IoMcuDio.txt](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/raw_input_Gp_IoMcuDio.txt)

输出：

- [gp_iomcudio_requirement_bundle.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_iomcudio_requirement_bundle.yaml)
- [gp_iomcudio_architecture_seed.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_iomcudio_architecture_seed.yaml)
- [gp_iomcudio_test_seed.yaml](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_iomcudio_test_seed.yaml)
- [gp_iomcudio_bundle_validation.json](/Users/chenkunjie/Downloads/SBPAI/Proj/Fc_Stack/artifacts/gp_iomcudio_bundle_validation.json)

收口结果：

- validation = `0 error / 2 warning`
- warning 已固化到 regression expectation，不再作为隐性漂移
- 当前已知 warning 包括 1 个 `coverage_gap` 与 1 个 `ready_gate_weak`

---

## 5. 已固化的方法能力

当前阶段已经固化的能力包括：

1. source of truth 前移到 requirement bundle
2. raw extraction 支持 section-aware 切条
3. raw item 支持 `formal_requirement / constraint / capability / architecture_seed_only / evidence / metadata / open_issue`
4. 非 formal item 不再误入正式 requirement pool
5. requirement 可输出 architecture seed / test seed
6. capability promotion 有显式判定与收口逻辑
7. 弱 requirement 会被压回 `draft`
8. enrichment 可补齐：
   - `DET`
   - `PWM dependency`
   - `SPI dependency`
   - `极性反转配置`
   - `故障清除与看门狗控制`

---

## 6. 当前回归命令

以下命令可作为当前阶段回归入口。

### 6.0 Regression Pack

推荐优先使用统一回归入口：

```bash
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py
```

仅回放单个 case：

```bash
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --case gp_nca95yy
```

### 6.1 Gp_NCA95yy

```bash
PYTHONPATH=.claude/skills/fc-requirement-workbench/src python3.11 -m fc_requirement_workbench.cli Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN.md --module Gp_NCA95yy --raw-input artifacts/raw_input_Gp_NCA95yy.txt --source-root /Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G --emit requirement-bundle --output artifacts/gp_nca95yy_requirement_bundle.yaml --no-cache
```

```bash
PYTHONPATH=.claude/skills/fc-requirement-workbench/src python3.11 -m fc_requirement_workbench.cli Novosense-NCA9539-Q1TSXR_DatasheetRev1.0_EN.md --module Gp_NCA95yy --raw-input artifacts/raw_input_Gp_NCA95yy.txt --source-root /Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G --emit bundle-validation --output artifacts/gp_nca95yy_bundle_validation.json --no-cache
```

### 6.2 Gp_TLE92104

```bash
PYTHONPATH=.claude/skills/fc-requirement-workbench/src python3.11 -m fc_requirement_workbench.cli artifacts/Gp_TLE92104_grounding_input.md --module Gp_TLE92104 --raw-input artifacts/raw_input_Gp_TLE92104.txt --source-root /Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G --emit requirement-bundle --output artifacts/gp_tle92104_requirement_bundle.yaml --no-cache
```

```bash
PYTHONPATH=.claude/skills/fc-requirement-workbench/src python3.11 -m fc_requirement_workbench.cli artifacts/Gp_TLE92104_grounding_input.md --module Gp_TLE92104 --raw-input artifacts/raw_input_Gp_TLE92104.txt --source-root /Users/chenkunjie/Downloads/SBPAI/Proj/FcStack-main-2/src/FcStackBase/AURIX2G --emit bundle-validation --output artifacts/gp_tle92104_bundle_validation.json --no-cache
```

当前阶段回归通过标准：

- bundle / architecture seed / test seed / validation 能成功生成并与 golden 对齐
- 生成态 `srs-markdown` 必须与对应 requirement bundle 一致
- 每个 case 的 validation summary 必须满足该 case 自身 expectation

---

## 7. 当前阶段不再继续扩展的点

本阶段建议停止继续扩展以下方向：

- 不在需求 skill 内直接生成正式架构文档
- 不在需求 skill 内承接架构文件列表/运行态/MemMap 最终冻结
- 不再继续为了“清 warning”而无边界增加新 rule

这一阶段已经收口，后续若继续推进，应进入：

1. regression baseline 固化与自动回放
2. requirement bundle contract 文档化
3. 架构 skill 独立定义如何消费 requirement bundle / architecture seed

---

## 8. 建议的下一阶段入口

建议下一阶段按以下顺序推进：

1. 固化 regression baseline
2. 整理 requirement bundle contract
3. 单独评估 `fc-architecture-workbench` 的输入契约

其中第 3 步必须坚持边界：

- 需求和架构独立
- 只定义交接格式
- 不合并 skill 职责
