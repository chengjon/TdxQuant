## ADDED Requirements

### Requirement: Trade CLI lifecycle supervisor SHALL expose process restart opt-in flags

The stable desktop trade lifecycle supervisor CLI entrypoints SHALL expose explicit opt-in fields for recorded-PID process restart.

#### Scenario: CLI parses process restart opt-in for supervisor tick

- **WHEN** a caller parses `trade lifecycle-supervisor-tick --process-restart --process-exe-path <path>`
- **THEN** the parser MUST preserve `process_restart=true`
- **AND** the parser MUST preserve the process executable path and force-process-restart flag.

#### Scenario: CLI forwards process restart opt-in for supervisor run

- **WHEN** a caller parses `trade lifecycle-supervisor-run --process-restart --process-exe-path <path>`
- **THEN** the parser MUST preserve the same opt-in fields for every bounded run tick
- **AND** dispatch MUST remain lifecycle-supervisor-only, without buy/sell/submit/task/report/catalog workflow execution.
