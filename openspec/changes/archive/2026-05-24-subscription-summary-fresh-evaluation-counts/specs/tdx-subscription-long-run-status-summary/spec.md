# tdx-subscription-long-run-status-summary Delta

## ADDED Requirements

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
