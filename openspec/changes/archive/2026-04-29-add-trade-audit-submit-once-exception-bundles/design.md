## Context

`trade_audit` 日报和区间报表已经支持：

- 单状态 `status`
- 多状态 `statuses`
- `method`
- `broker`

同时，完整提交流程 `buy_submit_once` 已经稳定，并且已有：

- `task-submit-once` catalog entry
- `submit-once-followup`

当前缺口不是底层过滤能力，而是日常入口没有把 “`buy_submit_once` + `rejected|failed`” 这一类高频排障视角做成稳定 preset / bundle。

## Goals / Non-Goals

**Goals:**

- 为 `report` 层增加 submit-once-oriented exception presets
- 为 `catalog` 层增加 submit-once-oriented exception entries
- 增加一个纯诊断 bundle 和一个直接承接完整提交流程的 follow-up bundle
- 不改变现有 `trade_audit` 聚合算法或 CLI 参数语义

**Non-Goals:**

- 不新增新的底层过滤字段
- 不新增新的 task / trade workflow
- 不做跨 `ledger` / `trade_audit` 的新聚合逻辑
- 不补 `buy` 的完整 method 矩阵

## Decisions

### 1. 先只覆盖 `buy_submit_once`

这包先只做 `method=buy_submit_once`，不同时扩到 `buy` 等其它方法。

原因：

- 它直接对应已经稳定的完整提交流程
- 能同时覆盖“多维异常 preset”和“submit-once follow-up bundle”两个剩余方向
- 范围足够小，能快速形成新的稳定日常入口

### 2. 继续复用现有 `statuses` 语义

新的异常 preset 固定：

- `method=buy_submit_once`
- `statuses=["rejected", "failed"]`

不引入新的 “exception_type” 一类抽象字段。

原因：

- 当前 task / CLI 语义已经稳定
- 直接复用已有过滤 contract，避免再开底层实现包
- 上层用户能从 preset 名直接理解它做了什么

### 3. 同时提供“纯诊断”和“提交流程 follow-up”两类 bundle

这包会同时增加：

- `audit-submit-once-exception-diagnostics`
- `submit-once-exception-review`

原因：

- 前者适合纯复盘排障
- 后者适合完整提交流程后直接进入异常审计复盘
- 两者都基于已稳定 entry 组合，不新增执行路径

## Risks / Trade-offs

- [命名继续膨胀] → 通过显式把范围压到 `buy_submit_once`，避免一次补全所有 method 组合
- [用户把 bundle 误认为新增业务逻辑] → 文档明确这些只是对既有 report/task preset 的组合
- [未来还要扩更多 method 维度] → 保持当前命名模式一致，后续可平行扩展
