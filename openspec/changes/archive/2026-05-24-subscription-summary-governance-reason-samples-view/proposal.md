# Change: Subscription Summary Governance Reason Samples View

## Why

`FUNCTION_TREE.md` records B-16/E-09 subscription long-run governance as partially implemented. The HTTP and CLI summary views already expose a compact `governance.reason_count`, but readers still cannot see any representative reason in the reduced summary payload without switching to the detailed payload.

A bounded reason-sample projection makes the summary view more useful as registry evidence while preserving the existing boundary: it remains advisory-only, read-only, and does not expose the full detailed `governance.reasons` list or perform reconnect/backoff/restart/lifecycle actions.

## What Changes

- Add bounded `governance.reason_samples` to HTTP and CLI subscription watch summary views.
- Add `governance.reason_sample_limit` and `governance.reason_sample_truncated` so callers can tell whether samples are complete.
- Cover HTTP and CLI summary view behavior with tests.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Non-Goals

- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior changes.
- No full `governance.reasons` or `governance.actions` projection in summary view.
- No production supervisor or daemon management.

