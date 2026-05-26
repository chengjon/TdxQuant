# Add subscription evaluation status key counts

## Why

Subscription long-run governance already exposes `evaluation_summary.component_status_counts` and `evaluation_summary.evaluated_status_counts`. Operators and automation can inspect the maps, but they still have to derive how many distinct status categories are present.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. Adding read-only key counts makes the existing status-count maps easier to scan while preserving the advisory-only boundary.

## What Changes

- Add read-only `status_summary.governance.evaluation_summary.component_status_key_count` derived from the number of keys in `component_status_counts`.
- Add read-only `status_summary.governance.evaluation_summary.evaluated_status_key_count` derived from the number of keys in `evaluated_status_counts`.
- Preserve the existing component lists, component counts, and status-count maps.
- Do not change staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/subscription_watch_background.py` evaluation-summary construction.
- Adds focused subscription-watch status summary assertions, with HTTP/CLI expected payloads updated only if exact projection tests require the additive fields.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

