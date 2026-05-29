## ADDED Requirements

### Requirement: Subscription watch background control SHALL persist latest supervisor-run observation

The worker-local subscription-watch background controller SHALL persist a compact latest observation after a bounded foreground supervisor run when an existing control statefile can be updated.

#### Scenario: Foreground run records compact wait observation

- **WHEN** supervisor run completes after bounded waiting ticks
- **THEN** the controller MUST persist `last_supervisor_run_observation` with schema version, status, final decision, tick count, max ticks, interval, reason, action flag, tick status counts, tick decision counts, and boundary
- **AND** it MUST NOT persist raw tick summaries, raw start results, raw start requests, logs, or file paths.

#### Scenario: Foreground run records compact recovery observation

- **WHEN** supervisor run stops early after a recovered tick
- **THEN** the persisted observation MUST include recovered final status and optional `previous_run_id` / `new_run_id`
- **AND** it MUST NOT change supervisor-run stop/continue semantics.

#### Scenario: No statefile does not create observation state

- **WHEN** supervisor run no-ops and no control statefile exists
- **THEN** the controller MUST NOT create a new lifecycle statefile only to store the observation
- **AND** it MUST still return the supervisor-run result to the caller.

