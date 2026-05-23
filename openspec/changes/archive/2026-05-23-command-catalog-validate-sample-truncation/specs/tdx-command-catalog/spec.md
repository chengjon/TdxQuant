## MODIFIED Requirements

### Requirement: Command catalog SHALL validate fixed registry entries without execution

The command catalog CLI SHALL provide a non-execution validation path that checks
selected catalog entries and bundles resolve through the existing registry
metadata and reports task/report bundle coverage.

#### Scenario: Caller validates the full catalog registry

- **WHEN** a caller runs `catalog validate --kind all`
- **THEN** the system MUST resolve all selected catalog entries and bundles without executing any task, report, trade, or bundle step
- **AND** the result MUST include entry count, bundle count, task/report bundle count, invalid count, and validation status

#### Scenario: Caller validates follow-up bundles by label

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the system MUST validate only selected bundles with that label
- **AND** the task/report bundle count MUST reflect bundles whose resolved steps include both task and report sources
- **AND** the result MUST include the bounded sample limit used for `task_report_bundle_samples`
- **AND** the result MUST indicate whether `task_report_bundle_samples` was truncated

#### Scenario: Caller validates an unsupported target

- **WHEN** a caller runs `catalog validate` for a missing entry or bundle
- **THEN** the system MUST return an invalid-request result with a structured error
- **AND** it MUST NOT execute any selected catalog target

### Requirement: Command catalog validate SHALL expose opt-in summary view

The command catalog validation workflow SHALL expose an opt-in summary view that projects validation counts and non-execution status without changing the default detailed validation payload.

#### Scenario: Caller validates follow-up bundles with summary view

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include validation mode, selected kind, selected label, bundle count, invalid count, and valid flag
- **AND** the summary payload MUST include `task_report_bundle_count`
- **AND** the summary payload MUST include a bounded deterministic `task_report_bundle_samples` list when matching task+report bundles exist
- **AND** the summary payload MUST include `task_report_bundle_sample_limit`
- **AND** the summary payload MUST include `task_report_bundle_sample_truncated`
- **AND** the summary payload MUST declare `non_execution=true`
- **AND** the summary payload MUST NOT include full entry or bundle detail rows

#### Scenario: Caller validates missing target with summary view

- **WHEN** a caller runs `catalog validate --bundle <missing> --view summary`
- **THEN** the summary payload MUST preserve the invalid request code and validation error details
- **AND** the summary payload MUST still declare `non_execution=true`

#### Scenario: Caller omits validate summary view

- **WHEN** a caller runs `catalog validate` without `--view summary`
- **THEN** the detailed validation payload MUST remain the default printed result
