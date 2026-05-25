## ADDED Requirements

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

