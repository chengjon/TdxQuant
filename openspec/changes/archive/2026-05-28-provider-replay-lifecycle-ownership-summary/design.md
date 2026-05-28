# provider replay lifecycle ownership summary design

## Context

Current provider replay lifecycle status is intentionally non-owning. It can describe foreground replay configuration and read-only probes, but it does not create or read ownership metadata. The newly archived lifecycle design says future lifecycle status must separate ownership from reachability.

## Design

Add `lifecycle.ownership_summary` with a stable read-only shape:

- `ownership_status`: currently `not_managed`
- `owned_process`: currently `false`
- `state_file_present`: currently `false`
- `state_file_stale`: currently `false`
- `control_allowed`: currently `false`
- `status_source`: currently `configured_boundary`
- `boundary`: `no_lifecycle_ownership; read_only_status`

The object is not computed from the operating system or network. It is a current-state boundary declaration and future compatibility point for explicit lifecycle control.

The CLI summary view should include a deep copy of this object under `summary_view.lifecycle.ownership_summary`. No new CLI command is added.

## Boundaries

- This change is read-only status metadata.
- It does not write or read pidfiles/statefiles.
- It does not start, stop, restart, daemonize, schedule, supervise, or back off provider replay.
- It does not probe process tables or infer ownership from ports or HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.

