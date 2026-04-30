## Context

`trade_audit` 日报和区间报表已经支持：

- 单状态 `status`
- 多状态 `statuses`
- `method`
- `broker`

同时，基础买入 `buy` 已经稳定，并且已有：

- `guarded-buy` catalog entry
- `guarded-trade-followup`

当前缺口不是底层过滤能力，而是日常入口没有把 “`buy` + `rejected|failed`” 这一类高频排障视角做成稳定 preset / bundle。

## Goals / Non-Goals

**Goals:**

- 为 `report` 层增加 buy-oriented exception presets
- 为 `catalog` 层增加 buy-oriented exception entries
- 增加一个纯诊断 bundle 和一个直接承接 guarded-buy 的 follow-up bundle
- 不改变现有 `trade_audit` 聚合算法或 CLI 参数语义

**Non-Goals:**

- 不新增新的底层过滤字段
- 不新增新的 task / trade workflow
- 不做跨 `ledger` / `trade_audit` 的新聚合逻辑
- 不补更多 method 组合以外的新抽象

## Decisions

### 1. 先只覆盖 `buy`

这包先只做 `method=buy`，与前两包 `confirm_current` 和 `buy_submit_once` 保持同一模式。

原因：

- 它是剩余最后一条稳定核心方法
- 能把 method 维度的第一轮异常入口矩阵补齐
- 范围足够小，不需要改底层实现

### 2. 继续复用现有 `statuses` 语义

新的异常 preset 固定：

- `method=buy`
- `statuses=["rejected", "failed"]`

不引入新的 “exception_type” 一类抽象字段。

原因：

- 当前 task / CLI 语义已经稳定
- 直接复用已有过滤 contract，避免再开底层实现包
- 用户能从 preset 名直接理解其含义

### 3. 同时提供“纯诊断”和“guarded-buy follow-up”两类 bundle

这包会同时增加：

- `audit-buy-exception-diagnostics`
- `guarded-buy-exception-review`

原因：

- 前者适合纯复盘排障
- 后者适合受保护买入后直接进入异常审计复盘
- 两者都基于已稳定 entry 组合，不新增执行路径

## Risks / Trade-offs

- [命名继续膨胀] → 通过沿用既有命名模式，保持可预测性
- [bundle 被误认为新增业务逻辑] → 文档明确这些只是对既有 report/task preset 的组合
- [后续仍需扩更多维度] → 先补齐 method 第一轮矩阵，再考虑 broker 或更复杂组合
