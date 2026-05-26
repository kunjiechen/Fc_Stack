# FC Requirement Workbench Regression Pack

本目录用于固化 `fc-requirement-workbench` 的需求层回归基线。

当前目标：

- 固化 golden baseline
- 提供一键回放入口
- 让 bundle / architecture seed / test seed / validation 都进入回归检查
- 支持 pre-push hook 和 CI 两种集成方式

## 目录结构

```text
regression/
├── README.md
└── cases/
    ├── gp_iomcudio.json
    ├── gp_nca95yy.json
    └── gp_tle92104.json
```

## 执行方式

在仓库根目录执行：

```bash
# 完整回归（含 byte-exact golden 对比）
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py

# 仅执行指定 case
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --case gp_nca95yy

# CI 模式：只检查 expectations 和 validation summary，不做 byte-exact 对比
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --ci

# 刷新 golden baseline（修改了流水线逻辑后）
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --refresh-golden
```

## Source Root 配置

回归 case 默认使用 `source_root_abs` 字段中的绝对路径。可通过以下方式覆盖：

```bash
FC_SOURCE_ROOT=/path/to/project/src python3.11 scripts/run_regression_pack.py
```

## 当前通过标准

- `requirement bundle` 与 golden 一致（CI 模式下跳过 byte-exact 对比）
- `architecture seed` 与 golden 一致（CI 模式下跳过 byte-exact 对比）
- `test seed` 与 golden 一致（CI 模式下跳过 byte-exact 对比）
- `bundle validation` 与 golden 一致（CI 模式下跳过 byte-exact 对比）
- 生成态 `srs-markdown` 与 `requirement bundle` 保持一致
- `validation.summary.error` 必须与 case expectation 一致
- `validation.summary.warning` 必须与 case expectation 一致
- 所有 `expectations.architecture_interfaces` 出现在生成的 architecture seed 中
- 所有 `expectations.requirement_titles` 出现在生成的 requirement bundle 中

## Git Hook 集成

### 安装 pre-push hook

```bash
bash .claude/skills/fc-requirement-workbench/scripts/install-hooks.sh
```

这会在 `.git/hooks/pre-push` 创建 symlink。每次 `git push` 前自动运行 `--ci` 模式回归检查。

### 卸载 hook

```bash
rm .git/hooks/pre-push
```

### Hook 行为

- 仅当 `.claude/skills/fc-requirement-workbench/` 下有文件变更时才运行回归
- 使用 `--ci` 模式（只检查 expectations，不做 byte-exact 对比）
- 回归失败时阻止 push

## CI 集成

在 CI pipeline 中添加：

```yaml
# 示例 GitHub Actions step
- name: Requirement Regression
  run: |
    python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --ci
  env:
    FC_SOURCE_ROOT: ${{ github.workspace }}/src/FcStackBase/AURIX2G
```

## 添加新 Regression Case

1. 在 `regression/cases/` 下创建 `{case_id}.json`
2. 定义 `input_document`, `raw_input`, `source_root_abs`, `golden`, `expectations`
3. 所有路径相对于仓库根目录
4. 首次运行需用 `--refresh-golden` 生成 golden artifacts

## 边界说明

本回归包仅验证需求 skill 自身产物，不验证正式架构文档生成，也不替代 `fc-architecture-workbench` 的独立回归。
