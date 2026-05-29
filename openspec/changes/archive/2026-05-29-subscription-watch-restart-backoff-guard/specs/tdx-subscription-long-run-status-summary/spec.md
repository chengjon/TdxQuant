## ADDED Requirements

### Requirement: Subscription watch-status diagnostics SHALL expose restart backoff guard

Subscription watch-status diagnostics SHALL include compact read-only restart backoff guard metadata when detailed control state provides it.

#### Scenario: Diagnostics projects active restart backoff

- **WHEN** diagnostics view is built from detailed status whose `control` payload includes active `restart_backoff`
- **THEN** `diagnostics.restart_backoff.active` MUST be `true`
- **AND** diagnostics MUST include stable retry metadata and `BACKOFF_ACTIVE` reason code
- **AND** diagnostics MUST NOT expose raw control state, raw start result, full start request, logs, command line, HTTP health, or event-stream data.

#### Scenario: Diagnostics projects no restart backoff

- **WHEN** diagnostics view is built from detailed status without restart backoff metadata
- **THEN** `diagnostics.restart_backoff.active` MUST be `false`
- **AND** diagnostics MUST NOT call restart preflight, stop, start, restart, signal, schedule retry, or run a supervisor loop.
