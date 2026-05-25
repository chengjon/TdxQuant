## Why

Subscription long-run governance summaries already expose compact advisory action rollups, including counts by severity and action name. Operators can see how many actions exist and which action names are suggested, but the compact action summary does not show which governance source caused those actions without inspecting full `governance.actions`.

Adding an action reason-source count keeps the summary view compact while making it clear whether advisory actions are driven by heartbeat, watermark, reconnect, or overall status reasons.

## What Changes

- Add `governance.action_summary.reason_source_counts` to subscription long-run status summaries.
- Derive the counts from existing advisory action `reason` values using the same reason-source normalization as `governance.reason_source_counts`.
- Preserve existing observe/manual-review decisions, action generation, full detailed payloads, summary-view hiding of full action lists, and reconnect/backoff/restart lifecycle behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`
- Affected summary projections: CLI and HTTP watch-status summary views, through existing `action_summary` projection
- Affected specs: `tdx-subscription-long-run-status-summary`
- Verification: focused subscription background, bridge HTTP, and CLI tests plus OpenSpec and FUNCTION_TREE registry validation
