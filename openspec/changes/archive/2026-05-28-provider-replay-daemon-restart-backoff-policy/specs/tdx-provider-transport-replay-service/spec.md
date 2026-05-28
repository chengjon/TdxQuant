## ADDED Requirements

### Requirement: Provider replay daemon supervisor SHALL support opt-in restart/backoff

The provider replay foreground supervisor SHALL support a bounded, opt-in restart/backoff policy for non-zero child exits while keeping no-restart behavior as the default.

#### Scenario: Default supervisor does not restart

- **WHEN** the supervisor runs without an explicit restart policy
- **THEN** child exit MUST be recorded as `state=exited`
- **AND** the supervisor MUST NOT relaunch the child
- **AND** no backoff MUST be scheduled

#### Scenario: On-failure policy retries after backoff

- **WHEN** `restart_policy=on-failure` and a child exits with a non-zero code while restart budget remains
- **THEN** the supervisor MUST write `state=backoff`
- **AND** it MUST wait for the configured backoff seconds
- **AND** it MUST relaunch the child
- **AND** it MUST report restart and backoff counts

#### Scenario: Restart exhaustion records failed state

- **WHEN** a child exits with a non-zero code after restart budget is exhausted
- **THEN** the supervisor MUST write `state=failed`
- **AND** it MUST report `supervisor_status=restart_exhausted`
- **AND** it MUST NOT relaunch the child again

#### Scenario: Restart/backoff remains bounded

- **WHEN** restart/backoff is available
- **THEN** the implementation MUST NOT persist restart budget across separate supervisor invocations, infer ownership from ports, validate real provider readiness, assert broker/workflow/write readiness, or enable restart unless explicitly requested

