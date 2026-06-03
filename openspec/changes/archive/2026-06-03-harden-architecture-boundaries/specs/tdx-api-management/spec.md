## ADDED Requirements

### Requirement: Query API management SHALL support a shared manager-call envelope
The system SHALL provide a shared manager-call envelope for manager proxy methods that need profile metadata, timing capture, replay dispatch, and provider result metadata.

#### Scenario: Manager call envelope attaches standard metadata
- **WHEN** a manager proxy method executes through the shared manager-call envelope
- **THEN** the returned result MUST include the same standardized manager metadata and provider contract fields as equivalent manually wrapped manager calls

#### Scenario: Manager call envelope uses replay dispatch for supported capabilities
- **WHEN** the manager is in replay mode and a migrated manager proxy method executes through the shared manager-call envelope with a capability identity
- **THEN** the envelope MUST execute through the existing replay dispatch path
- **AND** it MUST NOT invoke the live call

#### Scenario: Manager call envelope preserves live behavior outside replay mode
- **WHEN** the manager is in live mode and a migrated manager proxy method executes through the shared manager-call envelope
- **THEN** the envelope MUST invoke the provided live call exactly once
