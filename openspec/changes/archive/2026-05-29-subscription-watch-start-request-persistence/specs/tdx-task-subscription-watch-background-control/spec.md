## ADDED Requirements

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

