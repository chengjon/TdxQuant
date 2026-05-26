# Add subscription governance sample counts to summary views

## Why

The compact subscription `watch-status` summary view already exposes bounded `governance.reason_samples` and `governance.action_samples` plus their limits and truncation flags. Consumers can infer the visible sample lengths, but they currently have to parse arrays to distinguish the displayed sample size from the full `reason_count` / `action_count` rollups.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. Adding explicit sample counts keeps the view machine-readable while preserving the reduced summary boundary.

## What Changes

- Add read-only `governance.reason_sample_count` to HTTP and CLI subscription watch-status summary views when reason samples are projected.
- Add read-only `governance.action_sample_count` to HTTP and CLI subscription watch-status summary views when action samples are projected.
- Keep full `governance.reasons` and `governance.actions` out of summary views.
- Do not change reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/bridge_http.py` and `tdxquant/cli.py` summary projection only.
- Adds focused HTTP and CLI summary-view assertions.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.
