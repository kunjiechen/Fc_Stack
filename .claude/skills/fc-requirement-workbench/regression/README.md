# FC Requirement Workbench Regression Pack

本目录用于固化 `fc-requirement-workbench` 的需求层回归基线。

当前目标：

- 固化 golden baseline
- 提供一键回放入口
- 让 bundle / architecture seed / test seed / validation 都进入回归检查

## 目录结构

```text
regression/
├── README.md
└── cases/
    ├── gp_nca95yy.json
    └── gp_tle92104.json
```

## 执行方式

在仓库根目录执行：

```bash
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py
```

仅执行指定 case：

```bash
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --case gp_nca95yy
```

刷新 golden baseline：

```bash
python3.11 .claude/skills/fc-requirement-workbench/scripts/run_regression_pack.py --refresh-golden
```

## 当前通过标准

- `requirement bundle` 与 golden 一致
- `architecture seed` 与 golden 一致
- `test seed` 与 golden 一致
- `bundle validation` 与 golden 一致
- `validation.summary.error == 0`
- `validation.summary.warning == 0`

## 边界说明

本回归包仅验证需求 skill 自身产物，不验证正式架构文档生成，也不替代 `fc-architecture-workbench` 的独立回归。
