## ADDED Requirements

### Requirement: Catalog Validate Entry Source/Label Key Counts

Catalog validate summary view SHALL expose read-only entry source and entry label key-count fields derived from already projected entry count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes entry source key count

- **GIVEN** a caller validates catalog entries with `--view summary`
- **WHEN** the summary view includes `entry_source_counts`
- **THEN** the summary view MUST include `entry_source_key_count` equal to the number of keys in `entry_source_counts`
- **AND** this field MUST count distinct projected entry source keys, not matched entries or executed entries.

#### Scenario: Summary includes entry label key count

- **GIVEN** a caller validates catalog entries with `--view summary`
- **WHEN** the summary view includes `entry_label_counts`
- **THEN** the summary view MUST include `entry_label_key_count` equal to the number of keys in `entry_label_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
