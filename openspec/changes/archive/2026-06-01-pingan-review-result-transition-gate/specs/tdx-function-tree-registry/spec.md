## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn review-result transition gate without promotion

`FUNCTION_TREE.md` SHALL record the PingAn review-result transition gate as D-07/D-08 partial pre-transition evidence while keeping both nodes `[部分实现]`.

#### Scenario: D-07 and D-08 register transition gate while staying partial

- **WHEN** D-07 or D-08 cites `pingan-review-result-transition-gate`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `implemented_status_transition_gate`
- **AND** evidence SHALL mention `eligible_for_status_transition_review`
- **AND** evidence SHALL mention `manual_status_transition_required`
- **AND** the boundary SHALL state that this gate does not execute PingAn workflows, does not automatically modify FUNCTION_TREE status, does not prove production readiness, and does not prove implemented status.
