## ADDED Requirements

### Requirement: Subscription watch background control SHALL persist latest supervisor-tick observation

The worker-local subscription-watch background controller SHALL record a compact latest observation for explicit supervisor tick calls when an existing control statefile can hold the observation.

#### Scenario: Tick wait records compact observation on existing backoff state

- **WHEN** supervisor tick is invoked while restart backoff is still active
- **THEN** the controller MUST persist `last_supervisor_tick_observation` with schema version, status, decision, action flag, reason codes, reason, and boundary
- **AND** the observation MUST NOT include raw restart backoff, raw start results, raw start requests, logs, file paths, or provider credentials.

#### Scenario: Tick recovery records compact handoff observation

- **WHEN** supervisor tick recovers by starting a replacement run after restart backoff expires
- **THEN** the controller MUST persist `last_supervisor_tick_observation` with schema version, recovered status/decision, action flag, previous run id, new run id, compact start-request summary, reason, and boundary
- **AND** the persisted observation MUST NOT expose the raw start result or raw start request.

#### Scenario: Tick noop without statefile does not create observation state

- **WHEN** supervisor tick is invoked without any actionable restart backoff or existing control statefile
- **THEN** the controller MUST return the existing no-op tick result
- **AND** it MUST NOT create a lifecycle statefile solely to record `last_supervisor_tick_observation`.

#### Scenario: Failed tick records compact failure observation when state exists

- **WHEN** supervisor tick cannot evaluate a replacement because existing restart backoff state is missing a valid start request
- **THEN** the controller MUST persist `last_supervisor_tick_observation` with failed status, failed decision, error code, reason codes, reason, and boundary
- **AND** it MUST NOT schedule automatic retry or execute an additional lifecycle action.
