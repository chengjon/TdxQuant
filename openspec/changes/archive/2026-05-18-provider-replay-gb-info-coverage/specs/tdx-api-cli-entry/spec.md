# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose gb-info replay entrypoints
The CLI SHALL allow gb-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested gb-info command uses replay manager
- **WHEN** a caller invokes `api gb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gb_info(...)`
- **AND** the CLI MUST NOT construct or call the live gb-info bridge path

#### Scenario: Flat gb-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-gb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gb_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened gb-info query metadata

