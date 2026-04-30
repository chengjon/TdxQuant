## Why

`catalog bundle` 已经可以把多条稳定命令固化为一个顺序流程，但当前仍然只能“从第一步跑到最后一步”。

这对日常使用有两个明显摩擦点：

- 某个 bundle 的前置刷新步骤已经完成，但想只重跑后面的报告步骤
- 某次排障只想验证其中一个 step，而不想再次触发整个交易或整套流程

需要在不修改底层 workflow 的前提下，给 bundle 增加稳定的步骤选择执行能力。

## What Changes

- 为 command bundle step 增加稳定的名称解析能力。
- 扩展 `catalog run --bundle ...`，支持按 step 名称或序号选择局部执行范围。
- 扩展 bundle 列表与结果元数据，使调用者能明确知道本次执行了哪些 step。
- 补充回归测试与使用文档。

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: 为多步骤 bundle 增加局部执行和补跑控制

### New Capabilities

None.

## Impact

- 影响 `tdxquant/catalog.py`、`tdxquant/cli.py`、runtime bundle 配置、测试与使用文档。
- 不修改 `TdxApiManager`、`TdxTaskManager`、`TdxTradeManager` 的业务行为。
- 不引入 bundle 分支、循环、并行或跨 step 数据传递。
