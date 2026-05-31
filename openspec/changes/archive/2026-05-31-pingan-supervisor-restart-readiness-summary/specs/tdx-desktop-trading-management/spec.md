## ADDED Requirements

### Requirement: PingAn lifecycle supervisor SHALL summarize post-restart broker health

PingAn lifecycle supervisor tick/run SHALL optionally perform one bounded broker health recheck after a successful recorded-PID process restart and expose a recovery summary.

#### Scenario: Successful restart recheck reports recovered lifecycle status

- **GIVEN** supervisor process restart is explicitly enabled
- **AND** the recorded-PID process restart succeeds
- **AND** restart recheck is explicitly enabled
- **WHEN** the post-restart broker health check returns OK
- **THEN** the supervisor payload MUST report `process_restart_recheck_requested=true`
- **AND** the supervisor payload MUST report `process_restart_recheck_executed=true`
- **AND** the supervisor payload MUST report `post_restart_broker_health_ok=true`
- **AND** the supervisor payload MUST report `lifecycle_recovery_status=recovered`.

#### Scenario: Failed restart recheck reports still unhealthy without failing restart evidence

- **GIVEN** supervisor process restart succeeds
- **AND** restart recheck is explicitly enabled
- **WHEN** the post-restart broker health check returns non-OK
- **THEN** the supervisor payload MUST report `process_restart_executed=true`
- **AND** the supervisor payload MUST report `post_restart_broker_health_ok=false`
- **AND** the supervisor payload MUST report `lifecycle_recovery_status=still_unhealthy`
- **AND** the supervisor result MUST remain structured lifecycle evidence rather than submitting or retrying an order.

#### Scenario: Recheck remains absent when restart is not executed

- **WHEN** supervisor is inside backoff, max restart attempts are exhausted, process restart is disabled, or process restart fails
- **THEN** the supervisor payload MUST report `process_restart_recheck_requested=false`
- **AND** the supervisor payload MUST report `process_restart_recheck_executed=false`.
