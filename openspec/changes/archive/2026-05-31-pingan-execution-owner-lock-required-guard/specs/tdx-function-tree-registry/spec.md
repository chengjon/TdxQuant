## ADDED Requirements

### Requirement: PingAn execution owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn execution owner-lock guard evidence as partial safety/lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Execution owner-lock guard evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `trade_safety.risk_gate.lifecycle_owner_lock_required_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the execution owner-lock guard
- **AND** the boundary SHALL state that the guard is opt-in local statefile safety evidence and does not provide real process lifecycle control, broker readiness, production readiness, or live/manual acceptance.
