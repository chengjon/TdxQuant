## ADDED Requirements

### Requirement: Worker bridge SHALL expose explicit supervisor daemon controls

The worker bridge HTTP control plane SHALL expose explicit operator-triggered supervisor daemon status, start, and stop controls without changing default watch status, event, stream, start, stop, restart, supervisor tick, or supervisor run behavior.

#### Scenario: Caller reads supervisor daemon status

- **WHEN** a caller invokes `GET /bridge/v1/watch/supervisor-daemon/status`
- **THEN** the bridge MUST dispatch to the background controller supervisor daemon status operation
- **AND** the response MUST preserve the controller supervisor daemon status envelope
- **AND** the bridge MUST NOT start, stop, restart, run supervisor ticks, run supervisor loops, schedule backoff, or execute task/report/trade/workflow/catalog steps.

#### Scenario: Caller starts supervisor daemon explicitly

- **WHEN** a caller invokes `POST /bridge/v1/watch/supervisor-daemon/start` with `max_ticks`, optional `interval_seconds`, optional `loop_sleep_seconds`, optional `reason`, and optional `owner_token`
- **THEN** the bridge MUST dispatch to the background controller supervisor daemon start operation
- **AND** the response MUST preserve the controller supervisor daemon start envelope
- **AND** the bridge MUST NOT infer daemon settings from status files, provider state, broker state, port ownership, catalog entries, task presets, reports, trades, workflows, or logs.

#### Scenario: Caller stops supervisor daemon explicitly

- **WHEN** a caller invokes `POST /bridge/v1/watch/supervisor-daemon/stop` with `owner_token` and optional `reason`
- **THEN** the bridge MUST dispatch to the background controller supervisor daemon stop operation
- **AND** the response MUST preserve the controller supervisor daemon stop envelope
- **AND** the bridge MUST NOT signal any process directly outside the controller ownership check.

#### Scenario: Registry dispatches supervisor daemon controls

- **WHEN** a caller invokes the bridge registry helpers for supervisor daemon status, start, or stop
- **THEN** the helpers MUST use the matching supervisor daemon control route
- **AND** they MUST NOT call restart, restart-preflight, supervisor-tick, supervisor-run, start, stop, status, events, logs, task, report, trade, workflow, or catalog routes.
