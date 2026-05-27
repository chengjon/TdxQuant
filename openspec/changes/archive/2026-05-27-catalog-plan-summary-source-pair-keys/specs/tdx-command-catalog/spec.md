## ADDED Requirements

### Requirement: Catalog plan summary SHALL expose source pair-key counts

Command catalog bundle plan summary views SHALL include additive read-only `plan_summary.step_source_name_key_count` and `plan_summary.step_source_entry_key_count` metadata derived from the existing selected-step summary without executing catalog entries, bundles, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Plan summary exposes source pair-key counts

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** `plan_summary.step_source_name_key_count` and `plan_summary.step_source_entry_key_count` MUST be present
- **AND** both fields MUST mirror the already-derived `selected_step_summary` pair-key count values
- **AND** existing `plan_summary`, `selected_step_summary`, and non-execution metadata MUST remain available

#### Scenario: Plan summary source pair-key counts remain non-executing

- **WHEN** the planning summary is built
- **THEN** it MUST NOT execute catalog entries, bundle steps, task commands, report commands, trade commands, or provider calls
- **AND** it MUST NOT expose full manifests, option values, resolved argument values, or workflow-builder internals
- **AND** it MUST NOT claim broker readiness, trade safety, or execution coverage
