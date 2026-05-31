## ADDED Requirements

### Requirement: Trade CLI SHALL expose a PingAn lifecycle owner lock subcommand

The stable desktop trade CLI SHALL expose a nested `trade lifecycle-owner-lock` subcommand for explicit local PingAn lifecycle owner lock operations.

#### Scenario: Caller parses lifecycle owner lock status command

- **WHEN** a caller parses `trade lifecycle-owner-lock --action status --statefile-path <path> --owner-token <token>`
- **THEN** the parser SHALL set `trade_command=lifecycle-owner-lock`
- **AND** it SHALL expose `action`, `statefile_path`, `owner_token`, `stale_after_seconds`, and `force_stale` arguments.

#### Scenario: Caller dispatches lifecycle owner lock command

- **WHEN** a caller dispatches `trade lifecycle-owner-lock`
- **THEN** the CLI SHALL call `TdxTradeManager.pingan.lifecycle_owner_lock(...)`
- **AND** it SHALL forward action, statefile path, owner token, stale timeout, and forced stale replacement.

#### Scenario: Lifecycle owner lock CLI remains explicit operator statefile control

- **WHEN** a caller uses `trade lifecycle-owner-lock`
- **THEN** the CLI SHALL NOT submit orders, run catalog workflows, start or stop the PingAn desktop process, restart, kill, supervise, or execute backoff.
