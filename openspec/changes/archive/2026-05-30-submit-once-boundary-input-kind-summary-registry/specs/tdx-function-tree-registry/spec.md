## MODIFIED Requirements

### Requirement: FUNCTION_TREE registry SHALL be mechanically validatable

`FUNCTION_TREE.md` SHALL remain a single feature registry where each feature row carries explicit status, evidence, and boundary text that can be mechanically validated.

#### Scenario: D-08 submit_once input-kind rollup evidence stays bounded

- **WHEN** D-08 cites submit_once bundle input-kind count evidence
- **THEN** D-08 MUST remain `[部分实现]`
- **AND** the row MUST cite `trade_plan_boundary_input_kind_counts` and `submit_once_order`
- **AND** the boundary MUST state that the field is read-only catalog plan/preview summary evidence
- **AND** the row MUST NOT imply catalog run execution, broker readiness, trading safety approval, production readiness, or independent desktop submit_once primitives.
