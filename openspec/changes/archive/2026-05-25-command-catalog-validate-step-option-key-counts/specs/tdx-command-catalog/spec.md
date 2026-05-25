## ADDED Requirements

### Requirement: Catalog validate SHALL summarize selected bundle step option keys

`catalog validate` SHALL include additive read-only option-key count maps for selected resolved bundle steps without executing catalog entries, tasks, reports, trades, or bundle steps.

#### Scenario: Detailed validation counts selected bundle step option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `bundle_step_option_key_counts`
- **AND** `bundle_step_option_key_counts` MUST count option keys from selected resolved bundle steps whose `options` value is an object
- **AND** the validation payload MUST remain non-executing

#### Scenario: Detailed validation counts task/report bundle step option keys

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `task_report_bundle_step_option_key_counts`
- **AND** the count map MUST be derived only from selected bundles that contain both task and report steps
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves selected bundle step option-key counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `bundle_step_option_key_counts`
- **AND** the summary payload MUST include `task_report_bundle_step_option_key_counts`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection
