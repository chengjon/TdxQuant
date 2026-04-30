## ADDED Requirements

### Requirement: Query API CLI SHALL provide a nested api command for client warn sending
The system SHALL expose client warn sending through a nested `api` subcommand that dispatches through `TdxApiManager.runtime`.

#### Scenario: Caller invokes nested api send-warn command
- **WHEN** a caller invokes `api send-warn`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.send_warn(...)`

### Requirement: Query API CLI SHALL expose a flat bridge command for client warn sending
The system SHALL keep flat bridge-oriented CLI access available for client warn sending alongside the nested `api` manager path.

#### Scenario: Caller invokes flat send-warn bridge command
- **WHEN** a caller invokes `tdx-send-warn`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `send_warn`

### Requirement: Query API CLI SHALL keep warn batch payloads explicit
The system SHALL require callers to pass warn batch payload lists explicitly and SHALL preserve the official `count` semantics for warn sending.

#### Scenario: CLI send-warn command requires stock and time payload lists
- **WHEN** a caller invokes `api send-warn` or `tdx-send-warn`
- **THEN** the CLI MUST require explicit repeated inputs for stock codes and warn times before dispatch

#### Scenario: CLI send-warn command preserves explicit count
- **WHEN** a caller invokes a send-warn CLI command with `--count 3`
- **THEN** the CLI MUST pass that `count` value through unchanged
