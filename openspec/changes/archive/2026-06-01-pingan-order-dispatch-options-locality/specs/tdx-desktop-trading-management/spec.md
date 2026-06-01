## ADDED Requirements

### Requirement: Desktop trading management SHALL centralize PingAn order desktop dispatch option construction
The desktop trading management layer SHALL centralize repeated PingAn order desktop dispatch option construction while preserving existing order execution behavior and public contracts.

#### Scenario: Dispatch options helper owns profile-derived runner kwargs

- **WHEN** buy, sell, or submit-once manager paths build desktop runner kwargs
- **THEN** they SHOULD use a shared internal dispatch options object/helper for profile-derived delays, dialog timeouts, result-close behavior, final UIA capture, and fast input-mode fields
- **AND** method-specific desktop runner selection SHOULD remain in the manager callsite
- **AND** the change MUST preserve existing order dispatch, idempotency, risk gate, lifecycle/broker guard, finalize, audit, and request-context behavior
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, live readiness, or production trading behavior

