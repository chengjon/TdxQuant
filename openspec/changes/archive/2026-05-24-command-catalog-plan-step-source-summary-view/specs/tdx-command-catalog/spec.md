# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog plan summary SHALL expose selected step source counts

The command catalog SHALL include a compact `step_source_counts` object in bundle `plan` and `preview` summary views, derived from the selected resolved steps without executing catalog dispatch.

#### Scenario: Caller plans a mixed task/report bundle summary

- **WHEN** a caller executes `catalog plan --bundle <task-report-bundle> --view summary`
- **THEN** the summary view MUST include `step_source_counts` with counts for the selected task and report steps
- **AND** the summary view MUST continue to include non-execution provenance and constraints
- **AND** the underlying catalog step dispatch workflow MUST NOT be invoked

#### Scenario: Caller previews a filtered bundle summary

- **WHEN** a caller executes `catalog preview --bundle <bundle> --only-step <step> --view summary`
- **THEN** `step_source_counts` MUST reflect only the selected step range
- **AND** the summary view MUST continue to report the selected step count

