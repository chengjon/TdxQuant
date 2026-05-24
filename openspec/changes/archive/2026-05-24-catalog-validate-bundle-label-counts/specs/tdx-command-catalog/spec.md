## ADDED Requirements

### Requirement: Catalog validate SHALL expose selected bundle label counts

`catalog validate` SHALL include an additive read-only `bundle_label_counts` object for selected bundle validation results, derived only from resolved bundle labels and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Bundle validation reports selected label counts

- **WHEN** a caller validates selected bundles
- **THEN** the validation payload MUST include `bundle_label_counts`
- **AND** `bundle_label_counts` MUST count labels from the selected resolved bundles
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves selected label counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_label_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection
