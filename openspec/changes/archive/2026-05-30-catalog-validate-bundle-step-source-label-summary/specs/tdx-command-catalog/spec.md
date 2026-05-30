## ADDED Requirements

### Requirement: Catalog bundle validation summary SHALL expose bundle step source-label counts

`catalog validate` summary output for bundles SHALL expose deterministic counts joining each selected bundle step source with labels from the parent bundle, without executing catalog dispatch or any selected step.

#### Scenario: Followup bundle validation reports task/report source-label counts

- **WHEN** a maintainer runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_label_counts.task:followup`
- **AND** the summary payload MUST include `bundle_step_source_label_counts.report:followup`
- **AND** the summary payload MUST include `task_report_bundle_step_source_label_counts.task:followup`
- **AND** the summary payload MUST include `task_report_bundle_step_source_label_counts.report:followup`
- **AND** the matching key-count fields MUST equal the number of keys in each source-label count map
- **AND** the command MUST NOT execute catalog dispatch or any bundle step.

#### Scenario: Empty bundle validation reports empty source-label counts

- **WHEN** a maintainer runs `catalog validate --kind bundle --label no-such-label --view summary`
- **THEN** `bundle_step_source_label_counts` MUST be an empty map
- **AND** `task_report_bundle_step_source_label_counts` MUST be an empty map
- **AND** the matching key-count fields MUST be `0`
- **AND** the command MUST NOT execute catalog dispatch or any bundle step.
