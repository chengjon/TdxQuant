## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn implemented-status transition writer without implying execution

`FUNCTION_TREE.md` SHALL record the PingAn implemented-status transition writer as available D-07/D-08 transition machinery while keeping the repository rows `[部分实现]` until a real transition is executed.

#### Scenario: D-07 and D-08 register transition writer while staying partial

- **WHEN** D-07 or D-08 cites `pingan-implemented-status-transition-writer`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `pingan_implemented_status_transition`
- **AND** evidence SHALL mention `implemented_status_transition_record`
- **AND** evidence SHALL mention `confirm_transition`
- **AND** the boundary SHALL state that this slice only provides guarded writer machinery and does not prove that the repository transition has been executed.
