# Design: PingAn supervisor restart readiness summary

## Scope

Add a bounded post-restart health recheck to the existing supervisor tick/run. It is opt-in and only runs after a successful recorded-PID process restart.

Inputs:

- `process_restart_recheck_enabled`: default `False`
- `process_restart_recheck_delay_seconds`: default `0.0`

CLI flags:

- `--process-restart-recheck`
- `--process-restart-recheck-delay-seconds`

## Flow

1. Supervisor does the existing owner-lock gate.
2. Supervisor observes pre-restart broker health.
3. If restart/backoff policy allows and `process_restart_enabled=True`, supervisor delegates to `lifecycle_process(action=restart)`.
4. If that process restart succeeds and `process_restart_recheck_enabled=True`, supervisor optionally waits for the configured delay and performs one more `PingAnBrokerAdapter.health_check()`.
5. Supervisor surfaces:
   - `process_restart_recheck_requested`
   - `process_restart_recheck_executed`
   - `post_restart_broker_health_ok`
   - `post_restart_broker_health_code`
   - `post_restart_broker_health_message`
   - `lifecycle_recovery_status`

## Boundaries

The summary is evidence, not readiness promotion. `recovered` means only that the immediate post-restart broker health check returned OK. It does not imply order submission is safe, UI login is complete, confirmation dialogs work, or live/manual acceptance exists.
