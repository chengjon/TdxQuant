# tdx-subscription-long-run-status-summary Spec Delta

## ADDED Requirements

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
