# provider replay lifecycle control plan design

## Context

Provider replay remains a foreground replay service. The current lifecycle operation summary marks `start`, `stop`, `restart`, and `backoff` as blocked. Operators can inspect status, but they cannot request a non-executing control plan for one operation.

## Design

Add CLI parser support:

```text
provider-replay lifecycle-plan --config <path> --operation start|stop|restart|backoff [--view detailed|summary]
```

The handler loads config, builds the same read-only status payload, and derives a plan from `lifecycle.operation_summary.operations`.

Detailed plan fields:

- `operation`
- `execution_mode`: `non_executing_lifecycle_plan`
- `operation_status`: current operation status, currently `blocked`
- `implemented`: current implementation flag, currently `false`
- `dispatch_executed`: `false`
- `control_allowed`: `false`
- `lifecycle_control_status`
- `blocking_reason`
- `ownership_required`
- `operator_action_required`
- `statefile_configured`
- `supervision_status`
- `required_capabilities`
- `boundary`

Summary view fields:

- `mode`: `lifecycle-plan`
- `provider_id`
- `operation`
- `operation_status`
- `dispatch_executed`
- `control_allowed`
- `lifecycle_control_status`
- `blocking_reason`
- `statefile_configured`
- `supervision_status`
- `boundary`

## Boundaries

- The command is read-only and non-executing.
- It does not start, stop, restart, daemonize, supervise, probe runtime, inspect processes, infer ownership from ports, or read/write statefiles.
- It does not prove readiness, live provider availability, broker readiness, workflow readiness, endpoint coverage, or write capability.
- Future executable lifecycle control still requires explicit implementation, ownership proof, state schema, stale detection policy, and opt-in control semantics.
