## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn promotion readiness rollup without promotion

`FUNCTION_TREE.md` SHALL register PingAn promotion readiness rollup evidence for D-07 and D-08 while preserving their `[部分实现]` status.

#### Scenario: D-07 and D-08 cite rollup evidence

- **WHEN** the promotion readiness rollup task exists
- **THEN** D-07 and D-08 SHALL cite `pingan-promotion-readiness-rollup`
- **AND** D-07 and D-08 SHALL cite `promotion_readiness_rollup`
- **AND** D-07 and D-08 SHALL cite `completed_gates` and `incomplete_gates`
- **AND** D-07 and D-08 SHALL remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents rollup overclaiming

- **WHEN** D-07 or D-08 evidence cites the rollup
- **THEN** the boundary SHALL state that the rollup is read-only evidence aggregation
- **AND** the boundary SHALL state that it does not execute broker/desktop/trade/report/catalog workflows
- **AND** the boundary SHALL state that it does not by itself prove production readiness or implemented status.
