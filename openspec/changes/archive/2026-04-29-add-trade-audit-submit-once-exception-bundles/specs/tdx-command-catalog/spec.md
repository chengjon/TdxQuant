## ADDED Requirements

### Requirement: Command catalog SHALL expose submit-once-oriented exception audit entries and bundles once multidimensional presets and full-submit workflows are stable
The system SHALL expose stable catalog entries mapped to submit-once-oriented exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine full-submit follow-up with the new submit-once exception review.

#### Scenario: Caller lists submit-once-oriented exception catalog entries
- **WHEN** a caller lists catalog entries after submit-once-oriented exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-submit-once-exceptions` and `audit-period-submit-once-exceptions`

#### Scenario: Caller lists submit-once-oriented diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after submit-once-oriented exception presets and full-submit workflows are stable
- **THEN** the catalog MUST include at least one submit-once-oriented diagnostics bundle and at least one submit-once-oriented follow-up bundle composed from existing catalog entries
