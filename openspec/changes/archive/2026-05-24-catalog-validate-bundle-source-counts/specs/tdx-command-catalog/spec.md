## ADDED Requirements

### Requirement: Catalog validate SHALL expose selected bundle step source counts

`catalog validate` SHALL include an additive read-only `bundle_step_source_counts` object for selected bundle validation results, derived only from resolved bundle steps and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Bundle validation reports selected step source counts

- **WHEN** a caller validates selected bundles
- **THEN** the validation payload MUST include `bundle_step_source_counts`
- **AND** `bundle_step_source_counts` MUST count step sources from the selected resolved bundles
- **AND** the sum of `bundle_step_source_counts` values MUST equal `bundle_step_count`
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves selected step source counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_source_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection
