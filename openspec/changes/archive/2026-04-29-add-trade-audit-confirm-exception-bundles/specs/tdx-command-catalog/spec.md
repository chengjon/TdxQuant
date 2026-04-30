## ADDED Requirements

### Requirement: Command catalog SHALL expose confirm-oriented exception audit entries and bundles once multidimensional presets and split-step confirm workflows are stable
The system SHALL expose stable catalog entries mapped to confirm-oriented exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine current confirmation with the new confirm-oriented exception review.

#### Scenario: Caller lists confirm-oriented exception catalog entries
- **WHEN** a caller lists catalog entries after confirm-oriented exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-confirm-exceptions` and `audit-period-confirm-exceptions`

#### Scenario: Caller lists confirm-oriented diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after confirm-oriented exception presets and split-step confirm workflows are stable
- **THEN** the catalog MUST include at least one confirm-oriented diagnostics bundle and at least one confirm-oriented follow-up bundle composed from existing catalog entries
