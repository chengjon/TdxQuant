## ADDED Requirements

### Requirement: Worker bridge watch-status SHALL project supervisor daemon diagnostics

The worker bridge HTTP control plane SHALL project compact supervisor daemon status in watch-status summary and diagnostics views without exposing sensitive owner token values or executing daemon lifecycle control.

#### Scenario: Summary view includes compact supervisor daemon status

- **WHEN** a caller invokes `GET /bridge/v1/watch/status?view=summary`
- **THEN** the response MUST include a compact `supervisor_daemon` object when the detailed status payload contains supervisor daemon status
- **AND** the compact object MUST include status, state, statefile validity, pidfile presence, PID, process-running flag, owner-token presence, generation, control allowance, and boundary
- **AND** it MUST NOT include raw owner token, daemon command, file paths, or full daemon settings.

#### Scenario: Diagnostics view includes compact supervisor daemon status

- **WHEN** a caller invokes `GET /bridge/v1/watch/status?view=diagnostics`
- **THEN** the response diagnostics MUST include the same compact supervisor daemon status
- **AND** it MUST NOT start, stop, restart, run supervisor ticks, run supervisor loops, schedule backoff, infer port ownership, or execute task/report/trade/workflow/catalog steps.
