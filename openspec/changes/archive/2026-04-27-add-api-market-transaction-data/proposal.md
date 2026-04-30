## Why

`transaction` 子域已经完成了股票交易数据与板块交易数据两批入口，剩余交易数据面主体只剩市场交易数据 `get_scjy_value` 与 `get_scjy_value_by_date`。这组接口和前两批不同，不带 `stock_list`，如果继续拖延，`transaction` 域就会一直停留在“同形接口扩展”，没有覆盖到它真正需要承接的特殊模型。

## What Changes

- 在独立 `transaction` 子域中新增市场交易数据能力，收口：
  - `get_scjy_value`
  - `get_scjy_value_by_date`
- 为 `TdxApiManager` 新增：
  - `manager.transaction.market_transaction_data(...)`
  - `manager.transaction.market_transaction_data_by_date(...)`
- 为 nested `api` 命令新增：
  - `api market-transaction-data`
  - `api market-transaction-data-by-date`
- 为 flat bridge CLI 新增：
  - `tdx-data-market-transaction`
  - `tdx-data-market-transaction-by-date`
- 保持 `field_list` 为显式调用参数，不通过 profile 默认值隐式补齐字段集合。
- 保留 `year=0, mmdd=0` 代表“最近一条数据”的官方语义。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展 `transaction` 子域，使其支持市场交易数据查询。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge CLI，使其支持市场交易数据标准入口。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/transaction.py`、`tdxquant/api/manager.py` 和 `tdxquant/cli.py`。
- 影响 `tests/test_api_manager.py` 与 `tests/test_api_cli.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与 `docs/TdxQuant_API_System_Plan.md`。
- 不影响 `financial`、`runtime`、`block`、桌面交易 capability、`task/report/catalog` 的既有行为。
