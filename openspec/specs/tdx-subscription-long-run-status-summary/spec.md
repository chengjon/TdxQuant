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

### Requirement: Subscription long-run status summary SHALL expose advisory governance posture

The system SHALL include an advisory `governance` object in `status_summary` that summarizes operator-review posture without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Governance observes healthy or unevaluated state

- **WHEN** no stale input or resilience state requires manual review
- **THEN** `governance.decision` MUST be `observe`
- **AND** `governance.requires_manual_review` MUST be `false`
- **AND** `governance.evaluation_summary` MUST identify not-evaluated components without triggering reconnect, backoff, restart, lifecycle, or event-stream changes

#### Scenario: Governance requests manual review

- **WHEN** explicit stale inputs or resilience state require manual review
- **THEN** `governance.decision` MUST be `manual_review`
- **AND** `governance.requires_manual_review` MUST be `true`
- **AND** `governance.reasons` MUST describe each review reason
- **AND** `governance.evaluation_summary` MUST identify evaluated components and stale components
- **AND** the governance result MUST remain advisory-only

### Requirement: Subscription long-run status summary SHALL expose advisory governance action hints
The system SHALL include an advisory `governance.actions` list in `status_summary` that turns existing manual-review reasons into machine-readable action hints without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Caller inspects active status without manual-review reasons
- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST be an empty list
- **AND** the existing advisory-only boundary MUST remain present

#### Scenario: Caller inspects resilience-state manual review
- **WHEN** the governance reasons include an `overall_status:*` reason
- **THEN** `governance.actions` MUST include an advisory action derived from that reason
- **AND** the action MUST NOT trigger reconnect, restart, backoff, or lifecycle behavior

#### Scenario: Caller evaluates stale heartbeat or watermark inputs
- **WHEN** explicit stale thresholds produce `heartbeat:stale` or `watermark:stale` governance reasons
- **THEN** `governance.actions` MUST include one advisory action per stale input
- **AND** the action list MUST NOT add reasons for inputs whose stale thresholds were omitted

### Requirement: Subscription long-run governance summary SHALL expose a manual-review boolean
The long-run status summary SHALL include `governance.requires_manual_review` as an additive boolean derived from the existing advisory governance decision without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Caller inspects observe posture
- **WHEN** the governance decision is `observe`
- **THEN** `governance.requires_manual_review` MUST be `false`
- **AND** existing `governance.actions` MUST remain an empty list

#### Scenario: Caller inspects manual-review posture
- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.requires_manual_review` MUST be `true`
- **AND** existing governance reasons and actions MUST remain available
- **AND** the flag MUST NOT trigger reconnect, backoff, restart, lifecycle, or event-stream behavior

### Requirement: Subscription long-run governance summary SHALL expose action rollup
The long-run status summary SHALL include an additive `governance.action_summary` object derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty action rollup
- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.count` MUST be `0`
- **AND** `governance.action_summary.primary_action` MUST be `null`
- **AND** `governance.action_summary.severity` MUST be `none`

#### Scenario: Governance manual-review state has action rollup
- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.count` MUST equal the number of `governance.actions`
- **AND** `governance.action_summary.primary_action` MUST equal the first advisory action name
- **AND** `governance.action_summary.primary_reason` MUST equal the first advisory action reason
- **AND** the rollup MUST remain advisory-only

### Requirement: Bridge watch-status CLI SHALL expose summary view

The bridge watch-status CLI SHALL expose an opt-in summary view that projects the existing detailed watch status payload without changing bridge HTTP, worker, reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: Caller requests bridge watch-status summary view

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI MUST still call the existing bridge watch-status request path
- **AND** the CLI MUST print a compact JSON payload
- **AND** the compact payload MUST include selected runtime identity fields derived from `control` and `watch_status` when present
- **AND** the compact payload MUST include `status_summary.governance.action_summary` when the detailed payload provides it
- **AND** the compact payload MUST include `status_summary.governance.evaluation_summary` when the detailed payload provides it
- **AND** the detailed payload MUST remain the default when no summary view is requested

#### Scenario: Bridge watch-status summary view preserves advisory boundary

- **WHEN** the detailed watch status payload contains governance advisory output
- **THEN** the summary view MUST treat governance fields and runtime identity fields as read-only projection data
- **AND** the summary view MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

### Requirement: Subscription long-run status SHALL evaluate reconnect staleness only when explicitly requested

The subscription long-run status summary SHALL expose read-only reconnect/degraded duration staleness only when the caller provides an explicit `reconnect_stale_after_seconds` threshold, and SHALL NOT change reconnect, backoff, restart, or lifecycle behavior.

#### Scenario: Caller omits reconnect stale threshold

- **WHEN** the persisted watch status contains reconnect or degraded timestamps
- **AND** the caller does not provide `reconnect_stale_after_seconds`
- **THEN** the reconnect summary MUST keep `staleness=not_evaluated`
- **AND** governance MUST NOT add reconnect stale reasons or actions

#### Scenario: Caller evaluates reconnect staleness

- **WHEN** the watch status is `reconnecting` or `degraded`
- **AND** the caller provides `reconnect_stale_after_seconds`
- **AND** the reconnect or degraded age exceeds that threshold
- **THEN** the reconnect summary MUST report `staleness=stale`, `age_seconds`, `stale_after_seconds`, and `evaluated_at`
- **AND** governance MUST include a `reconnect:stale` reason and review-only reconnect action

#### Scenario: Caller evaluates reconnect staleness outside resilience state

- **WHEN** the watch status is not `reconnecting` or `degraded`
- **AND** the caller provides `reconnect_stale_after_seconds`
- **THEN** the reconnect summary MUST report `staleness=not_applicable`
- **AND** governance MUST NOT add a reconnect stale reason

### Requirement: Subscription summary view SHALL expose staleness evaluation flag

The subscription long-run HTTP and CLI summary views SHALL include the read-only `governance.staleness_evaluated` flag when the underlying status summary provides it, without exposing full governance actions or changing reconnect/backoff behavior.

#### Scenario: HTTP summary view includes staleness evaluation flag

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.staleness_evaluated`
- **THEN** the HTTP summary result MUST include `governance.staleness_evaluated`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`

#### Scenario: CLI summary view includes staleness evaluation flag

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.staleness_evaluated`
- **THEN** the CLI summary payload MUST include `governance.staleness_evaluated`
- **AND** the CLI summary payload MUST continue to omit full `governance.actions`

#### Scenario: Summary flag remains projection-only

- **WHEN** the summary view includes `governance.staleness_evaluated`
- **THEN** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription summary views SHALL expose advisory governance boundary

The subscription long-run HTTP and CLI summary views SHALL include the read-only `governance.boundary` marker when the underlying status summary provides it, without exposing full governance actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance boundary

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.boundary`
- **THEN** the HTTP summary result MUST include `governance.boundary`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance boundary

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.boundary`
- **THEN** the CLI summary result MUST include `governance.boundary`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

