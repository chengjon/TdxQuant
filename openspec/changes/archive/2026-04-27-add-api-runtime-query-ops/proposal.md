## Why

官方接口文档中的 `refresh_kline`、`get_trading_dates`、`download_file` 仍未进入当前 query manager 标准入口，而它们又都不适合塞回 `market` 或 `meta` 这种单域读能力里。

当前项目已经有 `refresh_cache` 这类 manager 级治理动作，但它和官方文档里的 `refresh_kline(stock_list, period)` 不是同一能力。如果继续混用命名，会让接口覆盖矩阵和日常调用入口都越来越模糊。

## What Changes

- 为 query API 新增独立 `runtime` 子域，显式承载 `refresh_kline`、`get_trading_dates`、`download_file` 三类公共运行时能力。
- 为嵌套 `api` 命令新增 `trading-dates`、`refresh-kline`、`download-file` 标准入口。
- 为 bridge CLI 新增对应 flat 命令，保持当前“flat bridge + manager api”双入口模式一致。
- 保留现有 `refresh_cache` 作为 manager 顶层治理动作，不把它改名为 `refresh_kline`。
- 补充 parser、dispatch、manager metadata 与 domain delegation 测试，并更新覆盖矩阵。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-cli-entry`: 扩展嵌套 `api` 命令组与 flat bridge 查询命令，补齐 runtime 公共查询能力入口。
- `tdx-api-management`: 为 `TdxApiManager` 新增 `runtime` 子域，并显式暴露交易日、K 线缓存刷新、文件下载能力。

## Impact

- 影响 `tdxquant/cli.py` 的 parser、`api` 分发逻辑与 flat command 分发逻辑。
- 影响 `tdxquant/api/bridge.py`、新增 `tdxquant/api/runtime.py`，并修改 `tdxquant/api/manager.py` 与公开导出路径。
- 影响 `runtime/api-profiles.json` 的 runtime 公共查询默认项。
- 影响 `tests/test_api_cli.py`、`tests/test_api_manager.py` 与能力覆盖文档。
- 不影响桌面交易 capability、`TdxTradeManager`、`task/report/catalog` 的既有行为。
