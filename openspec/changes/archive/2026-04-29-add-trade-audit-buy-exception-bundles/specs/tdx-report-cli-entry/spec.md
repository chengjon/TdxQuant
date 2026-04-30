## ADDED Requirements

### Requirement: Report CLI SHALL expose buy-oriented exception trade-audit presets once multidimensional filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `method=buy` together with `statuses=[rejected, failed]` so callers can reuse base-buy exception diagnostics without retyping the same multidimensional filters.

#### Scenario: Caller lists buy-oriented exception report presets
- **WHEN** a caller lists report presets after stable `method + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-buy-exceptions` and `audit-period-buy-exceptions`

#### Scenario: Caller runs a buy-oriented exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `method=buy` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
