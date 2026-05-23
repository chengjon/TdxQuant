## Why

`status_summary.governance.actions` already exposes advisory action hints, but consumers must scan the list to answer basic questions such as whether any action is present and what the first operator-facing action is. A compact rollup keeps CLI/HTTP consumers simple while preserving the existing advisory-only boundary.

## What Changes

- Add `governance.action_summary` to subscription watch status summaries.
- Derive the rollup from existing `governance.actions`.
- Keep reconnect, backoff, restart, lifecycle, HTTP, SSE, and event-stream behavior unchanged.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: expose an additive advisory `governance.action_summary` rollup.

## Impact

- Runtime code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
