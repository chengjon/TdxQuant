## Why

随着 `catalog entry`、`catalog bundle` 持续增加，统一入口开始出现新的问题：虽然命令更短了，但“如何快速找到该用哪条”变得越来越依赖记忆。

尤其在日常场景里，用户更常按“用途”找入口：

- 开盘前要做什么
- 盘中交易后要看什么
- 排障时该看哪组报告

需要给 catalog 增加可维护的标签和按标签筛选的能力，同时补一组更贴近日常使用的默认 bundle。

## What Changes

- 为 command catalog entry / bundle 增加可选 `labels` 元数据。
- 扩展 `catalog list`，支持按标签筛选 entry、bundle 或两者。
- 在默认 runtime registry 中补一组更贴近日常使用的 bundle 与缺失的高频 report entry。
- 更新文档与测试。

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: 增加标签元数据与标签筛选能力

### New Capabilities

None.

## Impact

- 影响 `tdxquant/catalog.py`、`tdxquant/cli.py`、runtime catalog/bundle 配置、测试与文档。
- 不修改 `TdxApiManager`、`TdxTaskManager`、`TdxTradeManager` 的业务行为。
- 不改变既有 entry / bundle 的执行路径。
