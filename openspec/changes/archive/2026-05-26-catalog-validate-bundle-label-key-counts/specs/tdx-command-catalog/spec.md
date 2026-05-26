## ADDED Requirements

### Requirement: Catalog Validate Bundle Label Key Counts

Catalog validate summary view SHALL expose read-only bundle label key-count fields derived from already projected label-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `bundle_label_counts`
- **THEN** the summary view MUST include `bundle_label_key_count` equal to the number of keys in `bundle_label_counts`
- **AND** this field MUST count distinct label keys, not bundles.

#### Scenario: Summary includes task/report bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `task_report_bundle_label_counts`
- **THEN** the summary view MUST include `task_report_bundle_label_key_count` equal to the number of keys in `task_report_bundle_label_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
