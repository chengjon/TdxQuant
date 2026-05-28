# provider replay status supervision rollup design

## Context

`summary_view.status_summary` is the compact rollup intended for scanning. It already includes provider identity, replay source, probe health, lifecycle control, lifecycle ownership, and lifecycle operation counts. With `lifecycle.supervision_summary` now available, the compact rollup should expose a few stable supervision scalars so callers do not need to inspect the nested detailed object to learn that no supervisor exists.

## Design

Read `lifecycle.supervision_summary` from the detailed status payload and add these `summary_view.status_summary` fields:

- `lifecycle_supervision_status`
- `lifecycle_supervisor_configured`
- `lifecycle_desired_state`
- `lifecycle_observed_state`
- `lifecycle_process_identity_status`

The fields are copied from the supervision summary. They are intentionally scalar and read-only. They do not change `control_supported`, `managed_operation_count`, probe behavior, or the nested lifecycle summary.

## Boundaries

- This change only adds a compact summary projection.
- It does not implement supervisor loops, daemon start/stop, restart, pid tracking, statefile tracking, process ownership, scheduler behavior, retry timers, or automatic recovery.
- It does not infer ownership from configured ports or HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.
