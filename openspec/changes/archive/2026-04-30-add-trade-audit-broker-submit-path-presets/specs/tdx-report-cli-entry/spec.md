## ADDED Requirements

### Requirement: Report CLI SHALL expose broker-scoped submit-path exception presets once multidimensional broker filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `broker=pingan`, `methods=[buy_submit_once, confirm_current]`, and `statuses=[rejected, failed]` so callers can reuse broker-scoped submit-path exception diagnostics without retyping the same three-dimensional filter combination.

#### Scenario: Caller lists broker-scoped submit-path exception report presets
- **WHEN** a caller lists report presets after stable `broker + methods + statuses` trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-pingan-submit-path-exceptions` and `audit-period-pingan-submit-path-exceptions`

#### Scenario: Caller runs a broker-scoped submit-path exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `broker=pingan`, `methods=[buy_submit_once, confirm_current]`, and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
