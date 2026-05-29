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

### Requirement: Subscription summary views SHALL expose governance reason count

The subscription long-run HTTP and CLI summary views SHALL include a read-only `governance.reason_count` derived from the underlying detailed `governance.reasons` list when that list is present, without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance reason count

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes a `governance.reasons` list
- **THEN** the HTTP summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance reason count

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes a `governance.reasons` list
- **THEN** the CLI summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription summary views SHALL expose bounded governance reason samples

The subscription long-run HTTP and CLI summary views SHALL include bounded read-only `governance.reason_samples` derived from the underlying detailed `governance.reasons` list when that list is present, without exposing the full reasons/actions arrays or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes bounded governance reason samples

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes multiple `governance.reasons`
- **THEN** the HTTP summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the HTTP summary result MUST include `governance.reason_samples`
- **AND** the HTTP summary result MUST include `governance.reason_sample_limit`
- **AND** the HTTP summary result MUST include `governance.reason_sample_truncated`
- **AND** the HTTP summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

#### Scenario: CLI summary view includes bounded governance reason samples

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes multiple `governance.reasons`
- **THEN** the CLI summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the CLI summary result MUST include `governance.reason_samples`
- **AND** the CLI summary result MUST include `governance.reason_sample_limit`
- **AND** the CLI summary result MUST include `governance.reason_sample_truncated`
- **AND** the CLI summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the CLI summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

### Requirement: Subscription summary views SHALL expose bounded governance action samples

The subscription long-run HTTP and CLI summary views SHALL include bounded read-only `governance.action_samples` derived from the underlying detailed `governance.actions` list when that list is present, without exposing the full action list or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes bounded governance action samples

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes multiple `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.action_samples`
- **AND** each action sample MUST include compact action metadata such as action, reason, and severity without the full description text
- **AND** the HTTP summary result MUST include `governance.action_sample_limit`
- **AND** the HTTP summary result MUST include `governance.action_sample_truncated`
- **AND** the HTTP summary result MUST NOT include full `governance.actions`
- **AND** the summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

#### Scenario: CLI summary view includes bounded governance action samples

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes multiple `governance.actions`
- **THEN** the CLI summary result MUST include `governance.action_samples`
- **AND** each action sample MUST include compact action metadata such as action, reason, and severity without the full description text
- **AND** the CLI summary result MUST include `governance.action_sample_limit`
- **AND** the CLI summary result MUST include `governance.action_sample_truncated`
- **AND** the CLI summary result MUST NOT include full `governance.actions`
- **AND** the CLI summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

### Requirement: Subscription long-run governance action summary SHALL expose severity counts

The long-run status summary SHALL include an additive `governance.action_summary.severity_counts` object derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty severity counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.severity_counts` MUST be an empty object
- **AND** `governance.action_summary.severity` MUST remain `none`

#### Scenario: Governance manual-review state has severity counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.severity_counts` MUST count advisory action severities
- **AND** the severity counts MUST be derived from `governance.actions`
- **AND** the rollup MUST remain advisory-only

### Requirement: Subscription long-run governance summary SHALL expose reason source counts

The long-run status summary SHALL include an additive `governance.reason_source_counts` object derived from existing advisory `governance.reasons` without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty reason source counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.reasons` MUST remain an empty list
- **AND** `governance.reason_source_counts` MUST be an empty object
- **AND** `governance.requires_manual_review` MUST remain `false`

#### Scenario: Governance manual-review state has reason source counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.reason_source_counts` MUST count reason prefixes from `governance.reasons`
- **AND** `overall_status:*`, `heartbeat:*`, `watermark:*`, and `reconnect:*` reasons MUST be counted under their respective prefixes
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views expose compact reason source counts

- **WHEN** the CLI or HTTP watch status summary view includes governance details
- **THEN** the compact governance view MUST include `reason_source_counts`
- **AND** the compact governance view MUST continue to omit the full `governance.reasons` list
- **AND** `reason_source_counts` MUST remain a derived summary, not a replacement for full governance reasons in the full status payload

### Requirement: Subscription long-run evaluation summary SHALL expose fresh component counts

The subscription long-run status summary SHALL include additive `governance.evaluation_summary.fresh_components` and `governance.evaluation_summary.fresh_count` fields derived from existing heartbeat, watermark, and reconnect staleness summaries without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Default not-evaluated summary has no fresh components

- **WHEN** stale thresholds are not provided
- **THEN** `governance.evaluation_summary.fresh_components` MUST be an empty list
- **AND** `governance.evaluation_summary.fresh_count` MUST be `0`
- **AND** `governance.staleness_evaluated` MUST remain `false`

#### Scenario: Mixed fresh and stale components are explicit

- **WHEN** some evaluated components are fresh and at least one evaluated component is stale
- **THEN** `governance.evaluation_summary.fresh_components` MUST list the fresh evaluated component names
- **AND** `governance.evaluation_summary.fresh_count` MUST equal the number of fresh evaluated components
- **AND** existing stale component fields MUST remain present

#### Scenario: Reconnect stale summary preserves fresh counts

- **WHEN** reconnect/degraded duration is stale while heartbeat and watermark remain fresh
- **THEN** `governance.evaluation_summary.fresh_components` MUST include `heartbeat` and `watermark`
- **AND** `governance.evaluation_summary.fresh_count` MUST be `2`
- **AND** governance actions MUST remain advisory only

### Requirement: Subscription long-run governance summary SHALL expose detailed reason count

The detailed subscription watch status summary SHALL include an additive read-only `governance.reason_count` scalar derived from the existing advisory `governance.reasons` list without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Detailed observe governance has zero reason count

- **WHEN** the detailed status summary governance decision is `observe`
- **THEN** `governance.reasons` MUST remain an empty list
- **AND** `governance.reason_count` MUST be `0`
- **AND** `governance.requires_manual_review` MUST remain `false`

#### Scenario: Detailed manual-review governance counts reasons

- **WHEN** the detailed status summary governance decision is `manual_review`
- **THEN** `governance.reason_count` MUST equal the length of `governance.reasons`
- **AND** `governance.reason_count` MUST remain a derived scalar, not a replacement for the detailed reasons list
- **AND** the rollup MUST remain advisory-only

### Requirement: Subscription summary views SHALL expose status summary schema version

The subscription long-run CLI and HTTP summary views SHALL include additive read-only `status_summary.schema_version` when the underlying detailed status summary provides it, without exposing raw `control`, raw `watch_status`, full governance reasons, full governance actions, or changing reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: CLI summary view includes status summary schema version

- **WHEN** a caller runs `bridge watch-status --view summary`
- **AND** the underlying detailed payload includes `status_summary.schema_version`
- **THEN** the CLI summary result MUST include the same `status_summary.schema_version`
- **AND** the summary result MUST continue to omit raw `control`, raw `watch_status`, full `governance.reasons`, and full `governance.actions`

#### Scenario: HTTP summary view includes status summary schema version

- **WHEN** a caller requests `watch/status?view=summary`
- **AND** the underlying detailed payload includes `status_summary.schema_version`
- **THEN** the HTTP summary result MUST include the same `status_summary.schema_version`
- **AND** the summary result MUST continue to omit raw `control`, raw `watch_status`, full `governance.reasons`, and full `governance.actions`

### Requirement: Subscription long-run governance action summary SHALL expose action-name counts

The long-run status summary SHALL include an additive `governance.action_summary.action_name_counts` object derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty action-name counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.action_name_counts` MUST be an empty object
- **AND** `governance.action_summary.primary_action` MUST remain `null`

#### Scenario: Governance manual-review state has action-name counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.action_name_counts` MUST count advisory action names
- **AND** the action-name counts MUST be derived from `governance.actions`
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views preserve action-name counts without exposing full actions

- **WHEN** a caller requests the CLI or HTTP subscription watch status summary view
- **THEN** the summary view MUST include `governance.action_summary.action_name_counts`
- **AND** the summary view MUST NOT include the full `governance.actions` list
- **AND** the summary view MUST remain a read-only projection

### Requirement: Subscription long-run governance summary SHALL expose compact reason summary

The long-run status summary SHALL include an additive `governance.reason_summary` object derived from existing advisory `governance.reasons` without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty reason summary

- **WHEN** subscription watch status has no advisory governance reasons
- **THEN** `governance.reason_summary.count` MUST be `0`
- **AND** `governance.reason_summary.primary_reason` MUST be `null`
- **AND** `governance.reason_summary.primary_source` MUST be `null`
- **AND** `governance.reason_summary.source_counts` MUST be an empty object

#### Scenario: Governance manual-review state has primary reason summary

- **WHEN** subscription watch status has advisory governance reasons
- **THEN** `governance.reason_summary.count` MUST equal the number of advisory reasons
- **AND** `governance.reason_summary.primary_reason` MUST equal the first advisory reason
- **AND** `governance.reason_summary.primary_source` MUST equal the first advisory reason source prefix
- **AND** `governance.reason_summary.source_counts` MUST count reason source prefixes

#### Scenario: CLI summary view exposes compact reason summary

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reason_summary`
- **THEN** the CLI summary result MUST include `governance.reason_summary`
- **AND** the CLI summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the CLI summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

### Requirement: Subscription long-run governance SHALL expose advisory action count

The subscription long-run status summary SHALL include additive `governance.action_count` derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Detailed observe governance has zero action count

- **WHEN** a subscription watch status summary has no advisory governance actions
- **THEN** `governance.action_count` MUST be `0`
- **AND** `governance.action_summary.count` MUST also be `0`

#### Scenario: Detailed manual-review governance counts advisory actions

- **WHEN** a subscription watch status summary includes advisory governance actions
- **THEN** `governance.action_count` MUST equal the number of `governance.actions`
- **AND** `governance.action_count` MUST equal `governance.action_summary.count`

#### Scenario: HTTP summary view preserves advisory action count without full actions

- **WHEN** a caller requests bridge watch status with `view=summary`
- **THEN** the HTTP summary result MUST include `governance.action_count`
- **AND** `governance.action_count` MUST equal the detailed advisory action count
- **AND** the HTTP summary result MUST NOT include the full `governance.actions` list

#### Scenario: CLI summary view preserves advisory action count without full actions

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI summary result MUST include `governance.action_count`
- **AND** `governance.action_count` MUST equal the detailed advisory action count
- **AND** the CLI summary result MUST NOT include the full `governance.actions` list

### Requirement: Subscription long-run evaluation summary SHALL expose component status counts

The subscription long-run governance evaluation summary SHALL include additive `component_status_counts` derived from the heartbeat, watermark, and reconnect staleness classifications without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Default not-evaluated summary counts all components

- **WHEN** a subscription watch status summary is built without explicit staleness thresholds
- **THEN** `governance.evaluation_summary.component_status_counts` MUST count heartbeat, watermark, and reconnect as `not_evaluated`

#### Scenario: Mixed evaluation summary counts fresh and stale components

- **WHEN** a subscription watch status summary evaluates a mix of fresh, stale, and not-evaluated components
- **THEN** `governance.evaluation_summary.component_status_counts` MUST include the matching count for each present component status
- **AND** the sum of `component_status_counts` values MUST equal `3`

#### Scenario: Summary views preserve component status counts

- **WHEN** a caller requests bridge watch status with `view=summary`
- **THEN** the HTTP and CLI summary views MUST include `governance.evaluation_summary.component_status_counts`
- **AND** the summary views MUST remain read-only projections that omit raw `control`, raw `watch_status`, full reasons, and full actions

### Requirement: Subscription long-run governance reason summary SHALL expose reason-code counts

The long-run status summary SHALL include an additive `governance.reason_summary.reason_code_counts` object derived from existing advisory `governance.reasons` without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty reason-code counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.reasons` MUST remain an empty list
- **AND** `governance.reason_summary.reason_code_counts` MUST be an empty object
- **AND** `governance.reason_summary.count` MUST remain `0`

#### Scenario: Governance manual-review state has reason-code counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.reason_summary.reason_code_counts` MUST count advisory reason strings from `governance.reasons`
- **AND** the count keys MUST be exact advisory reason codes such as `heartbeat:stale`
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views preserve reason-code counts without exposing full reasons

- **WHEN** a compact summary view includes `governance.reason_summary`
- **THEN** `governance.reason_summary.reason_code_counts` MUST remain present
- **AND** the summary view MUST NOT expose raw `governance.reasons` or `governance.actions`

### Requirement: Subscription long-run governance evaluation summary SHALL expose evaluated status counts

The long-run status summary SHALL include additive `governance.evaluation_summary.evaluated_status_counts`, derived only from explicitly evaluated heartbeat, watermark, and reconnect components without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No evaluated components have empty evaluated status counts

- **WHEN** no heartbeat, watermark, or reconnect stale thresholds are explicitly evaluated
- **THEN** `governance.evaluation_summary.evaluated_status_counts` MUST be an empty object
- **AND** `governance.evaluation_summary.component_status_counts` MUST continue to count `not_evaluated` components
- **AND** the governance decision MUST remain advisory-only

#### Scenario: Evaluated fresh and stale components are counted

- **WHEN** one or more components have explicit staleness evaluation results
- **THEN** `governance.evaluation_summary.evaluated_status_counts` MUST count evaluated statuses such as `fresh` and `stale`
- **AND** the counts MUST exclude `not_evaluated` components
- **AND** existing evaluated, stale, fresh, and not-evaluated component lists MUST remain present

#### Scenario: Summary views preserve evaluated status counts

- **WHEN** a compact summary view includes `governance.evaluation_summary`
- **THEN** `governance.evaluation_summary.evaluated_status_counts` MUST remain present
- **AND** the summary view MUST remain a read-only projection

### Requirement: Subscription long-run evaluation summary SHALL expose evaluated component lists and counts

Subscription long-run governance evaluation summaries SHALL expose additive component lists and count fields derived from heartbeat, watermark, and reconnect staleness evaluation without changing reconnect, backoff, restart, or lifecycle behavior.

#### Scenario: Default not-evaluated summary lists skipped components

- **WHEN** stale thresholds are not provided
- **THEN** `governance.evaluation_summary.evaluated_components` MUST be an empty list
- **AND** `governance.evaluation_summary.evaluated_count` MUST be `0`
- **AND** `governance.evaluation_summary.not_evaluated_components` MUST list heartbeat, watermark, and reconnect
- **AND** `governance.evaluation_summary.not_evaluated_count` MUST equal the length of `not_evaluated_components`

#### Scenario: Explicit stale evaluation lists evaluated and stale components

- **WHEN** heartbeat, watermark, or reconnect staleness is explicitly evaluated
- **THEN** `governance.evaluation_summary.evaluated_components` MUST list evaluated component names
- **AND** `governance.evaluation_summary.evaluated_count` MUST equal the length of `evaluated_components`
- **AND** `governance.evaluation_summary.stale_components` MUST list components whose staleness is `stale`
- **AND** `governance.evaluation_summary.stale_count` MUST equal the length of `stale_components`
- **AND** the summary MUST remain advisory-only and read-only

#### Scenario: Fresh component contract remains unchanged

- **WHEN** an explicitly evaluated component is fresh
- **THEN** `governance.evaluation_summary.fresh_components` MUST list that component
- **AND** `governance.evaluation_summary.fresh_count` MUST equal the length of `fresh_components`
- **AND** component list/count fields MUST NOT trigger reconnect, backoff, restart, or lifecycle control

### Requirement: Subscription long-run governance action summary SHALL expose action reason-source counts

The long-run status summary SHALL include an additive `governance.action_summary.reason_source_counts` object derived from existing advisory governance action reasons without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty action reason-source counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.reason_source_counts` MUST be an empty object
- **AND** `governance.action_summary.primary_action` MUST remain `null`

#### Scenario: Governance manual-review state has action reason-source counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.reason_source_counts` MUST count source prefixes from advisory action `reason` values
- **AND** the action reason-source counts MUST be derived from `governance.actions`
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views preserve action reason-source counts without exposing full actions

- **WHEN** a caller requests the CLI or HTTP subscription watch status summary view
- **THEN** the summary view MUST include `governance.action_summary.reason_source_counts`
- **AND** the summary view MUST NOT include the full `governance.actions` list
- **AND** the summary view MUST remain a read-only projection

### Requirement: Subscription long-run governance action summary SHALL expose action reason-code counts

The long-run status summary SHALL include an additive `governance.action_summary.reason_code_counts` object derived from existing advisory governance action reasons without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty action reason-code counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.reason_code_counts` MUST be an empty object
- **AND** `governance.action_summary.primary_action` MUST remain `null`

#### Scenario: Governance manual-review state has action reason-code counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.reason_code_counts` MUST count non-empty advisory action `reason` strings
- **AND** the action reason-code counts MUST be derived from `governance.actions`
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views preserve action reason-code counts without exposing full actions

- **WHEN** a caller requests the CLI or HTTP subscription watch status summary view
- **THEN** the summary view MUST include `governance.action_summary.reason_code_counts`
- **AND** the summary view MUST NOT include the full `governance.actions` list
- **AND** the summary view MUST remain a read-only projection

### Requirement: Subscription governance action summary SHALL expose primary reason source

Subscription long-run status summaries SHALL include additive `governance.action_summary.primary_reason_source` derived from the first advisory action reason without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty action summary has no primary reason source

- **WHEN** no advisory governance actions are present
- **THEN** `governance.action_summary.primary_reason_source` MUST be `null`

#### Scenario: Advisory action summary exposes primary reason source

- **WHEN** advisory governance actions are present
- **THEN** `governance.action_summary.primary_reason_source` MUST equal the parsed source prefix of `governance.action_summary.primary_reason`
- **AND** aggregate action counts MUST remain unchanged

#### Scenario: Summary views preserve primary reason source

- **WHEN** callers request CLI or HTTP subscription watch status summary views
- **THEN** the compact governance action summary MUST include `primary_reason_source`
- **AND** the summary view MUST remain advisory-only and MUST NOT expose full action details

### Requirement: Subscription governance evaluation summary SHALL expose primary stale component

The subscription long-run status summary SHALL include additive `status_summary.governance.evaluation_summary.primary_stale_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No stale components have null primary stale component

- **WHEN** no evaluated governance component is stale
- **THEN** `governance.evaluation_summary.primary_stale_component` MUST be `null`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Stale components expose first stale component

- **WHEN** one or more evaluated governance components are stale
- **THEN** `governance.evaluation_summary.primary_stale_component` MUST equal the first entry in `stale_components`
- **AND** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior

#### Scenario: Summary views preserve primary stale component

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.primary_stale_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

### Requirement: Subscription governance evaluation summary SHALL expose primary not-evaluated component

The subscription long-run status summary SHALL include additive `status_summary.governance.evaluation_summary.primary_not_evaluated_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No not-evaluated components have null primary not-evaluated component

- **WHEN** all governance components are explicitly evaluated
- **THEN** `governance.evaluation_summary.primary_not_evaluated_component` MUST be `null`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Not-evaluated components expose first not-evaluated component

- **WHEN** one or more governance components are not evaluated
- **THEN** `governance.evaluation_summary.primary_not_evaluated_component` MUST equal the first entry in `not_evaluated_components`
- **AND** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior

#### Scenario: Summary views preserve primary not-evaluated component

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.primary_not_evaluated_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

### Requirement: Subscription governance evaluation summary SHALL expose primary fresh component

The subscription long-run status summary SHALL include additive `status_summary.governance.evaluation_summary.primary_fresh_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No fresh components have null primary fresh component

- **WHEN** no governance component is explicitly fresh
- **THEN** `governance.evaluation_summary.primary_fresh_component` MUST be `null`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Fresh components expose first fresh component

- **WHEN** one or more governance components are explicitly fresh
- **THEN** `governance.evaluation_summary.primary_fresh_component` MUST equal the first entry in `fresh_components`
- **AND** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior

#### Scenario: Summary views preserve primary fresh component

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.primary_fresh_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

### Requirement: Subscription governance action summary SHALL expose primary severity

Subscription long-run status summaries SHALL include additive `governance.action_summary.primary_severity` derived from the first advisory governance action severity without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty action summary has no primary severity

- **WHEN** no advisory governance actions are present
- **THEN** `governance.action_summary.primary_severity` MUST be `"none"`
- **AND** action counts MUST remain zero

#### Scenario: Advisory action summary exposes primary severity

- **WHEN** one or more advisory governance actions are present
- **THEN** `governance.action_summary.primary_severity` MUST equal the first action severity
- **AND** aggregate action counts MUST remain unchanged

#### Scenario: Summary views preserve primary severity

- **WHEN** callers request CLI or HTTP subscription watch status summary views
- **THEN** the compact governance action summary MUST include `primary_severity`
- **AND** the summary view MUST remain advisory-only and MUST NOT expose full action details

### Requirement: Subscription governance reason summary SHALL expose primary reason source

Subscription long-run status summaries SHALL include additive `governance.reason_summary.primary_reason_source` derived from the first advisory governance reason without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty reason summary has no primary reason source

- **WHEN** no advisory governance reasons are present
- **THEN** `governance.reason_summary.primary_reason_source` MUST be `null`
- **AND** `governance.reason_summary.primary_source` MUST remain available for compatibility

#### Scenario: Advisory reason summary exposes primary reason source

- **WHEN** one or more advisory governance reasons are present
- **THEN** `governance.reason_summary.primary_reason_source` MUST equal `governance.reason_summary.primary_source`
- **AND** aggregate reason counts MUST remain unchanged

#### Scenario: Summary views preserve primary reason source

- **WHEN** callers request CLI or HTTP subscription watch status summary views
- **THEN** the compact governance reason summary MUST include `primary_reason_source`
- **AND** the summary view MUST remain advisory-only and MUST NOT expose full reason details

### Requirement: Subscription summary views SHALL expose governance sample counts

The subscription long-run HTTP and CLI summary views SHALL include read-only `governance.reason_sample_count` and `governance.action_sample_count` fields derived from their bounded visible sample arrays when those arrays are projected, without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance sample counts

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.reason_sample_count` equal to the length of `governance.reason_samples`
- **AND** the HTTP summary result MUST include `governance.action_sample_count` equal to the length of `governance.action_samples`
- **AND** the HTTP summary result MUST keep `governance.reason_count` and `governance.action_count` as full underlying list counts
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance sample counts

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the CLI summary result MUST include `governance.reason_sample_count` equal to the length of `governance.reason_samples`
- **AND** the CLI summary result MUST include `governance.action_sample_count` equal to the length of `governance.action_samples`
- **AND** the CLI summary result MUST keep `governance.reason_count` and `governance.action_count` as full underlying list counts
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription summary runtime SHALL expose state match

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.state_match` field derived from `control.state` and `watch_status.state` when both source states are present, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes runtime state match

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status payload includes both `control.state` and `watch_status.state`
- **THEN** the HTTP summary result MUST include `runtime.state_match` equal to whether those two state strings are equal
- **AND** the HTTP summary result MUST continue to expose `runtime.control_state` and `runtime.watch_state`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes runtime state match

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status payload includes both `control.state` and `watch_status.state`
- **THEN** the CLI summary result MUST include `runtime.state_match` equal to whether those two state strings are equal
- **AND** the CLI summary result MUST continue to expose `runtime.control_state` and `runtime.watch_state`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription summary runtime SHALL expose run-id source

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.run_id_source` field derived from the source that supplied `runtime.run_id`, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes runtime run-id source

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status payload supplies `runtime.run_id` from `watch_status.run_id` or `control.run_id`
- **THEN** the HTTP summary result MUST include `runtime.run_id_source` equal to `watch_status` when `watch_status.run_id` is present
- **AND** the HTTP summary result MUST include `runtime.run_id_source` equal to `control` when `watch_status.run_id` is absent and `control.run_id` supplies the value
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes runtime run-id source

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status payload supplies `runtime.run_id` from `watch_status.run_id` or `control.run_id`
- **THEN** the CLI summary result MUST include `runtime.run_id_source` equal to `watch_status` when `watch_status.run_id` is present
- **AND** the CLI summary result MUST include `runtime.run_id_source` equal to `control` when `watch_status.run_id` is absent and `control.run_id` supplies the value
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription summary runtime SHALL expose run-id match

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.run_id_match` field derived from `control.run_id` and `watch_status.run_id` when both raw run ids are present, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes runtime run-id match

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status payload includes both `control.run_id` and `watch_status.run_id`
- **THEN** the HTTP summary result MUST include `runtime.run_id_match` equal to whether those two raw run ids are equal
- **AND** the HTTP summary result MUST continue to expose `runtime.run_id` and `runtime.run_id_source`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes runtime run-id match

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status payload includes both `control.run_id` and `watch_status.run_id`
- **THEN** the CLI summary result MUST include `runtime.run_id_match` equal to whether those two raw run ids are equal
- **AND** the CLI summary result MUST continue to expose `runtime.run_id` and `runtime.run_id_source`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription Summary Runtime PID Source

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.pid_source` field derived from the source that supplied `runtime.pid`, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes runtime PID source

- **GIVEN** a subscription watch status payload with `control.pid`
- **WHEN** a caller requests `watch/status?view=summary`
- **THEN** the HTTP summary result MUST include `runtime.pid` from `control.pid`
- **AND** the HTTP summary result MUST include `runtime.pid_source` equal to `control`
- **AND** this field MUST NOT imply PID liveness, process ownership, readiness, or lifecycle control.

#### Scenario: CLI summary includes runtime PID source

- **GIVEN** a subscription watch status payload with `control.pid`
- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI summary result MUST include `runtime.pid` from `control.pid`
- **AND** the CLI summary result MUST include `runtime.pid_source` equal to `control`
- **AND** this field MUST NOT imply PID liveness, process ownership, readiness, or lifecycle control.

### Requirement: Subscription governance evaluation summary SHALL expose status key counts

Subscription long-run status summaries SHALL include additive `status_summary.governance.evaluation_summary.component_status_key_count` and `status_summary.governance.evaluation_summary.evaluated_status_key_count` fields derived from existing evaluation status-count maps without changing staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Evaluation summary reports all component status key count

- **WHEN** `governance.evaluation_summary.component_status_counts` contains one or more status keys
- **THEN** `governance.evaluation_summary.component_status_key_count` MUST equal the number of keys in `component_status_counts`
- **AND** existing component lists, scalar counts, and status-count maps MUST remain available

#### Scenario: Evaluation summary reports evaluated status key count

- **WHEN** `governance.evaluation_summary.evaluated_status_counts` contains zero or more status keys
- **THEN** `governance.evaluation_summary.evaluated_status_key_count` MUST equal the number of keys in `evaluated_status_counts`
- **AND** the field MUST be `0` when no components were explicitly evaluated

#### Scenario: Status key counts remain advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** the status key count fields MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the fields MUST NOT be treated as health, readiness, PID liveness, or process ownership proof

### Requirement: Subscription governance reason summary SHALL expose reason map key counts

Subscription long-run status summaries SHALL include additive `status_summary.governance.reason_summary.source_key_count` and `status_summary.governance.reason_summary.reason_code_key_count` fields derived from existing reason-summary count maps without changing governance decisions, staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Reason summary reports source key count

- **WHEN** `governance.reason_summary.source_counts` contains zero or more source keys
- **THEN** `governance.reason_summary.source_key_count` MUST equal the number of keys in `source_counts`
- **AND** the field MUST be `0` when no advisory reasons exist

#### Scenario: Reason summary reports reason-code key count

- **WHEN** `governance.reason_summary.reason_code_counts` contains zero or more reason-code keys
- **THEN** `governance.reason_summary.reason_code_key_count` MUST equal the number of keys in `reason_code_counts`
- **AND** existing `governance.reason_count`, `source_counts`, and `reason_code_counts` MUST remain available

#### Scenario: Reason key counts remain advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** the reason key-count fields MUST NOT expose full reasons in compact summary view
- **AND** the fields MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the fields MUST NOT be treated as health, readiness, PID liveness, process ownership, or governance policy proof

### Requirement: Subscription governance action summary SHALL expose action map key counts

Subscription long-run status summaries SHALL include additive `status_summary.governance.action_summary.severity_key_count`, `action_name_key_count`, `reason_source_key_count`, and `reason_code_key_count` fields derived from existing action-summary count maps without changing advisory action generation, governance decisions, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty action summary reports zero key counts

- **WHEN** no advisory governance actions exist
- **THEN** `governance.action_summary.severity_key_count` MUST be `0`
- **AND** `governance.action_summary.action_name_key_count` MUST be `0`
- **AND** `governance.action_summary.reason_source_key_count` MUST be `0`
- **AND** `governance.action_summary.reason_code_key_count` MUST be `0`

#### Scenario: Action summary reports count-map key counts

- **WHEN** advisory governance actions produce severity, action-name, reason-source, and reason-code count maps
- **THEN** each action-summary `*_key_count` field MUST equal the number of keys in its corresponding count map
- **AND** existing `governance.action_count`, `governance.action_summary.count`, and action-summary count maps MUST remain available

#### Scenario: Action key counts remain advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** the action key-count fields MUST NOT expose full actions in compact summary view
- **AND** the fields MUST NOT execute actions or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the fields MUST NOT be treated as health, readiness, PID liveness, process ownership, escalation policy, or governance policy proof

### Requirement: Subscription governance summary SHALL expose reason source key count

Subscription long-run status summaries SHALL include additive `status_summary.governance.reason_source_key_count` derived from the existing top-level `governance.reason_source_counts` map without changing governance decisions, staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance reason source key count is empty

- **WHEN** no advisory governance reasons exist
- **THEN** `governance.reason_source_counts` MUST remain an empty map
- **AND** `governance.reason_source_key_count` MUST be `0`

#### Scenario: Governance reason source key count reflects source distribution

- **WHEN** advisory governance reasons produce one or more reason-source count-map keys
- **THEN** `governance.reason_source_key_count` MUST equal the number of keys in `governance.reason_source_counts`
- **AND** existing `governance.reason_count`, `governance.reason_source_counts`, and `governance.reason_summary` MUST remain available

#### Scenario: Reason source key count remains advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** `governance.reason_source_key_count` MUST NOT expose full reasons in compact summary view
- **AND** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the field MUST NOT be treated as health, readiness, PID liveness, process ownership, escalation policy, or governance policy proof

### Requirement: Subscription evaluation summary SHALL expose the primary evaluated component

The subscription long-run status summary SHALL include additive read-only `governance.evaluation_summary.primary_evaluated_component` derived from the existing ordered `evaluated_components` list without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Components have been explicitly evaluated

- **WHEN** a caller builds a subscription long-run status summary with explicit heartbeat, watermark, or reconnect staleness thresholds
- **THEN** `governance.evaluation_summary.primary_evaluated_component` MUST equal the first item in `governance.evaluation_summary.evaluated_components`
- **AND** the existing evaluated/stale/fresh/not-evaluated component lists and counts MUST remain unchanged

#### Scenario: No component has been explicitly evaluated

- **WHEN** a caller builds a subscription long-run status summary without explicit staleness thresholds
- **THEN** `governance.evaluation_summary.evaluated_components` MUST be empty
- **AND** `governance.evaluation_summary.primary_evaluated_component` MUST be `null`

#### Scenario: Primary evaluated component remains advisory

- **WHEN** a caller inspects `governance.evaluation_summary.primary_evaluated_component`
- **THEN** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the field MUST NOT be treated as a health guarantee, readiness guarantee, or automatic recovery condition

### Requirement: Subscription summary views SHALL expose governance hidden sample counts

The subscription long-run HTTP and CLI summary views SHALL include read-only `governance.reason_sample_hidden_count` and `governance.action_sample_hidden_count` fields derived from the difference between full underlying governance list counts and bounded visible sample counts when those samples are projected, without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance hidden sample counts

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.reason_sample_hidden_count` equal to `governance.reason_count - governance.reason_sample_count`
- **AND** the HTTP summary result MUST include `governance.action_sample_hidden_count` equal to `governance.action_count - governance.action_sample_count`
- **AND** the hidden counts MUST be non-negative integers
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance hidden sample counts

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the CLI summary result MUST include `governance.reason_sample_hidden_count` equal to `governance.reason_count - governance.reason_sample_count`
- **AND** the CLI summary result MUST include `governance.action_sample_hidden_count` equal to `governance.action_count - governance.action_sample_count`
- **AND** the hidden counts MUST be non-negative integers
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Subscription summary view SHALL expose governance sample summary

Subscription long-run HTTP and CLI summary views SHALL include additive read-only `governance.sample_summary` metadata derived from the existing bounded reason/action sample projection without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance sample summary

- **WHEN** a caller requests the worker bridge watch-status HTTP summary view and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.sample_summary.reason_count` equal to the full underlying reason count
- **AND** it MUST include `reason_sample_count`, `reason_sample_hidden_count`, `reason_sample_limit`, and `reason_sample_truncated` matching the sibling governance sample fields
- **AND** it MUST include `action_count`, `action_sample_count`, `action_sample_hidden_count`, `action_sample_limit`, and `action_sample_truncated` matching the sibling governance sample fields
- **AND** hidden counts MUST be non-negative integers
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance sample summary

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the CLI summary result MUST include `governance.sample_summary.reason_count` equal to the full underlying reason count
- **AND** it MUST include `reason_sample_count`, `reason_sample_hidden_count`, `reason_sample_limit`, and `reason_sample_truncated` matching the sibling governance sample fields
- **AND** it MUST include `action_count`, `action_sample_count`, `action_sample_hidden_count`, `action_sample_limit`, and `action_sample_truncated` matching the sibling governance sample fields
- **AND** hidden counts MUST be non-negative integers
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

### Requirement: Watch-status summary SHALL expose runtime identity summary

HTTP and CLI watch-status summary views SHALL include additive read-only `runtime.identity_summary` metadata derived from existing runtime identity fields without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes runtime identity summary

- **WHEN** a caller requests bridge HTTP `watch/status?view=summary`
- **THEN** the response MUST include `runtime.identity_summary`
- **AND** it MUST derive control/watch state, state match, run ID presence/source/match, and PID presence/source from existing runtime summary sibling fields
- **AND** existing runtime sibling fields MUST remain available
- **AND** the summary MUST NOT expose raw control payloads, raw watch-status payloads, event-stream data, lifecycle controls, or executable instructions

#### Scenario: CLI summary includes runtime identity summary

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `runtime.identity_summary`
- **AND** `has_run_id`, `run_id_source`, `run_id_match`, `has_pid`, and `pid_source` MUST match the existing compact runtime sibling fields
- **AND** the summary MUST NOT prove PID liveness, run ownership, run freshness, health/readiness, or process ownership
- **AND** the summary MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior

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

### Requirement: Subscription governance evaluation summary SHALL expose stale presence

The subscription long-run status summary SHALL include additive read-only `status_summary.governance.evaluation_summary.has_stale_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No stale components reports false

- **WHEN** no evaluated governance component is stale
- **THEN** `governance.evaluation_summary.has_stale_component` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Stale components report true

- **WHEN** one or more evaluated governance components are stale
- **THEN** `governance.evaluation_summary.has_stale_component` MUST be `true`
- **AND** the field MUST remain consistent with `stale_count > 0`

#### Scenario: Summary views preserve stale presence

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.has_stale_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

### Requirement: Subscription governance evaluation summary SHALL expose not-evaluated presence

The subscription long-run status summary SHALL include additive read-only `status_summary.governance.evaluation_summary.has_not_evaluated_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Fully evaluated components report false

- **WHEN** all governance components have been evaluated as stale or fresh
- **THEN** `governance.evaluation_summary.has_not_evaluated_component` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Not-evaluated components report true

- **WHEN** one or more governance components are not evaluated
- **THEN** `governance.evaluation_summary.has_not_evaluated_component` MUST be `true`
- **AND** the field MUST remain consistent with `not_evaluated_count > 0`

#### Scenario: Summary views preserve not-evaluated presence

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.has_not_evaluated_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

### Requirement: Subscription governance evaluation summary SHALL expose fresh presence

The subscription long-run status summary SHALL include additive read-only `status_summary.governance.evaluation_summary.has_fresh_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No fresh components report false

- **WHEN** no evaluated governance component is fresh
- **THEN** `governance.evaluation_summary.has_fresh_component` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Fresh components report true

- **WHEN** one or more evaluated governance components are fresh
- **THEN** `governance.evaluation_summary.has_fresh_component` MUST be `true`
- **AND** the field MUST remain consistent with `fresh_count > 0`

#### Scenario: Summary views preserve fresh presence

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.has_fresh_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

### Requirement: Subscription governance evaluation summary SHALL expose all-components evaluated flag

The subscription long-run status summary SHALL include additive read-only `status_summary.governance.evaluation_summary.all_components_evaluated` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Not-evaluated components report false

- **WHEN** one or more governance components are not evaluated
- **THEN** `governance.evaluation_summary.all_components_evaluated` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Fully evaluated components report true

- **WHEN** all governance components have been evaluated as stale or fresh
- **THEN** `governance.evaluation_summary.all_components_evaluated` MUST be `true`
- **AND** the field MUST remain consistent with `not_evaluated_count == 0`

#### Scenario: Summary views preserve all-components evaluated flag

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.all_components_evaluated`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

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

### Requirement: Subscription governance evaluation rollup SHALL expose compact completeness fields

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.evaluation_rollup` completeness fields derived from existing advisory `governance.evaluation_summary` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes evaluation rollup completeness

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.evaluation_rollup.has_not_evaluated_component` MUST indicate whether any component was not evaluated
- **AND** `governance.evaluation_rollup.component_status_key_count` MUST mirror `governance.evaluation_summary.component_status_key_count`
- **AND** `governance.evaluation_rollup.evaluated_status_key_count` MUST mirror `governance.evaluation_summary.evaluated_status_key_count`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes evaluation rollup completeness

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.evaluation_rollup.has_not_evaluated_component` MUST indicate whether any component was not evaluated
- **AND** `governance.evaluation_rollup.component_status_key_count` MUST mirror `governance.evaluation_summary.component_status_key_count`
- **AND** `governance.evaluation_rollup.evaluated_status_key_count` MUST mirror `governance.evaluation_summary.evaluated_status_key_count`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription governance evaluation rollup SHALL expose evaluated-component fields

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.evaluation_rollup` evaluated-component fields derived from existing advisory `governance.evaluation_summary` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes evaluated-component rollup fields

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.evaluation_rollup.primary_evaluated_component` MUST mirror `governance.evaluation_summary.primary_evaluated_component`
- **AND** `governance.evaluation_rollup.has_evaluated_component` MUST indicate whether `governance.evaluation_summary.evaluated_count` is greater than zero
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes evaluated-component rollup fields

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.evaluation_rollup.primary_evaluated_component` MUST mirror `governance.evaluation_summary.primary_evaluated_component`
- **AND** `governance.evaluation_rollup.has_evaluated_component` MUST indicate whether `governance.evaluation_summary.evaluated_count` is greater than zero
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription governance decision summary SHALL expose primary action fields

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary` primary action fields derived from existing advisory `governance.action_summary` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes primary action fields

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.primary_action` MUST mirror `governance.action_summary.primary_action`
- **AND** `governance.decision_summary.primary_action_reason` MUST mirror `governance.action_summary.primary_reason`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes primary action fields

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.primary_action` MUST mirror `governance.action_summary.primary_action`
- **AND** `governance.decision_summary.primary_action_reason` MUST mirror `governance.action_summary.primary_reason`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription governance decision summary SHALL expose primary action reason source

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.primary_action_reason_source` derived from existing advisory `governance.action_summary.primary_reason_source` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes primary action reason source

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.primary_action_reason_source` MUST mirror `governance.action_summary.primary_reason_source`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes primary action reason source

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.primary_action_reason_source` MUST mirror `governance.action_summary.primary_reason_source`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription governance decision summary SHALL expose primary reason

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.primary_reason` derived from existing advisory `governance.reason_summary.primary_reason` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes primary reason

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.primary_reason` MUST mirror `governance.reason_summary.primary_reason`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes primary reason

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.primary_reason` MUST mirror `governance.reason_summary.primary_reason`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription governance decision summary SHALL expose reason key counts

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.reason_source_key_count` and `governance.decision_summary.reason_code_key_count` fields derived from existing advisory `governance.reason_summary` key-count data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes reason key counts

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.reason_source_key_count` MUST mirror `governance.reason_summary.source_key_count`
- **AND** `governance.decision_summary.reason_code_key_count` MUST mirror `governance.reason_summary.reason_code_key_count`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes reason key counts

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.reason_source_key_count` MUST mirror `governance.reason_summary.source_key_count`
- **AND** `governance.decision_summary.reason_code_key_count` MUST mirror `governance.reason_summary.reason_code_key_count`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription governance summary SHALL expose reconnect rollup

Subscription long-run status summaries SHALL include additive read-only `governance.reconnect_rollup` metadata derived from existing reconnect diagnostics without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Core status summary exposes reconnect rollup

- **WHEN** `build_subscription_watch_status_summary()` builds reconnect diagnostics
- **THEN** `governance.reconnect_rollup.staleness` MUST mirror `reconnect.staleness`
- **AND** `governance.reconnect_rollup.reconnect_count` MUST mirror `reconnect.reconnect_count`
- **AND** `governance.reconnect_rollup.consecutive_reconnect_failures` MUST mirror `reconnect.consecutive_reconnect_failures`
- **AND** `governance.reconnect_rollup.has_reconnects` MUST be true only when `reconnect_count` is a positive non-boolean integer
- **AND** `governance.reconnect_rollup.has_reconnect_failures` MUST be true only when `consecutive_reconnect_failures` is a positive non-boolean integer
- **AND** `governance.reconnect_rollup.has_last_error` MUST be true only when `reconnect.last_error` is a non-empty object
- **AND** `governance.reconnect_rollup.has_next_reconnect_at` MUST be true only when `reconnect.next_reconnect_at` is a non-empty string
- **AND** the rollup MUST remain a read-only projection.

#### Scenario: HTTP summary view projects reconnect rollup

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** the response MUST include `governance.reconnect_rollup` when the detailed governance payload provides it
- **AND** the response MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: CLI summary view projects reconnect rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `governance.reconnect_rollup` when the detailed governance payload provides it
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription status summary SHALL expose control rollup

Subscription long-run status summaries SHALL include additive read-only `status_summary.control_rollup` metadata derived from the existing reconciled `control` payload without changing lock handling, PID liveness checks, process ownership, restart, backoff, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Core status summary exposes control rollup

- **WHEN** `build_subscription_watch_status_summary()` receives a reconciled `control` payload
- **THEN** `status_summary.control_rollup.control_state` MUST mirror `control.state` or be `unknown` when absent
- **AND** `status_summary.control_rollup.control_active` MUST mirror boolean `control.active`
- **AND** `status_summary.control_rollup.has_control_run_id` MUST be true only when `control.run_id` is a non-empty string
- **AND** `status_summary.control_rollup.has_control_pid` MUST be true only when `control.pid` is a positive non-boolean integer
- **AND** `status_summary.control_rollup.control_reason` MUST mirror `control.reason` or be `null` when absent
- **AND** `status_summary.control_rollup.stale_process_state` MUST be true only when `control.reason` equals `stale_process_state`
- **AND** `status_summary.control_rollup.startup_persistence_failed` MUST be true only when `control.reason` equals `startup_persistence_failed`
- **AND** the rollup MUST remain a read-only projection.

#### Scenario: HTTP summary view projects control rollup

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** the response MUST include `status_summary.control_rollup` when the detailed status summary provides it
- **AND** the response MUST NOT acquire locks, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: CLI summary view projects control rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `status_summary.control_rollup` when the detailed status summary provides it
- **AND** the command MUST NOT acquire locks, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription status summary SHALL expose consistency rollup

Subscription long-run status summaries SHALL include additive read-only `status_summary.consistency_rollup` metadata derived from existing `control` and `watch_status` payloads without changing lock handling, PID-file reads, PID liveness checks, process ownership, restart, backoff, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Core status summary exposes consistency rollup

- **WHEN** `build_subscription_watch_status_summary()` receives `control` and `watch_status` payloads
- **THEN** `status_summary.consistency_rollup.control_state` MUST mirror `control.state` or be `unknown` when absent
- **AND** `status_summary.consistency_rollup.watch_state` MUST mirror `watch_status.state` or be `null` when absent
- **AND** `status_summary.consistency_rollup.has_watch_status` MUST be true only when `watch_status` is a non-empty object
- **AND** `status_summary.consistency_rollup.has_control_run_id` MUST be true only when `control.run_id` is a non-empty string
- **AND** `status_summary.consistency_rollup.has_watch_run_id` MUST be true only when `watch_status.run_id` is a non-empty string
- **AND** `status_summary.consistency_rollup.run_id_match` MUST compare run IDs only when both run IDs are present, otherwise be `null`
- **AND** `status_summary.consistency_rollup.state_match` MUST compare states only when both states are present, otherwise be `null`
- **AND** `status_summary.consistency_rollup.has_mismatch` MUST be true only when a comparable state or run ID is explicitly mismatched
- **AND** the rollup MUST remain a read-only projection.

#### Scenario: HTTP summary view projects consistency rollup

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** the response MUST include `status_summary.consistency_rollup` when the detailed status summary provides it
- **AND** the response MUST NOT acquire locks, read PID files, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: CLI summary view projects consistency rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `status_summary.consistency_rollup` when the detailed status summary provides it
- **AND** the command MUST NOT acquire locks, read PID files, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

### Requirement: Subscription watch-status SHALL expose read-only diagnostics view

HTTP and CLI watch-status commands SHALL expose an opt-in diagnostics view derived from existing summary rollups without changing reconnect, backoff, restart, lifecycle, HTTP route defaults, SSE, or event-stream behavior.

#### Scenario: CLI diagnostics view projects combined diagnostics

- **WHEN** a caller runs `bridge watch-status --view diagnostics`
- **THEN** the command MUST emit a compact payload with `result.mode` equal to `diagnostics`
- **AND** the payload MUST include a top-level `result.diagnostics` object
- **AND** diagnostics fields MUST be derived from existing summary rollups
- **AND** the command MUST NOT acquire locks, read PID files, signal processes, prove ownership, prove readiness, or trigger reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: Diagnostics view does not expose raw payloads

- **WHEN** diagnostics view is requested
- **THEN** the result MUST NOT expose raw `control` or raw `watch_status`
- **AND** the result MUST NOT expose full governance `reasons` or full governance `actions`.

### Requirement: Subscription watch-status diagnostics SHALL expose restartability summary

Subscription watch-status diagnostics SHALL include an additive read-only restartability summary derived from existing detailed status data without triggering lifecycle control.

#### Scenario: Diagnostics projects restartable active state

- **WHEN** diagnostics view is built from detailed status whose `control` payload is active and includes a valid persisted `start_request`
- **THEN** `diagnostics.restartability.ready` MUST be `true`
- **AND** `diagnostics.restartability.decision` MUST be `ready`
- **AND** `diagnostics.restartability.reason_codes` MUST be empty
- **AND** `diagnostics.restartability.start_request_summary` MUST include compact request shape fields
- **AND** diagnostics MUST NOT expose raw `control`, raw `watch_status`, full governance reasons, or full governance actions.

#### Scenario: Diagnostics projects blocked restartability reasons

- **WHEN** diagnostics view is built from detailed status that is not restartable
- **THEN** `diagnostics.restartability.ready` MUST be `false`
- **AND** `diagnostics.restartability.decision` MUST be `blocked`
- **AND** `diagnostics.restartability.reason_codes` MUST include stable reason code `NO_ACTIVE_RUN`, `MISSING_START_REQUEST`, or `INVALID_START_REQUEST`
- **AND** diagnostics MUST NOT stop, start, restart, signal, schedule backoff, or run a supervisor loop.

### Requirement: Subscription watch-status diagnostics SHALL expose latest restart observation

Subscription watch-status diagnostics SHALL include a compact read-only latest restart observation when detailed control state provides one.

#### Scenario: Diagnostics projects persisted restart observation

- **WHEN** diagnostics view is built from detailed status whose `control` payload includes `last_restart_observation`
- **THEN** `diagnostics.restart_observation.has_observation` MUST be `true`
- **AND** `diagnostics.restart_observation` MUST include stable summary fields for the previous run id, new run id, reason, stop state, start state, start request summary, and boundary
- **AND** diagnostics MUST NOT expose raw `control`, raw `watch_status`, raw stop result, raw start result, full start request, logs, command line, or event-stream payloads.

#### Scenario: Diagnostics has no restart observation

- **WHEN** diagnostics view is built from detailed status without a persisted restart observation
- **THEN** `diagnostics.restart_observation.has_observation` MUST be `false`
- **AND** diagnostics MUST NOT call restart preflight, stop, start, restart, signal, schedule backoff, or run a supervisor loop.

### Requirement: Subscription watch-status diagnostics SHALL expose restart backoff guard

Subscription watch-status diagnostics SHALL include compact read-only restart backoff guard metadata when detailed control state provides it.

#### Scenario: Diagnostics projects active restart backoff

- **WHEN** diagnostics view is built from detailed status whose `control` payload includes active `restart_backoff`
- **THEN** `diagnostics.restart_backoff.active` MUST be `true`
- **AND** diagnostics MUST include stable retry metadata and `BACKOFF_ACTIVE` reason code
- **AND** diagnostics MUST NOT expose raw control state, raw start result, full start request, logs, command line, HTTP health, or event-stream data.

#### Scenario: Diagnostics projects no restart backoff

- **WHEN** diagnostics view is built from detailed status without restart backoff metadata
- **THEN** `diagnostics.restart_backoff.active` MUST be `false`
- **AND** diagnostics MUST NOT call restart preflight, stop, start, restart, signal, schedule retry, or run a supervisor loop.

### Requirement: Subscription long-run status summary SHALL expose supervisor daemon projection

Subscription-watch status summary SHALL include an additive read-only `supervisor_daemon` projection when the background controller has a supervisor daemon status read model.

#### Scenario: Detailed status summary includes supervisor daemon projection

- **WHEN** subscription-watch background status is requested
- **AND** the controller can derive supervisor daemon status from its existing local supervisor statefile and pidfile evidence
- **THEN** `status_summary.supervisor_daemon` MUST include stable compact fields from the existing supervisor daemon status projection
- **AND** the projection MUST include `daemon_status`, `statefile_exists`, `statefile_valid`, `pidfile_exists`, `process_running`, `control_allowed`, and `boundary` when those fields are available
- **AND** the top-level detailed `supervisor_daemon` payload MUST remain present for detailed consumers

#### Scenario: Summary view preserves supervisor daemon projection

- **WHEN** bridge watch status is requested with summary view
- **THEN** the summary payload MUST include `status_summary.supervisor_daemon` when detailed status summary includes it
- **AND** the summary payload MUST NOT expose daemon command, settings, owner token, raw statefile content, or full detailed payload through this projection

#### Scenario: Supervisor daemon projection remains read-only

- **WHEN** `status_summary.supervisor_daemon` is produced
- **THEN** the projection MUST NOT start, stop, restart, supervise, backoff, probe, or mutate provider state
- **AND** the projection MUST NOT claim provider readiness, broker readiness, live行情 availability, production lifecycle health, or trading readiness

### Requirement: Subscription long-run status summary SHALL expose statefile ownership projection

Subscription-watch status summary SHALL include an additive read-only `statefile_ownership` projection when the background controller has local statefile ownership diagnostics.

#### Scenario: Detailed status summary includes statefile ownership projection

- **WHEN** subscription-watch background status is requested
- **AND** the controller derives local statefile ownership diagnostics from existing statefile and pidfile evidence
- **THEN** `status_summary.statefile_ownership` MUST include compact stable fields from the existing `statefile_ownership` diagnostic
- **AND** the projection MUST include `status`, `reason_codes`, `statefile_exists`, `pidfile_exists`, `active`, `control_state`, `pid_matches_owned_state`, and `boundary` when those fields are available
- **AND** the top-level detailed `statefile_ownership` payload MUST remain present for detailed consumers

#### Scenario: Summary view preserves statefile ownership projection

- **WHEN** bridge watch status is requested with summary view
- **THEN** the summary payload MUST include `status_summary.statefile_ownership` when detailed status summary includes it
- **AND** the summary payload MUST NOT expose raw statefile content, lock handles, command arguments, or full detailed payload through this projection

#### Scenario: Statefile ownership projection remains read-only

- **WHEN** `status_summary.statefile_ownership` is produced
- **THEN** the projection MUST NOT acquire the control lock, start, stop, restart, supervise, backoff, probe, or mutate provider state
- **AND** the projection MUST NOT claim provider readiness, broker readiness, live行情 availability, production lifecycle health, or process ownership beyond local PID evidence

### Requirement: Subscription HTTP summary view SHALL preserve local state projections

HTTP `GET /bridge/v1/watch/status?view=summary` SHALL preserve compact local-state projections already present in detailed `status_summary`.

#### Scenario: HTTP summary view includes statefile ownership projection

- **WHEN** HTTP watch status summary view is requested
- **AND** detailed status includes `status_summary.statefile_ownership`
- **THEN** the HTTP summary payload MUST include `status_summary.statefile_ownership`
- **AND** it MUST NOT expose raw statefile content, lock handles, command arguments, or full detailed payload through this projection

#### Scenario: HTTP summary view includes supervisor daemon projection

- **WHEN** HTTP watch status summary view is requested
- **AND** detailed status includes `status_summary.supervisor_daemon`
- **THEN** the HTTP summary payload MUST include `status_summary.supervisor_daemon`
- **AND** the existing top-level summary `supervisor_daemon` projection MAY remain present for compatibility
- **AND** the projection MUST NOT expose owner token, command, settings, raw statefile content, or full detailed payload

#### Scenario: HTTP local-state projections remain read-only

- **WHEN** HTTP summary view preserves local-state projections
- **THEN** it MUST NOT start, stop, restart, supervise, backoff, probe, mutate provider state, or stream events
- **AND** it MUST NOT claim provider readiness, broker readiness, live行情 availability, production lifecycle health, or trading readiness

### Requirement: Subscription summary views SHALL expose status summary boundary

CLI and HTTP subscription-watch summary views SHALL preserve the existing `status_summary.boundary` field when detailed status summary includes it.

#### Scenario: CLI summary view includes status summary boundary

- **WHEN** `bridge watch-status --view summary` is requested
- **AND** detailed status includes `status_summary.boundary`
- **THEN** the CLI summary payload MUST include `status_summary.boundary`
- **AND** the boundary MUST be copied without changing lifecycle behavior

#### Scenario: HTTP summary view includes status summary boundary

- **WHEN** HTTP `GET /bridge/v1/watch/status?view=summary` is requested
- **AND** detailed status includes `status_summary.boundary`
- **THEN** the HTTP summary payload MUST include `status_summary.boundary`
- **AND** the boundary MUST be copied without changing lifecycle behavior

#### Scenario: Status summary boundary remains non-executing

- **WHEN** summary views preserve `status_summary.boundary`
- **THEN** the projection MUST NOT start, stop, restart, supervise, backoff, probe, mutate provider state, stream events, or claim provider/broker/trading readiness

