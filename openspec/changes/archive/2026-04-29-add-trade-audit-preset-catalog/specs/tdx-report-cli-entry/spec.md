## ADDED Requirements

### Requirement: Report CLI preset catalog SHALL expose audit-oriented review presets once trade audit reports are stable
The system SHALL expose stable report preset definitions for the existing trade audit daily and period workflows so callers can reuse common review defaults without retyping command arguments.

#### Scenario: Caller lists audit daily review presets
- **WHEN** a caller executes the report preset listing command after trade audit daily reporting is stable
- **THEN** the preset catalog MUST include at least one stable preset mapped to the audit daily workflow

#### Scenario: Caller runs an audit period preset
- **WHEN** a caller executes a named report preset mapped to the audit period workflow
- **THEN** the report CLI MUST resolve the preset defaults and run the existing audit period workflow through the shared report dispatcher
