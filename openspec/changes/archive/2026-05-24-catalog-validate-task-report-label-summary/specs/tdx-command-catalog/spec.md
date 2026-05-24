# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize task/report bundle labels

Catalog validation SHALL include an additive `task_report_bundle_label_counts` object derived from labels on resolved bundles that contain both task and report steps, without executing entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation exposes task/report label counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_label_counts`
- **AND** the counts MUST be derived only from resolved bundles containing both task and report steps
- **AND** the validation MUST remain non-executing

#### Scenario: Summary validation projects task/report label counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_label_counts`
- **AND** the summary value MUST match the detailed validation value
- **AND** the summary payload MUST continue to omit full entry and bundle definitions

#### Scenario: Missing or empty matches produce empty label counts

- **WHEN** no resolved task+report bundles match validation filters
- **THEN** `task_report_bundle_label_counts` MUST be an empty object
- **AND** the validation payload MUST still report existing validity and error fields
