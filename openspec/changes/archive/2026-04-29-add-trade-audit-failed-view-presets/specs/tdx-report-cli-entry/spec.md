## ADDED Requirements

### Requirement: Report CLI SHALL expose failed-oriented stable trade-audit presets once failed status filtering is stable
The system SHALL expose stable report presets for failed-oriented trade-audit daily and period workflows so callers can reuse those diagnostics without repeating the same status filter.

#### Scenario: Caller lists failed-oriented trade-audit report presets
- **WHEN** a caller lists report presets after stable `status=failed` filtering is available for trade-audit reports
- **THEN** the preset registry MUST include failed-oriented presets for the existing trade-audit daily and period workflows

#### Scenario: Caller runs a failed-oriented trade-audit report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `status=failed`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
