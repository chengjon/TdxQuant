## ADDED Requirements

### Requirement: Desktop trading management SHALL centralize PingAn order runner kwargs selection
The desktop trading management layer SHALL expose an internal dispatch-options method for selecting PingAn order runner kwargs while preserving existing base and fast kwargs shapes.

#### Scenario: Order dispatch options select base or fast runner kwargs

- **WHEN** buy/sell/submit-once manager callsites prepare to dispatch a PingAn order runner
- **THEN** they SHOULD ask `PingAnOrderDispatchOptions` for runner kwargs using an explicit fast-inputs selector
- **AND** base runner kwargs MUST preserve the existing common order fields, delay, timeout, result-close, and final UIA capture fields
- **AND** fast runner kwargs MUST preserve the existing base fields plus price/quantity input mode and dialog lookup mode fields
- **AND** manager callsites MUST continue to choose the concrete desktop runner explicitly
- **AND** the change MUST preserve existing public manager, CLI, task, catalog, metadata, safety metadata, audit, idempotency, risk gate, and result payload behavior
- **AND** the change MUST NOT introduce workflow builder, desktop primitive, broker readiness, live acceptance, or production trading behavior
