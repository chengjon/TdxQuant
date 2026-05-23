## ADDED Requirements

### Requirement: Subscription long-run status summary SHALL expose advisory governance posture
The system SHALL include an advisory `governance` object in `status_summary` that summarizes operator-review posture without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Caller inspects active status without explicit stale evaluation
- **WHEN** the background status is active and no stale threshold is provided
- **THEN** the governance summary MUST report `decision=observe`
- **AND** it MUST report that staleness inputs were not evaluated
- **AND** it MUST include an advisory-only boundary

#### Scenario: Caller inspects reconnecting or degraded status
- **WHEN** the persisted watch status identifies `reconnecting`, `degraded`, or `failed` state
- **THEN** the governance summary MUST report `decision=manual_review`
- **AND** it MUST include a machine-readable reason derived from the overall status
- **AND** it MUST NOT change reconnect/backoff behavior

#### Scenario: Caller evaluates stale heartbeat or watermark
- **WHEN** a caller provides an explicit stale threshold and the heartbeat or watermark summary evaluates to `stale`
- **THEN** the governance summary MUST report `decision=manual_review`
- **AND** it MUST include a machine-readable stale reason for each stale input
- **AND** it MUST NOT infer staleness for inputs whose thresholds were omitted
