## ADDED Requirements

### Requirement: Command catalog SHALL expose audit-oriented report entries and a diagnostic bundle once trade audit reports are stable
The system SHALL expose stable catalog entries for the existing trade audit report presets and allow at least one named bundle to combine audit review with an existing diagnostic entry.

#### Scenario: Caller lists audit-oriented catalog entries
- **WHEN** a caller lists catalog entries after stable trade audit report presets are available
- **THEN** the catalog MUST include audit-oriented report entries mapped to those presets

#### Scenario: Caller lists an audit diagnostic bundle
- **WHEN** a caller lists catalog bundles after stable trade audit report presets are available
- **THEN** the catalog MUST include at least one audit-oriented bundle composed from existing catalog entries
