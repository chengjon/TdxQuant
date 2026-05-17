## Why

The subscription runtime already exposes `subscribe_hq`, `unsubscribe_hq`, and `get_subscribe_hq_stock_list` through persistent sessions, foreground `subscription-watch`, and bridge control-plane flows. The remaining gap is a small query-style one-shot CLI surface for callers that need to invoke those runtime subscription methods once without starting a watch run or background worker.

## What Changes

- Add one-shot runtime API wrappers for subscription subscribe, unsubscribe, and subscribed-stock-list operations.
- Add nested `api subscription-subscribe`, `api subscription-unsubscribe`, and `api subscription-list` CLI commands.
- Return machine-readable one-shot metadata that distinguishes these commands from `subscription-watch` runs.
- Preserve existing `subscription-watch` artifact contracts, bridge control-plane semantics, and long-running governance scope.
- Update `FUNCTION_TREE.md` from designed/pending to partially implemented with explicit evidence and boundaries.

## Capabilities

### New Capabilities
- `tdx-subscription-query-one-shot-cli`: Covers query-style one-shot CLI operations for `subscribe_hq`, `unsubscribe_hq`, and `get_subscribe_hq_stock_list`.

### Modified Capabilities
- `tdx-api-cli-entry`: Adds dedicated API CLI entries for one-shot subscription runtime operations.

## Impact

- Affected code: `tdxquant/api/bridge.py`, `tdxquant/api/runtime.py`, `tdxquant/cli.py`, and focused API/CLI tests.
- Affected docs/specs: OpenSpec specs and `FUNCTION_TREE.md`.
- No changes to `subscription-watch` run artifacts, worker bridge control plane, provider SSE transport, reconnect/backoff governance, or replay fixture semantics.
