## ADDED Requirements

### Requirement: Report CLI SHALL expose submit-once-oriented exception trade-audit presets once multidimensional filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `method=buy_submit_once` together with `statuses=[rejected, failed]` so callers can reuse full-submit exception diagnostics without retyping the same multidimensional filters.

#### Scenario: Caller lists submit-once-oriented exception report presets
- **WHEN** a caller lists report presets after stable `method + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-submit-once-exceptions` and `audit-period-submit-once-exceptions`

#### Scenario: Caller runs a submit-once-oriented exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `method=buy_submit_once` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
