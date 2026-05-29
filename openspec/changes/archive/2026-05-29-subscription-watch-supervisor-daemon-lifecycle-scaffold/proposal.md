## Why

B-16/E-09 now has explicit restart, backoff, supervisor tick, bounded foreground supervisor run, and observation hardening, but it still lacks a local lifecycle scaffold for running the supervisor loop as an owned process. A small controller-local daemon lifecycle layer is the next prerequisite before any restart/backoff policy can be safely enabled.

## What Changes

- Add separate supervisor daemon state, pid, and lock paths under the subscription-watch run root.
- Add local controller methods to start, status-check, and stop an explicit opt-in supervisor daemon process.
- Add a real daemon runner module that repeatedly calls the existing bounded `supervisor_run()`.
- Require statefile owner-token matching before stop can signal the owned supervisor pid.
- Preserve the boundary: no default daemon start, no HTTP/CLI/registry entrypoint, no catalog/task integration, no provider readiness claim, and no automatic policy attached to watch status/restart/event streams.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: add controller-local supervisor daemon lifecycle scaffold over existing bounded supervisor run.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/subscription_watch_supervisor_daemon.py`.
- Affected tests: `tests/test_subscription_watch_background.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, background-control OpenSpec.
