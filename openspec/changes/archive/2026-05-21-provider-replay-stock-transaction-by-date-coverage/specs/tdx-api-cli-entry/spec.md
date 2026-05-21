## ADDED Requirements

### Requirement: Query API CLI SHALL expose stock transaction by-date replay entrypoints
The CLI SHALL allow stock transaction by-date query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested stock transaction by-date command uses replay manager
- **WHEN** a caller invokes `api stock-transaction-data-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.stock_transaction_data_by_date(...)`
- **AND** the CLI MUST NOT construct or call the live stock transaction by-date bridge path

#### Scenario: Flat stock transaction by-date command uses replay manager
- **WHEN** a caller invokes `tdx-data-stock-transaction-by-date --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").transaction.stock_transaction_data_by_date(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened stock transaction by-date query metadata
