## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn implemented-status review packet without promotion

`FUNCTION_TREE.md` SHALL record that D-07 and D-08 include an implemented-status review packet as partial status-review evidence only.

#### Scenario: D-07 and D-08 register review packet while staying partial

- **WHEN** D-07 or D-08 cites `pingan-implemented-status-review-packet`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `implemented_status_review_packet`
- **AND** evidence SHALL mention `ready_for_manual_review`
- **AND** the boundary SHALL state that the packet is a read-only manual status review input and does not execute PingAn workflows, submit orders, prove production readiness, or promote implemented status.
