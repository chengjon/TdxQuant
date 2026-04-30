## MODIFIED Requirements

### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller invokes nested api user-sectors command
- **WHEN** a caller invokes the nested `api user-sectors` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.block.user_sectors(...)`

#### Scenario: Caller invokes nested api create-sector command
- **WHEN** a caller invokes the nested `api create-sector` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.block.create_sector(...)`

#### Scenario: Caller invokes nested api delete-sector command
- **WHEN** a caller invokes the nested `api delete-sector` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.block.delete_sector(...)`

#### Scenario: Caller invokes nested api rename-sector command
- **WHEN** a caller invokes the nested `api rename-sector` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.block.rename_sector(...)`

#### Scenario: Caller invokes nested api clear-sector command
- **WHEN** a caller invokes the nested `api clear-sector` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.block.clear_sector(...)`

## ADDED Requirements

### Requirement: Query API CLI SHALL expose flat bridge commands for custom-sector lifecycle actions
The system SHALL expose flat bridge commands for custom-sector lifecycle actions so that bridge-oriented callers can use the same capabilities without going through the manager layer.

#### Scenario: Caller invokes flat get-user-sector bridge command
- **WHEN** a caller invokes `tdx-get-user-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_user_sector`

#### Scenario: Caller invokes flat create-sector bridge command
- **WHEN** a caller invokes `tdx-create-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `create_sector`

#### Scenario: Caller invokes flat delete-sector bridge command
- **WHEN** a caller invokes `tdx-delete-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `delete_sector`

#### Scenario: Caller invokes flat rename-sector bridge command
- **WHEN** a caller invokes `tdx-rename-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `rename_sector`

#### Scenario: Caller invokes flat clear-sector bridge command
- **WHEN** a caller invokes `tdx-clear-sector`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `clear_sector`
