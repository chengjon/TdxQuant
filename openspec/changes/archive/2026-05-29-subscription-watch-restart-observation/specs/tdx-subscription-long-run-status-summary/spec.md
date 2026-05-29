## ADDED Requirements

### Requirement: Subscription watch-status diagnostics SHALL expose latest restart observation

Subscription watch-status diagnostics SHALL include a compact read-only latest restart observation when detailed control state provides one.

#### Scenario: Diagnostics projects persisted restart observation

- **WHEN** diagnostics view is built from detailed status whose `control` payload includes `last_restart_observation`
- **THEN** `diagnostics.restart_observation.has_observation` MUST be `true`
- **AND** `diagnostics.restart_observation` MUST include stable summary fields for the previous run id, new run id, reason, stop state, start state, start request summary, and boundary
- **AND** diagnostics MUST NOT expose raw `control`, raw `watch_status`, raw stop result, raw start result, full start request, logs, command line, or event-stream payloads.

#### Scenario: Diagnostics has no restart observation

- **WHEN** diagnostics view is built from detailed status without a persisted restart observation
- **THEN** `diagnostics.restart_observation.has_observation` MUST be `false`
- **AND** diagnostics MUST NOT call restart preflight, stop, start, restart, signal, schedule backoff, or run a supervisor loop.
