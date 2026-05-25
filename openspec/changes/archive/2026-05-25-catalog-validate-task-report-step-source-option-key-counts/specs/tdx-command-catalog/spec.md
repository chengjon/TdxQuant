## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize task/report step source option keys

`catalog validate` SHALL include additive `task_report_bundle_step_source_option_key_counts` for selected resolved bundles that contain both task and report steps without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts task/report source option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_option_key_counts`
- **AND** each key MUST be formatted as `source:option_key`
- **AND** the count map MUST be derived only from selected bundles that contain both task and report steps
- **AND** the sum of values MUST equal the sum of `task_report_bundle_step_option_key_counts` values for resolved task/report bundle steps with a source
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty task/report source option-key counts

- **WHEN** a caller validates only catalog entries
- **THEN** `task_report_bundle_step_source_option_key_counts` MUST be an empty object

#### Scenario: Summary view preserves task/report source option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_option_key_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection
