## ADDED Requirements

### Requirement: Desktop trading management SHALL expose explicit PingAn lifecycle owner lock control

The PingAn desktop trading management layer SHALL expose a deterministic local lifecycle owner lock surface that can inspect, acquire, and release ownership without controlling the real desktop process.

#### Scenario: Caller inspects lifecycle owner lock status

- **WHEN** a caller requests PingAn lifecycle owner lock `status` with a statefile path and owner token
- **THEN** the manager SHALL return a successful read-only payload
- **AND** the payload SHALL include the requested action, statefile path, lock path, owner token, stale detection fields, and `statefile_write_executed=false`.

#### Scenario: Caller acquires lifecycle owner lock

- **WHEN** a caller requests PingAn lifecycle owner lock `acquire` with a statefile path and owner token
- **THEN** the manager SHALL create the parent directory when needed
- **AND** the manager SHALL write a sibling lock file and lifecycle statefile recording `status=owned`
- **AND** the result payload SHALL report `lock_acquired=true`, `statefile_write_executed=true`, and the owner token.

#### Scenario: Caller releases lifecycle owner lock

- **WHEN** a caller requests PingAn lifecycle owner lock `release` with the same owner token recorded in the statefile
- **THEN** the manager SHALL remove the sibling lock file when present
- **AND** the manager SHALL write a lifecycle statefile recording `status=released`
- **AND** the result payload SHALL report `lock_released=true` and `statefile_write_executed=true`.

#### Scenario: Caller does not own an active lifecycle lock

- **WHEN** a caller attempts to acquire a non-stale lock owned by another owner token
- **THEN** the manager SHALL reject the request without overwriting the statefile or lock file
- **AND** the payload SHALL report the blocking owner token, stale status, and `statefile_write_executed=false`.

#### Scenario: Caller handles stale lifecycle lock explicitly

- **WHEN** a caller attempts to acquire a stale lock
- **THEN** the manager SHALL report stale status
- **AND** the manager SHALL replace the stale lock only when the caller explicitly enables stale replacement.
