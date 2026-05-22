## ADDED Requirements

### Requirement: Query API CLI SHALL expose sector-list replay entrypoints
The CLI SHALL allow sector-list query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested sector-list command uses replay manager
- **WHEN** a caller invokes `api sector-list --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.sector_list(...)`
- **AND** the CLI MUST NOT construct or call the live sector-list bridge path

#### Scenario: Flat sector-list command uses replay manager
- **WHEN** a caller invokes `tdx-data-sector-list --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.sector_list(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened sector-list query metadata
