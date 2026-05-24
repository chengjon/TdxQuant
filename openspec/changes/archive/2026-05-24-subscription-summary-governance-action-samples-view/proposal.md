# Change: Subscription Summary Governance Action Samples View

## Why

`FUNCTION_TREE.md` records B-16/E-09 subscription long-run governance as partially implemented. The HTTP and CLI summary views expose `governance.action_summary` and bounded reason samples, but a reader still cannot see representative advisory actions without switching to the detailed payload.

A bounded action-sample projection makes the reduced summary more operationally useful while preserving the existing boundary: it remains advisory-only, read-only, and does not expose the full detailed `governance.actions` list or perform reconnect/backoff/restart/lifecycle actions.

## What Changes

- Add bounded `governance.action_samples` to HTTP and CLI subscription watch summary views.
- Add `governance.action_sample_limit` and `governance.action_sample_truncated` so callers can tell whether samples are complete.
- Keep action samples compact by omitting full action descriptions.
- Cover HTTP and CLI summary view behavior with focused tests.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Non-Goals

- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior changes.
- No full `governance.actions` projection in summary view.
- No production supervisor or daemon management.

