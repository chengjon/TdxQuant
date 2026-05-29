## Why

Subscription long-run status now exposes summary, diagnostics, and lifecycle readiness signals. Operators still need a single read-only checklist view that turns those signals into a compact manual runbook without requiring them to inspect several nested objects.

## What Changes

- Add a `runbook` watch-status view for CLI and HTTP.
- Derive the runbook from the existing summary/diagnostics payloads, including lifecycle readiness.
- Include stable checklist metadata: overall runbook decision, check counts, blocking checks, manual-review flag, and compact operator checks.
- Keep the view strictly read-only: no lifecycle control, no restart preflight call, no process signal, no supervisor scheduling.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: add a read-only operator runbook view to the existing watch-status view contract.

## Impact

- Code: `tdxquant/subscription_watch_status_diagnostics.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`.
- Tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]` with explicit read-only runbook evidence and boundary.
