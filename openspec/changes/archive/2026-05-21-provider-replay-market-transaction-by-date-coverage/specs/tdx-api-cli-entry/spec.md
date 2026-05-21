## ADDED Requirements

### Requirement: Query API CLI SHALL expose market transaction by-date replay entrypoints
The CLI SHALL allow market transaction by-date query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested market transaction by-date command uses replay manager
- **WHEN** a caller invokes `api market-transaction-data-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.market_transaction_data_by_date(...)`
- **AND** the CLI MUST NOT construct or call the live market transaction by-date bridge path

#### Scenario: Flat market transaction by-date command uses replay manager
- **WHEN** a caller invokes `tdx-data-market-transaction-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.market_transaction_data_by_date(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened market transaction by-date query metadata
