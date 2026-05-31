## MODIFIED Requirements

### Requirement: Daily trade audit report SHALL expose acceptance outcome coverage status

The daily trade audit report SHALL include a read-only `acceptance_outcome_coverage_status` object derived from the selected immutable audit entries and, when explicitly supplied, a live/manual acceptance evidence manifest.

#### Scenario: Caller generates a daily report with audit outcomes

- **WHEN** a caller generates a trade audit daily report
- **THEN** the result data SHALL include `acceptance_outcome_coverage_status`
- **AND** the payload SHALL identify `schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **AND** it SHALL include covered outcome statuses and counts from the selected daily report entries
- **AND** it SHALL include required automated outcome statuses and missing automated outcome statuses.

#### Scenario: Daily report separates automated coverage from full acceptance

- **WHEN** the daily report includes `acceptance_outcome_coverage_status`
- **THEN** the payload SHALL include `automated_outcome_coverage_complete`
- **AND** it SHALL include `live_manual_acceptance_complete=false` when live/manual acceptance evidence is not provided
- **AND** it SHALL keep `acceptance_complete=false` when live/manual acceptance evidence is not provided.

#### Scenario: Caller supplies complete daily live manual acceptance evidence

- **WHEN** a caller generates a daily report with a live/manual acceptance evidence manifest covering `confirmed`, `rejected`, `failed`, and `exception`
- **THEN** the payload SHALL include `live_manual_acceptance.status=complete`
- **AND** it SHALL include `live_manual_acceptance_complete=true`
- **AND** it SHALL include `acceptance_complete=true` only when automated outcome coverage is also complete.

#### Scenario: Caller supplies incomplete daily live manual acceptance evidence

- **WHEN** a caller generates a daily report with a live/manual acceptance evidence manifest missing required outcomes
- **THEN** the payload SHALL include `live_manual_acceptance.status=incomplete`
- **AND** it SHALL include `live_manual_acceptance.missing_outcomes`
- **AND** it SHALL keep `live_manual_acceptance_complete=false`.

#### Scenario: Daily acceptance coverage remains read-only evidence

- **WHEN** the daily report includes `acceptance_outcome_coverage_status`
- **THEN** the payload SHALL state `execution_mode=readonly_report`
- **AND** it SHALL state `side_effect_level=none`
- **AND** it SHALL NOT claim order submission, desktop control dispatch, broker readiness, production readiness, or D-07/D-08 implemented status.
