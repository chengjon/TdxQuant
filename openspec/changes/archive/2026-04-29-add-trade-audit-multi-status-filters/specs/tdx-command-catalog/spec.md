## ADDED Requirements

### Requirement: Command catalog SHALL expose exception-oriented trade-audit presets and a diagnostics bundle once multi-status filtering is stable
The system SHALL expose stable preset-backed catalog entries for exception-oriented trade-audit review and allow at least one named diagnostics bundle to combine that review with an existing failure-oriented entry.

#### Scenario: Caller lists exception-oriented trade-audit entries
- **WHEN** a caller lists catalog entries after multi-status trade-audit filtering is available
- **THEN** the catalog MUST include entries backed by stable exception-oriented trade-audit presets

#### Scenario: Caller lists an exception diagnostics bundle
- **WHEN** a caller lists catalog bundles after multi-status trade-audit filtering is available
- **THEN** the catalog MUST include at least one exception-oriented diagnostics bundle composed from existing catalog entries
