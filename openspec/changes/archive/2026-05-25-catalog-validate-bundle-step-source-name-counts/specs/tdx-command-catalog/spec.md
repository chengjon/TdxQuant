## ADDED Requirements

### Requirement: Catalog validation SHALL expose selected bundle step source/name counts

`catalog validate` SHALL include additive `bundle_step_source_name_counts` for selected resolved bundle steps without executing task, report, trade, or bundle steps.

#### Scenario: Detailed validation counts selected bundle step source/name pairs

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_source_name_counts`
- **AND** keys MUST combine the selected step `source` and `name` as `source:name`
- **AND** the sum of `bundle_step_source_name_counts` values MUST equal `bundle_step_count`

#### Scenario: Summary view preserves selected bundle step source/name counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_name_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection
