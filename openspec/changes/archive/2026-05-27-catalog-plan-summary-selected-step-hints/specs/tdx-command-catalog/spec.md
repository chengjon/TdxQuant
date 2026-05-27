## ADDED Requirements

### Requirement: Catalog plan summary SHALL expose selected step hint rollup

Command catalog plan summary views SHALL include additive read-only `plan_summary` selected-step hint metadata derived from the existing `selected_step_summary` payload without executing catalog entries, bundles, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Plan summary exposes selected step hints

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** `plan_summary.first_step_index`, `last_step_index`, `first_step_name`, `last_step_name`, `first_step_source`, `last_step_source`, `first_step_command_name`, and `last_step_command_name` MUST be present
- **AND** those fields MUST mirror the already-derived `selected_step_summary` values
- **AND** existing `plan_summary` and `selected_step_summary` sibling fields MUST remain available

#### Scenario: Selected step hints remain non-executing

- **WHEN** the planning summary is built
- **THEN** it MUST NOT execute bundle steps, resolve new arguments, or mutate catalog state
- **AND** it MUST NOT expose raw manifests, option values, resolved args, or workflow-builder internals
- **AND** it MUST NOT claim readiness or execution coverage
