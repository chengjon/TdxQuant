## ADDED Requirements

### Requirement: Subscription watch background control SHALL expose statefile ownership diagnostics

The worker-local subscription-watch background controller SHALL include a compact read-only `statefile_ownership` diagnostic in status responses.

#### Scenario: Missing statefile reports not-present ownership

- **WHEN** no active subscription-watch statefile exists
- **THEN** controller status MUST include `statefile_ownership.status` set to `not_present`
- **AND** it MUST report that the statefile and pidfile are absent
- **AND** it MUST NOT acquire the control lock or start/stop/restart a worker.

#### Scenario: Active statefile matches owned pidfile

- **WHEN** the reconciled active statefile is active, its payload PID matches the owned pidfile, and the PID is alive
- **THEN** controller status MUST include `statefile_ownership.status` set to `owned_active`
- **AND** it MUST report `pid_matches_owned_state=true` and `process_alive=true`
- **AND** it MUST include a boundary indicating local statefile/pidfile evidence only.

#### Scenario: Active statefile has ownership mismatch

- **WHEN** the reconciled active statefile is active but the payload PID does not match the owned pidfile or the PID is not alive
- **THEN** controller status MUST include `statefile_ownership.status` set to `mismatch`
- **AND** it MUST include stable reason codes describing the mismatch
- **AND** it MUST NOT claim provider readiness, process ownership beyond the local PID evidence, or production lifecycle health.

