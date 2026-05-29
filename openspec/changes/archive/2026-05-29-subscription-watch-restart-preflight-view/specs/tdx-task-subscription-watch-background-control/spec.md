## ADDED Requirements

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
