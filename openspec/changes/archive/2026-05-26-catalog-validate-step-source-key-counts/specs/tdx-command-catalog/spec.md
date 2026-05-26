## ADDED Requirements

### Requirement: Catalog Validate Step Source Key Counts

Catalog validate summary view SHALL expose read-only step source key-count fields derived from already projected source-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes bundle step source key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_step_source_counts`
- **THEN** the summary view MUST include `bundle_step_source_key_count` equal to the number of keys in `bundle_step_source_counts`
- **AND** this field MUST count distinct source keys, not resolved steps.

#### Scenario: Summary includes task/report bundle step source key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_step_source_counts`
- **THEN** the summary view MUST include `task_report_bundle_step_source_key_count` equal to the number of keys in `task_report_bundle_step_source_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
