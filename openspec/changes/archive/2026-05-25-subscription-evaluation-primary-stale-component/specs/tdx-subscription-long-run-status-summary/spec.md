## ADDED Requirements

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

