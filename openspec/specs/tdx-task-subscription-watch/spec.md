# tdx-task-subscription-watch Specification

## Purpose
TBD - created by archiving change task-runtime-subscription-watch. Update Purpose after archive.
## Requirements
### Requirement: Subscription watch task SHALL provide a stable foreground runtime watch workflow
The system SHALL provide a stable `subscription-watch` task workflow that opens a persistent TongDaXin runtime subscription session, subscribes to an explicit stock list, keeps the session alive in the foreground, and returns a structured completion summary.

#### Scenario: Caller runs a bounded subscription watch task
- **WHEN** a caller invokes the subscription watch task with an explicit stock list and a bounded run condition such as `max_events` or `max_seconds`
- **THEN** the task MUST open one runtime subscription session, register the subscription once, and return a structured summary after the bound is reached

#### Scenario: Caller interrupts a foreground subscription watch task
- **WHEN** a caller stops the foreground subscription watch task with `Ctrl+C`
- **THEN** the task MUST close the runtime subscription session gracefully and return a structured result that records the interrupt stop reason instead of silently dropping task state

### Requirement: Subscription watch task SHALL emit normalized event artifacts
The system SHALL normalize subscription callback payloads into machine-readable event rows and append them to durable task artifacts instead of exposing only raw callback side effects.

#### Scenario: Subscription callback is normalized into stable event rows
- **WHEN** a runtime subscription callback delivers one or more market update payloads
- **THEN** the task MUST append normalized rows to a canonical `events.jsonl` artifact inside the current run directory
- **AND** each normalized row MUST conform to the provider-level subscription event contract

#### Scenario: Task writes a lightweight flat artifact view
- **WHEN** the subscription watch task appends normalized event rows
- **THEN** the task MUST also maintain a lightweight CSV artifact view for routine inspection
- **AND** the CSV artifact MUST remain a compatibility projection of the canonical JSONL event stream rather than an independent contract

### Requirement: Subscription watch task SHALL maintain a structured status artifact
The system SHALL maintain structured run artifacts for the watch run so external callers can observe run state and final outcome without parsing the whole event stream.

#### Scenario: Status artifact tracks active and completed run state
- **WHEN** a subscription watch task starts, receives events, or finishes
- **THEN** the task MUST write `status.json` for the current run
- **AND** the status artifact MUST record run state, stop reason, subscribed symbols, event counts, and artifact paths

#### Scenario: Completion summary exposes run artifacts
- **WHEN** a subscription watch task completes
- **THEN** the task MUST write `summary.json` for the current run
- **AND** the returned structured result MUST expose the `run_id`, canonical JSONL/CSV/status/summary/manifest artifact paths, and the final event summary

### Requirement: Subscription watch task SHALL create a run manifest artifact
The system SHALL create a machine-readable manifest for each `subscription-watch` run so callers can discover the run identity, requested symbols, provider mode, and canonical artifact locations without inferring them from terminal output.

#### Scenario: Run manifest is created at start
- **WHEN** a caller starts a foreground subscription watch task
- **THEN** the task MUST create a unique `run_id` directory for that execution
- **AND** the task MUST write `manifest.json` in that directory with the run identity, requested symbols, provider metadata, and canonical output paths

### Requirement: Subscription watch task SHALL support replay-mode run artifact materialization
The system SHALL let `subscription-watch` run in replay mode by materializing a completed run artifact bundle from fixture-backed event data instead of opening a live runtime subscription session.

#### Scenario: Replay-mode subscription watch materializes a completed run from built-in fixtures
- **WHEN** a caller invokes `subscription-watch` in replay mode without explicitly overriding the fixture source
- **THEN** the task MUST create a fresh `run_id` directory and write canonical `events.jsonl`, `status.json`, `summary.json`, and `manifest.json` artifacts from the built-in replay bundle
- **AND** the returned task result MUST report a completed replay run without opening a live runtime subscription session

#### Scenario: Replay-mode subscription watch uses an explicit replay artifact source
- **WHEN** a caller invokes `subscription-watch` in replay mode with an explicit replay manifest path or replay run directory
- **THEN** the task MUST materialize a fresh completed run from that replay source
- **AND** the task MUST rewrite run identity and artifact paths for the new materialized run instead of reusing the original source paths verbatim

#### Scenario: Replay-mode subscription watch returns canonical and legacy artifact aliases
- **WHEN** a replay-mode `subscription-watch` task completes successfully
- **THEN** the returned task result MUST expose canonical artifact paths for the new run including `run_dir`, `manifest_path`, `status_path`, `summary_path`, `events_jsonl_path`, and `events_csv_path`
- **AND** the returned task result MUST also preserve the compatibility aliases `jsonl_output_path`, `csv_output_path`, and `status_output_path`

#### Scenario: Replay-mode subscription watch rejects malformed replay input without opening live session
- **WHEN** a caller invokes `subscription-watch` in replay mode with an incomplete or malformed replay source bundle
- **THEN** the task MUST return a stable failed task result with `INVALID_REQUEST`
- **AND** the failed result MUST include replay source metadata for `subscription.watch`
- **AND** the task MUST NOT open a live runtime subscription session

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

