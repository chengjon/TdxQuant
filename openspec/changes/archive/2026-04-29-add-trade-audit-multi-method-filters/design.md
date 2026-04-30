## Context

当前 `trade_audit` daily / period workflow 已支持：

- `status`
- `statuses`
- `method`
- `broker`

并且围绕固定单方法，已经有三组异常入口：

- `confirm_current`
- `buy_submit_once`
- `buy`

当前缺口不是新的底层 trade workflow，而是无法把多个方法按同一条执行链路组合起来做 OR 过滤，因此还做不出稳定的 “submit path exceptions” 这一类更高层视角。

## Goals / Non-Goals

**Goals:**

- 为 `trade_audit` daily / period 增加 `methods` OR 过滤
- 为 CLI 增加重复 `--method-any`
- 增加第一组基于多方法过滤的 submit-path exception presets / entries / bundles
- 保持现有单方法 `method` 调用不变

**Non-Goals:**

- 不改变现有 `status` / `statuses` 语义
- 不引入多 broker OR 过滤
- 不增加新的 trade/task workflow
- 不做跨 `ledger` / `trade_audit` 的聚合

## Decisions

### 1. `method` 与 `methods` 并存，语义对齐 `status` / `statuses`

新增：

- Python: `methods: list[str] | None`
- CLI: `--method-any` repeated

约束：

- `method` 和 `methods` 不能同时使用

原因：

- 与已稳定的 `status` / `statuses` 保持完全同构
- 不破坏现有单方法调用
- 便于后续继续扩 broker 维度时复用同样模式

### 2. 第一组多方法 preset 只覆盖 submit path

第一批新入口固定：

- `methods=["buy_submit_once", "confirm_current"]`
- `statuses=["rejected", "failed"]`

原因：

- 这是当前最自然的高阶组合视角
- 它直接连接完整提交与确认推进两步
- 范围小，足够证明多方法过滤已经可日常复用

### 3. 继续把 bundle 建在既有 entry 上

这包会增加：

- `audit-submit-path-exception-diagnostics`
- `confirm-submit-path-exception-review`

原因：

- 前者适合纯诊断
- 后者适合在确认推进后直接回看整条 submit path 的异常
- 不新增执行路径，只组合既有 entry

## Risks / Trade-offs

- [过滤接口继续变复杂] → 保持与 `status` / `statuses` 对称，降低理解成本
- [后续还要加 brokers OR 过滤] → 先把 `methods` 模式走通，后续可按同样结构扩展
- [submit path 定义过窄] → 先固定为 `buy_submit_once + confirm_current`，后续需要时再扩
