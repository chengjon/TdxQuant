## ADDED Requirements

### Requirement: Query API CLI SHALL expose sector transaction range replay entrypoints
The CLI SHALL allow sector transaction range query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested sector transaction range command uses replay manager
- **WHEN** a caller invokes `api sector-transaction-data --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data(...)`
- **AND** the CLI MUST NOT construct or call the live sector transaction range bridge path

#### Scenario: Flat sector transaction range command uses replay manager
- **WHEN** a caller invokes `tdx-data-sector-transaction --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened sector transaction range query metadata
