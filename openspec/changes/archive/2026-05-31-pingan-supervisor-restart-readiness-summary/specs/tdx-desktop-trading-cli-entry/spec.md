## ADDED Requirements

### Requirement: Trade CLI lifecycle supervisor SHALL expose post-restart recheck flags

The stable desktop trade lifecycle supervisor CLI entrypoints SHALL expose explicit opt-in fields for post-restart broker health recheck.

#### Scenario: CLI parses restart recheck opt-in for supervisor tick

- **WHEN** a caller parses `trade lifecycle-supervisor-tick --process-restart --process-restart-recheck`
- **THEN** the parser MUST preserve `process_restart_recheck=true`
- **AND** the parser MUST preserve `process_restart_recheck_delay_seconds` when supplied.

#### Scenario: CLI forwards restart recheck opt-in for supervisor run

- **WHEN** a caller parses `trade lifecycle-supervisor-run --process-restart --process-restart-recheck`
- **THEN** the parser MUST preserve the same recheck fields for every bounded run tick
- **AND** dispatch MUST remain lifecycle-supervisor-only.
