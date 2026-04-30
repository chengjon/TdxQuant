## Why

当前 `guarded_trade_buy` 已经支持：

- snapshot 当前价上限检查
- block 成分归属检查
- 条件通过后执行 trade workflow
- 生成 JSON/CSV 报告

但很多实际交易前置判断并不只看价格和板块，还需要一个简单的公式筛选条件。既然项目已经具备 `formula_scan` 能力，就应该把它接入这个完整交易模板。

## What Changes

- 为 `guarded_trade_buy` 增加可选 formula 前置检查。
- CLI 支持在 `task guarded-trade-buy` 上直接传入公式约束参数。
- 报告产物中纳入公式前置检查结果。

## Capabilities

### Modified Capabilities

- `tdx-task-management`

## Impact

- `guarded_trade_buy` 形成 `snapshot + block + formula + trade + report` 的完整模板。
- 日常调用可以直接在一个 task 里完成最常见的买入前保护。
