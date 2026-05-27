## ADDED Requirements

### Requirement: Catalog bundle plan summary SHALL expose selected step summary

`catalog plan --view summary` and `catalog preview --view summary` for bundle targets SHALL include additive read-only `selected_step_summary` metadata derived from existing selected-step fields, bounded step views, and step count maps without executing catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

#### Scenario: Bundle plan summary includes selected step summary

- **WHEN** a caller runs `catalog plan --bundle confirm-complete-review --view summary`
- **THEN** the summary payload MUST include `selected_step_summary`
- **AND** the object MUST derive selected step count, optional from/to step boundaries, first/last selected step hints, and key counts from existing summary siblings
- **AND** existing `steps`, count maps, `constraints`, and `plan_outcome` MUST remain available

#### Scenario: Selected step summary remains non-executing

- **WHEN** catalog plan or preview reports `selected_step_summary`
- **THEN** the object MUST NOT indicate that any entry, bundle, task/report step, trade command, provider call, or workflow action was executed
- **AND** the summary MUST NOT claim workflow-builder support, broker readiness, trade safety approval, or execution coverage
