## Why

B-16/E-09 subscription governance reason summaries already expose `primary_source`, while action summaries use the more explicit `primary_reason_source`. Compact consumers that handle both reason and action rollups need to special-case the shorter reason field name. An additive `primary_reason_source` alias keeps the reason summary self-describing without breaking existing `primary_source` readers.

## What Changes

- Add additive `status_summary.governance.reason_summary.primary_reason_source`.
- Derive it from the existing primary reason source, matching `primary_source`.
- Preserve the field through detailed status, HTTP summary view, and CLI summary view.

## Impact

- Code: `tdxquant/subscription_watch_background.py`.
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry: update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No reconnect, backoff, restart, lifecycle, HTTP, SSE, event-stream, or action execution behavior changes.
