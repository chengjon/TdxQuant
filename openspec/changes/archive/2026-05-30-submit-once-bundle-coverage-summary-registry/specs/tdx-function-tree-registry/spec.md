## MODIFIED Requirements

### Requirement: FUNCTION_TREE registry SHALL be mechanically validatable

The repository SHALL maintain `FUNCTION_TREE.md` as a single feature registry whose rows explicitly separate status, evidence, and boundary.

#### Scenario: D-08 submit-once input coverage rollup evidence stays bounded

- **WHEN** D-08 cites submit-once bundle input coverage status count evidence
- **THEN** D-08 MUST remain `[部分实现]`
- **AND** the D-08 boundary MUST state that the coverage counts are read-only, non-executing catalog summary evidence
- **AND** the row MUST NOT imply catalog run execution, broker readiness, safety approval, or complete desktop exception coverage.
