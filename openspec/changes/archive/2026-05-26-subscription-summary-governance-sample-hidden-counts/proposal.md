# Add subscription governance hidden sample counts to summary views

## Why

The compact subscription `watch-status` summary view exposes full governance list counts, bounded visible samples, sample limits, and truncation flags. Consumers can tell that samples were truncated, but they still need to subtract visible sample counts from full counts to know how many reasons or actions are hidden behind the compact boundary.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. Adding explicit hidden sample counts keeps the summary view machine-readable while preserving the existing reduced payload boundary.

## What Changes

- Add read-only `governance.reason_sample_hidden_count` to HTTP and CLI subscription watch-status summary views when reason samples are projected.
- Add read-only `governance.action_sample_hidden_count` to HTTP and CLI subscription watch-status summary views when action samples are projected.
- Derive each hidden count from the full list count minus the bounded visible sample count.
- Keep full `governance.reasons` and `governance.actions` out of summary views.
- Do not change reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches the bridge watch-status summary projection only.
- Adds focused HTTP and CLI summary-view assertions.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.
