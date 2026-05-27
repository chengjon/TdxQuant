## ADDED Requirements

### Requirement: Watch-status summary SHALL expose governance decision summary

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary` metadata derived from existing advisory governance fields without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes governance decision summary

- **WHEN** a caller requests bridge HTTP `watch/status?view=summary`
- **THEN** the response MUST include `governance.decision_summary`
- **AND** it MUST derive decision, manual-review flag, staleness-evaluated flag, reason/action counts, primary reason source, and primary severity from existing governance summary sibling fields
- **AND** existing governance sibling fields MUST remain available
- **AND** the summary MUST NOT expose raw control payloads, raw watch-status payloads, full reasons/actions, event-stream data, lifecycle controls, or executable instructions

#### Scenario: CLI summary includes governance decision summary

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `governance.decision_summary`
- **AND** `decision`, `requires_manual_review`, `reason_count`, and `action_count` MUST match existing compact governance sibling fields
- **AND** the summary MUST NOT prove health/readiness, PID liveness, run ownership, or production governance strategy
- **AND** the summary MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
