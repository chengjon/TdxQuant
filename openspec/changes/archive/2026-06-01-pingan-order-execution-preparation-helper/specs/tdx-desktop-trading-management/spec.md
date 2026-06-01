## ADDED Requirements

### Requirement: Desktop trading management SHALL centralize PingAn order execution preparation before dispatch
The desktop trading management layer SHALL centralize repeated PingAn order execution preparation for buy, sell, and submit-once paths while preserving existing dispatch and public contracts.

#### Scenario: Order preparation helper owns request and guard preparation

- **WHEN** buy, sell, or submit-once manager paths prepare to call `execute_pingan_order`
- **THEN** they SHOULD use a shared internal preparation helper for effective profile, idempotency, risk gate, broker-readiness guard, lifecycle owner-lock guard, `PingAnExecutionRequest`, and handler bundle preparation
- **AND** method-specific desktop dispatch SHOULD remain in the manager callsite
- **AND** the change MUST preserve existing order dispatch, idempotency, risk gate, lifecycle/broker guard, finalize, audit, and request-context behavior
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, live readiness, or production trading behavior

