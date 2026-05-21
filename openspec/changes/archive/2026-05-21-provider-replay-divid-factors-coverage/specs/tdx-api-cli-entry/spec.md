# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose divid-factors replay entrypoints
The CLI SHALL allow divid-factors query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested divid-factors command uses replay manager
- **WHEN** a caller invokes `api divid-factors --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.divid_factors(...)`
- **AND** the CLI MUST NOT construct or call the live divid-factors bridge path

#### Scenario: Flat divid-factors command uses replay manager
- **WHEN** a caller invokes `tdx-data-divid-factors --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.divid_factors(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened divid-factors query metadata

