## MODIFIED Requirements

### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller invokes nested api divid-factors command
- **WHEN** a caller invokes the nested `api divid-factors` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.meta.divid_factors(...)`

#### Scenario: Caller invokes nested api ipo-info command
- **WHEN** a caller invokes the nested `api ipo-info` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.meta.ipo_info(...)`

## ADDED Requirements

### Requirement: Query API CLI SHALL expose flat bridge commands for reference data queries
The system SHALL expose flat bridge commands for dividend-factor and IPO reference data so that bridge-oriented callers can use the same capabilities without going through the manager layer.

#### Scenario: Caller invokes flat divid-factors bridge command
- **WHEN** a caller invokes `tdx-data-divid-factors`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_divid_factors`

#### Scenario: Caller invokes flat ipo-info bridge command
- **WHEN** a caller invokes `tdx-data-ipo-info`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_ipo_info`
