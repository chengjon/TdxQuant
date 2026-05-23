## MODIFIED Requirements

### Requirement: Command catalog validate SHALL expose opt-in summary view

The command catalog validation workflow SHALL expose an opt-in summary view that projects validation counts and non-execution status without changing the default detailed validation payload.

#### Scenario: Caller validates follow-up bundles with summary view

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include validation mode, selected kind, selected label, bundle count, invalid count, and valid flag
- **AND** the summary payload MUST include `task_report_bundle_count`
- **AND** the summary payload MUST include a bounded deterministic `task_report_bundle_samples` list when matching task+report bundles exist
- **AND** the summary payload MUST declare `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows

#### Scenario: Caller validates missing target with summary view

- **WHEN** a caller runs `catalog validate --bundle <missing> --view summary`
- **THEN** the summary payload MUST preserve the invalid request code and validation error details
- **AND** the summary payload MUST still declare `non_execution=true`

#### Scenario: Caller omits validate summary view

- **WHEN** a caller runs `catalog validate` without `--view summary`
- **THEN** the detailed validation payload MUST remain the default printed result
