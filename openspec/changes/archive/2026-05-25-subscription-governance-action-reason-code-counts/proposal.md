## Why

Subscription governance summaries expose full reason-code counts for `governance.reasons`, and now expose action reason-source counts inside `governance.action_summary`. Compact action consumers can identify action source families, but cannot distinguish the exact advisory reason strings attached to actions without reading the full `governance.actions` list.

Adding action reason-code counts keeps summary views compact and avoids exposing full action payloads while preserving an exact deterministic rollup of advisory action reasons.

## What Changes

- Add `governance.action_summary.reason_code_counts` to subscription long-run status summaries.
- Derive the counts from existing advisory action `reason` values.
- Preserve existing observe/manual-review decisions, reason generation, action generation, summary-view hiding of full action lists, and reconnect/backoff/restart lifecycle behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`
- Affected summary projections: CLI and HTTP watch-status summary views, through existing `action_summary` projection
- Affected specs: `tdx-subscription-long-run-status-summary`
- Verification: focused subscription background, bridge HTTP, and CLI tests plus OpenSpec and FUNCTION_TREE registry validation
