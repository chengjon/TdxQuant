# TdxQuant Desktop Trade Audit Contract

本文定义稳定桌面交易主线当前的 `trade_audit` contract。

它关注的是：

- finalized stable trade result 的单次不可变审计对象
- `trade_audit` 摘要字段
- 与现有 `last_order_state` / `order_event_log` 的关联关系

它不关注：

- read-only trade workflow 的结果 schema
- `submission_ledger` 的幂等语义细节
- 上层 report / lookup 如何消费这些审计文件

## 1. 当前目标

当前第一版 `trade_audit` contract 解决 3 件事：

- 为每个 finalized stable trade result 写一份不可变 JSON audit artifact
- 在返回结果中暴露稳定 `data.trade_audit` 摘要
- 把同一份 `trade_audit` 摘要回灌到 `last_order_state` 和 `order_event_log`

## 2. 当前覆盖范围

当前会写 `trade_audit` 的路径是：

- `TdxTradeManager.pingan.buy(...)`
- `TdxTradeManager.pingan.buy_submit_once(...)`
- `TdxTradeManager.pingan.confirm_current(...)` 的 finalized path

更准确地说，凡是走到稳定 `_finalize_result(...)` 持久化路径的结果，当前都会写 `trade_audit`。

当前不会写 `trade_audit` 的路径包括：

- `trade health`
- `trade preflight`
- `trade dialog-readiness`
- `trade submit-ready`
- 未推进确认框成功的 `confirm_current(...)`

## 3. Canonical Result Additions

当前 stable trade result 的 `data` 中会新增：

```json
{
  "trade_audit": {
    "schema_version": "2026-04-29",
    "audit_id": "0f3d0d8c7f9f4acda1aa7fa2c6fead88",
    "recorded_at": "2026-04-29T09:32:01.123456+00:00",
    "status": "confirmed",
    "broker": "pingan",
    "method": "buy",
    "contract_no": "B202604290001",
    "submission_key": "buy-20260429-001",
    "side_effect_level": "live_side_effecting",
    "risk_gate_passed": true,
    "idempotency_decision": "execute"
  },
  "artifacts": {
    "last_order_state_path": "runtime/pingan-last-order.json",
    "order_event_log_path": "runtime/pingan-order-events.jsonl",
    "submission_ledger_path": "runtime/pingan-submission-ledger.jsonl",
    "trade_audit_path": "runtime/trade-audits/20260429T093201123456Z-buy-confirmed-0f3d0d8c.json"
  }
}
```

## 4. Field Rules

### `data.trade_audit`

当前固定字段：

- `schema_version`
- `audit_id`
- `recorded_at`
- `status`
- `broker`
- `method`
- `contract_no`
- `submission_key`
- `side_effect_level`
- `risk_gate_passed`
- `idempotency_decision`

### `status`

当前第一版状态枚举：

- `confirmed`
- `replayed`
- `rejected`
- `failed`

语义：

- `confirmed`：真实 finalized trade result 成功完成
- `replayed`：因 `submission_key` duplicate short-circuit 而复用既有结果
- `rejected`：风险门或冲突治理拒绝了 finalized 请求
- `failed`：进入 finalized 持久化路径，但执行结果不是成功且不属于 replay/reject

## 5. Audit Artifact

当前默认目录：

- `runtime/trade-audits/`

单个审计文件当前至少包含：

- `schema_version`
- `trade_audit`
- `result`

其中：

- `trade_audit` 是当前标准摘要
- `result` 是本次 finalized stable trade result 的结构化快照

审计文件是**不可变单体对象**，用于替代“只靠可覆盖 state 文件或连续 event log 复盘”的模式。

## 6. Existing Artifact Correlation

当前 contract 明确要求：

- `last_order_state` 保存同一份 `trade_audit`
- `order_event_log` 每行保存同一份 `trade_audit`

因此，后续跨对象关联优先使用：

- `trade_audit.audit_id`

而不是依赖文件名或人工比对时间戳。

## 7. Companion Lookup Contract

当前 `trade_audit` 已经有配套消费入口，见：

- [TdxQuant_Trade_Audit_Lookup_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Trade_Audit_Lookup_Contract.md)

当前已补齐的消费面包括：

- `TdxTaskManager.trade_audit_lookup(...)`
- `TdxTaskManager.trade_audit_daily_report(...)`
- `TdxTaskManager.trade_audit_period_report(...)`
- `tdxquant task trade-audit-lookup ...`
- `tdxquant task trade-audit-daily-report ...`
- `tdxquant task trade-audit-period-report ...`
- `tdxquant report audit-lookup ...`
- `tdxquant report audit-daily ...`
- `tdxquant report audit-period ...`
- report presets：`audit-daily-review` / `audit-daily-confirmed` / `audit-period-review`
- catalog entries：`audit-daily-review` / `audit-daily-confirmed` / `audit-period-review`
- audit bundle：`audit-diagnostics`
- CLI 级别的 `--audit-dir`
- 基于 `audit_id` / `contract_no` / `submission_key` / `code` 的稳定查询
- 按日与按区间的稳定聚合

## 8. Current Limits

当前剩余缺口主要是：

- 更丰富的 audit bundle / preset 扩展
- 审计目录索引缓存
- 跨 `trade_audit` / task ledger / submission ledger 的组合查询
