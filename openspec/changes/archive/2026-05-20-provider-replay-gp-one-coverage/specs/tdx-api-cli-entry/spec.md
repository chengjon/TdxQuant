# tdx-api-cli-entry Delta

## ADDED Requirements

### Requirement: Query API CLI SHALL expose gp-one replay entrypoints
The CLI SHALL allow gp-one query entrypoints to run in explicit replay mode through the fixture-backed manager path.

#### Scenario: Nested gp-one command uses replay manager
- **WHEN** a caller invokes `api gp-one --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gp_one_data(...)`
- **AND** the CLI MUST NOT construct or call the live gp-one bridge path

#### Scenario: Flat gp-one command uses replay manager
- **WHEN** a caller invokes `tdx-data-gp-one --provider-mode replay`
- **THEN** the CLI MUST dispatch through `TdxApiManager(provider_mode="replay").meta.gp_one_data(...)`
- **AND** the CLI output MUST preserve the provider result envelope and hardened gp-one query metadata

