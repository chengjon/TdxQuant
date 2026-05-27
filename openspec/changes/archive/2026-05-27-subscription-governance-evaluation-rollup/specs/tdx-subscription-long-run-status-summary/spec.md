## ADDED Requirements

### Requirement: Watch-status summary SHALL expose governance evaluation rollup

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.evaluation_rollup` metadata derived from existing advisory `governance.evaluation_summary` fields without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes governance evaluation rollup

- **WHEN** a caller requests bridge HTTP `watch/status?view=summary`
- **THEN** the response MUST include `governance.evaluation_rollup`
- **AND** the rollup MUST derive evaluated/stale/fresh/not-evaluated counts and primary component hints from existing `governance.evaluation_summary`
- **AND** existing governance sibling fields MUST remain available
- **AND** the summary MUST NOT expose raw control payloads, raw watch-status payloads, full reasons/actions, event-stream data, lifecycle controls, or executable instructions

#### Scenario: CLI summary includes governance evaluation rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `governance.evaluation_rollup`
- **AND** the rollup MUST include conservative booleans for stale, fresh, and all-components-evaluated state derived from existing count fields
- **AND** the summary MUST NOT prove health/readiness, PID liveness, run ownership, or production governance strategy
- **AND** the summary MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
