## Why

查询主线已经补齐了 `runtime`、`block` 和轻量参考数据，但真正的专业财务数据主体仍未进入标准 manager 和 CLI 路径。与其一次性引入财务与交易数据全家桶，更合适的下一步是先独立收口最核心的两项专业财务数据接口。

## What Changes

- 新增独立 `financial` 子域，先收口：
  - `get_financial_data`
  - `get_financial_data_by_date`
- 为 `TdxApiManager` 新增 `manager.financial.<method>()` 入口，并附加标准管理元数据。
- 为 nested `api` 命令新增：
  - `api financial-data`
  - `api financial-data-by-date`
- 为 flat bridge CLI 新增：
  - `tdx-data-financial`
  - `tdx-data-financial-by-date`
- 保持 `field_list` 为显式调用参数，不通过 profile 默认值隐式补齐字段集合。
- 补充 parser、dispatch、domain delegation、manager metadata 测试，并更新覆盖矩阵与主 spec。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-api-management`: 扩展查询 manager 域边界，使专业财务数据通过独立 `financial` 子域暴露。
- `tdx-api-cli-entry`: 扩展 nested `api` 与 flat bridge CLI，使其支持专业财务数据标准入口。

## Impact

- 影响 `tdxquant/api/bridge.py`、`tdxquant/api/manager.py` 和 `tdxquant/cli.py`。
- 新增 `tdxquant/api/financial.py`。
- 影响 `tests/test_api_manager.py` 与 `tests/test_api_cli.py`。
- 影响 `docs/TdxQuant_Interface_Coverage_Matrix.md`，必要时补记 `docs/TdxQuant_API_System_Plan.md`。
- 不影响 `runtime`、`block`、桌面交易 capability、`task/report/catalog` 的既有行为。
