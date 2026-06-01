## ADDED Requirements

### Requirement: Desktop trading management SHALL own confirm-current gate rejection result construction in the confirm seam module
The desktop trading management layer SHALL construct PingAn confirm-current lifecycle owner-lock and broker-readiness gate rejection results through the confirm-current seam module rather than inline manager-only policy code.

#### Scenario: Confirm-current gate rejection result shape is preserved

- **WHEN** confirm-current is rejected by lifecycle owner-lock or broker-readiness gate requirements
- **THEN** the result builder MUST preserve the existing failed result code, message, next action, input echo, confirm-current status fields, health-check detail, and empty result dialog payload
- **AND** manager routing MUST continue to attach existing manager metadata and trade safety metadata through the confirm-current seam
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, or live readiness behavior

