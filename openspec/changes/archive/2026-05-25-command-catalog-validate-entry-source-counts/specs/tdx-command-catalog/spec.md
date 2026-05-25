## ADDED Requirements

### Requirement: Catalog validate SHALL expose selected entry source counts

`catalog validate` SHALL include additive read-only `entry_source_counts` for selected resolved catalog entries without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation counts selected entry sources

- **WHEN** a caller validates selected entries
- **THEN** the validation payload MUST include `entry_source_counts`
- **AND** `entry_source_counts` MUST count sources from resolved entries that matched the validation filters
- **AND** the validation payload MUST remain non-executing

#### Scenario: Bundle-only validation has empty entry source counts

- **WHEN** a caller validates only bundles
- **THEN** `entry_source_counts` MUST be an empty object
- **AND** existing bundle validation counts MUST remain unchanged

#### Scenario: Summary view preserves selected entry source counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `entry_source_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only aggregate projection
