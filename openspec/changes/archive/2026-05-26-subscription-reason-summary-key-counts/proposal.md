# Add subscription reason summary key counts

## Why

Subscription long-run governance already exposes `governance.reason_summary.source_counts` and `governance.reason_summary.reason_code_counts`. Those maps are useful for diagnostics, but callers still need to derive how many distinct reason sources or reason codes are present.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. Adding explicit key counts keeps the existing reason rollup easier to scan without making it an execution policy or lifecycle trigger.

## What Changes

- Add read-only `status_summary.governance.reason_summary.source_key_count` derived from the number of keys in `source_counts`.
- Add read-only `status_summary.governance.reason_summary.reason_code_key_count` derived from the number of keys in `reason_code_counts`.
- Preserve existing `primary_reason`, `primary_source`, `primary_reason_source`, `source_counts`, and `reason_code_counts`.
- Do not expose full reasons in summary view and do not change reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/subscription_watch_background.py` reason-summary construction.
- Adds focused subscription-watch status summary assertions and preserves HTTP/CLI summary projection expectations.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

