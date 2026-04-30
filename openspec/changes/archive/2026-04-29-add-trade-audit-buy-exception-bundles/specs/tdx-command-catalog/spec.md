## ADDED Requirements

### Requirement: Command catalog SHALL expose buy-oriented exception audit entries and bundles once multidimensional presets and guarded-buy workflows are stable
The system SHALL expose stable catalog entries mapped to buy-oriented exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine guarded-buy follow-up with the new buy exception review.

#### Scenario: Caller lists buy-oriented exception catalog entries
- **WHEN** a caller lists catalog entries after buy-oriented exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-buy-exceptions` and `audit-period-buy-exceptions`

#### Scenario: Caller lists buy-oriented diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after buy-oriented exception presets and guarded-buy workflows are stable
- **THEN** the catalog MUST include at least one buy-oriented diagnostics bundle and at least one buy-oriented follow-up bundle composed from existing catalog entries
