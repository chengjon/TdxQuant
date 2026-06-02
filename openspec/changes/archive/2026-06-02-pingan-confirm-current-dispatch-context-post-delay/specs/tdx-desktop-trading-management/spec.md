## ADDED Requirements

### Requirement: Desktop trading management SHALL keep confirm-current click post-delay in the internal dispatch context
The desktop trading management layer SHALL resolve the PingAn confirm-current click post-delay into the internal confirm-current dispatch context before dispatch.

#### Scenario: Confirm-current dispatch context owns post-click timing

- **WHEN** `confirm_current` prepares dispatch options before calling `execute_pingan_confirm_current`
- **THEN** the prepared `PingAnConfirmCurrentDispatchContext` SHOULD include the resolved `confirm_post_delay`
- **AND** manager dispatch SHOULD use that context value for the confirm dialog click post-delay
- **AND** desktop confirm lookup, confirm click, result-dialog lookup, and result-dialog close primitives SHOULD remain in the manager callsite
- **AND** the change MUST preserve existing public manager, CLI, task, catalog, metadata, safety metadata, audit, and result payload behavior
- **AND** the change MUST NOT introduce workflow builder, desktop primitive, broker readiness, live acceptance, or production trading behavior
