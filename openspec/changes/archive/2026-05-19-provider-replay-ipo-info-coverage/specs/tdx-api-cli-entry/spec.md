# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose ipo-info replay entrypoints
The CLI SHALL allow ipo-info query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested ipo-info command uses replay manager
- **WHEN** a caller invokes `api ipo-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.ipo_info(...)`
- **AND** the CLI MUST NOT construct or call the live ipo-info bridge path

#### Scenario: Flat ipo-info command uses replay manager
- **WHEN** a caller invokes `tdx-data-ipo-info --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.ipo_info(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened ipo-info query metadata

