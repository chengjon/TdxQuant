## ADDED Requirements

### Requirement: Command catalog SHALL expose submit-path exception entries and bundles once multi-method presets are stable
The system SHALL expose stable catalog entries mapped to submit-path exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine current confirmation with the new submit-path exception review.

#### Scenario: Caller lists submit-path exception catalog entries
- **WHEN** a caller lists catalog entries after submit-path exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-submit-path-exceptions` and `audit-period-submit-path-exceptions`

#### Scenario: Caller lists submit-path diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after submit-path exception presets and stable confirm workflows are available
- **THEN** the catalog MUST include at least one submit-path diagnostics bundle and at least one submit-path follow-up bundle composed from existing catalog entries
