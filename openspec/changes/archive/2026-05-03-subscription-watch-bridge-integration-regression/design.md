## Context

`subscription-watch` 当前已经有三层稳定实现：

- worker-local background control
- worker HTTP bridge
- master-side registry/client + CLI remote-control entrypoints

而 `subscription-watch-runtime-resilience` 也已经把 `running / reconnecting / degraded / failed(stale_process_state)` 这些状态固定下来。当前剩下的不是新增功能，而是把“跨层投射不漂移”这件事正式写成 contract。

## Goals / Non-Goals

**Goals:**

- 固定 worker bridge 的 auth/allowlist 与 HTTP envelope 语义。
- 固定 `watch/status` 的 controller verbatim projection 语义。
- 固定 `health` 与 active `run_id` fallback 的 control-only read 语义。
- 固定 master-side registry/client 的 transport failure normalization。
- 固定 CLI `bridge health/watch-*` 的 JSON pass-through 语义。

**Non-Goals:**

- 不新增 bridge endpoint。
- 不新增 SSE / stream transport。
- 不新增 worker 自注册或调度。
- 不修改 foreground `subscription-watch` 业务语义。
- 不扩到 `trade`、`block` 或其他远控能力。

## Decisions

### 1. `watch/status` 是 controller 读模型的 verbatim projection

`GET /bridge/v1/watch/status` 不再在 bridge 层重建 worker-local 状态；bridge 只读取 controller 的 `status()` 并直接包装到 success envelope。

这意味着：

- `control.state`
- `watch_status.state`
- resilience 字段，例如 `reconnect_count`、`last_error`、`degraded_since`

都必须由 controller 决定，bridge 不得自行改写。

### 2. `health` 和 active-run fallback 使用 control-only read

`GET /bridge/v1/health` 以及 `/watch/artifacts|events|logs` 在未显式传 `run_id` 时的 active-run fallback，都必须通过 controller 的 control-only 读路径完成，而不是依赖解析 `status.json`。

这样即使当前 run 的 `status.json` 损坏：

- `health` 仍可返回 bridge 在线 + control 可读
- active run fallback 仍可解析到当前 `run_id`

### 3. auth / allowlist 失败保持 transport-scoped

bridge 的负路径继续只表达 transport boundary：

- `401 UNAUTHORIZED`
- `403 FORBIDDEN_SOURCE`
- `404 NOT_FOUND`
- `400 INVALID_REQUEST`
- `500 INTERNAL_ERROR`

这些错误不应伪装成 background task failure，也不应透传成 watch runtime state。

### 4. registry/client 负责 transport failure normalization

master-side `call_worker(...)` 需要把下列问题统一成稳定 transport failure，而不是 task/runtime failure：

- invalid UTF-8 success body
- invalid JSON success body
- non-object JSON success payload
- `URLError(ConnectionRefusedError(...))`

同时保留 HTTP error body 中的 bridge JSON envelope 原样透传。

### 5. CLI bridge 远程读入口保持 transport-only pass-through

CLI 的这些入口：

- `bridge health`
- `bridge watch-status`
- `bridge watch-list`
- `bridge watch-artifacts`
- `bridge watch-events`
- `bridge watch-logs`

都继续只是 registry/client 的 transport shell。

规则：

- stdout 直接打印 registry/client 返回的 JSON payload
- 不二次加工 `result`
- `ok=true` 返回 exit code `0`
- `ok=false` 返回 exit code `1`

## Risks / Trade-offs

- [bridge/control 语义分裂] -> 强制 `watch/status` 采用 verbatim projection，减少 bridge 自行拼接状态。
- [损坏的 `status.json` 影响 bridge 自检] -> `health` 和 active-run fallback 改走 control-only read。
- [transport failure 与 task failure 混淆] -> registry/client 负责错误归一化，CLI 只透传 transport contract。
- [CLI 文档漂移] -> 在 `TdxQuant_Task_Subscription_Watch_Contract.md`、`Function Map`、`Next Steps` 中明确 remote-control read contract。

## Migration Plan

1. 保持既有 endpoint 和 route 不变。
2. 将 `watch/status`、`health`、active-run fallback 收敛到 controller read model。
3. 固定 registry/client 的 success-body parsing 与 connection-refused normalization。
4. 固定 CLI `bridge health/watch-*` 的 pass-through 语义。
5. 用 focused bridge/registry/CLI regression 验证 contract。

回滚策略：

- 若 integration hardening 引发回归，可回退到先前 bridge/client 实现。
- 不涉及 run artifact schema 变更，因此回滚不会影响已有 `subscription-watch` run 目录。
