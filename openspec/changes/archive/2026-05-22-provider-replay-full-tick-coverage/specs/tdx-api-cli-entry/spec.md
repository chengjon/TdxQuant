## ADDED Requirements

### Requirement: Query API CLI SHALL expose full-tick replay entrypoint
The CLI SHALL allow the full-tick query entrypoint to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested full-tick command uses replay manager
- **WHEN** a caller invokes `api full-tick --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.full_tick(...)`
- **AND** the CLI MUST NOT construct or call the live full-tick bridge path
