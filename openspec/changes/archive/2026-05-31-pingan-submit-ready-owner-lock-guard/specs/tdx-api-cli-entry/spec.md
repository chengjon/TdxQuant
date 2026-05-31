## ADDED Requirements

### Requirement: Submit-ready CLI SHALL expose lifecycle owner-lock guard options
The stable PingAn submit-ready CLI entrypoint SHALL accept lifecycle owner-lock guard options and forward them to the PingAn manager without acquiring or releasing owner locks.

#### Scenario: Trade submit-ready CLI forwards owner-lock guard options
- **WHEN** a caller runs `trade submit-ready` with lifecycle statefile path, owner token, stale timeout, and `--require-lifecycle-owner-lock`
- **THEN** the CLI MUST pass those values to `TdxTradeManager.pingan.submit_ready(...)`
- **AND** the CLI MUST NOT acquire, release, or write lifecycle owner-lock artifacts directly.

#### Scenario: Task submit-ready CLI forwards owner-lock guard options
- **WHEN** a caller runs `task trade-submit-ready` with lifecycle owner-lock guard options
- **THEN** the CLI MUST pass those values to `TdxTaskManager.trade_submit_ready(...)`
- **AND** the CLI MUST keep default submit-ready dispatch unchanged when the options are omitted.
