## ADDED Requirements

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
