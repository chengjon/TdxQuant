## ADDED Requirements

### Requirement: Report and task CLI SHALL expose multi-method trade-audit filtering without breaking existing single-method calls
The system SHALL expose a stable CLI way to express multi-method trade-audit filtering for the existing daily and period workflows while preserving the current single-method option.

#### Scenario: Caller passes repeated multi-method arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow and repeats the multi-method argument
- **THEN** the CLI MUST forward the collected methods into the existing stable workflow using OR semantics

#### Scenario: Caller mixes single-method and multi-method CLI arguments
- **WHEN** a caller invokes the stable trade-audit daily or period CLI workflow with both single-method and multi-method arguments
- **THEN** the CLI MUST reject the request as invalid instead of guessing precedence

### Requirement: Report CLI SHALL expose submit-path exception presets once multi-method filtering is stable
The system SHALL expose stable report presets for trade-audit daily and period workflows that fix `methods=[buy_submit_once, confirm_current]` together with `statuses=[rejected, failed]` so callers can reuse submit-path exception diagnostics.

#### Scenario: Caller lists submit-path exception report presets
- **WHEN** a caller lists report presets after stable multi-method trade-audit filtering is available
- **THEN** the preset registry MUST include `audit-daily-submit-path-exceptions` and `audit-period-submit-path-exceptions`

#### Scenario: Caller runs a submit-path exception report preset
- **WHEN** a caller executes a named report preset whose target command is `audit-daily` or `audit-period` and whose defaults fix `methods=[buy_submit_once, confirm_current]` and `statuses=[rejected, failed]`
- **THEN** the system MUST resolve the preset defaults and run the existing stable report workflow through the report/task path
