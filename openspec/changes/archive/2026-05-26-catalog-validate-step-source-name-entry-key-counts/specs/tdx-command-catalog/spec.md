## ADDED Requirements

### Requirement: Catalog Validate Step Source-Name/Source-Entry Key Counts

Catalog validate summary view SHALL expose read-only selected bundle and task+report bundle source-qualified step name/entry key-count fields derived from already projected step count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes selected bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_name_counts`
- **THEN** the summary view MUST include `bundle_step_source_name_key_count` equal to the number of keys in `bundle_step_source_name_counts`
- **AND** this field MUST count distinct projected `source:name` keys, not resolved steps or executed steps.

#### Scenario: Summary includes selected bundle step source-entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_entry_counts`
- **THEN** the summary view MUST include `bundle_step_source_entry_key_count` equal to the number of keys in `bundle_step_source_entry_counts`
- **AND** this field MUST count distinct projected `source:entry` keys, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_name_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_name_key_count` equal to the number of keys in `task_report_bundle_step_source_name_counts`
- **AND** this field MUST count distinct projected task+report `source:name` keys, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step source-entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_entry_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_entry_key_count` equal to the number of keys in `task_report_bundle_step_source_entry_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
