## Context

当前项目在接口说明文档中的下一大块缺口是“财务 / 交易数据面”。但这组能力跨度太大：

- 分红配送 / 除权因子
- IPO / 新发债参考信息
- 专业财务数据
- 股票 / 板块 / 市场交易数据

如果一次性推进，既会让单次变更过大，也会把“是否新增 `financial` / `transaction` 子域”的决策提前绑定在一个高复杂度补丁里。

相比之下，`get_divid_factors` 和 `get_ipo_info` 更接近参考数据查询：

- 它们不涉及实时订阅、状态文件或交易执行。
- 参数模型简单，适合先验证扩展 `meta` 域是否仍然合理。
- 可以作为后续进入 `financial_data` 与 `transaction value` 大包前的低风险样板。

## Goals / Non-Goals

**Goals:**

- 为 `meta` 域补齐 `divid_factors(...)` 与 `ipo_info(...)`。
- 为 nested `api` 和 flat bridge CLI 补齐对应标准入口。
- 保持现有 `meta` 域风格：显式参数、domain 无 profile 逻辑、manager 附加元数据。

**Non-Goals:**

- 不在本次引入 `financial` 或 `transaction` 新域。
- 不在本次覆盖 `get_financial_data*`、`get_gpjy_value*`、`get_bkjy_value*`、`get_scjy_value*`。
- 不做下载、缓存刷新、任务编排或报表聚合。

## Decisions

### 1. `get_divid_factors` 与 `get_ipo_info` 先归入 `meta` 域

决策：

- `manager.meta.divid_factors(...)`
- `manager.meta.ipo_info(...)`

原因：

- `ipo_info` 明显是参考信息，放在 `meta` 最自然。
- `divid_factors` 虽然与行情复权有关，但它本身仍更接近参考因子数据，而不是实时行情或 K 线读取。
- 这能避免为两项轻量能力过早新增新域。

备选方案：

- 方案 A：把 `divid_factors` 放进 `market`
  - 放弃，原因是当前 `market` 已聚焦行情与快照读取。
- 方案 B：为这两项单独建 `reference` 域
  - 放弃，原因是当前收益不足以支撑再引入一个新域。

### 2. nested `api` 与 flat bridge 命名保持现有 meta 风格

决策：

- nested `api`：
  - `api divid-factors`
  - `api ipo-info`
- flat bridge：
  - `tdx-data-divid-factors`
  - `tdx-data-ipo-info`

原因：

- 现有 `stock-info`、`cb-info`、`gb-info` 都使用 `api` 的轻量业务名。
- flat bridge 的 meta / market 查询已有 `tdx-data-*` 约定，继续沿用最一致。

## Risks / Trade-offs

- [`divid_factors` 是否应属于 `market`] → 本次先按参考数据放进 `meta`，后续如果真正出现更大的 corporate action 数据簇，再重评域边界。
- [命名采用 `divid-factors` 而非更自然的 `dividend-factors`] → 为保持与官方函数名和现有 CLI 命名风格的一致性，本次优先保留原函数词根。
- [仍未触达真正大的财务/交易数据簇] → 这是有意分包，先把风险小的参考数据补齐，再进入更大的数据面设计。
