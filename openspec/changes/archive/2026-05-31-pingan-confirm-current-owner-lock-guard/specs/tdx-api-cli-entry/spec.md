## ADDED Requirements

### Requirement: Confirm-current CLI SHALL expose lifecycle owner-lock guard options
The stable PingAn confirm-current CLI entrypoint SHALL accept lifecycle owner-lock guard options and forward them to the PingAn manager without acquiring or releasing owner locks.

#### Scenario: Trade confirm-current CLI forwards owner-lock guard options
- **WHEN** a caller runs `trade confirm-current` with lifecycle statefile path, owner token, stale timeout, and `--require-lifecycle-owner-lock`
- **THEN** the CLI MUST pass those values to `TdxTradeManager.pingan.confirm_current(...)`
- **AND** the CLI MUST NOT acquire, release, or write lifecycle owner-lock artifacts directly.

#### Scenario: Task confirm-current CLI forwards owner-lock guard options
- **WHEN** a caller runs `task trade-confirm-current` with lifecycle owner-lock guard options
- **THEN** the CLI MUST pass those values to `TdxTaskManager.trade_confirm_current(...)`
- **AND** the CLI MUST keep default confirm-current dispatch unchanged when the options are omitted.
