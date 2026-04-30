## MODIFIED Requirements

### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily API workflows.

#### Scenario: Code caller uses manager to access formula domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke formula-related capabilities through `manager.formula.<method>()`

#### Scenario: Code caller uses manager to access block domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke block-related capabilities through `manager.block.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market`, `meta`, `formula`, and `block` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Formula domain receives standardized parameters
- **WHEN** a formula domain method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Block domain receives standardized parameters
- **WHEN** a block domain method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

### Requirement: Query API management SHALL keep block writes outside the read-only meta domain
The system SHALL represent user-block write actions through a dedicated `block` domain rather than placing them inside the read-only `meta` domain.

#### Scenario: Caller updates a user block through manager
- **WHEN** a caller requests a user-block update through the manager
- **THEN** the manager MUST expose that action through `manager.block` rather than through `manager.meta`

#### Scenario: Meta domain remains read-oriented
- **WHEN** a caller accesses `manager.meta`
- **THEN** that domain MUST remain focused on read-oriented metadata capabilities rather than user-block write actions

### Requirement: Query API management SHALL keep formula preparation and execution as explicit manager-visible actions
The system SHALL expose formula data preparation and formula execution capabilities through explicit manager-visible methods instead of collapsing them into an opaque single-step manager behavior.

#### Scenario: Caller prepares formula runtime data
- **WHEN** a caller needs to prepare or inspect formula runtime data
- **THEN** the manager MUST expose explicit formula preparation methods through `manager.formula`

#### Scenario: Caller executes batch formula workflows
- **WHEN** a caller needs batch indicator or stock-picking formula execution
- **THEN** the manager MUST expose explicit batch formula methods through `manager.formula`
