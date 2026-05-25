## ADDED Requirements

### Requirement: Catalog validation SHALL expose bundle step source-entry counts

`catalog validate` SHALL include additive `bundle_step_source_entry_counts` for selected resolved bundle steps without executing catalog entries, task entries, report entries, trade commands, or bundle steps.

#### Scenario: Bundle source-entry counts are included in detailed validation

- **WHEN** a caller validates selected catalog bundles
- **THEN** the validation payload MUST include `bundle_step_source_entry_counts`
- **AND** keys MUST be `source:entry` strings derived from selected resolved bundle steps
- **AND** the sum of `bundle_step_source_entry_counts` values MUST equal `bundle_step_count`
- **AND** validation MUST remain non-executing

#### Scenario: Non-bundle selections have empty source-entry counts

- **WHEN** a caller validates only catalog entries
- **THEN** `bundle_step_source_entry_counts` MUST be an empty object

#### Scenario: Summary view preserves bundle source-entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_entry_counts`
- **AND** the summary payload MUST NOT include full bundle definitions
