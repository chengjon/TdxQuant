## Context

稳定桌面交易主线目前已经有三种持久化对象：
- 可覆盖的 `last_order_state`
- 追加式 `order_event_log`
- keyed workflow 的 `submission_ledger`

这三者各自有价值，但还缺少“一次 finalized trade result 对应一份不可变审计快照”的对象。`last_order_state` 会被后续结果覆盖，`order_event_log` 更适合连续流审阅，`submission_ledger` 又只覆盖带 `submission_key` 的 workflow。结果是：对单次稳定交易结果做复盘、排障或跨系统对账时，还没有统一的单体审计对象。

## Goals / Non-Goals

**Goals:**
- 为所有通过 `TdxTradeManager._finalize_result(...)` 落盘的稳定交易结果补一份不可变 `trade_audit` JSON artifact。
- 在结果中增加规范化 `trade_audit` 摘要，并把同样的摘要写进现有 state/event artifacts，用于跨对象关联。
- 让 trade artifact target discovery 同时暴露 audit 目录。

**Non-Goals:**
- 不改桌面自动化买入、确认、结果窗处理本身。
- 不新增新的 CLI 交易命令。
- 不把 read-only workflow 变成会写审计文件的路径。
- 不重做 submission ledger 语义。

## Decisions

### 1. 审计写入挂在 `_finalize_result(...)`，而不是散落在各个 workflow

稳定交易里真正会落盘 state/event 的路径已经统一收口到 `_finalize_result(...)`。把 audit 也挂在这里，能自动覆盖：
- `buy`
- `buy_submit_once`
- `confirm_current` 成功推进后的 finalized path
- duplicate replay / conflict reject / risk reject 这些已经走 finalized persistence 的结果

这样不需要在每条 workflow 里重复接线，也能保证审计对象和既有持久化语义一致。

### 2. `trade_audit` 摘要先附着，再写 state/event

为了让现有 `last_order_state` 和 `order_event_log` 都拥有可关联的 `audit_id`，本包会先把规范化 `trade_audit` 摘要挂到 `result.data`，然后再写 state/event。这样旧 artifact 不需要重构结构，只要把摘要透传进去即可。

### 3. 审计状态按 finalized outcome 分层，而不是只区分 success/failure

如果只用 `ok` 区分审计状态，duplicate replay 和 pre-trade reject 这类治理信息会丢失。当前计划使用统一状态枚举：
- `confirmed`
- `replayed`
- `rejected`
- `failed`

判定依据来自：
- `result.ok`
- `risk_gate.passed`
- `idempotency.decision`

这样既能保留审计可读性，也不会把所有非成功路径压成一个 `failed`。

### 4. 第一版只提供默认 audit 目录和 manager-level override

本包会给 `TdxTradeManager` 增加 `trade_audit_dir` 配置，并提供默认目录 `runtime/trade-audits`。但不会在这一包里继续把 `--audit-dir` 扩到所有 trade/task CLI 命令，避免接口面膨胀。

这能满足：
- 生产默认落盘
- 测试临时目录隔离
- 后续 CLI 扩展的前置基础

## Risks / Trade-offs

- [审计对象覆盖范围比“confirmed trade”更广] → 明确把 contract 定义为 finalized stable trade audit，而不是只记录成功成交。
- [state/event 会增加少量冗余字段] → 只回灌轻量 `trade_audit` 摘要，不重复整份审计 payload。
- [未来 CLI 可能还想控制 audit 目录] → 先稳定 manager-level contract，CLI 作为后续独立增量包处理。

## Migration Plan

1. 先补 trade manager RED tests，覆盖 confirmed / replayed / confirm-current / read-only paths。
2. 在 `trade/context.py` 增加 audit summary / audit file helper。
3. 在 `trade/manager.py` 的 `_finalize_result(...)` 中接入 audit 流程。
4. 更新文档并跑 focused/full verification。

## Open Questions

- 后续是否需要把 `trade_audit` 再上收到 report/task 层做单次交易审计查询；本包先不处理。
