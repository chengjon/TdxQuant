## MODIFIED Requirements

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
