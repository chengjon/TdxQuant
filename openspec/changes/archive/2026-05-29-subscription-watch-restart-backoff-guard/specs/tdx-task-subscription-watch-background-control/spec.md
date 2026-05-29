## ADDED Requirements

### Requirement: Subscription watch restart SHALL enforce bounded backoff after replacement start failure

The worker-local subscription-watch background controller SHALL record and enforce a bounded explicit-restart backoff when replacement start fails after the prior active run has been stopped.

#### Scenario: Replacement start failure records restart backoff

- **WHEN** explicit restart stops an active run but replacement `start()` fails
- **THEN** the controller MUST persist a compact `restart_backoff` object in control state
- **AND** the persisted control state MUST include `state` set to `restart_backoff`, `active` set to `false`, and stable retry metadata
- **AND** the restart failure response MUST include the same compact backoff metadata
- **AND** the backoff metadata MUST NOT include raw logs, command line, full start request, HTTP health, event-stream data, or provider credentials.

#### Scenario: Active restart backoff rejects repeated restart

- **WHEN** explicit restart is requested while persisted `restart_backoff.retry_after_at` is still in the future
- **THEN** the controller MUST return stable `RESTART_BACKOFF_ACTIVE`
- **AND** it MUST include retry metadata and `BACKOFF_ACTIVE` reason code
- **AND** it MUST NOT call stop, start, restart-preflight, schedule automatic retry, or run a supervisor loop.

#### Scenario: Expired restart backoff no longer hides missing active run

- **WHEN** explicit restart is requested after the persisted restart backoff has expired
- **THEN** the controller MUST treat the control state as non-active for restart purposes
- **AND** it MUST NOT automatically start a replacement run.
