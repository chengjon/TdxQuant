# Change: Provider Replay Status Lifecycle Support Summary View

## Why

`FUNCTION_TREE.md` records E-06 `daemon fake provider` as partially implemented. The provider replay status summary already exposes lifecycle fields such as `start_stop_managed=false`, `daemon_managed=false`, and `restart_policy=not_managed`, but readers still need to interpret several fields to understand whether the replay provider offers lifecycle control.

A derived lifecycle support summary makes the boundary harder to misread: the replay provider is foreground/replay-only and does not support daemon, scheduler, restart, or start/stop control.

## What Changes

- Add derived `summary_view.lifecycle.control_supported`.
- Add derived `summary_view.lifecycle.managed_operation_count`.
- Cover the fields in provider replay CLI summary tests.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Non-Goals

- No start, stop, restart, scheduler, daemon, or supervisor implementation.
- No change to detailed provider replay status payload.
- No live market session or write capability.

