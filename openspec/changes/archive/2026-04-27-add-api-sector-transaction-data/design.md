## Context

当前查询主线已经有独立 `transaction` 子域，并已纳入第一批股票交易数据能力：

- `get_gpjy_value`
- `get_gpjy_value_by_date`

接下来的交易数据面还剩两簇：

- 板块交易数据 `bkjy`
- 市场交易数据 `scjy`

其中 `bkjy` 与 `gpjy` 的参数模型基本一致，都是 `stock_list + field_list + start/end` 与 `stock_list + field_list + year/mmdd` 双入口；而 `scjy` 没有 `stock_list`，接口形态不同。如果本次把二者一起推进，会把“同形扩展”和“特殊模型”绑进同一个补丁。

## Goals / Non-Goals

**Goals:**

- 继续沿 `transaction` 子域扩展板块交易数据能力。
- 补齐 bridge、domain、manager、nested CLI、flat CLI 的标准入口。
- 保持 `field_list` 显式输入，不从 API profile 推断默认字段。
- 保留 `get_bkjy_value_by_date(year=0, mmdd=0)` 返回最近一条数据的官方语义。

**Non-Goals:**

- 不在本次覆盖 `get_scjy_value*`。
- 不回退到 `market` 域承载交易数据。
- 不新增 task/report/catalog 高层编排。
- 不为 `BKxx` 字段建立额外字段别名或预置字段组。

## Decisions

### 1. 继续扩展现有 `transaction` 子域，而不是新增 `sector-transaction` 独立域

决策：

- 在现有 `TransactionApi` 和 `manager.transaction` 上继续增加：
  - `sector_transaction_data(...)`
  - `sector_transaction_data_by_date(...)`

原因：

- `bkjy` 与 `gpjy` 同属交易数据资源族，且参数结构相近。
- 复用现有 `transaction` 分层比再拆一个独立域更一致、更低成本。

备选方案：

- 新建单独 `sector_transaction` 域
  - 放弃，原因是边界过细，后续 `scjy` 还会再次引入新的拆分判断。

### 2. CLI 使用语义化命名 `sector-transaction-data`

决策：

- nested `api`
  - `api sector-transaction-data`
  - `api sector-transaction-data-by-date`
- flat bridge
  - `tdx-data-sector-transaction`
  - `tdx-data-sector-transaction-by-date`

原因：

- 当前 CLI 已经优先采用语义化名称，而不是直接暴露 `bkjy` 缩写。
- 与已经存在的 `stock-transaction-data` 命名保持并列关系。

### 3. `year/mmdd` 继续保留官方零值语义

决策：

- `by_date` manager 和 CLI 入口允许 `year=0, mmdd=0`，并原样透传到底层 bridge。

原因：

- 这已经是文档明示的契约，应通过测试锁定，而不是在 manager 层重新解释。

## Risks / Trade-offs

- [`transaction` 子域会继续扩张] → 本次仍只收一对 `bkjy` 接口，保持小包推进。
- [`scjy` 仍未纳入] → 这是刻意范围控制，下一包再处理无 `stock_list` 的市场交易数据特殊模型。
- [CLI 名称不直接对应官方缩写] → 继续沿用项目现有语义化命名，并保留 flat bridge 一致性。
