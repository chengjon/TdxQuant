## MODIFIED Requirements

### Requirement: FUNCTION_TREE registry SHALL be mechanically validatable

`FUNCTION_TREE.md` SHALL remain a single feature registry where each feature row carries explicit status, evidence, and boundary text that can be mechanically validated.

#### Scenario: D-07 PingAn input-kind rollup evidence stays bounded

- **WHEN** D-07 cites PingAn bundle trade boundary input-kind count evidence
- **THEN** D-07 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade_plan_boundary_input_kind_counts`
- **AND** the boundary MUST state that the field is read-only catalog plan/preview summary evidence
- **AND** the row MUST NOT imply task/trade/report/bundle execution, broker readiness, trading safety approval, production readiness, or complete desktop exception coverage.
