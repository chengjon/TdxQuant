## ADDED Requirements

### Requirement: Catalog Validate Step Name/Entry Key Counts

Catalog validate summary view SHALL expose read-only selected bundle and task+report bundle step name/entry key-count fields derived from already projected step count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes selected bundle step name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_name_counts`
- **THEN** the summary view MUST include `bundle_step_name_key_count` equal to the number of keys in `bundle_step_name_counts`
- **AND** this field MUST count distinct projected step names, not resolved steps or executed steps.

#### Scenario: Summary includes selected bundle step entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_entry_counts`
- **THEN** the summary view MUST include `bundle_step_entry_key_count` equal to the number of keys in `bundle_step_entry_counts`
- **AND** this field MUST count distinct projected step entry keys, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_name_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_name_key_count` equal to the number of keys in `task_report_bundle_step_name_counts`
- **AND** this field MUST count distinct projected task+report step names, not resolved steps or executed steps.

#### Scenario: Summary includes task+report bundle step entry key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_entry_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_entry_key_count` equal to the number of keys in `task_report_bundle_step_entry_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
