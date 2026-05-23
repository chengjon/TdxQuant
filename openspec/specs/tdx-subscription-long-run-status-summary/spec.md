# tdx-subscription-long-run-status-summary Specification

## Purpose
TBD - created by archiving change subscription-long-run-status-summary. Update Purpose after archive.
## Requirements
### Requirement: Subscription long-run status SHALL expose stable summary projection
The system SHALL expose a stable `status_summary` projection for subscription-watch background status responses while preserving raw `control` and `watch_status` payloads.

#### Scenario: Caller inspects stopped background status
- **WHEN** a caller requests background subscription-watch status with no active run
- **THEN** the response MUST include `status_summary`
- **AND** the summary MUST identify the state as `stopped`
- **AND** the summary MUST include heartbeat, watermark, and reconnect sub-objects

#### Scenario: Caller inspects active background status
- **WHEN** a caller requests background subscription-watch status for an active run with a persisted status payload
- **THEN** the summary MUST include the active run id
- **AND** the summary MUST include event watermark metadata from the persisted status payload
- **AND** the raw `control` and `watch_status` payloads MUST remain available

### Requirement: Subscription long-run status summary SHALL surface resilience metadata without changing lifecycle behavior
The system SHALL surface reconnect and degraded metadata in the status summary and MUST NOT change process lifecycle, reconnect scheduling, or bridge event-stream behavior.

#### Scenario: Caller inspects reconnecting status
- **WHEN** the persisted watch status contains reconnect or degraded metadata
- **THEN** the summary MUST include reconnect count, last disconnect, last reconnect, next reconnect, degraded-since, consecutive failure count, and last error fields
- **AND** the summary MUST identify the overall status as `reconnecting` or `degraded` according to the current state

#### Scenario: Caller inspects heartbeat metadata without a stale threshold
- **WHEN** the persisted watch status contains `heartbeat_at`
- **THEN** the summary heartbeat sub-object MUST report heartbeat presence
- **AND** the summary MUST NOT infer clock-based heartbeat staleness by default

#### Scenario: Caller evaluates heartbeat staleness with an explicit threshold
- **WHEN** a caller requests status with a heartbeat stale threshold and the persisted watch status contains `heartbeat_at`
- **THEN** the summary heartbeat sub-object MUST include the evaluated staleness state, age in seconds, threshold seconds, and evaluation timestamp
- **AND** the response MUST preserve the raw `control` and `watch_status` payloads
- **AND** the evaluation MUST NOT change process lifecycle, reconnect scheduling, or bridge event-stream behavior

### Requirement: Subscription long-run status SHALL evaluate watermark staleness only when explicitly requested

The long-run status summary SHALL support explicit watermark staleness diagnostics without changing reconnect, backoff, restart, or event-stream behavior.

#### Scenario: Caller omits watermark stale threshold

- **WHEN** the persisted watch status contains a watermark timestamp and the caller does not provide `watermark_stale_after_seconds`
- **THEN** the watermark summary MUST keep `staleness=not_evaluated`

#### Scenario: Caller evaluates watermark staleness

- **WHEN** the persisted watch status contains `last_event_ts` and the caller provides a positive watermark stale threshold
- **THEN** the watermark summary MUST include fresh/stale state, age seconds, stale threshold, and evaluated timestamp
- **AND** the summary MUST NOT change reconnect/backoff behavior

