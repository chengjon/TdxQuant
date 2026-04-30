## ADDED Requirements

### Requirement: Report CLI SHALL expose rejected-oriented trade audit presets once stable trade audit reports support status filtering
The system SHALL expose stable report presets for rejected-oriented trade audit daily and period workflows so callers can reuse those diagnostics without retyping the same status filters.

#### Scenario: Caller lists rejected audit report presets
- **WHEN** a caller lists report presets after stable trade audit status filtering is available
- **THEN** the preset registry MUST include rejected-oriented presets for the existing trade audit daily and period workflows

#### Scenario: Caller runs a rejected audit report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `status=rejected`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
