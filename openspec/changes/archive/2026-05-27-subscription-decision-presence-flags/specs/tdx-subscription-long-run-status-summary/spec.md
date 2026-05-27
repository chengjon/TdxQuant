## ADDED Requirements

### Requirement: Watch-status decision summary SHALL expose reason/action presence flags

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.has_reasons` and `governance.decision_summary.has_actions` fields derived from existing advisory governance count fields without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes decision presence flags

- **WHEN** a caller requests bridge HTTP `watch/status?view=summary`
- **THEN** the response MUST include `governance.decision_summary.has_reasons`
- **AND** the response MUST include `governance.decision_summary.has_actions`
- **AND** `has_reasons` MUST be derived from the already-projected `reason_count`
- **AND** `has_actions` MUST be derived from the already-projected `action_count`
- **AND** existing governance sibling fields MUST remain available
- **AND** the summary MUST NOT expose raw control payloads, raw watch-status payloads, full reasons/actions, event-stream data, lifecycle controls, or executable instructions

#### Scenario: CLI summary includes decision presence flags

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `governance.decision_summary.has_reasons`
- **AND** the printed summary payload MUST include `governance.decision_summary.has_actions`
- **AND** `has_reasons` MUST be derived from the already-projected `reason_count`
- **AND** `has_actions` MUST be derived from the already-projected `action_count`
- **AND** the summary MUST NOT prove health/readiness, PID liveness, run ownership, or production governance strategy
- **AND** the summary MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
