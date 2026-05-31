## ADDED Requirements

### Requirement: Trade CLI SHALL expose PingAn lifecycle supervisor control subcommands

The stable desktop trade CLI SHALL expose explicit PingAn lifecycle supervisor control entrypoints for one-shot tick and bounded foreground run operations.

#### Scenario: CLI parses a supervisor tick command

- **WHEN** a caller parses `trade lifecycle-supervisor-tick --statefile-path <path> --owner-token <token>`
- **THEN** the parser MUST route the command to the trade subcommand dispatcher as `trade_command=lifecycle-supervisor-tick`
- **AND** the parsed arguments MUST preserve statefile path, owner token, stale timeout, restart-attempt limit, and backoff settings.

#### Scenario: CLI parses a bounded supervisor run command

- **WHEN** a caller parses `trade lifecycle-supervisor-run --statefile-path <path> --owner-token <token> --max-ticks <N>`
- **THEN** the parser MUST route the command to the trade subcommand dispatcher as `trade_command=lifecycle-supervisor-run`
- **AND** the parsed arguments MUST preserve statefile path, owner token, max tick count, interval, stale timeout, restart-attempt limit, and backoff settings.

#### Scenario: CLI dispatch remains explicit lifecycle control only

- **WHEN** the trade CLI dispatches either supervisor command
- **THEN** it MUST call the corresponding PingAn manager lifecycle supervisor method
- **AND** it MUST NOT dispatch buy, sell, submit-once, task, report, catalog, or bundle workflow execution.
