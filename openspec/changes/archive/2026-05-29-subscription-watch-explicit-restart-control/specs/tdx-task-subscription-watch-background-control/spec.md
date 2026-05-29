## ADDED Requirements

### Requirement: Subscription watch background control SHALL expose explicit restart

The worker-local subscription-watch background controller SHALL expose an explicit restart operation that reuses the active run's persisted start request and existing stop/start behavior.

#### Scenario: Operator restarts active run from persisted start request

- **WHEN** a caller explicitly restarts an active background run that has a valid persisted `start_request`
- **THEN** the controller MUST stop the current owned run
- **AND** it MUST start a replacement run using the persisted `stock_list`, `max_events`, `max_seconds`, and `poll_interval`
- **AND** the result MUST include `previous_run_id`, `new_run_id`, `stop_result`, `start_result`, and `start_request`
- **AND** the restart MUST NOT infer start parameters from logs, process args, port state, HTTP health, or event-stream data.

#### Scenario: Restart does not proceed without restartable metadata

- **WHEN** a caller explicitly restarts but the active control state has no valid `start_request`
- **THEN** the controller MUST return a stable `MISSING_START_REQUEST` failure
- **AND** it MUST NOT stop or start a process.

#### Scenario: Stop failure prevents replacement start

- **WHEN** the stop phase fails during explicit restart
- **THEN** the controller MUST return the stop failure
- **AND** it MUST NOT start a replacement run.
