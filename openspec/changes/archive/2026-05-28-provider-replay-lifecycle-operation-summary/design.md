# provider replay lifecycle operation summary design

## Context

`lifecycle.control_summary` exposes aggregate blocked-control posture. A per-operation matrix is useful because future lifecycle work can enable operations independently without changing the high-level shape.

## Design

Add `lifecycle.operation_summary` with this current shape:

- `operation_count`: `4`
- `blocked_count`: `4`
- `available_count`: `0`
- `operations`: a list of four entries for `start`, `stop`, `restart`, and `backoff`

Each operation entry contains:

- `operation`
- `status`: currently `blocked`
- `blocking_reason`: `lifecycle_control_not_implemented`
- `ownership_required`
- `operator_action_required`
- `implemented`: `false`

For current semantics:

- `start`: ownership is not required yet because there is no owned process to prove before initial start, but explicit operator action is required.
- `stop`: ownership proof is required.
- `restart`: ownership proof is required.
- `backoff`: ownership proof and operator opt-in are required.

The object is static for the current implementation and is copied into the CLI summary view. No lifecycle command is added.

## Boundaries

- This change is read-only status metadata.
- It does not implement start, stop, restart, backoff, scheduler, or supervisor behavior.
- It does not read/write pidfiles or statefiles.
- It does not scan process tables or infer ownership from ports/HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.

