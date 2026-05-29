## ADDED Requirements

### Requirement: Subscription watch restart SHALL persist latest successful restart observation

The worker-local subscription-watch background controller SHALL persist a compact observation after an explicit restart successfully replaces an active run.

#### Scenario: Explicit restart records replacement observation

- **WHEN** a caller explicitly restarts an active background run with a valid persisted `start_request`
- **THEN** the controller MUST include `last_restart_observation` in the restart result
- **AND** it MUST persist the same observation on the replacement active control state when that state matches the new run id
- **AND** the observation MUST include stable fields for `schema_version`, `status`, `previous_run_id`, `new_run_id`, `reason`, `stop_state`, `start_state`, `start_request_summary`, and `boundary`
- **AND** the observation MUST NOT include raw stop result, raw start result, full start request, process command line, logs, HTTP health, or event-stream data.

#### Scenario: Failed restart does not record success observation

- **WHEN** the stop or replacement start phase fails during explicit restart
- **THEN** the controller MUST NOT persist a successful `last_restart_observation`
- **AND** it MUST NOT schedule automatic restart, retry, backoff, or supervisor recovery.
