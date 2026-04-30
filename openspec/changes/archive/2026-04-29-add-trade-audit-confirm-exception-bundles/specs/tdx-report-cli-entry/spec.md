## ADDED Requirements

### Requirement: Report CLI SHALL expose confirm-oriented exception trade-audit presets once multidimensional filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `method=confirm_current` together with `statuses=[rejected, failed]` so callers can reuse confirm-step exception diagnostics without retyping the same multidimensional filters.

#### Scenario: Caller lists confirm-oriented exception report presets
- **WHEN** a caller lists report presets after stable `method + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-confirm-exceptions` and `audit-period-confirm-exceptions`

#### Scenario: Caller runs a confirm-oriented exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `method=confirm_current` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
