## Context

现有交易 task 只有：

- `trade_buy`
- `trade_submit_once`

它们解决的是“如何编排交易执行”，但没有解决“什么时候应该执行交易”。如果日常调用要每次自己先查一遍 snapshot、再查板块成分、再下单，task 层就还不够高层。

## Goals

- 实现一个带前置检查的买入 task 模板。
- 保持前置检查逻辑简单、可解释、可测试。
- 输出结构化任务报告。

## Non-Goals

- 本次不做公式规则引擎。
- 本次不做卖出模板。
- 本次不做复杂多条件 DSL。

## Decisions

### 1. 先支持两个最稳定的前置检查

- `max_snapshot_price`
  - 当前价必须小于等于给定上限
- `required_block_code`
  - 目标证券必须属于指定板块

这两个检查都能稳定用已有 API manager 完成，且语义直观。

### 2. 交易执行复用现有 `trade_buy`

`guarded_trade_buy` 不直接调用 trade manager，而是复用现有 `trade_buy(...)` task。这样：

- 环境刷新逻辑不重复
- trade 产物结构保持一致
- 新 task 只负责前置检查与报告整合

### 3. 生成任务报告

该 task 除返回标准 `Result` 外，还额外生成：

- JSON 完整报告
- CSV 单行摘要

用于日常留痕与问题排查。

## Verification

- task manager 测试验证前置检查与报告产物。
- CLI 测试验证 `task guarded-trade-buy` 分发。
- 回归测试验证既有 task/trade 不受影响。
