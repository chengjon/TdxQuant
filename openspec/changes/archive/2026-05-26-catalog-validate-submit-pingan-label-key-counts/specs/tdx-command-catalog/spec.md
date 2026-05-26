## ADDED Requirements

### Requirement: Catalog Validate Submit/PingAn Label Key Counts

Catalog validate summary view SHALL expose read-only submit-once and PingAn bundle label key-count fields derived from already projected subset label-count maps, without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Summary includes submit-once bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `submit_once_bundle_label_counts`
- **THEN** the summary view MUST include `submit_once_bundle_label_key_count` equal to the number of keys in `submit_once_bundle_label_counts`
- **AND** this field MUST count distinct label keys, not bundles.

#### Scenario: Summary includes PingAn bundle label key count

- **GIVEN** a caller validates catalog bundles with `--view summary`
- **WHEN** the summary view includes `pingan_bundle_label_counts`
- **THEN** the summary view MUST include `pingan_bundle_label_key_count` equal to the number of keys in `pingan_bundle_label_counts`
- **AND** this field MUST NOT imply complete workflow coverage, execution readiness, broker readiness, or trading safety.
