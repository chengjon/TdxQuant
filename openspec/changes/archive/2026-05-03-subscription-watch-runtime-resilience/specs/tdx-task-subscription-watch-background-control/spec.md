## ADDED Requirements

### Requirement: Subscription watch background control SHALL reconcile reconnecting and degraded as active-process states
The system SHALL extend worker-local background-control reconciliation so resilience runtime states are interpreted consistently with process ownership and liveness.

#### Scenario: Reconnecting or degraded process loss becomes stale-process failure
- **WHEN** background control finds `active.json` in `reconnecting` or `degraded` but the owned pid is missing, mismatched, or no longer alive
- **THEN** the system MUST normalize the run to `failed`
- **AND** the normalization reason MUST be `stale_process_state`

#### Scenario: Stopping process loss remains a stopped terminal normalization
- **WHEN** background control finds `active.json` in `stopping` but the owned pid is missing or dead
- **THEN** the system MUST normalize the run to `stopped`

### Requirement: Subscription watch background control SHALL expose terminal resilience cleanup coherently
The system SHALL keep terminal background-control views coherent with the foreground resilience contract when a run leaves reconnect/degraded states.

#### Scenario: Terminal status clears stale reconnect schedule
- **WHEN** a `subscription-watch` run reaches `completed`, `interrupted`, or `failed`
- **THEN** the persisted terminal `status.json` MUST clear `next_reconnect_at`
- **AND** background and bridge readers MUST NOT expose a future reconnect probe time for that terminal run
