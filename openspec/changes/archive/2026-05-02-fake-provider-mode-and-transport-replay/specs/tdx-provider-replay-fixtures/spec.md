## ADDED Requirements

### Requirement: Provider replay fixtures SHALL support deterministic replay selection for supported capabilities
The system SHALL let replay-mode callers resolve built-in fixtures by capability-default mapping or by explicit fixture name so supported capabilities can run offline without bespoke fixture lookup logic in every caller.

#### Scenario: Replay caller resolves default fixture by capability
- **WHEN** a replay-mode caller requests a supported capability without naming a fixture
- **THEN** the replay fixture layer MUST expose a deterministic built-in default fixture for that capability

#### Scenario: Replay caller resolves explicit built-in fixture name
- **WHEN** a replay-mode caller names a built-in fixture explicitly
- **THEN** the replay fixture layer MUST resolve that fixture by stable manifest name
- **AND** the resolved fixture metadata MUST still describe its capability, format, and path

### Requirement: Provider replay fixtures SHALL validate explicit external fixture sources
The system SHALL allow replay callers to override built-in fixtures with explicit JSON or JSONL assets while preserving stable loader semantics and early validation.

#### Scenario: Replay caller provides explicit external fixture path
- **WHEN** a replay-mode caller provides an explicit fixture file path for a supported capability
- **THEN** the loader MUST parse that asset according to its expected JSON or JSONL contract
- **AND** the loader MUST reject unsupported file formats or malformed payloads before replay execution begins
