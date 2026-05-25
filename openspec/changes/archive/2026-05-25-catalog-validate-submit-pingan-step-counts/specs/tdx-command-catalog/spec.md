## ADDED Requirements

### Requirement: Command catalog validate SHALL summarize submit-once and PingAn step counts

`catalog validate` SHALL include additive `submit_once_bundle_step_count` and `pingan_bundle_step_count` for selected resolved submit-once and PingAn bundle subsets without executing catalog entries, task commands, reports, trades, or bundle steps.

#### Scenario: Bundle validation counts submit-once and PingAn steps

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the validation payload MUST include `submit_once_bundle_step_count`
- **AND** the validation payload MUST include `pingan_bundle_step_count`
- **AND** each count MUST be derived only from the matching selected resolved bundle subset
- **AND** validation MUST NOT execute catalog entries, task commands, reports, trades, or bundle steps

#### Scenario: Non-bundle selections have zero submit-once and PingAn step counts

- **WHEN** a caller validates only catalog entries
- **THEN** `submit_once_bundle_step_count` MUST be `0`
- **AND** `pingan_bundle_step_count` MUST be `0`

#### Scenario: Summary view preserves submit-once and PingAn step counts

- **WHEN** a caller runs `catalog validate --kind bundle --label followup --view summary`
- **THEN** the summary payload MUST include `submit_once_bundle_step_count`
- **AND** the summary payload MUST include `pingan_bundle_step_count`
- **AND** both summary values MUST mirror the detailed validation values
- **AND** the summary payload MUST remain a read-only aggregate projection
