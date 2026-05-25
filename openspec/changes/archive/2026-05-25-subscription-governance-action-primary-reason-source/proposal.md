## Why

Subscription governance summaries expose advisory action counts, names, severities, reason-source counts, and reason-code counts. Consumers can infer the source of the primary action reason from `primary_reason`, but the compact action summary does not expose that source directly.

Adding `action_summary.primary_reason_source` keeps B-16/E-09 evidence compact and read-only while making the first advisory action's origin explicit.

## What Changes

- Add `governance.action_summary.primary_reason_source` to subscription long-run status summaries.
- Derive the field from the existing first advisory action reason using the existing reason-source parser.
- Return `null` when there is no primary action reason.
- Preserve advisory-only behavior: no reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior changes.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-subscription-long-run-status-summary`
- Verification: focused subscription/API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
