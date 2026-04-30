## Context

当前查询主线已经有独立 `transaction` 子域，并已纳入两批交易数据能力：

- `get_gpjy_value`
- `get_gpjy_value_by_date`
- `get_bkjy_value`
- `get_bkjy_value_by_date`

接下来的交易数据面只剩：

- 市场交易数据 `scjy`

与前两批不同，`scjy` 的参数模型不再包含 `stock_list`，而是只接受 `field_list + start/end` 与 `field_list + year/mmdd`。因此本次不是简单的“同形接口平移”，而是 `transaction` 子域第一次承接无证券列表的交易数据查询。

## Goals / Non-Goals

**Goals:**

- 继续沿 `transaction` 子域扩展市场交易数据能力。
- 补齐 bridge、domain、manager、nested CLI、flat CLI 的标准入口。
- 保持 `field_list` 显式输入，不从 API profile 推断默认字段。
- 保留 `get_scjy_value_by_date(year=0, mmdd=0)` 返回最近一条数据的官方语义。

**Non-Goals:**

- 不回退到 `market` 域承载交易数据。
- 不新增 task/report/catalog 高层编排。
- 不为 `SCxx` 字段建立额外字段别名或预置字段组。
- 不在本次引入市场交易数据缓存、订阅或额外聚合逻辑。

## Decisions

### 1. 继续扩展现有 `transaction` 子域，而不是把 `scjy` 放回 `market`

决策：

- 在现有 `TransactionApi` 和 `manager.transaction` 上继续增加：
  - `market_transaction_data(...)`
  - `market_transaction_data_by_date(...)`

原因：

- `scjy` 与 `gpjy/bkjy` 同属交易数据资源族，差异主要在参数模型，不在业务归属。
- 如果把 `scjy` 放回 `market`，会让交易数据面重新跨域，削弱刚建立起来的 `transaction` 边界。

备选方案：

- 放入 `market`
  - 放弃，原因是会重新制造“行情/交易数据”混装。
- 新建 `market_transaction` 独立域
  - 放弃，原因是边界过细，不足以支撑单独域存在。

### 2. CLI 使用语义化命名 `market-transaction-data`

决策：

- nested `api`
  - `api market-transaction-data`
  - `api market-transaction-data-by-date`
- flat bridge
  - `tdx-data-market-transaction`
  - `tdx-data-market-transaction-by-date`

原因：

- 当前 CLI 已经优先采用语义化名称，而不是直接暴露 `scjy` 缩写。
- 与已经存在的 `stock-transaction-data`、`sector-transaction-data` 保持并列关系。

### 3. `year/mmdd` 继续保留官方零值语义

决策：

- `by_date` manager 和 CLI 入口允许 `year=0, mmdd=0`，并原样透传到底层 bridge。

原因：

- 这已经是文档明示的契约，应通过测试锁定，而不是在 manager 层重新解释。

### 4. 显式体现 `scjy` 无 `stock_list` 的特殊模型

决策：

- `transaction` 域、manager 和 CLI 都不接收 `stock_list` / `--code`。
- 时间区间接口只接收 `field_list`、`start_time`、`end_time`。
- 指定日期接口只接收 `field_list`、`year`、`mmdd`。

原因：

- 这正是 `scjy` 与 `gpjy/bkjy` 的核心差异，应在外层 API 形态上直观体现。

## Risks / Trade-offs

- [`transaction` 子域继续扩张] → 这是预期方向，但本次仍只收一对 `scjy` 接口，范围受控。
- [`scjy` 与前两批接口形状不同] → 通过单独 change 和单独测试锁定，避免把特殊模型混入旧补丁。
- [CLI 不再带 `--code`] → 这是官方签名的直接映射，应在 parser 与 dispatch 测试中明确固定下来。
