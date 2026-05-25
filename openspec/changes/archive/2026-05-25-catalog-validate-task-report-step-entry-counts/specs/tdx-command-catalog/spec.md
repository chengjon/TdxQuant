## ADDED Requirements

### Requirement: Catalog validation SHALL expose task/report bundle step entry counts

`catalog validate` SHALL include additive `task_report_bundle_step_entry_counts` for selected resolved bundles that contain both task and report steps without executing task, report, trade, or bundle steps.

#### Scenario: Detailed validation counts task/report bundle step entries

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_entry_counts`
- **AND** the sum of `task_report_bundle_step_entry_counts` values MUST equal `task_report_bundle_step_count`
- **AND** the count keys MUST be catalog step `entry` values

#### Scenario: Summary view preserves task/report bundle step entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_entry_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection

