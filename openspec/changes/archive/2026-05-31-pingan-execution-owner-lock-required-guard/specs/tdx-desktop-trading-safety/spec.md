## ADDED Requirements

### Requirement: PingAn execution SHALL optionally require local lifecycle owner lock ownership

Side-effecting PingAn desktop trade execution methods SHALL support an opt-in local lifecycle owner-lock requirement that is evaluated before desktop automation dispatch.

#### Scenario: Required owner lock blocks buy execution before desktop dispatch

- **WHEN** a caller executes PingAn buy with `require_lifecycle_owner_lock=true`
- **AND** the local lifecycle owner lock is missing, stale, released, unknown, or held by another owner token
- **THEN** the result MUST be rejected before desktop automation dispatch
- **AND** `trade_safety.risk_gate.lifecycle_owner_lock_required_status` MUST report `requirement_status=failed`
- **AND** the guard MUST NOT acquire or release owner locks.

#### Scenario: Required owner lock allows execution when owned by caller token

- **WHEN** a caller executes PingAn buy, sell, buy-submit-once, or sell-submit-once with `require_lifecycle_owner_lock=true`
- **AND** the local lifecycle owner lock is `owned`, non-stale, and owned by the caller token
- **THEN** the guard MUST report `requirement_status=passed`
- **AND** the desktop execution path MAY proceed to the existing risk/idempotency and desktop automation flow.

### Requirement: PingAn execution owner-lock guard SHALL remain local safety evidence

The PingAn execution owner-lock guard SHALL remain a local statefile safety guard and SHALL NOT imply real process lifecycle control.

#### Scenario: Execution guard remains bounded

- **WHEN** PingAn execution reports `lifecycle_owner_lock_required_status`
- **THEN** the status MUST report `pid_ownership_claimed=false`
- **AND** it MUST report no start, stop, restart, kill, supervisor ownership, backoff execution, owner lock acquire/release, or lifecycle statefile write from the guard itself.
