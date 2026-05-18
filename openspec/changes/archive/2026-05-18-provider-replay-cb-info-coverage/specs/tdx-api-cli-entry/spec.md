# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose cb-info replay entrypoints
The CLI SHALL allow cb-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested cb-info command uses replay manager
- **WHEN** a caller invokes `api cb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.cb_info(...)`
- **AND** the CLI MUST NOT construct or call the live cb-info bridge path

#### Scenario: Flat cb-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-cb-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").market.cb_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened cb-info query metadata
