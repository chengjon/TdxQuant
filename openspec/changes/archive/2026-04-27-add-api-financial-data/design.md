## Context

当前查询主线已经形成 `market / meta / formula / runtime / block` 的稳定分层，但专业财务数据仍停留在接口说明文档层面，尚未进入 `TdxApiManager` 和标准 CLI。与前面已完成的 `divid_factors`、`ipo_info` 不同，`get_financial_data*` 属于真正的数据面主体，返回体更大、字段选择更敏感，也更容易把现有域边界做乱。

同时，接口说明文档已经给出了比较明确的参数模型：

- `get_financial_data(stock_list, field_list, start_time, end_time, report_type='report_time')`
- `get_financial_data_by_date(stock_list, field_list, year, mmdd)`

其中 `field_list` 在文档语义上是显式筛选条件，不适合作为 profile 默认值自动补齐。

## Goals / Non-Goals

**Goals:**

- 为专业财务数据建立独立 `financial` 子域，而不是继续扩张 `market` 或 `meta`。
- 补齐 bridge、domain、manager、nested CLI、flat CLI 的完整标准入口。
- 保持 `field_list` 显式输入，避免默认字段集造成结果体不可控或语义漂移。
- 保持与现有查询主线一致的元数据、耗时和错误处理风格。

**Non-Goals:**

- 不在本次引入 `get_gpjy_value*`、`get_bkjy_value*`、`get_scjy_value*`。
- 不新增 task/report/catalog 高层编排。
- 不设计专业财务字段字典，也不为 `field_list` 提供预置别名集。
- 不改变既有 `market`、`meta`、`runtime`、`block` 的公开行为。

## Decisions

### 1. 新增 `tdxquant/api/financial.py`，并由 `TdxApiManager.financial` 聚合

决策：

- 新建 `FinancialApi` 域模块。
- 在 `TdxApiManager` 中新增 `_financial_api` 和 `financial` proxy。

原因：

- `get_financial_data*` 是专业财务数据面，不属于行情读取，也不是轻量参考信息。
- 后续 `financial` 域仍可继续承接财务数据族能力，不需要再修改 `market` 或 `meta` 的定位。

备选方案：

- 放入 `market`
  - 放弃，原因是会继续模糊行情域与财务域边界。
- 放入 `meta`
  - 放弃，原因是这组接口已超出“静态资料/参考数据”的范畴。

### 2. `field_list` 维持显式参数，不接入 profile 默认字段解析

决策：

- `manager.financial.financial_data(...)` 和 `manager.financial.financial_data_by_date(...)` 都要求调用方显式传入 `fields`。
- CLI 侧使用重复 `--field` 收集字段列表，并直接透传。

原因：

- 文档本身强调字段筛选，且 `get_financial_data_by_date` 明确写出“不能为空”。
- 专业财务字段数量大，使用 profile 默认字段会让结果不可预测，也会让日常脚本难以审计。

备选方案：

- 允许 profile 提供 `default_fields.financial_data`
  - 放弃，原因是与“显式字段选择”目标冲突。

### 3. nested `api` 与 flat bridge 同时补齐，命名保持现有查询 CLI 风格

决策：

- nested `api`
  - `api financial-data`
  - `api financial-data-by-date`
- flat bridge
  - `tdx-data-financial`
  - `tdx-data-financial-by-date`

原因：

- 项目当前明确要求 flat bridge 兼容保留，同时优先引导日常使用走 manager 路径。
- 命名与现有 `tdx-data-kline`、`api trading-dates`、`api ipo-info` 风格一致。

### 4. `report_type` 只做显式透传，不在本次引入枚举封装

决策：

- `report_type` 保持字符串透传。
- 测试覆盖至少验证常见值如 `report_time`、`announce_time`、`tag_time` 能原样传递。

原因：

- 当前目标是先建立稳定入口，不是扩展官方参数模型。
- 过早做枚举包装会增加 CLI 和 manager 的约束面，收益不高。

## Risks / Trade-offs

- [`financial` 域首次引入后，后续是否继续膨胀] → 本次只收两个接口，后续财务族能力仍按小包推进，不一次性吞入交易数据面。
- [`field_list` 必填会让调用稍显繁琐] → 这是有意限制，换取结果确定性和可审计性。
- [`report_type` 不做枚举校验可能让非法值晚失败] → 保持桥接透传优先，错误交由底层运行时返回，后续如出现频繁误用再补输入校验。
- [`flat CLI` 命名与官方方法名不完全一致] → 延续现有 `tdx-data-*` 兼容风格，避免命令体系碎片化。
