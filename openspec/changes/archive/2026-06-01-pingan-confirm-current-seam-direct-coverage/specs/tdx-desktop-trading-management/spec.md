## ADDED Requirements

### Requirement: Desktop trading management SHALL directly verify PingAn confirm-current seam branches
The desktop trading management test suite SHALL directly verify the internal confirm-current execution seam branches for rejected gate, non-advanced dispatch result, and advanced finalized result without invoking manager or desktop UI lookup code.

#### Scenario: Direct confirm-current seam coverage remains non-public

- **WHEN** direct seam coverage is added for `execute_pingan_confirm_current`
- **THEN** the tests MUST assert gate-before-dispatch behavior, non-advanced metadata behavior, and advanced finalize behavior
- **AND** the tests MUST preserve `method=confirm_current`, timing label `pingan.confirm_current`, null request context, not-applicable idempotency, and confirm-current-specific non-order semantics
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, or desktop primitive behavior

