## ADDED Requirements

### Requirement: Query API CLI SHALL expose sector transaction by-date replay entrypoints
The CLI SHALL allow sector transaction by-date query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested sector transaction by-date command uses replay manager
- **WHEN** a caller invokes `api sector-transaction-data-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data_by_date(...)`
- **AND** the CLI MUST NOT construct or call the live sector transaction by-date bridge path

#### Scenario: Flat sector transaction by-date command uses replay manager
- **WHEN** a caller invokes `tdx-data-sector-transaction-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data_by_date(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened sector transaction by-date query metadata
