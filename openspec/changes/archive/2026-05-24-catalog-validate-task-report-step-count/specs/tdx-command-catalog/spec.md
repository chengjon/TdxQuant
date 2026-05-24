# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog validation SHALL expose task report bundle step count

Catalog validation SHALL include an additive `task_report_bundle_step_count` scalar derived from the number of resolved steps in bundles that contain both task and report steps, without executing entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation includes step count

- **WHEN** a caller runs catalog validation for bundles that contain both task and report steps
- **THEN** the validation payload MUST include `task_report_bundle_step_count`
- **AND** the count MUST equal the total resolved step count across matching task/report bundles
- **AND** validation MUST remain non-executing

#### Scenario: Summary validation includes step count

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `task_report_bundle_step_count`
- **AND** existing task/report bundle samples and aggregate counts MUST remain present

#### Scenario: No matching task report bundles has zero step count

- **WHEN** catalog validation selects no task/report bundles
- **THEN** `task_report_bundle_step_count` MUST be `0`
- **AND** task/report bundle source and label counts MUST remain empty objects
