## ADDED Requirements

### Requirement: Command catalog validate SHALL expose bundle step count

The command catalog validation payload SHALL expose an additive read-only `bundle_step_count` scalar derived from the resolved bundle steps already processed by validation without executing catalog steps or changing dispatch behavior.

#### Scenario: Validation counts all resolved bundle steps

- **WHEN** a caller runs `catalog validate` against bundle rows
- **THEN** the validation payload MUST include `bundle_step_count`
- **AND** `bundle_step_count` MUST equal the total number of resolved steps across the selected bundles
- **AND** the validation payload MUST remain non-executing

#### Scenario: Summary view preserves bundle step count

- **WHEN** a caller runs `catalog validate --view summary`
- **THEN** the summary payload MUST include `bundle_step_count`
- **AND** the summary payload MUST mirror the detailed validation value
- **AND** the summary payload MUST remain a read-only projection
