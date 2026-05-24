# tdx-command-catalog Delta

## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize selected bundle step entries

`catalog validate` SHALL include an additive read-only `bundle_step_entry_counts` object for selected bundle validation results, derived only from resolved bundle step entries and without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation includes selected bundle step entry counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_entry_counts`
- **AND** `bundle_step_entry_counts` MUST count step entries from the selected resolved bundles
- **AND** the sum of `bundle_step_entry_counts` values MUST equal `bundle_step_count`

#### Scenario: Summary view preserves selected bundle step entry counts

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_entry_counts`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection
