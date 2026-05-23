## ADDED Requirements

### Requirement: Bridge CLI SHALL expose read-only watch event inspection commands
The system SHALL expose bridge CLI commands for read-only subscription watch event inspection by forwarding to the existing master registry client helpers.

#### Scenario: Caller inspects watch events as JSON
- **WHEN** a caller invokes `bridge watch-events` with a registry and worker
- **THEN** the CLI MUST dispatch through the bridge registry watch-events helper
- **AND** the CLI MUST print the existing bridge JSON envelope

#### Scenario: Caller inspects watch events as SSE text
- **WHEN** a caller invokes `bridge watch-events-stream` with a registry and worker
- **THEN** the CLI MUST dispatch through the bridge registry watch-events-stream helper
- **AND** the CLI MUST print raw SSE text without wrapping it in a JSON envelope

#### Scenario: Watch event inspection remains read-only
- **WHEN** a caller invokes either bridge watch event inspection command
- **THEN** the CLI MUST NOT start, stop, restart, schedule, or mutate a subscription-watch worker
- **AND** the command MUST preserve the existing worker registry and authentication semantics
