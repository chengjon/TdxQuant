## Context

当前查询主线已经有 `market / meta / financial / formula / runtime / block` 等稳定分层，但交易数据面仍全部未进入标准 manager 路径。文档中的交易数据又天然分成三簇：

- 股票交易数据 `gpjy`
- 板块交易数据 `bkjy`
- 市场交易数据 `scjy`

如果一次性把三簇都做进来，既会让变更范围失控，也会把命名和域边界决策一次性压到一个补丁里。相比之下，`gpjy` 这对接口参数最接近已经完成的 `financial` 路径，适合作为 `transaction` 子域的第一批能力。

## Goals / Non-Goals

**Goals:**

- 建立独立 `transaction` 子域，并以股票交易数据作为首批能力落点。
- 补齐 bridge、domain、manager、nested CLI、flat CLI 的标准入口。
- 保持 `field_list` 显式输入，不从 API profile 推断默认字段。
- 保留 `get_gpjy_value_by_date(year=0, mmdd=0)` 返回最近一条数据的官方语义。

**Non-Goals:**

- 不在本次覆盖 `get_bkjy_value*`、`get_scjy_value*`。
- 不把交易数据能力塞回 `market`。
- 不新增 task/report/catalog 高层编排。
- 不为 `GPxx` 字段建立额外字段别名或预置字段组。

## Decisions

### 1. 新增 `tdxquant/api/transaction.py`，并由 `TdxApiManager.transaction` 聚合

决策：

- 新建 `TransactionApi` 域模块。
- 在 `TdxApiManager` 中新增 `_transaction_api` 和 `transaction` proxy。

原因：

- 股票交易数据与行情、参考数据、专业财务数据都不是同一资源族。
- 后续板块/市场交易数据可以平滑继续扩进 `transaction`，不需要重新拆域。

备选方案：

- 放入 `market`
  - 放弃，原因是会继续把非行情读取能力堆进 `market`。
- 为 `gpjy` 单独建域
  - 放弃，原因是后续 `bkjy/scjy` 很可能共享同一资源边界。

### 2. CLI 使用语义化命名，而不是直接暴露 `gpjy` 缩写

决策：

- nested `api`
  - `api stock-transaction-data`
  - `api stock-transaction-data-by-date`
- flat bridge
  - `tdx-data-stock-transaction`
  - `tdx-data-stock-transaction-by-date`

原因：

- `financial-data` 已经说明当前 CLI 更偏向语义化而非完全照搬官方函数名。
- `gpjy` 缩写对日常使用者不够直观。

### 3. `field_list` 维持显式参数，`year/mmdd` 维持官方零值语义

决策：

- 两个 manager 方法和 CLI 入口都要求显式传 `field_list`。
- `by_date` 入口允许 `year=0, mmdd=0`，并原样透传到底层 bridge。

原因：

- 文档明确要求字段筛选不能为空。
- 零值语义已经是官方契约，不应在 manager 层额外改写。

## Risks / Trade-offs

- [`transaction` 域后续可能继续变大] → 本次只收 `gpjy`，后续仍按小包推进，不把 `bkjy/scjy` 一次性并入。
- [CLI 语义名与官方方法名不完全一致] → 继续沿用当前项目的语义化命名策略，同时保留 flat bridge 兼容入口。
- [`year/mmdd=0` 语义不够直观] → 在设计和 spec 中显式记录，并通过测试锁定透传行为。
