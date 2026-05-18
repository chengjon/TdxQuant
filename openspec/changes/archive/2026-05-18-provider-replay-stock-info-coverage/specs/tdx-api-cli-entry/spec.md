# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose stock-info replay entrypoints
The CLI SHALL allow stock-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested stock-info command uses replay manager
- **WHEN** a caller invokes `api stock-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.stock_info(...)`
- **AND** the CLI MUST NOT construct or call the live stock-info bridge path

#### Scenario: Flat stock-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-stock-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.stock_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened stock-info query metadata
