## ADDED Requirements

### Requirement: Command catalog SHALL expose broker-scoped submit-path exception entries and bundles once broker-scoped presets are stable
The system SHALL expose stable catalog entries mapped to broker-scoped submit-path exception trade-audit presets and allow named bundles that either combine those diagnostics with existing failure-oriented review or combine current confirmation with the new broker-scoped submit-path exception review.

#### Scenario: Caller lists broker-scoped submit-path exception catalog entries
- **WHEN** a caller lists catalog entries after broker-scoped submit-path exception trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to `audit-daily-pingan-submit-path-exceptions` and `audit-period-pingan-submit-path-exceptions`

#### Scenario: Caller lists broker-scoped submit-path diagnostics and follow-up bundles
- **WHEN** a caller lists catalog bundles after broker-scoped submit-path exception presets and stable confirm workflows are available
- **THEN** the catalog MUST include at least one broker-scoped submit-path diagnostics bundle and at least one broker-scoped submit-path follow-up bundle composed from existing catalog entries
