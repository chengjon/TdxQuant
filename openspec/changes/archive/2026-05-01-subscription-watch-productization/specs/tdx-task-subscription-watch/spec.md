## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Subscription watch task SHALL create a run manifest artifact
The system SHALL create a machine-readable manifest for each `subscription-watch` run so callers can discover the run identity, requested symbols, provider mode, and canonical artifact locations without inferring them from terminal output.

#### Scenario: Run manifest is created at start
- **WHEN** a caller starts a foreground subscription watch task
- **THEN** the task MUST create a unique `run_id` directory for that execution
- **AND** the task MUST write `manifest.json` in that directory with the run identity, requested symbols, provider metadata, and canonical output paths
