## Why

专业财务数据已经进入标准 manager/CLI 路径，查询主线下一步最自然的缺口就是股票交易数据面。与其一次性把股票、板块、市场三类交易数据全部并入，更稳妥的做法是先独立收口 `get_gpjy_value` 与 `get_gpjy_value_by_date`，验证 `transaction` 子域边界。

## What Changes

- 新增独立 `transaction` 子域的首批能力，先收口：
  - `get_gpjy_value`
  - `get_gpjy_value_by_date`
- 为 `TdxApiManager` 新增 `manager.transaction.<method>()` 入口，并附加标准管理元数据。
- 为 nested `api` 命令新增：
  - `api stock-transaction-data`
  - `api stock-transaction-data-by-date`
- 为 flat bridge CLI 新增：
  - `tdx-data-stock-transaction`
  - `tdx-data-stock-transaction-by-date`
- 保持 `field_list` 为显式调用参数，不通过 profile 默认值隐式补齐字段集合。
- 保留 `year=0, mmdd=0` 代表“最近一条数据”的官方语义。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展查询 manager 域边界，使股票交易数据通过独立 `transaction` 子域暴露。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge CLI，使其支持股票交易数据标准入口。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/manager.py` 和 `tdxquant/cli.py`。
- 新增 `tdxquant/api/transaction.py`。
- 影响 `tests/test_api_manager.py` 与 `tests/test_api_cli.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与相关主 spec。
- 不影响 `financial`、`runtime`、`block`、桌面交易 capability、`task/report/catalog` 的既有行为。
