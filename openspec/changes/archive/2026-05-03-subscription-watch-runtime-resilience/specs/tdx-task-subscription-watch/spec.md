## ADDED Requirements

### Requirement: Subscription watch task SHALL preserve a single run identity across reconnects
The system SHALL treat reconnect and degraded recovery as part of the same foreground `subscription-watch` run instead of splitting a disconnect into a new run identity.

#### Scenario: Recovered watch run keeps the same run directory
- **WHEN** a live `subscription-watch` run enters `reconnecting` or `degraded` and later recovers
- **THEN** the task MUST preserve the same `run_id`
- **AND** the task MUST continue writing the same canonical `events.jsonl`, `status.json`, and `summary.json` artifacts

### Requirement: Subscription watch task SHALL expose bounded reconnect and degraded runtime states
The system SHALL expose stable runtime-state semantics for reconnect and degraded recovery in the foreground `subscription-watch` task.

#### Scenario: Session probe failure enters reconnecting and may recover
- **WHEN** a live `subscription-watch` run detects a runtime subscription failure during its liveness probe
- **THEN** the task MUST enter `reconnecting`
- **AND** the task MUST perform bounded reconnect attempts before deciding whether to recover or enter `degraded`

#### Scenario: Reconnect budget exhaustion enters degraded instead of exiting immediately
- **WHEN** bounded reconnect attempts fail to restore the subscription session
- **THEN** the task MUST enter `degraded`
- **AND** the process MUST remain alive while performing low-frequency recovery probes

#### Scenario: Degraded recovery returns to running
- **WHEN** a degraded `subscription-watch` run successfully restores its runtime subscription session
- **THEN** the task MUST transition back to `running`
- **AND** the task MUST continue the same watch run instead of materializing a new run

### Requirement: Subscription watch task SHALL persist reconnect runtime state in status and summary artifacts
The system SHALL persist reconnect/degraded runtime-state fields in `status.json` and `summary.json` so foreground, background, and bridge readers observe the same resilience contract.

#### Scenario: Status artifact records reconnect runtime fields
- **WHEN** a live `subscription-watch` run writes `status.json`
- **THEN** the status artifact MUST include `heartbeat_at`, `last_event_ts`, `last_source_ts`, `reconnect_count`, `consecutive_reconnect_failures`, `last_disconnect_at`, `last_reconnect_at`, `next_reconnect_at`, `degraded_since`, and `last_error`

#### Scenario: Summary artifact records reconnect outcome fields
- **WHEN** a live `subscription-watch` run writes `summary.json`
- **THEN** the summary artifact MUST include `reconnect_count`, `degraded_duration_ms`, and `final_last_error`
- **AND** `degraded_duration_ms` MUST accumulate all degraded intervals from the run

#### Scenario: Event stream remains free of synthetic reconnect lifecycle rows
- **WHEN** a live `subscription-watch` run reconnects or enters degraded
- **THEN** the task MUST NOT emit synthetic reconnect lifecycle rows into `events.jsonl`
- **AND** ordinary subscription event rows MAY continue to expose empty `reconnect_metadata`
