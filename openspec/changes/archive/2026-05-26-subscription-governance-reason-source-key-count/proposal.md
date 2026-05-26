# Add subscription governance reason source key count

## Why

Subscription governance exposes top-level `governance.reason_source_counts` as a compact source distribution for advisory reasons. Consumers can derive the number of distinct reason sources, but summary readers currently have to inspect the map.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. A top-level read-only key count makes the existing reason-source rollup easier to scan without changing advisory behavior.

## What Changes

- Add read-only `status_summary.governance.reason_source_key_count` derived from the number of keys in `governance.reason_source_counts`.
- Preserve `governance.reason_count`, `governance.reason_source_counts`, and `governance.reason_summary`.
- Do not expose full reasons in compact summary view.
- Do not change staleness evaluation, governance decisions, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/subscription_watch_background.py` top-level governance summary construction.
- Adds focused subscription-watch status summary assertions and preserves HTTP/CLI summary projection expectations.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

