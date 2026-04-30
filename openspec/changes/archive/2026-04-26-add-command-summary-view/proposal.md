## Why

当前 `catalog run` 和 `catalog plan` 已经能统一执行和预览，但输出仍然偏长。对日常终端使用来说，很多时候只需要一个更短的结果视图：

- 这次执行的是哪条 entry / 哪个 bundle
- 是否成功
- 实际执行了哪些 step
- 关键交易字段或报告字段是什么

如果每次都翻完整 JSON，日常使用成本仍然偏高。

## What Changes

- 为 `catalog run` / `catalog plan` 增加可选 `summary` 输出视图。
- 默认仍保留完整 JSON，不影响现有行为。
- `summary` 视图只裁剪输出，不改变内部执行和结果判定逻辑。
- 补充测试与使用文档。

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: 增加面向日常终端查看的 summary view

### New Capabilities

None.

## Impact

- 影响 `tdxquant/cli.py`、catalog 相关测试与使用文档。
- 不修改 `TdxApiManager`、`TdxTaskManager`、`TdxTradeManager` 的业务行为。
- 不改变默认完整 JSON 输出。
