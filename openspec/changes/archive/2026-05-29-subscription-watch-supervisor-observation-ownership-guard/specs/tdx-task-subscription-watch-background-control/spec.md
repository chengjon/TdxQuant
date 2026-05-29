## ADDED Requirements

### Requirement: Subscription watch background control SHALL guard supervisor observation writes by run ownership

The worker-local subscription-watch background controller SHALL avoid attaching supervisor tick/run observations to a control statefile that no longer belongs to the run associated with the observation.

#### Scenario: Supervisor tick observation is skipped after ownership changes

- **WHEN** supervisor tick produces a recovered observation for an expected replacement run
- **AND** the active statefile points at a different run before the observation merge
- **THEN** the controller MUST return the original tick result unchanged
- **AND** it MUST NOT write `last_supervisor_tick_observation` into the different run's control statefile.

#### Scenario: Supervisor run observation is skipped after ownership changes

- **WHEN** bounded supervisor run produces an aggregate observation for an expected recovered run
- **AND** the active statefile points at a different run before the observation merge
- **THEN** the controller MUST return the original supervisor-run result unchanged
- **AND** it MUST NOT write `last_supervisor_run_observation` into the different run's control statefile.

#### Scenario: Missing ownership evidence preserves best-effort behavior

- **WHEN** a supervisor observation has no expected run id
- **THEN** the controller MAY keep the existing best-effort observation merge into an existing active payload
- **AND** it MUST NOT create a lifecycle statefile solely to record an observation.
