## ADDED Requirements

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
