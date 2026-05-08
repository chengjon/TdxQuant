## MODIFIED Requirements

### Requirement: Query API management SHALL keep block writes outside the read-only meta domain
The system SHALL represent user-block write actions through a dedicated `block` domain rather than placing them inside the read-only `meta` domain.

#### Scenario: Caller updates a user block through manager
- **WHEN** a caller requests a user-block update through the manager
- **THEN** the manager MUST expose that action through `manager.block` rather than through `manager.meta`

#### Scenario: Meta domain remains read-oriented
- **WHEN** a caller accesses `manager.meta`
- **THEN** that domain MUST remain focused on read-oriented metadata capabilities rather than user-block write actions

#### Scenario: Caller manages custom-sector lifecycle through block domain
- **WHEN** a caller needs to list, create, rename, clear, or delete a custom sector
- **THEN** the manager MUST expose those actions through `manager.block` rather than through `manager.meta`

#### Scenario: Caller synchronizes a watchlist into a custom sector through block domain
- **WHEN** a caller needs to push a normalized watchlist into a custom sector with `replace` or `merge` semantics
- **THEN** the manager MUST expose that action through `manager.block.sync_watchlist(...)`
