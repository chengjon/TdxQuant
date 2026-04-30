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
- **THEN** the task MUST append normalized rows to a JSONL artifact
- **AND** each normalized row MUST conform to the provider-level subscription event contract

#### Scenario: Task writes a lightweight flat artifact view
- **WHEN** the subscription watch task appends normalized event rows
- **THEN** the task MUST also maintain a lightweight CSV artifact view for routine inspection

### Requirement: Subscription watch task SHALL maintain a structured status artifact
The system SHALL maintain a structured status artifact for the watch run so external callers can observe run state without parsing the whole event stream.

#### Scenario: Status artifact tracks active and completed run state
- **WHEN** a subscription watch task starts, receives events, or finishes
- **THEN** the task MUST write a status artifact that records run state, stop reason, subscribed symbols, event counts, and artifact paths

#### Scenario: Completion summary exposes artifact paths
- **WHEN** a subscription watch task completes
- **THEN** the returned structured result MUST expose the JSONL, CSV, and status artifact paths together with the final event summary

