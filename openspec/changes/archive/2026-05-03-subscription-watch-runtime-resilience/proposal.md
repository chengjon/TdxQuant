## Why

`subscription-watch` 的 foreground/background/bridge 主线已经能跑，但 live 运行还缺少长期运行治理：断线重连、bounded backoff、`degraded` 状态、以及同一次 run 内的恢复轨迹摘要还没有收成正式 contract。当前这些行为既没有 OpenSpec capability，也没有对应的 resilience fixtures。

## What Changes

- 为 `subscription-watch` foreground task 增加 runtime resilience contract：
  - bounded reconnect
  - `reconnecting`
  - `degraded`
  - degraded 后低频恢复探测
  - 同一 `run_id` 持续运行
- 扩展 `status.json` / `summary.json` 的 runtime state fields，但不引入 synthetic reconnect lifecycle events。
- 扩展 worker-local background reconcile 语义，使 `reconnecting / degraded` 成为显式 active-process states。
- 为 replay fixture bundle 增加 representative resilience status/summary samples。

## Capabilities

### Modified Capabilities
- `tdx-task-subscription-watch`
- `tdx-task-subscription-watch-background-control`
- `tdx-provider-replay-fixtures`

## Impact

- Affected code:
  - `tdxquant/subscription_watch_run.py`
  - `tdxquant/api/task.py`
  - `tdxquant/subscription_watch_background.py`
  - `tdxquant/subscription_watch_background_runner.py`
  - subscription-watch fixtures/tests/docs
- Affected APIs:
  - live `subscription-watch` runtime-state contract
  - background-control reconcile/read semantics
  - replay fixture catalog for subscription-watch resilience samples
- No new transport, worker discovery, or multi-worker scheduling is introduced.
