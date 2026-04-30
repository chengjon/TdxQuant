## Context

当前已经具备的稳定报表/回溯能力有：

- `task ledger-summary`
- `task daily-trade-report`
- `task trade-period-report`
- `task trade-report-lookup`

这些能力本质上都是“读取已有 ledger / report 产物”的查询型入口，与执行型 task 已经明显分层。继续全部挂在 `task` 树下会让日常命令面越来越杂。

## Goals / Non-Goals

**Goals:**

- 提供独立的 `report` CLI 命令组。
- 用更短的子命令名暴露现有稳定报表能力。
- 让 `report` 子命令默认携带对应 profile。
- 保持 `task ...` 旧入口兼容。

**Non-Goals:**

- 不重写现有 task 报表逻辑。
- 不改变 task manager 的能力边界。
- 不移除已有 `task` 报表命令。

## Decisions

### 1. `report` 只作为 CLI 入口层，不新增 manager

本次不新建 `ReportManager`，而是继续复用 `TdxTaskManager`。这样：

- 业务逻辑仍然只有一份
- `task` 与 `report` 只是两套不同的用户入口
- 测试和文档更容易保持同步

### 2. `report` 组使用短子命令

采用：

- `report ledger`
- `report daily`
- `report period`
- `report lookup`

这样比在 `task` 下继续暴露长命令更适合日常使用。

### 3. 为 `report` 子命令设置更合理的默认 profile

`report daily` 默认使用 `daily_trade_report`，其他子命令同理。这样用户不需要每次都手工指定 profile，但仍然允许覆盖。

### 4. 提取共享分发 helper，避免 task/report 双份分支逻辑

由于 `task` 和 `report` 都会调用同一批报表能力，本次会把报表分发逻辑提成内部 helper，避免两条 CLI 路径分别维护参数映射。

## Risks / Trade-offs

- [CLI 入口变多] → 通过职责分层解决：`task` 仍偏 workflow，`report` 明确偏查询复盘。
- [双入口维护成本上升] → 用共享分发 helper 降低重复实现。
- [默认 profile 可能掩盖实现来源] → 文档明确说明 `report` 只是 `task` 报表能力的快捷入口。
