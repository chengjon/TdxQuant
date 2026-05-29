## ADDED Requirements

### Requirement: Worker bridge SHALL expose bounded supervisor run

The worker bridge SHALL expose a bounded foreground supervisor-run control operation.

#### Scenario: Caller posts supervisor run

- **WHEN** a caller posts to `POST /bridge/v1/watch/supervisor-run` with `max_ticks`, optional `interval_seconds`, and optional `reason`
- **THEN** the bridge MUST dispatch to the background controller supervisor run
- **AND** it MUST return the controller result through the normal bridge control envelope
- **AND** it MUST NOT execute task/report/trade/workflow steps.

#### Scenario: Registry and CLI dispatch supervisor run

- **WHEN** a caller invokes the registry helper or `bridge watch-supervisor-run`
- **THEN** the request MUST use the supervisor-run control route
- **AND** it MUST pass only `max_ticks`, `interval_seconds`, and `reason`
- **AND** it MUST preserve the foreground bounded boundary.

