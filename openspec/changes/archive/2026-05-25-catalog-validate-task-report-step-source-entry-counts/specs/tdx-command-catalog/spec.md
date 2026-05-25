## ADDED Requirements

### Requirement: Catalog validation SHALL expose task/report bundle step source-entry counts

`catalog validate` SHALL include additive `task_report_bundle_step_source_entry_counts` for selected resolved bundles that contain both task and report steps without executing task, report, trade, catalog entry, or bundle steps.

#### Scenario: Task/report bundle source-entry counts are included in detailed validation

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_source_entry_counts`
- **AND** keys MUST be `source:entry` strings derived from resolved task/report bundle steps
- **AND** the sum of `task_report_bundle_step_source_entry_counts` values MUST equal `task_report_bundle_step_count`
- **AND** validation MUST remain non-executing

#### Scenario: Non task/report selections have empty source-entry counts

- **WHEN** a caller validates selected bundles that do not contain both task and report steps
- **THEN** `task_report_bundle_step_source_entry_counts` MUST be an empty object

#### Scenario: Summary view preserves task/report source-entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_source_entry_counts`
- **AND** the summary payload MUST NOT include full bundle definitions
