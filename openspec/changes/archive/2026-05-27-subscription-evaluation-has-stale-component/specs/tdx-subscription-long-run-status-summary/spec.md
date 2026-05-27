## ADDED Requirements

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
