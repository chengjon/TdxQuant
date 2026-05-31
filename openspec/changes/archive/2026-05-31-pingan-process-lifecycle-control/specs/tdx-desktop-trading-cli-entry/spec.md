## ADDED Requirements

### Requirement: Trade CLI SHALL expose PingAn process lifecycle control

The stable desktop trade CLI SHALL expose an explicit PingAn process lifecycle control entrypoint.

#### Scenario: CLI parses process lifecycle control

- **WHEN** a caller parses `trade lifecycle-process --action start --statefile-path <path> --owner-token <token> --exe-path <path>`
- **THEN** the parser MUST route the command to `trade_command=lifecycle-process`
- **AND** the parsed arguments MUST preserve action, statefile path, owner token, stale timeout, executable path, and force restart flag.

#### Scenario: CLI dispatches only lifecycle process control

- **WHEN** the trade CLI dispatches `trade lifecycle-process`
- **THEN** it MUST call the PingAn lifecycle process manager method
- **AND** it MUST NOT dispatch buy, sell, submit-once, task, report, catalog, or bundle workflow execution.
