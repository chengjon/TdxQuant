# tdx-subscription-long-run-status-summary Delta

## ADDED Requirements

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

