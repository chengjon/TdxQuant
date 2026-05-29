## Why

`status_summary.lifecycle_readiness` now gives a compact read-only gate for manual lifecycle control, but operators using `watch-status --view diagnostics` still need to inspect `status_summary` separately. Diagnostics should surface the same readiness gate alongside the existing restartability, backoff, statefile ownership, and supervisor daemon diagnostics.

## What Changes

- Add a read-only `diagnostics.lifecycle_readiness` projection to CLI and HTTP diagnostics view.
- Derive the diagnostics projection only from the already-built summary payload, primarily `status_summary.lifecycle_readiness`.
- Preserve stable readiness fields: `ready`, `decision`, `reason_codes`, input status summaries, and boundary.
- Keep the diagnostics view non-executing: no lifecycle control, no restart preflight call, no process signal, no supervisor scheduling.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: diagnostics view now exposes the existing lifecycle readiness summary as a compact read-only diagnostics object.

## Impact

- Code: `tdxquant/subscription_watch_status_diagnostics.py`.
- Tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]` with explicit read-only diagnostics evidence and boundary.
