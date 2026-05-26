## ADDED Requirements

### Requirement: Catalog Validate Submit/PingAn Step Source-Name Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle step source-name key-count fields derived from already projected subset step `source:name` count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_step_source_name_counts`
- **THEN** the summary view MUST include `submit_once_bundle_step_source_name_key_count` equal to the number of keys in `submit_once_bundle_step_source_name_counts`
- **AND** this field MUST count distinct `source:name` keys, not resolved steps.

#### Scenario: Summary includes PingAn bundle step source-name key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_step_source_name_counts`
- **THEN** the summary view MUST include `pingan_bundle_step_source_name_key_count` equal to the number of keys in `pingan_bundle_step_source_name_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
