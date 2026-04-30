## ADDED Requirements

### Requirement: Command catalog SHALL expose split-step desktop trade task entries and a confirm follow-up bundle once the workflows are stable
The system SHALL expose stable catalog entries for the existing split-step desktop trade task presets and allow at least one named bundle to combine confirmation with an existing audit review entry.

#### Scenario: Caller lists split-step catalog entries
- **WHEN** a caller lists catalog entries after stable split-step desktop trade task presets are available
- **THEN** the catalog MUST include split-step task entries mapped to those presets

#### Scenario: Caller lists a confirm follow-up bundle
- **WHEN** a caller lists catalog bundles after stable split-step desktop trade task presets are available
- **THEN** the catalog MUST include at least one confirm-oriented bundle composed from existing catalog entries
