## ADDED Requirements

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
