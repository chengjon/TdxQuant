## Why

B-16/E-09 subscription long-run governance already exposes advisory actions, action counts, action names, reason rollups, and a legacy `severity` field in `governance.action_summary`. The legacy field represents the first advisory action severity, but compact consumers must infer that from the name. An explicit `primary_severity` keeps the summary self-describing while preserving backward compatibility.

## What Changes

- Add additive `status_summary.governance.action_summary.primary_severity`.
- Derive the value from the first advisory governance action severity, matching the existing `severity` value.
- Preserve the field through detailed status, HTTP summary view, and CLI summary view.

## Impact

- Code: `tdxquant/subscription_watch_background.py`.
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry: update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No reconnect, backoff, restart, lifecycle, HTTP, SSE, event-stream, or action execution behavior changes.
