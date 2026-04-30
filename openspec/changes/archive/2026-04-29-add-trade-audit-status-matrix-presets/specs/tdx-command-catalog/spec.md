## ADDED Requirements

### Requirement: Command catalog SHALL expose richer trade-audit status entries and review bundles once those status presets are stable
The system SHALL expose stable catalog entries for the richer confirmed/replayed trade-audit presets and allow at least one named confirmed-review bundle and at least one replay-review bundle composed from existing catalog entries.

#### Scenario: Caller lists richer trade-audit status catalog entries
- **WHEN** a caller lists catalog entries after richer trade-audit status presets are available
- **THEN** the catalog MUST include entries mapped to those richer status presets

#### Scenario: Caller lists richer trade-audit status review bundles
- **WHEN** a caller lists catalog bundles after richer trade-audit status presets are available
- **THEN** the catalog MUST include at least one confirmed-review bundle and at least one replay-review bundle composed from existing catalog entries
