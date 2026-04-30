## Why

`transaction` 子域已经完成了股票交易数据首包，下一步最自然的低风险增量就是板块交易数据。`get_bkjy_value` 与 `get_bkjy_value_by_date` 的参数模型和刚完成的 `gpjy` 基本同形，适合作为第二个独立小包推进，而不必把市场交易数据 `scjy` 一并拉入。

## What Changes

- 在独立 `transaction` 子域中新增板块交易数据能力，先收口：
  - `get_bkjy_value`
  - `get_bkjy_value_by_date`
- 为 `TdxApiManager` 新增：
  - `manager.transaction.sector_transaction_data(...)`
  - `manager.transaction.sector_transaction_data_by_date(...)`
- 为 nested `api` 命令新增：
  - `api sector-transaction-data`
  - `api sector-transaction-data-by-date`
- 为 flat bridge CLI 新增：
  - `tdx-data-sector-transaction`
  - `tdx-data-sector-transaction-by-date`
- 保持 `field_list` 为显式调用参数，不通过 profile 默认值隐式补齐字段集合。
- 保留 `year=0, mmdd=0` 代表“最近一条数据”的官方语义。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展 `transaction` 子域，使其支持板块交易数据查询。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge CLI，使其支持板块交易数据标准入口。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/transaction.py`、`tdxquant/api/manager.py` 和 `tdxquant/cli.py`。
- 影响 `tests/test_api_manager.py` 与 `tests/test_api_cli.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与相关主 spec。
- 不影响 `financial`、`runtime`、`block`、桌面交易 capability、`task/report/catalog` 的既有行为。
