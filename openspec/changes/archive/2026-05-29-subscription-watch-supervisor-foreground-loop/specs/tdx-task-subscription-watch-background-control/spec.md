## ADDED Requirements

### Requirement: Subscription watch background control SHALL support bounded foreground supervisor run

The worker-local subscription-watch background controller SHALL provide an explicit bounded foreground supervisor run that repeatedly invokes the existing supervisor tick operation.

#### Scenario: Foreground run waits while backoff remains active

- **WHEN** a caller invokes supervisor run with `max_ticks > 1` while each tick returns an active backoff wait decision
- **THEN** the controller MUST call supervisor tick no more than `max_ticks` times
- **AND** it MUST return compact tick summaries, `tick_count`, `final_status`, and `final_decision`
- **AND** it MUST NOT create a daemon, scheduler, timer, background worker, or automatic retry service.

#### Scenario: Foreground run stops early after recovery

- **WHEN** a tick returns recovered status before `max_ticks` is reached
- **THEN** the controller MUST stop the foreground run immediately
- **AND** it MUST report the recovered tick as the final decision
- **AND** it MUST NOT call `stop()` or `restart()` outside the existing supervisor tick behavior.

#### Scenario: Foreground run stops early with no actionable backoff

- **WHEN** the first tick returns no-action status
- **THEN** the controller MUST stop after one tick
- **AND** it MUST report final status `noop`.

#### Scenario: Foreground run rejects invalid limits

- **WHEN** `max_ticks` is less than 1 or `interval_seconds` is negative
- **THEN** the controller MUST return `INVALID_REQUEST`
- **AND** it MUST NOT call supervisor tick.

