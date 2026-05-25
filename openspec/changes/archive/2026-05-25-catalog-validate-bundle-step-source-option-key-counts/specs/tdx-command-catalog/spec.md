## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize selected bundle step source option keys

`catalog validate` SHALL include additive `bundle_step_source_option_key_counts` for selected resolved bundle steps without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts source option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_source_option_key_counts`
- **AND** each key MUST be formatted as `source:option_key`
- **AND** the sum of values MUST equal the sum of `bundle_step_option_key_counts` values for resolved steps with a source
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have empty source option-key counts

- **WHEN** a caller validates only catalog entries
- **THEN** `bundle_step_source_option_key_counts` MUST be an empty object

#### Scenario: Summary view preserves source option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_option_key_counts`
- **AND** the summary payload MUST NOT include full bundle definitions

