## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize submit-once and PingAn step source entries

`catalog validate` SHALL include additive `submit_once_bundle_step_source_entry_counts` and `pingan_bundle_step_source_entry_counts` for selected resolved submit-once and PingAn bundle subsets without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts submit-once and PingAn source entries

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `submit_once_bundle_step_source_entry_counts`
- **AND** the validation payload MUST include `pingan_bundle_step_source_entry_counts`
- **AND** each key MUST be formatted as `source:entry`
- **AND** each count map MUST be derived only from the matching selected resolved bundle subset
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty submit-once and PingAn source-entry counts

- **WHEN** a caller validates only catalog entries
- **THEN** `submit_once_bundle_step_source_entry_counts` MUST be an empty object
- **AND** `pingan_bundle_step_source_entry_counts` MUST be an empty object

#### Scenario: Summary view preserves submit-once and PingAn source-entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_step_source_entry_counts`
- **AND** the summary payload MUST include `pingan_bundle_step_source_entry_counts`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection
