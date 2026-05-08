## Context

当前项目已经完成几条高价值 provider contract 的收口：

- provider result envelope
- capability discovery / health / doctor
- formula screen
- block mutation / block sync
- subscription event / replay / subprocess replay

但 `market / meta / financial / transaction` 四条查询主线仍停留在“入口存在、结果可用”，而不是“查询 contract 稳定”。现状问题主要有三类：

- 查询结果缺少统一的 query metadata
- CLI / manager / replay fixture / discovery 没有围绕查询主线做统一约束
- 上层项目必须按 capability 特例消费，而不是先走通用 query adapter

这条 change 的目标不是新增查询能力，而是把现有正式入口整理成 provider-ready query contract。

## Goals / Non-Goals

**Goals:**

- 为 `market / meta / financial / transaction` 建立稳定的共性 query metadata contract。
- 保持现有 manager、nested CLI、flat CLI 入口不变，但让它们输出一致的查询 contract。
- 为查询主线补齐 replay fixtures，并让 fake/replay mode 可以稳定复现这些 contract。
- 在 capability discovery 中为查询能力补齐可消费的 query metadata。

**Non-Goals:**

- 不新增查询命令或新 API 形态。
- 不把四条查询主线压成同一套 row schema。
- 不新增 HTTP service 或 task/report 场景封装。
- 不修改已完成的 provider result envelope 顶层字段定义。
- 不扩展到 trade、subscription 或 block 场景任务。

## Decisions

### 1. 采用“共性元数据统一 + domain-native rows 保留”的方案

不对四条查询主线做深度 payload 重塑，而是在 `data.query_meta` 内补齐共性字段：

- `query_kind`
- `row_count`
- `requested_fields`
- `returned_fields`

并在适用时补条件字段，例如：

- `symbol`
- `symbols`
- `date`
- `date_range`
- `market`
- `block_code`
- `query_params`

同时保留各能力原有的 `rows` 记录结构。这样上层可以统一消费查询元数据，而无需这条 change 先把所有业务记录改成同一 schema。

统一布局：

```json
{
  "data": {
    "query_meta": {
      "query_kind": "market.snapshot",
      "row_count": 1,
      "requested_fields": ["price", "vol"],
      "returned_fields": ["price", "vol", "amount"],
      "symbol": "000001.SZ"
    },
    "rows": [...]
  }
}
```

`query_meta` 与 `rows` 分离，避免查询元数据和 domain-native row keys 发生层级冲突。

### 2. 不新增查询入口，只 harden 现有正式入口

这条 change 只覆盖现有正式入口：

- manager query methods
- nested `api` commands
- flat CLI query commands

不新增批量查询命令或新的 wrapper command。这样可以把范围锁在“统一 contract”，而不是“扩新入口”。

### 3. `query_kind` 使用 capability-owned 注册表

第一版不允许各能力自行发明自由字面量，稳定值直接对齐当前 capability 名称：

- `market.snapshot`
- `market.full_tick`
- `market.market_snapshot`
- `market.kline`
- `market.stock_info`
- `market.more_info`
- `market.cb_info`
- `meta.stock_list`
- `meta.sector_list`
- `meta.sector_stocks`
- `meta.divid_factors`
- `meta.ipo_info`
- `meta.gb_info`
- `meta.gp_one_data`
- `financial.financial_data`
- `financial.financial_data_by_date`
- `transaction.stock_transaction_data`
- `transaction.stock_transaction_data_by_date`
- `transaction.sector_transaction_data`
- `transaction.sector_transaction_data_by_date`
- `transaction.market_transaction_data`
- `transaction.market_transaction_data_by_date`

这让上层 adapter 能直接按 `{domain}.{method}` 做稳定分派，而不需要额外映射一层私有别名。

### 4. `requested_fields` 和 `returned_fields` 使用“有效请求 vs 实际返回”语义

这一包不把 `requested_fields` 定义成调用者的原始文本输入，而是定义成**最终传给 provider 的规范化字段列表**：

- 对于 `manager._resolve_fields(...)` 参与的能力，`requested_fields` 反映解析后的 effective field list
- 对于 `fields` 本就是显式必填参数的能力，`requested_fields` 反映规范化后的调用参数
- 对于不支持字段筛选的能力，`requested_fields=[]`

`returned_fields` 反映实际 `rows` 中稳定可观察到的字段集合：

- 正常有结果时，从实际返回的 row keys / header 提取
- 空结果时固定为 `[]`

这样 contract 锁的是 provider 实际消费和实际返回的字段，而不是调用路径中的中间文本形态。

### 5. 共性 selector 之外使用 `query_params` 保留能力特有参数

共性 selector 只覆盖第一层高频语义：

- `symbol`
- `symbols`
- `date`
- `date_range`
- `market`
- `block_code`

当查询还需要其他 selector，而这些 selector 不适合膨胀成全局共性字段时，统一进入 `query_params`。例如：

- `list_type`
- `block_type`
- `ipo_type`
- `count`
- `period`
- `report_type`

规则：

- 单值标的参数映射到 `symbol`
- 列表标的参数映射到 `symbols`
- `symbol` 与 `symbols` 不同时出现
- `date` 与 `date_range` 不同时出现
- 无法自然投影到共性字段的参数才进入 `query_params`

### 6. replay fixtures 作为 query contract 的锁定器，而不是附属样例

`market / meta / financial / transaction` 都必须补 representative fixtures，至少覆盖：

- success
- empty-result
- representative failure

这些 fixture 要锁住的不只是 envelope，而是查询主线的共性字段和值类型。这样 fake provider mode、CLI subprocess replay 和上层 contract tests 才能共用。

最低 representative coverage：

- `market`: `snapshot`, `kline`
- `meta`: `stock_list`, `sector_stocks`
- `financial`: `financial_data`, `financial_data_by_date`
- `transaction`: `stock_transaction_data`, `market_transaction_data`

### 7. capability discovery 必须暴露查询能力的结构化元数据

查询主线不能只在文档里说明“这是个 query”。discovery metadata 需要显式暴露：

- `query_metadata.query_shapes`
- `query_metadata.supports_requested_fields`
- `query_metadata.supports_empty_results`
- `query_metadata.supports_replay`

这样上层在 capability discovery 阶段就能知道：

- 如何调用
- 能否传字段筛选
- 是否可以离线联调

`query_shapes` 第一版固定为对象数组，元素最少包含：

```json
{
  "query_kind": "market.kline",
  "selectors": ["symbols", "date_range"],
  "query_params": ["period", "count", "dividend_type", "fill_data"]
}
```

### 8. 顶层 provider result envelope 保持不变

这条 change 不修改：

- `success`
- `ok`
- `code`
- `message`
- `capability`
- `runtime`

等已经固定的 envelope 规则。查询主线的变化只落在 capability-specific `data` payload 和 discovery / replay 侧车信息上。

### 9. 这是 additive hardening，不升级 capability major version

这条 change 只做 additive hardening：

- 既有 capability 名称保持不变
- 顶层 envelope 保持不变
- 仅增加 `data.query_meta`、fixture coverage 和 discovery metadata

因此第一版不要求提升 capability major version。fixture `schema_version` 可以随当前 contract 日期推进，但不把这次 change 定义成 breaking migration。

## Risks / Trade-offs

- [四条查询主线参数差异较大] → 只统一共性 query metadata，不强推统一 row schema。
- [CLI / manager / replay 可能继续漂移] → 把四层一起纳入 change，并用 representative tests 锁定。
- [query selector 字段可能不完全共形] → 只要求在语义适用时补 `symbol/symbols/date/date_range/market/block_code`，其余 capability-specific selector 统一收进 `query_params`。
- [fixture 数量上升] → 只补 representative success / empty / failure，不追求每个 query 入口都铺满矩阵。
- [空结果下 `returned_fields` 难以推断] → contract 明确固定为 `[]`，不从请求字段反推。

## Migration Plan

1. 在 bridge/provider result 边界补齐 `data.query_meta`，而不是在 CLI 层二次拼装。
2. 让 manager / nested CLI / flat CLI 统一透传这些结果，不新增命令。
3. 补充 query replay fixtures 与 default mapping，保证 replay 与 live 共用同一 `query_meta` contract。
4. 更新 capability discovery metadata。
5. 用 manager / CLI / replay / discovery tests 锁住 contract，再更新文档。

回滚策略：

- 若某条查询 contract 改动造成兼容问题，可先回退该能力的 query metadata 注入逻辑。
- 顶层 result envelope 不变，因此回滚不会影响已完成的 provider result contract。

## Open Questions

- 无。第一版范围已经锁定为既有 query 入口的 contract hardening，不扩展新入口或新 transport。
