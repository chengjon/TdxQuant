## Why

`subscription-watch` 的 worker-local background control、worker HTTP bridge、master-side registry/client、以及 CLI `bridge` 远程读入口已经落地，但这层 control plane 之前没有被正式收成 OpenSpec contract。当前实现已经补齐了几个关键回归点：

- `watch/status` 直接投射 controller 读模型
- `health` 和 active `run_id` fallback 使用 control-only read，而不是依赖解析损坏的 `status.json`
- auth / allowlist 失败保持 transport-scoped
- registry/client 对 invalid JSON、invalid UTF-8、non-object JSON、connection refused 做稳定失败归一化
- CLI `bridge health/watch-*` 直接透传 master-side client payload

现在需要把这组已实现 contract 正式写回 OpenSpec，避免 bridge/control-plane 继续只靠测试和文档维持。

## What Changes

- 新增 `tdx-worker-bridge-http-control-plane` capability，正式定义 worker bridge 的 HTTP envelope、auth/allowlist 负路径、状态投射、以及 master-side registry/client 的 transport failure normalization。
- 补充 `tdx-api-cli-entry` 中的 remote-control CLI contract，明确 `bridge health/watch-status/watch-list/watch-artifacts/watch-events/watch-logs` 的 JSON pass-through 语义。
- 把这条实现线作为 regression hardening change 归档，不新增 endpoint、不扩新 transport。

## Capabilities

### New Capabilities
- `tdx-worker-bridge-http-control-plane`: worker bridge HTTP control-plane contract，包括 `Authorization + master_allowlist` 边界、`watch/status` 的 verbatim controller projection、`health`/active-run fallback 行为，以及 master-side registry/client 的 transport failure normalization。

### Modified Capabilities
- `tdx-api-cli-entry`: CLI `bridge` 远程读入口需要稳定透传 registry/client payload，并对 bridge/client failure 保持统一 JSON failure 语义。

## Impact

- Affected code:
  - `tdxquant/bridge_http.py`
  - `tdxquant/subscription_watch_background.py`
  - `tdxquant/bridge_registry.py`
  - `tdxquant/cli.py`
  - bridge/control-plane tests and docs
- Affected APIs:
  - worker bridge `/bridge/v1/health`
  - worker bridge `/bridge/v1/watch/status|list|artifacts|events|logs`
  - master-side `run_bridge_*` helpers
  - CLI `bridge health/watch-*`
- No new endpoint, transport, worker discovery, or scheduling layer is introduced.
