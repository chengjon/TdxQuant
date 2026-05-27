## ADDED Requirements

### Requirement: Provider replay daemon lifecycle design SHALL define future control boundaries

The provider replay daemon lifecycle design SHALL define future start, stop, lifecycle status, restart, and backoff boundaries without changing the current provider-replay runtime behavior.

#### Scenario: Current status remains non-lifecycle-managing

- **WHEN** a caller uses the existing provider-replay status, probe, or summary view commands
- **THEN** the commands MUST remain read-only lifecycle boundary inspections
- **AND** they MUST NOT start, stop, restart, daemonize, schedule, supervise, or apply backoff
- **AND** lifecycle support fields MUST continue to distinguish configured replay capability from managed daemon control

#### Scenario: Future start is explicit and ownership-tracked

- **WHEN** a future lifecycle controller introduces provider-replay start behavior
- **THEN** start MUST require an explicit operator action and explicit replay config
- **AND** it MUST record ownership metadata sufficient to distinguish controller-owned replay processes from arbitrary already-running services
- **AND** it MUST NOT imply live provider, broker, workflow, or write readiness

#### Scenario: Future stop fails closed without ownership proof

- **WHEN** a future lifecycle controller introduces provider-replay stop behavior
- **THEN** stop MUST target only a process that the controller can prove it owns
- **AND** it MUST NOT kill arbitrary processes discovered only by port, probe, or HTTP reachability
- **AND** absence of an owned process MUST be reported as a lifecycle boundary, not hidden as successful daemon control

#### Scenario: Future lifecycle status separates ownership from reachability

- **WHEN** a future lifecycle controller reports daemon lifecycle status
- **THEN** status MUST distinguish configured replay capability, owned process state, observed HTTP health, and stale or missing ownership metadata
- **AND** a reachable probe alone MUST NOT be treated as proof that the lifecycle controller owns the process
- **AND** status MUST remain safe to run without mutating provider or daemon state

#### Scenario: Future restart and backoff remain explicit lifecycle control

- **WHEN** a future lifecycle controller introduces restart or supervised backoff behavior
- **THEN** restart MUST require ownership proof and explicit lifecycle control
- **AND** read-only status, probe, summary, catalog discovery, or validation commands MUST NOT trigger restart
- **AND** backoff policy MUST expose retry count, delay window, last failure reason, and whether the next retry is pending or blocked
- **AND** automatic restart/backoff MUST be opt-in and bounded rather than implied by the current replay status surface

