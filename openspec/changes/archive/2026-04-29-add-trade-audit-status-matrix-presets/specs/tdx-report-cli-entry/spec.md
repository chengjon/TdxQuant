## ADDED Requirements

### Requirement: Report CLI SHALL expose a richer stable trade-audit status preset matrix once status filtering is stable
The system SHALL expose additional stable report presets for confirmed-period and replayed-oriented trade-audit workflows so callers can reuse those review views without repeating the same status filters.

#### Scenario: Caller lists richer trade-audit status report presets
- **WHEN** a caller lists report presets after stable trade-audit status filtering is available
- **THEN** the preset registry MUST include presets for `audit-period-confirmed`, `audit-daily-replayed`, and `audit-period-replayed`

#### Scenario: Caller runs a richer trade-audit status report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `status=confirmed` or `status=replayed`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
