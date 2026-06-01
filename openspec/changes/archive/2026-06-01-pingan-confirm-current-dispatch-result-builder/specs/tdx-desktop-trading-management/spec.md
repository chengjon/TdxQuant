## ADDED Requirements

### Requirement: Desktop trading management SHALL own confirm-current dispatch result construction in the confirm seam module
The desktop trading management layer SHALL construct PingAn confirm-current dispatch result envelopes through the confirm-current seam module rather than inline manager-only policy code.

#### Scenario: Confirm-current dispatch result shape is preserved

- **WHEN** confirm-current dispatch returns failed lookup, failed click, warning, or success results
- **THEN** the result builder MUST preserve the existing result code, message, input echo, confirm-current status fields, checks, warnings, next action, and result-dialog payload
- **AND** manager routing MUST continue to perform the existing UI lookup/click/result-close primitives before calling the builder
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, or live readiness behavior

