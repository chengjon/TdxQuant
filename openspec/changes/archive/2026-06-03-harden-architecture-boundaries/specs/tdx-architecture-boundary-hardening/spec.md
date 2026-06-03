## ADDED Requirements

### Requirement: Architecture boundaries SHALL preserve public behavior while moving ownership to deeper modules
The system SHALL allow behavior-preserving extraction of command, manager, provider, and configuration responsibilities into deeper modules without changing public CLI command names, manager method names, replay-mode contracts, or provider result payload shape.

#### Scenario: Root CLI delegates a command family to a deeper module
- **WHEN** a command family is extracted from the root CLI module
- **THEN** the root CLI MUST continue to expose the same public command names
- **AND** the extracted module MUST own parser registration and command dispatch for that command family

#### Scenario: Public manager method remains stable after internal helper extraction
- **WHEN** a manager proxy method is migrated to a shared internal call envelope
- **THEN** callers MUST be able to invoke the same public method signature
- **AND** the provider-facing result envelope MUST keep the same capability, profile, timing, warnings, and artifact semantics

### Requirement: Architecture boundaries SHALL expose capability risk metadata
The system SHALL expose stable capability risk metadata that distinguishes read-only query capabilities, provider mutations, native trade mutations, and desktop trade mutations.

#### Scenario: Read-only query capability is classified
- **WHEN** code asks for the risk class of a read-only query capability
- **THEN** the system MUST return a stable `read_only_query` classification

#### Scenario: Trading-shaped mutation capability is classified
- **WHEN** code asks for the risk class of a native trade or desktop trade mutation capability
- **THEN** the system MUST return a stable mutation-oriented classification instead of treating it as read-only query behavior

### Requirement: Architecture boundaries SHALL centralize runtime config file discovery
The system SHALL provide a central runtime configuration registry for project runtime JSON files used by API profiles, task profiles, trade profiles, report presets, command catalog entries, and command bundles.

#### Scenario: Runtime config path is resolved from project root
- **WHEN** code requests a registered runtime config path
- **THEN** the system MUST resolve the path from the project root rather than process current working directory

#### Scenario: Runtime config JSON object is loaded
- **WHEN** code loads a registered runtime config file that exists and contains a JSON object
- **THEN** the system MUST return the parsed object without changing its contents

#### Scenario: Runtime config JSON is not an object
- **WHEN** code loads a registered runtime config file whose top-level JSON value is not an object
- **THEN** the system MUST reject the file with a stable validation error

### Requirement: Architecture boundaries SHALL preserve strict replay behavior during provider seam refactors
The system SHALL preserve strict replay behavior while provider execution boundaries are refactored.

#### Scenario: Replay mode handles unsupported capability
- **WHEN** a replay-mode call targets an unsupported capability
- **THEN** the system MUST return a stable replay failure
- **AND** the system MUST NOT call live Windows runtime code
