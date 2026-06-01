## ADDED Requirements

### Requirement: Desktop trading management SHALL centralize PingAn confirm-current execution preparation before dispatch
The desktop trading management layer SHALL centralize repeated PingAn confirm-current execution preparation while preserving existing confirm-current dispatch behavior and public contracts.

#### Scenario: Confirm-current preparation helper owns request and guard preparation

- **WHEN** `confirm_current` prepares to call `execute_pingan_confirm_current`
- **THEN** it SHOULD use a shared internal preparation helper for effective profile, timeout overrides, broker-readiness guard, lifecycle owner-lock guard, `PingAnConfirmCurrentExecutionRequest`, rejection context, and dispatch context preparation
- **AND** desktop confirm lookup, click, result-dialog lookup, and result-dialog close dispatch SHOULD remain in the manager callsite
- **AND** the change MUST preserve existing confirm-current guard, metadata, safety metadata, dispatch, finalize, audit, and request-context behavior
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, live readiness, or production trading behavior

