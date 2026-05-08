# TdxQuant Provider Query Contract

本文定义 `market / meta / financial / transaction` 四条查询主线当前统一后的 provider-ready query contract。

目标不是把四类查询压成同一套业务 row schema，而是让上层项目可以先按统一查询元数据消费，再按能力自己的 `rows` 结构做细化解析。

## 1. Scope

当前 contract 覆盖这些正式入口：

- Python manager
  - `TdxApiManager.market.*`
  - `TdxApiManager.meta.*`
  - `TdxApiManager.financial.*`
  - `TdxApiManager.transaction.*`
- nested CLI
  - `tdxquant api ...`
- flat CLI
  - `tdxquant tdx-data-*`
- replay fixtures
- capability discovery metadata

不覆盖：

- 新批量查询命令
- HTTP query service
- task/report/catalog 场景封装
- 强行统一四类查询的 `rows` 业务字段

## 2. Stable Payload Shape

同步 provider envelope 继续沿用既有 hardened result contract。  
查询主线新增、并稳定承诺的是 `data.query_meta`。

典型形态：

```json
{
  "success": true,
  "ok": true,
  "code": "ok",
  "capability": "market.snapshot",
  "data": {
    "query_meta": {
      "query_kind": "market.snapshot",
      "row_count": 1,
      "requested_fields": ["Now", "Volume"],
      "returned_fields": ["symbol", "Now", "Volume", "amount"],
      "symbol": "000001.SZ",
      "query_params": {}
    },
    "rows": [
      {
        "symbol": "000001.SZ",
        "Now": 12.34,
        "Volume": 567890,
        "amount": 7000000
      }
    ]
  }
}
```

## 3. `query_meta` Rules

所有覆盖到的查询能力都稳定返回：

- `query_kind`
- `row_count`
- `requested_fields`
- `returned_fields`
- `query_params`

按查询语义补充选择器字段：

- `symbol`
- `symbols`
- `date`
- `date_range`
- `market`
- `block_code`

约束：

- `query_kind` 固定使用 `{domain}.{method}` 稳定字面值
- `row_count` 始终为数值
- `requested_fields` 始终存在，不支持字段筛选时为 `[]`
- `returned_fields` 始终存在，空结果时为 `[]`
- `symbol` 与 `symbols` 不同时出现
- `date` 与 `date_range` 不同时出现
- `query_params` 保留无法投影为共性选择器的能力特有参数

## 4. `requested_fields` vs `returned_fields`

`requested_fields` 表示**最终传给 provider 的规范化字段列表**，不是调用者原始文本。  
`returned_fields` 表示**实际返回 row/header 中可观察到的字段集合**。

这意味着：

- manager 内部如果做了字段别名解析或有效字段裁剪，`requested_fields` 反映的是解析后的 effective fields
- 空结果场景下，`returned_fields` 固定为 `[]`

## 5. Preserved Domain-native Rows

这条 contract **不**统一四类查询的业务 row schema。

- `market` 保留行情 / K 线原始字段
- `meta` 保留列表和板块成员字段
- `financial` 保留财务字段
- `transaction` 保留交易统计字段

统一的只是 `data.query_meta`，不是 `data.rows` 的业务语义。

## 6. Replay and Discovery

当前已提供 representative replay fixtures，覆盖：

- `market.snapshot`
- `market.kline`
- `meta.stock_list`
- `meta.sector_stocks`
- `financial.financial_data`
- `financial.financial_data_by_date`
- `transaction.stock_transaction_data`
- `transaction.market_transaction_data`

并补了：

- empty-result representatives
- representative failure fixtures

`runtime.capabilities` 对这些查询能力还会额外暴露：

- `query_metadata.query_shapes`
- `query_metadata.supports_requested_fields`
- `query_metadata.supports_empty_results`
- `query_metadata.supports_replay`

## 7. Recommended Consumer Strategy

上层项目建议先按下面顺序消费查询结果：

1. 读顶层 provider envelope：`success / code / message / capability`
2. 读 `data.query_meta`
3. 再按能力特有语义解析 `data.rows`

这样可以把 `market / meta / financial / transaction` 统一挂到一个 query adapter 上，而不必为每条能力先做完全独立的 transport contract。
