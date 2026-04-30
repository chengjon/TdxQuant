## ADDED Requirements

### Requirement: Command catalog SHALL expose richer audit diagnostics and confirm follow-up bundles once trade audit and split-step workflows are stable
The system SHALL expose stable catalog entries for rejected-oriented audit presets and allow named bundles that combine those diagnostics or combine current confirmation with existing report follow-up entries.

#### Scenario: Caller lists rejected audit catalog entries
- **WHEN** a caller lists catalog entries after rejected-oriented trade audit presets are available
- **THEN** the catalog MUST include entries mapped to those rejected-oriented presets

#### Scenario: Caller lists richer audit and confirm follow-up bundles
- **WHEN** a caller lists catalog bundles after stable rejected audit presets and split-step confirm workflows are available
- **THEN** the catalog MUST include at least one rejection-diagnostic bundle and at least one confirm follow-up bundle composed from existing catalog entries
