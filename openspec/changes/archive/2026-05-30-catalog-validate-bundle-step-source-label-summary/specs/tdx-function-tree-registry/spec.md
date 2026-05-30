## MODIFIED Requirements

### Requirement: FUNCTION_TREE registry SHALL be mechanically validatable

`FUNCTION_TREE.md` SHALL remain a single feature registry where each feature row carries explicit status, evidence, and boundary text that can be mechanically validated.

#### Scenario: E-11 source-label summary evidence stays bounded

- **WHEN** E-11 cites catalog bundle step source-label count evidence
- **THEN** E-11 MUST remain `[部分实现]`
- **AND** the row MUST cite `bundle_step_source_label_counts` and `task_report_bundle_step_source_label_counts`
- **AND** the boundary MUST state that the fields are read-only catalog validation summary evidence
- **AND** the row MUST NOT imply workflow execution, arbitrary workflow builder completion, task/report/trade execution, or production readiness.
