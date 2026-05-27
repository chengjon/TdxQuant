## ADDED Requirements

### Requirement: Command catalog plan summary SHALL expose selected step entry counts

The command catalog SHALL include additive read-only `step_entry_counts` maps in `selected_step_summary` and `plan_summary` for bundle `plan` and `preview` summary views, derived from already-selected resolved steps without executing catalog dispatch.

#### Scenario: Plan summary includes selected step entry counts

- **WHEN** a caller executes `catalog plan --bundle <task-report-bundle> --view summary`
- **THEN** the summary view MUST include `selected_step_summary.step_entry_counts`
- **AND** the summary view MUST include `plan_summary.step_entry_counts`
- **AND** both maps MUST be derived from the selected resolved steps
- **AND** the summary view MUST continue to include non-execution provenance and constraints
- **AND** the underlying catalog step dispatch workflow MUST NOT be invoked

#### Scenario: Preview summary includes selected step entry counts

- **WHEN** a caller executes `catalog preview --bundle <task-report-bundle> --view summary`
- **THEN** `plan_summary.step_entry_counts` MUST match `selected_step_summary.step_entry_counts`
- **AND** the summary view MUST continue to report the selected step count and source key count
- **AND** the preview MUST remain non-executing
