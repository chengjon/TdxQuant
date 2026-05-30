# tdx-task-trade-audit-period-report Specification

## Purpose
TBD - created by archiving change add-trade-audit-aggregation-reports. Update Purpose after archive.
## Requirements
### Requirement: Task trade audit period report SHALL provide a stable range-level audit aggregation workflow
The system SHALL provide a stable task-facing workflow that reads immutable trade-audit artifacts, filters entries by local-date range, and returns structured aggregation data for that period.

#### Scenario: Caller generates a single-day audit period report
- **WHEN** a caller provides only one boundary date
- **THEN** the workflow MUST treat the report period as that single local trade date

#### Scenario: Caller generates a multi-day audit period report
- **WHEN** a caller provides a start date and an end date
- **THEN** the workflow MUST include all trade-audit entries whose local dates fall within the inclusive range before aggregation

#### Scenario: Caller exports the audit period report
- **WHEN** a caller provides output paths for the trade audit period report workflow
- **THEN** the workflow MUST write a structured JSON report and a CSV daily aggregation view

### Requirement: Period trade audit report SHALL expose requested-value diagnostics
The period trade audit report SHALL include a read-only requested-value diagnostic derived only from existing audit result payload fields.

#### Scenario: Caller requests a period report with priced audit entries
- **WHEN** a caller generates a trade audit period report from audit entries that contain numeric `price` and `quantity`
- **THEN** the result includes `value_diagnostics`
- **AND** the diagnostic reports priced and unpriced entry counts across the selected period
- **AND** the diagnostic reports requested order value by status and method

#### Scenario: Period requested value remains a diagnostic boundary
- **WHEN** the period report includes `value_diagnostics`
- **THEN** the diagnostic states that requested order value is calculated from `price * quantity`
- **AND** the diagnostic does not claim filled value, execution quality, fees, account balances, or PnL

### Requirement: Period trade audit report SHALL expose acceptance outcome coverage status

The period trade audit report SHALL include a read-only `acceptance_outcome_coverage_status` object derived only from the selected immutable audit entries in the inclusive report period.

#### Scenario: Caller generates a period report with audit outcomes

- **WHEN** a caller generates a trade audit period report
- **THEN** the result data SHALL include `acceptance_outcome_coverage_status`
- **AND** the payload SHALL identify `schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **AND** it SHALL include covered outcome statuses and counts from the selected period report entries
- **AND** it SHALL include required automated outcome statuses and missing automated outcome statuses.

#### Scenario: Period report separates automated coverage from full acceptance

- **WHEN** the period report includes confirmed, rejected, failed, and exception audit outcomes
- **THEN** the payload SHALL include `automated_outcome_coverage_complete=true`
- **AND** it SHALL include `live_manual_acceptance_complete=false`
- **AND** it SHALL keep `acceptance_complete=false` when live/manual acceptance evidence is not provided.

#### Scenario: Period acceptance coverage remains read-only partial evidence

- **WHEN** the period report includes `acceptance_outcome_coverage_status`
- **THEN** the payload SHALL state `execution_mode=readonly_report`
- **AND** it SHALL state `side_effect_level=none`
- **AND** it SHALL state that live/manual acceptance evidence is `not_provided`
- **AND** it SHALL NOT claim order submission, desktop control dispatch, broker readiness, production readiness, or D-07/D-08 implemented status.

