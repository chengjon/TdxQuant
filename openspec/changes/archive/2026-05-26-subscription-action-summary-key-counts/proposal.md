# Add subscription action summary key counts

## Why

Subscription long-run governance already exposes `governance.action_summary` count maps for advisory action severity, action name, reason source, and reason code. Consumers can derive distinct key counts from those maps, but repeated derivation makes compact status inspection noisier.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. Adding explicit key counts keeps the advisory action rollup machine-readable without turning advisory actions into an execution queue or lifecycle policy.

## What Changes

- Add read-only `severity_key_count`, `action_name_key_count`, `reason_source_key_count`, and `reason_code_key_count` to `status_summary.governance.action_summary`.
- Derive each field from the corresponding existing count map.
- Preserve existing action summary fields and count maps.
- Do not execute actions or change reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/subscription_watch_background.py` action-summary construction.
- Adds focused subscription-watch status summary assertions and preserves HTTP/CLI summary projection expectations.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

