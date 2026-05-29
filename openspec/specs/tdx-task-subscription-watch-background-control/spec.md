# tdx-task-subscription-watch-background-control Specification

## Purpose
TBD - created by archiving change subscription-watch-background-control. Update Purpose after archive.
## Requirements
### Requirement: Subscription watch background control SHALL enforce single-active lifecycle semantics
The system SHALL provide a worker-local background control layer for `subscription-watch` that manages at most one active watch run at a time and governs `start` / `stop` behavior through file-backed state and process ownership.

#### Scenario: Start request creates a new active background run when idle
- **WHEN** a caller starts `subscription-watch` background control while the worker has no active run
- **THEN** the system MUST create a fresh `run_id`, persist `active.json` and `pid` ownership state, and transition the run into `starting` or `running`

#### Scenario: Same idempotency key replays the current active run
- **WHEN** a caller retries `start` with the same `idempotency_key` while the current active run is still in `starting`, `running`, or `stopping`
- **THEN** the system MUST return the same active `run_id` instead of creating a second background run

#### Scenario: Different start request is rejected while a run is active
- **WHEN** a caller sends a new `start` request while another background run is active and the request does not qualify for same-`idempotency_key` replay
- **THEN** the system MUST reject the request with an `ALREADY_RUNNING`-style control error

#### Scenario: Start request fails when runner does not leave startup state in time
- **WHEN** a caller starts `subscription-watch` background control and the runner does not reach a stable post-start state within the configured startup timeout
- **THEN** the system MUST return a stable failed result instead of reporting the run as successfully started
- **AND** the failure MUST preserve the active run details needed for operator diagnosis

#### Scenario: Stop request is a noop when no run is active
- **WHEN** a caller sends `stop` and the worker has no run in `starting`, `running`, or `stopping`
- **THEN** the system MUST return a successful noop result instead of raising a transport-level failure

### Requirement: Subscription watch background control SHALL reconcile stale local process state
The system SHALL normalize worker-local control state by reconciling `active.json`, `pid`, and process liveness before reporting status or deciding whether a run is still active.

#### Scenario: Missing or mismatched owned pid marks an active run as stale
- **WHEN** background control finds `active.json` claiming `starting`, `running`, or `stopping` but the owned `pid` file is missing, mismatched, or no longer alive
- **THEN** the system MUST normalize the run to a terminal state instead of continuing to report it as active
- **AND** the normalization reason MUST record stale-process semantics

#### Scenario: Terminal runs release owned pid state
- **WHEN** background control encounters a run already in `completed`, `failed`, or `stopped`
- **THEN** the system MUST remove stale owned pid state and keep the terminal payload readable through `active.json`

### Requirement: Subscription watch background control SHALL expose stable status and list read models
The system SHALL expose worker-local read models for current background state and recent run summaries so transport layers do not have to reconstruct lifecycle semantics directly from scattered files.

#### Scenario: Status view returns active control plus current run status
- **WHEN** a caller asks for background watch status while a run is active
- **THEN** the system MUST return the active control payload and the current run `status.json` payload for that `run_id`

#### Scenario: Status view returns explicit empty watch status when no run is active
- **WHEN** a caller asks for background watch status and no run is active
- **THEN** the system MUST return a stable control payload showing no active run
- **AND** the watch-status view MUST remain explicitly empty instead of silently falling back to the last historical run

#### Scenario: List view returns active and recent terminal summaries
- **WHEN** a caller asks for the background watch list view
- **THEN** the system MUST return the current `active` view plus `last_completed` and `last_failed` summaries when available
- **AND** the system MUST NOT require a full historical index in the first version

### Requirement: Subscription watch background control SHALL derive diagnostics from canonical run artifacts
The system SHALL derive artifact paths and diagnostic reads from the canonical `subscription-watch` run directory contract instead of inventing a second background-only artifact format.

#### Scenario: Artifact view exposes canonical run bundle paths
- **WHEN** a caller requests artifacts for the active run or an explicit `run_id`
- **THEN** the system MUST return canonical paths for `manifest.json`, `status.json`, `summary.json`, `events.jsonl`, `events.csv`, and `runner.log`

#### Scenario: Events and logs views read from canonical run artifacts
- **WHEN** a caller requests recent events or logs for the active run or an explicit `run_id`
- **THEN** the system MUST tail `events.jsonl` and `runner.log` from the canonical run directory for that run
- **AND** the system MUST return machine-readable event rows and log lines without opening a live runtime session

### Requirement: Subscription watch background control SHALL reconcile reconnecting and degraded as active-process states
The system SHALL extend worker-local background-control reconciliation so resilience runtime states are interpreted consistently with process ownership and liveness.

#### Scenario: Reconnecting or degraded process loss becomes stale-process failure
- **WHEN** background control finds `active.json` in `reconnecting` or `degraded` but the owned pid is missing, mismatched, or no longer alive
- **THEN** the system MUST normalize the run to `failed`
- **AND** the normalization reason MUST be `stale_process_state`

#### Scenario: Stopping process loss remains a stopped terminal normalization
- **WHEN** background control finds `active.json` in `stopping` but the owned pid is missing or dead
- **THEN** the system MUST normalize the run to `stopped`

### Requirement: Subscription watch background control SHALL expose terminal resilience cleanup coherently
The system SHALL keep terminal background-control views coherent with the foreground resilience contract when a run leaves reconnect/degraded states.

#### Scenario: Terminal status clears stale reconnect schedule
- **WHEN** a `subscription-watch` run reaches `completed`, `interrupted`, or `failed`
- **THEN** the persisted terminal `status.json` MUST clear `next_reconnect_at`
- **AND** background and bridge readers MUST NOT expose a future reconnect probe time for that terminal run

### Requirement: Background watch status SHALL include status summary
The background subscription-watch control plane SHALL include a stable `status_summary` object in watch status responses.

#### Scenario: Caller receives bridge watch status
- **WHEN** a caller requests background watch status through the bridge control plane
- **THEN** the response MUST include raw `control`
- **AND** the response MUST include raw `watch_status`
- **AND** the response MUST include `status_summary`
- **AND** adding `status_summary` MUST NOT change watch start, stop, list, artifact, event, or log behavior

### Requirement: Subscription watch background control SHALL persist start request metadata

The worker-local subscription-watch background controller SHALL persist the normalized start request in active control state when a new background run is started.

#### Scenario: Start request records restartable request metadata

- **WHEN** a caller starts `subscription-watch` background control while the worker has no active run
- **THEN** the persisted active control state MUST include `start_request.stock_list`
- **AND** it MUST include `start_request.max_events`, `start_request.max_seconds`, and `start_request.poll_interval`
- **AND** these fields MUST match the normalized request used to spawn the runner
- **AND** the change MUST NOT start a second process, restart a process, schedule backoff, supervise a process, or change stop behavior.

#### Scenario: Same idempotency replay preserves start request metadata

- **WHEN** a caller retries `start` with the same `idempotency_key` while the current active run is still active
- **THEN** the replayed result MUST include the persisted `start_request`
- **AND** the replay MUST NOT rewrite the active start request from the retry payload.

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

### Requirement: Subscription watch background control SHALL expose restart preflight

The worker-local subscription-watch background controller SHALL expose a read-only restart preflight view derived from reconciled active state and persisted `start_request`.

#### Scenario: Active run with valid start request is restartable

- **WHEN** a caller requests restart preflight for an active background run with a valid persisted `start_request`
- **THEN** the result MUST report `ready=true`
- **AND** it MUST include `decision=ready`, `run_id`, `state`, and a compact `start_request_summary`
- **AND** it MUST NOT stop, start, signal, write state files, schedule backoff, or supervise a process.

#### Scenario: Missing active run blocks restart preflight

- **WHEN** a caller requests restart preflight without an active background run
- **THEN** the result MUST report `ready=false`
- **AND** it MUST include stable reason code `NO_ACTIVE_RUN`
- **AND** it MUST remain read-only.

#### Scenario: Missing or invalid start request blocks restart preflight

- **WHEN** a caller requests restart preflight for an active background run without a valid persisted `start_request`
- **THEN** the result MUST report `ready=false`
- **AND** it MUST include stable reason code `MISSING_START_REQUEST` or `INVALID_START_REQUEST`
- **AND** it MUST remain read-only.

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

### Requirement: Subscription watch restart SHALL enforce bounded backoff after replacement start failure

The worker-local subscription-watch background controller SHALL record and enforce a bounded explicit-restart backoff when replacement start fails after the prior active run has been stopped.

#### Scenario: Replacement start failure records restart backoff

- **WHEN** explicit restart stops an active run but replacement `start()` fails
- **THEN** the controller MUST persist a compact `restart_backoff` object in control state
- **AND** the persisted control state MUST include `state` set to `restart_backoff`, `active` set to `false`, and stable retry metadata
- **AND** the restart failure response MUST include the same compact backoff metadata
- **AND** the backoff metadata MUST NOT include raw logs, command line, full start request, HTTP health, event-stream data, or provider credentials.

#### Scenario: Active restart backoff rejects repeated restart

- **WHEN** explicit restart is requested while persisted `restart_backoff.retry_after_at` is still in the future
- **THEN** the controller MUST return stable `RESTART_BACKOFF_ACTIVE`
- **AND** it MUST include retry metadata and `BACKOFF_ACTIVE` reason code
- **AND** it MUST NOT call stop, start, restart-preflight, schedule automatic retry, or run a supervisor loop.

#### Scenario: Expired restart backoff no longer hides missing active run

- **WHEN** explicit restart is requested after the persisted restart backoff has expired
- **THEN** the controller MUST treat the control state as non-active for restart purposes
- **AND** it MUST NOT automatically start a replacement run.

