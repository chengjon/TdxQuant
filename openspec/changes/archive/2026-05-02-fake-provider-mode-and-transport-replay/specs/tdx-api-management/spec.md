## ADDED Requirements

### Requirement: Query API management SHALL support replay provider mode for supported capabilities
The system SHALL let `TdxApiManager` dispatch selected capabilities through replay mode so offline callers can use the same manager entrypoints as live callers.

#### Scenario: Manager constructs replay mode for a supported synchronous capability
- **WHEN** a caller constructs `TdxApiManager` with replay provider mode enabled and invokes a supported synchronous capability
- **THEN** the manager MUST resolve that capability through replay execution rather than through the live bridge path
- **AND** the returned result MUST preserve current manager metadata and provider-facing result semantics

#### Scenario: Manager accepts replay fixture selectors
- **WHEN** a caller constructs `TdxApiManager` with replay-mode fixture selectors such as a fixture name, fixture path, or capability-keyed replay map
- **THEN** the manager MUST use those selectors to choose replay assets for supported capabilities
- **AND** explicit selectors MUST take precedence over default capability-to-fixture mapping
