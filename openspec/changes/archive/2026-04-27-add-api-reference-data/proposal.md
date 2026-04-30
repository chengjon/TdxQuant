## Why

查询主线已经完成了 `market`、`runtime`、`block` 三条近期优先包，但财务/交易数据面仍然整体未覆盖。直接一次性引入 `financial_data`、`gpjy_value`、`bkjy_value`、`scjy_value` 会把范围拉得过大，也会提前引入新的域划分决策。

更合适的下一步，是先补一组更轻量的参考数据能力：

- `get_divid_factors`
- `get_ipo_info`

这两项都属于“常用但范围相对小”的查询能力，适合作为进入财务/交易数据面之前的过渡包。

## What Changes

- 为 `meta` 子域新增：
  - `divid_factors(...)`
  - `ipo_info(...)`
- 为 nested `api` 命令新增：
  - `divid-factors`
  - `ipo-info`
- 为 flat bridge CLI 新增：
  - `tdx-data-divid-factors`
  - `tdx-data-ipo-info`
- 补充 parser、dispatch、domain delegation、manager metadata 测试，并更新覆盖矩阵。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展 `meta` 子域，使其支持分红配送因子和新股申购参考数据查询。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge CLI，使其支持 `divid_factors` 与 `ipo_info` 标准入口。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/meta.py`、`tdxquant/api/manager.py` 和 `tdxquant/cli.py`。
- 影响 `tests/test_api_manager.py` 与 `tests/test_api_cli.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md` 与主 spec。
- 不影响 `runtime`、`block`、桌面交易 capability、task/report/catalog` 的现有行为。
