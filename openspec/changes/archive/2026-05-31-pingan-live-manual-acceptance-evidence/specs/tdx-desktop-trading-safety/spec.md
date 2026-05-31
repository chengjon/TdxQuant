## ADDED Requirements

### Requirement: PingAn live manual acceptance evidence SHALL remain report-only

PingAn live/manual acceptance evidence SHALL be accepted only as explicit read-only report evidence and SHALL NOT execute trades, control the desktop, or promote D-07/D-08 status by itself.

#### Scenario: Manual acceptance evidence is summarized without execution

- **WHEN** a trade audit daily or period report is generated with a live/manual acceptance evidence manifest
- **THEN** the report SHALL summarize the manifest under `acceptance_outcome_coverage_status.live_manual_acceptance`
- **AND** the report SHALL keep `execution_mode=readonly_report`
- **AND** the report SHALL keep `side_effect_level=none`
- **AND** the report SHALL keep `order_submitted=false`
- **AND** the report SHALL keep `control_dispatch_executed=false`.

#### Scenario: Manual acceptance completion does not imply production readiness

- **WHEN** `live_manual_acceptance_complete=true`
- **THEN** that result SHALL mean only that the supplied manifest covers required acceptance outcomes
- **AND** it SHALL NOT prove broker production readiness, UI login readiness, order safety, or full D-07/D-08 implementation.
