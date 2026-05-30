# tdx-task-trade-audit-daily-report Specification

## Purpose
TBD - created by archiving change add-trade-audit-aggregation-reports. Update Purpose after archive.
## Requirements
### Requirement: Task trade audit daily report SHALL provide a stable day-level audit aggregation workflow
The system SHALL provide a stable task-facing workflow that reads immutable trade-audit artifacts, filters entries by local trade date, and returns structured daily aggregation data.

#### Scenario: Caller generates report for the default local trade date
- **WHEN** a caller runs the trade audit daily report workflow without explicitly providing a report date
- **THEN** the workflow MUST generate the report using the current date in the configured local timezone

#### Scenario: Caller generates report for a specific audit date
- **WHEN** a caller provides an explicit report date and timezone
- **THEN** the workflow MUST filter trade-audit entries using that local-date boundary before aggregation

#### Scenario: Caller exports the daily audit report
- **WHEN** a caller provides output paths for the trade audit daily report workflow
- **THEN** the workflow MUST write a structured JSON report and a CSV aggregation view

### Requirement: Daily trade audit report SHALL expose requested-value diagnostics
The daily trade audit report SHALL include a read-only requested-value diagnostic derived only from existing audit result payload fields.

#### Scenario: Caller requests a daily report with priced audit entries
- **WHEN** a caller generates a trade audit daily report from audit entries that contain numeric `price` and `quantity`
- **THEN** the result includes `value_diagnostics`
- **AND** the diagnostic reports priced and unpriced entry counts
- **AND** the diagnostic reports requested order value by status and method

#### Scenario: Daily requested value remains a diagnostic boundary
- **WHEN** the daily report includes `value_diagnostics`
- **THEN** the diagnostic states that requested order value is calculated from `price * quantity`
- **AND** the diagnostic does not claim filled value, execution quality, fees, account balances, or PnL

### Requirement: Daily trade audit report SHALL expose acceptance outcome coverage status

The daily trade audit report SHALL include a read-only `acceptance_outcome_coverage_status` object derived only from the selected immutable audit entries.

#### Scenario: Caller generates a daily report with audit outcomes

- **WHEN** a caller generates a trade audit daily report
- **THEN** the result data SHALL include `acceptance_outcome_coverage_status`
- **AND** the payload SHALL identify `schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **AND** it SHALL include covered outcome statuses and counts from the selected daily report entries
- **AND** it SHALL include required automated outcome statuses and missing automated outcome statuses.

#### Scenario: Daily report separates automated coverage from full acceptance

- **WHEN** the daily report includes `acceptance_outcome_coverage_status`
- **THEN** the payload SHALL include `automated_outcome_coverage_complete`
- **AND** it SHALL include `live_manual_acceptance_complete=false`
- **AND** it SHALL keep `acceptance_complete=false` when live/manual acceptance evidence is not provided.

#### Scenario: Daily acceptance coverage remains read-only partial evidence

- **WHEN** the daily report includes `acceptance_outcome_coverage_status`
- **THEN** the payload SHALL state `execution_mode=readonly_report`
- **AND** it SHALL state `side_effect_level=none`
- **AND** it SHALL state that live/manual acceptance evidence is `not_provided`
- **AND** it SHALL NOT claim order submission, desktop control dispatch, broker readiness, production readiness, or D-07/D-08 implemented status.

