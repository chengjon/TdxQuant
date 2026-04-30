# TdxQuant Provider Formula Screen Contract

本文定义 `formula.screen` 的稳定 provider-facing contract。

## 1. Capability Identity

正式 capability 名固定为：

- `formula.screen`

推荐入口：

- Python: `TdxApiManager.formula.screen(...)`
- Nested CLI: `tdxquant api formula-screen ...`
- Flat CLI: `tdxquant tdx-formula-screen ...`

保留但不推荐作为上层正式 contract 的旧入口：

- `TdxApiManager.formula.process_mul_xg(...)`
- `tdxquant api formula-mul-xg ...`
- `tdxquant tdx-formula-mul-xg ...`

旧入口继续可用，但它们返回的是更接近 TongDaXin 原始结构的结果，不应作为上层长期稳定 schema 依赖。

## 2. Contract Goal

`formula.screen` 的目标不是暴露 TongDaXin 公式原始 shape，而是把“批量选股公式执行”整理成一个稳定、可直接消费的股票筛选 contract。

它需要同时满足两类需求：

- 上层可以直接拿 `matched_symbols` 做 watchlist / block / 后续任务输入
- 上层仍然可以从 `rows[*].series` 里拿到逐 symbol、逐字段、逐日期的原始判定上下文

## 3. Data Payload Shape

`formula.screen` 的 capability-specific payload 位于 provider result envelope 的 `data` 字段中。

顶层 `data` 至少包含：

- `input`
- `summary`
- `matched_symbols`
- `unmatched_symbols`
- `rows`

其中：

- `input` 描述本次公式筛选请求参数
- `summary` 提供输入股票数、命中数、未命中数和命中率
- `matched_symbols` 提供简化后的命中股票列表
- `unmatched_symbols` 提供未命中股票列表
- `rows` 提供逐 symbol 的完整归一化结果

## 4. Row Schema

每个 `rows[*]` 至少包含：

- `symbol`
- `matched`
- `field_names`
- `matched_dates`
- `latest_match_date`
- `series`

字段语义：

- `symbol`: 股票代码
- `matched`: 该 symbol 是否至少有一个归一化命中点
- `field_names`: 本 symbol 下返回过的公式字段名列表
- `matched_dates`: 所有命中日期，按归一化遍历顺序去重保留
- `latest_match_date`: `matched_dates` 的最后一个值；无命中时为 `null`
- `series`: 逐公式字段的归一化点位序列

每个 `series[*]` 至少包含：

- `field`
- `points`

每个 `points[*]` 至少包含：

- `date`
- `value`
- `matched`

## 5. Match Normalization Rules

第一版固定 truth normalization 规则如下：

- `1`
- `1.0`
- `"1"`
- `true`

以上值视为命中，其余值视为未命中。

归一化后：

- 单个点位是否命中，体现在 `points[*].matched`
- 单个 symbol 是否命中，体现在 `rows[*].matched`
- 命中 symbol 列表，体现在 `matched_symbols`

原始值仍保留在 `points[*].value`，避免丢失诊断信息。

## 6. Example

示例 `data` 如下：

```json
{
  "input": {
    "formula_name": "UPN",
    "formula_arg": "3",
    "stock_list": ["000001.SZ", "600519.SH"],
    "return_count": 2,
    "return_date": true,
    "stock_period": "1d",
    "start_time": "",
    "end_time": "",
    "count": 5,
    "dividend_type": 1
  },
  "summary": {
    "input_symbol_count": 2,
    "result_symbol_count": 2,
    "matched_symbol_count": 1,
    "unmatched_symbol_count": 1,
    "match_rate": 0.5
  },
  "matched_symbols": ["000001.SZ"],
  "unmatched_symbols": ["600519.SH"],
  "rows": [
    {
      "symbol": "000001.SZ",
      "matched": true,
      "field_names": ["UP3"],
      "matched_dates": ["20260204"],
      "latest_match_date": "20260204",
      "series": [
        {
          "field": "UP3",
          "points": [
            {"date": "20260203", "value": "0", "matched": false},
            {"date": "20260204", "value": "1", "matched": true}
          ]
        }
      ]
    },
    {
      "symbol": "600519.SH",
      "matched": false,
      "field_names": ["UP3"],
      "matched_dates": [],
      "latest_match_date": null,
      "series": [
        {
          "field": "UP3",
          "points": [
            {"date": "20260203", "value": "0", "matched": false}
          ]
        }
      ]
    }
  ]
}
```

## 7. Relationship To The Provider Envelope

`formula.screen` 只定义 `data` 的业务 payload。

完整同步输出仍需包在统一 provider result envelope 中，见：

- [TdxQuant_Provider_Result_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Result_Contract.md)

## 8. Recommended Usage

对上层系统，当前建议是：

- 把 `formula.screen` 视为正式稳定入口
- 把 `formula-mul-xg` 视为原始桥接入口
- 直接消费 `matched_symbols` 做 watchlist / block / 后续任务输入
- 在需要诊断时再读取 `rows[*].series`
