## ADDED Requirements

### Requirement: Period trade audit report SHALL expose acceptance outcome coverage status

The period trade audit report SHALL include a read-only `acceptance_outcome_coverage_status` object derived only from the selected immutable audit entries in the inclusive report period.

#### Scenario: Caller generates a period report with audit outcomes

- **WHEN** a caller generates a trade audit period report
- **THEN** the result data SHALL include `acceptance_outcome_coverage_status`
- **AND** the payload SHALL identify `schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **AND** it SHALL include covered outcome statuses and counts from the selected period report entries
- **AND** it SHALL include required automated outcome statuses and missing automated outcome statuses.

#### Scenario: Period acceptance coverage remains read-only partial evidence

- **WHEN** the period report includes `acceptance_outcome_coverage_status`
- **THEN** the payload SHALL state `execution_mode=readonly_report`
- **AND** it SHALL state `side_effect_level=none`
- **AND** it SHALL state that live/manual acceptance evidence is `not_provided`
- **AND** it SHALL NOT claim order submission, desktop control dispatch, broker readiness, production readiness, or D-07/D-08 implemented status.

