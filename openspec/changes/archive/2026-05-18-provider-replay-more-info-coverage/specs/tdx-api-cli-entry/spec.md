# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose more-info replay entrypoints
The CLI SHALL allow more-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested more-info command uses replay manager
- **WHEN** a caller invokes `api more-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.more_info(...)`
- **AND** the CLI MUST NOT construct or call the live more-info bridge path

#### Scenario: Flat more-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-more-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.more_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened more-info query metadata
