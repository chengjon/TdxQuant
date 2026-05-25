## ADDED Requirements

### Requirement: Catalog validate SHALL expose selected entry label counts

`catalog validate` SHALL include additive read-only `entry_label_counts` for selected resolved catalog entries without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation counts selected entry labels

- **WHEN** a caller validates selected entries
- **THEN** the validation payload MUST include `entry_label_counts`
- **AND** `entry_label_counts` MUST count labels from resolved entries that matched the validation filters
- **AND** the validation payload MUST remain non-executing

#### Scenario: Bundle-only validation has empty entry label counts

- **WHEN** a caller validates only bundles
- **THEN** `entry_label_counts` MUST be an empty object
- **AND** existing bundle validation counts MUST remain unchanged

#### Scenario: Summary view preserves selected entry label counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `entry_label_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection
