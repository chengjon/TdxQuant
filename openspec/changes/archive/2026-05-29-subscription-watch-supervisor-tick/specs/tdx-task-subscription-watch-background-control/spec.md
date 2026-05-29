## ADDED Requirements

### Requirement: Subscription watch background control SHALL support explicit supervisor tick

The worker-local subscription-watch background controller SHALL provide an explicit single-step supervisor tick over restart backoff state.

#### Scenario: Tick waits while restart backoff is active

- **WHEN** a caller invokes supervisor tick while persisted restart backoff has not expired
- **THEN** the controller MUST return a no-op wait result with `decision` set to `wait`
- **AND** it MUST include compact restart backoff metadata
- **AND** it MUST NOT call `start()`, `restart()`, `stop()`, schedule retry, or run a supervisor loop.

#### Scenario: Tick recovers once after restart backoff expires

- **WHEN** a caller invokes supervisor tick after persisted restart backoff has expired and a valid persisted `start_request` exists
- **THEN** the controller MUST attempt exactly one replacement `start()` using the persisted request
- **AND** a successful result MUST include `status` set to `recovered`, `previous_run_id`, `new_run_id`, `start_result`, and `start_request_summary`
- **AND** it MUST NOT loop, schedule another tick, infer process ownership from ports, or claim provider health/readiness beyond the start result.

#### Scenario: Tick records new backoff when recovery start fails

- **WHEN** supervisor tick attempts recovery start and `start()` fails
- **THEN** the controller MUST return a stable failed tick error
- **AND** it MUST persist a new compact restart backoff guard
- **AND** it MUST NOT retry again inside the same tick.

#### Scenario: Tick has no actionable restart backoff

- **WHEN** supervisor tick is invoked without restart backoff state
- **THEN** the controller MUST return a no-op result with `decision` set to `no_action`
- **AND** it MUST NOT call `start()`, `restart()`, or `stop()`.
