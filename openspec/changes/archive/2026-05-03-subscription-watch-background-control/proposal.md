## Why

`subscription-watch` 的前台 run artifact contract 和 worker HTTP bridge 已经落地，但 worker-local background control 仍然缺少独立 OpenSpec capability。当前本地控制语义分散在 `subscription_watch_background.py` 和 `bridge_http.py` 之间，需要把 single-active lifecycle、状态修正和诊断读取正式收口成稳定 contract。

## What Changes

- 新增 worker-local `subscription-watch` background control capability，正式定义单活后台 watch 的 `start` / `stop` / `status` / `list` / artifact 诊断语义。
- 固定 background control 的文件状态模型，包括 `active.json`、`pid`、`lock` 与 canonical run artifact bundle 的关系。
- 固定 stale-process reconciliation、same-`idempotency_key` replay、`stop` noop、active-only status view 等治理规则。
- 让 HTTP bridge 继续作为 transport shell，消费 background control 的读写模型，而不是在 bridge 层继续拼接本地状态语义。

## Capabilities

### New Capabilities
- `tdx-task-subscription-watch-background-control`: worker-local single-active `subscription-watch` 后台控制 contract，包括 lifecycle、状态修正和 run artifact 诊断读取。

### Modified Capabilities

## Impact

- Affected code:
  - `tdxquant/subscription_watch_background.py`
  - `tdxquant/bridge_http.py`
  - `tdxquant/subscription_watch_background_runner.py`
  - background/bridge tests and task contract docs
- Affected APIs:
  - worker-local background control behavior consumed by `tdxquant bridge serve`
  - stable semantics for bridge `watch/status/list/artifacts/events/logs`
- No new external dependency or transport is introduced in this change.
