# FC Implementation Workbench Regression Pack

本目录用于固化 `fc-implementation-workbench` 当前已经稳定的详细设计生成链路。

当前回归目标：

- 校验 generation bundle 结构和跨层一致性
- 从真实 bundle 渲染 detailed design markdown
- 校验 architecture 与 rendered detailed design 的接口一致性
- 固化 rendered detailed design golden baseline

## 目录结构

```text
regression/
├── README.md
└── cases/
    └── gp_nca95yy.json
```

## 依赖

建议使用装有以下依赖的当前解释器执行：

```bash
python3 -m pip install -r .claude/skills/fc-implementation-workbench/requirements-dev.txt
```

当前脚本会优先复用调用它的 Python 解释器，并在依赖缺失时输出明确安装命令。

## 执行方式

在仓库根目录执行：

```bash
# 完整回归
python3 .claude/skills/fc-implementation-workbench/scripts/run_regression_pack.py

# 仅执行指定 case
python3 .claude/skills/fc-implementation-workbench/scripts/run_regression_pack.py --case gp_nca95yy

# 刷新 rendered DD golden
python3 .claude/skills/fc-implementation-workbench/scripts/run_regression_pack.py --refresh-golden
```

## 当前通过标准

- `validate_generation_bundle.py` 对 case bundle 校验通过
- `render_detailed_design.py` 能从 case bundle 成功生成 markdown
- `validate_fc_docs.py` 对 `architecture -> rendered DD` 一致性校验通过
- rendered markdown 与 golden 保持 byte-exact 一致

## 当前边界

- 本回归当前固化的是 `bundle -> rendered DD -> arch/DD validator` 这条稳定链路
- `SRS -> architecture -> detailed design` 的全链一致性还没有正式进入本回归包
- `references/examples/` 下的示例 bundle 主要用于说明结构，不替代 regression baseline
