## MODIFIED Requirements

### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily API workflows.

#### Scenario: Code caller uses manager to access block lifecycle domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke custom-sector lifecycle capabilities through `manager.block.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market`, `meta`, `formula`, `block`, and `runtime` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Block lifecycle method receives standardized parameters
- **WHEN** a block lifecycle method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

## ADDED Requirements

### Requirement: Query API management SHALL keep custom-sector resource lifecycle inside the block domain
The system SHALL represent custom-sector listing and lifecycle actions through the `block` domain instead of splitting them across `meta` and `block`.

#### Scenario: Caller reads custom-sector list through manager
- **WHEN** a caller requests the current custom-sector list
- **THEN** the manager MUST expose that action through `manager.block.user_sectors(...)`

#### Scenario: Caller manages custom-sector lifecycle through manager
- **WHEN** a caller creates, renames, deletes, clears, or appends to a custom sector
- **THEN** the manager MUST expose those actions through `manager.block`
