# subscription decision presence flags

## Why

`bridge watch-status --view summary` and bridge HTTP `watch/status?view=summary` already expose a compact advisory `governance.decision_summary`, but callers still need to compare numeric counts to answer the common read-only question: did this snapshot contain any advisory reasons or actions?

Adding stable boolean presence flags keeps summary consumers from re-implementing that count logic while staying inside the current B-16/E-09 boundary: discovery and status projection only, not reconnect/backoff execution or long-running process governance.

## What Changes

- Add `governance.decision_summary.has_reasons` derived from existing `governance.reason_count`.
- Add `governance.decision_summary.has_actions` derived from existing `governance.action_count`.
- Preserve the same fields in both HTTP and CLI watch-status summary views.
- Cover the fields with focused tests and update `FUNCTION_TREE.md` evidence/boundary text.

## Impact

- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence.
- No reconnect/backoff behavior, lifecycle management, HTTP control actions, SSE/event-stream behavior, task/report/trade execution, workflow execution, or readiness claim is added.

