## MODIFIED Requirements

### Requirement: Query API CLI SHALL expose replay provider mode on supported query entrypoints
The system SHALL expose replay provider mode on supported nested `api` and flat bridge-oriented query entrypoints so offline callers can validate current provider contracts without live runtime access.

#### Scenario: Caller enables replay mode on a supported nested api command
- **WHEN** a caller invokes a supported nested `api` command with replay mode enabled
- **THEN** the CLI MUST dispatch that request through replay execution rather than live runtime execution
- **AND** the CLI MUST preserve the same provider-facing JSON envelope and exit-code semantics used by live mode

#### Scenario: Caller enables replay mode on an unsupported nested api command
- **WHEN** a caller invokes a nested `api` command outside the supported replay matrix with replay mode enabled
- **THEN** the CLI MUST reject the request before constructing live runtime manager execution
- **AND** the returned failure JSON MUST include replay source metadata for the rejected capability

#### Scenario: Caller selects replay fixture source on a supported command
- **WHEN** a caller invokes a supported query command with replay mode plus either an explicit built-in fixture name or an explicit fixture path
- **THEN** the CLI MUST forward the replay selection unchanged to the underlying manager or replay execution layer
- **AND** the CLI MUST reject mutually exclusive or invalid replay fixture arguments before execution

#### Scenario: Caller relies on default replay fixture resolution
- **WHEN** a caller invokes a supported replay-enabled query command without `--fixture` or `--fixture-path`
- **THEN** the CLI MUST let replay execution resolve the capability-default built-in fixture
- **AND** the CLI MUST NOT silently fall back to live Windows runtime execution when replay fixture resolution fails

#### Scenario: Caller uses output mirroring in replay mode
- **WHEN** a caller invokes a supported replay-enabled query command with `--output`
- **THEN** stdout MUST still emit exactly one machine-readable JSON result
- **AND** the file written through `--output` MUST contain the same JSON payload as stdout

#### Scenario: Caller invokes an unsupported flat replay command
- **WHEN** a caller invokes a flat command outside the supported replay matrix with replay mode enabled
- **THEN** the CLI MUST return a stable failure JSON result instead of dispatching to live bridge execution
- **AND** the failure payload MUST include replay source metadata for the rejected flat command
