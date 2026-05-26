## ADDED Requirements

### Requirement: Catalog Validate Bundle/Task-Report Option-Key Counts

Catalog validate summary view SHALL expose read-only selected bundle and task+report option-key/source-option-key key-count fields derived from already projected step option count maps, without exposing option values or executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes selected bundle step option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_option_key_counts`
- **THEN** the summary view MUST include `bundle_step_option_key_count` equal to the number of keys in `bundle_step_option_key_counts`
- **AND** this field MUST count distinct projected option keys, not resolved steps or option values.

#### Scenario: Summary includes selected bundle step source-option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_option_key_counts`
- **THEN** the summary view MUST include `bundle_step_source_option_key_count` equal to the number of keys in `bundle_step_source_option_key_counts`
- **AND** this field MUST count distinct projected `source:option_key` keys, not resolved steps or option values.

#### Scenario: Summary includes task+report bundle step option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_option_key_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_option_key_count` equal to the number of keys in `task_report_bundle_step_option_key_counts`
- **AND** this field MUST count distinct projected task+report option keys, not resolved steps or option values.

#### Scenario: Summary includes task+report bundle step source-option-key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_option_key_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_option_key_count` equal to the number of keys in `task_report_bundle_step_source_option_key_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, option semantic validation, or trading safety.
