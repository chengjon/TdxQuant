## ADDED Requirements

### Requirement: Task management SHALL expose PingAn promotion readiness rollup as a stable read-only workflow

The task manager SHALL provide a stable PingAn promotion readiness rollup workflow that reads existing JSON evidence artifacts and summarizes D-07/D-08 promotion gates without executing PingAn trading workflows.

#### Scenario: Caller generates a partial promotion readiness rollup

- **WHEN** a caller provides preflight, dialog readiness, and acceptance coverage evidence paths
- **THEN** the task result SHALL include `promotion_readiness_rollup`
- **AND** the rollup SHALL identify `schema=tdx.desktop_trade.pingan_promotion_readiness_rollup.v1`
- **AND** it SHALL include named gate statuses for provider/broker ownership, safety gates, desktop lifecycle, audit evidence, live/manual acceptance, and acceptance evidence
- **AND** it SHALL include completed and incomplete gate lists.

#### Scenario: Caller generates a complete promotion readiness rollup

- **WHEN** all required gate evidence explicitly reports complete or ready status
- **THEN** the rollup SHALL report `status=complete`
- **AND** it SHALL keep `promotion_status_transition_executed=false`.

#### Scenario: Missing evidence remains visible

- **WHEN** a caller omits one or more evidence paths
- **THEN** the rollup SHALL mark the corresponding gates incomplete
- **AND** it SHALL include `missing_evidence_kinds`.

#### Scenario: Rollup remains read-only

- **WHEN** the rollup task runs
- **THEN** it SHALL report `execution_mode=readonly_evidence_rollup`
- **AND** it SHALL report `side_effect_level=none`
- **AND** it SHALL report `order_submitted=false`
- **AND** it SHALL report `control_dispatch_executed=false`.
