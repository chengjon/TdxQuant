## ADDED Requirements

### Requirement: Query API CLI SHALL expose replay provider mode on supported query entrypoints
The system SHALL expose replay provider mode on supported nested `api` and flat bridge-oriented query entrypoints so offline callers can validate current provider contracts without live runtime access.

#### Scenario: Caller enables replay mode on nested api command
- **WHEN** a caller invokes a supported nested `api` command with replay mode enabled
- **THEN** the CLI MUST dispatch that request through replay execution rather than live runtime execution
- **AND** the CLI MUST preserve the same provider-facing JSON envelope and exit-code semantics used by live mode

#### Scenario: Caller selects replay fixture source on a supported command
- **WHEN** a caller invokes a supported query command with replay mode plus either an explicit built-in fixture name or an explicit fixture path
- **THEN** the CLI MUST forward the replay selection unchanged to the underlying manager or replay execution layer
- **AND** the CLI MUST reject mutually exclusive or invalid replay fixture arguments before execution
