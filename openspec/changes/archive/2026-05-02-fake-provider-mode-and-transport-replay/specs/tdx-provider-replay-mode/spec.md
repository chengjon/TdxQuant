## ADDED Requirements

### Requirement: Provider replay mode SHALL serve supported capabilities through deterministic fixture-backed execution
The system SHALL provide an in-process replay provider mode for selected provider-facing capabilities so callers can consume stable offline responses through the same public entrypoints used by live mode.

#### Scenario: Replay mode uses default built-in fixture for a supported synchronous capability
- **WHEN** a caller invokes a supported synchronous provider-facing capability in replay mode without explicitly selecting a fixture
- **THEN** the system MUST resolve a stable built-in fixture for that capability
- **AND** the returned result MUST match the provider contract for that capability without touching live Windows runtime code

#### Scenario: Replay mode uses an explicit built-in fixture override
- **WHEN** a caller invokes a supported capability in replay mode with an explicit built-in fixture name
- **THEN** the system MUST load that named fixture instead of the default capability mapping
- **AND** the returned result MUST preserve the current capability-specific contract fields

#### Scenario: Replay mode uses an explicit fixture path override
- **WHEN** a caller invokes a supported capability in replay mode with an explicit JSON or JSONL fixture path
- **THEN** the system MUST load the caller-supplied fixture asset instead of a built-in sample
- **AND** the system MUST reject malformed fixture content before emitting a replay result

### Requirement: Provider replay mode SHALL reject unsupported or unresolved replay execution without live fallback
The system SHALL treat replay mode as a strict offline execution path and MUST never silently route replay-mode calls to live Windows runtime code.

#### Scenario: Replay mode rejects unsupported capability
- **WHEN** a caller invokes a capability that replay mode does not support
- **THEN** the system MUST return a stable failure result describing the unsupported replay capability
- **AND** the system MUST NOT attempt a live provider call

#### Scenario: Replay mode rejects missing fixture resolution
- **WHEN** a caller invokes replay mode and no default, named, or path-based fixture can be resolved for the requested capability
- **THEN** the system MUST return a stable failure result describing the unresolved replay fixture
- **AND** the system MUST NOT attempt a live provider call
