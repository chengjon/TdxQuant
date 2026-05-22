## ADDED Requirements

### Requirement: Query API CLI SHALL expose market-snapshot replay entrypoints
The CLI SHALL allow market-snapshot query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested market-snapshot command uses replay manager
- **WHEN** a caller invokes `api market-snapshot --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.market_snapshot(...)`
- **AND** the CLI MUST NOT construct or call the live market-snapshot bridge path

#### Scenario: Flat market-snapshot command uses replay manager
- **WHEN** a caller invokes `tdx-data-market-snapshot --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.market_snapshot(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened market-snapshot query metadata
