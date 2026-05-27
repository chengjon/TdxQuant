## ADDED Requirements

### Requirement: Catalog selected-step summary SHALL expose source pair-key counts

Command catalog bundle plan summary views SHALL include additive read-only `selected_step_summary.step_source_name_key_count` and `selected_step_summary.step_source_entry_key_count` metadata derived from existing selected bundle plan pair-key counts without executing catalog entries, bundles, tasks, reports, trades, providers, or bundle steps.

#### Scenario: Selected-step summary exposes source pair-key counts

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** `selected_step_summary.step_source_name_key_count` and `selected_step_summary.step_source_entry_key_count` MUST be present
- **AND** both fields MUST mirror the already-derived top-level `step_source_name_key_count` and `step_source_entry_key_count` values
- **AND** existing selected-step range, first/last hints, and key count fields MUST remain available

#### Scenario: Source pair-key counts remain non-executing

- **WHEN** the selected-step summary is built
- **THEN** it MUST NOT execute catalog entries, bundle steps, task commands, report commands, trade commands, or provider calls
- **AND** it MUST NOT expose full manifests, option values, resolved argument values, or workflow-builder internals
- **AND** it MUST NOT claim broker readiness, trade safety, or execution coverage
