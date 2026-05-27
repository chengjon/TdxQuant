## ADDED Requirements

### Requirement: Catalog plan summary SHALL expose selected entry hint rollup

Command catalog plan summary views SHALL include additive read-only `plan_summary.first_step_entry` and `plan_summary.last_step_entry` metadata derived from the existing `selected_step_summary` payload without executing catalog entries, bundles, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Plan summary exposes selected entry hints

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** `plan_summary.first_step_entry` and `plan_summary.last_step_entry` MUST be present
- **AND** both fields MUST mirror the already-derived `selected_step_summary` values
- **AND** existing `plan_summary`, `selected_step_summary`, and non-execution metadata MUST remain available

#### Scenario: Selected entry hints remain non-executing

- **WHEN** the planning summary is built
- **THEN** it MUST NOT execute catalog entries, bundle steps, task commands, report commands, trade commands, or provider calls
- **AND** it MUST NOT expose full manifests, option values, resolved argument values, or workflow-builder internals
- **AND** it MUST NOT claim broker readiness, trade safety, or execution coverage
