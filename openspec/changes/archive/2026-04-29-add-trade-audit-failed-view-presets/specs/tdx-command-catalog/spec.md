## ADDED Requirements

### Requirement: Command catalog SHALL expose failed-oriented trade-audit entries and a failure diagnostics bundle once those presets are stable
The system SHALL expose stable catalog entries for the failed-oriented trade-audit presets and allow at least one named bundle to combine failed audit review with an existing failure-oriented entry.

#### Scenario: Caller lists failed-oriented trade-audit catalog entries
- **WHEN** a caller lists catalog entries after failed-oriented trade-audit presets are available
- **THEN** the catalog MUST include entries mapped to those failed-oriented presets

#### Scenario: Caller lists a failed-oriented diagnostics bundle
- **WHEN** a caller lists catalog bundles after failed-oriented trade-audit presets are available
- **THEN** the catalog MUST include at least one failed-oriented diagnostics bundle composed from existing catalog entries
