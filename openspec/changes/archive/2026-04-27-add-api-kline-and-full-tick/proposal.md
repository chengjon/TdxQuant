## Why

当前 query manager 已经在 Python 层支持 `market.kline(...)`，底层 bridge 也已经存在 `get_full_tick` 调用锚点，但标准 `api` 二级 CLI 还没有形成对应入口。这会造成“Python 可用、标准 CLI 不对齐”的断层，也让接口说明文档中的 K 线与分笔查询能力无法被当前 manager 体系完整表达。

## What Changes

- 为 `api` 二级命令新增显式 K 线查询入口，和现有 `TdxApiManager.market.kline(...)` 对齐。
- 为 `market` 域新增显式 full-tick / 分笔查询入口，并通过 `TdxApiManager` 与 `api` 二级命令暴露。
- 保持现有扁平命令兼容，不移除 `tdx-data-kline`、`tdx-data-snapshot` 等既有入口。
- 补充 parser、manager 分发与 CLI 输出路径测试，确保 query manager 的标准入口覆盖继续可验证。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-cli-entry`: 扩展嵌套 `api` 命令组，使其支持 K 线与 full-tick 查询入口。
- `tdx-api-management`: 扩展 query manager 的 `market` 域，使其暴露显式 K 线与 full-tick 查询能力。

## Impact

- 影响 `tdxquant/cli.py` 的 `api` parser 与分发逻辑。
- 影响 `tdxquant/api/market.py`、`tdxquant/api/manager.py` 和可能的 `tdxquant/api/bridge.py` 包装路径。
- 影响 `tests/test_api_cli.py`、`tests/test_api_manager.py` 等 query API 回归测试。
- 不影响桌面交易 capability、`TdxTradeManager`、`task/report/catalog` 的既有行为。
