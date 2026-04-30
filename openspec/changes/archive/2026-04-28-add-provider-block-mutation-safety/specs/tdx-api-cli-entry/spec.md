## ADDED Requirements

### Requirement: Query API CLI SHALL expose block mutation safety options on write commands
The system SHALL expose explicit block mutation safety arguments on both nested `api` and flat bridge-oriented block write commands.

#### Scenario: Caller passes mutation safety options through nested api block write
- **WHEN** a caller invokes `api create-sector`, `delete-sector`, `rename-sector`, `clear-sector`, or `send-user-block` with `--mutation-key` and/or `--audit-dir`
- **THEN** the CLI MUST dispatch those values unchanged through the manager block write action

#### Scenario: Caller passes mutation safety options through flat bridge block write
- **WHEN** a caller invokes `tdx-create-sector`, `tdx-delete-sector`, `tdx-rename-sector`, `tdx-clear-sector`, or `tdx-send-user-block` with `--mutation-key` and/or `--audit-dir`
- **THEN** the CLI MUST dispatch those values unchanged through the corresponding bridge wrapper

### Requirement: Query API CLI SHALL emit the block mutation safety contract on write commands
The system SHALL emit the standardized block mutation summary and audit artifact metadata for supported block write commands.

#### Scenario: Nested api block write returns standardized mutation contract
- **WHEN** a nested `api` block write command completes
- **THEN** the JSON result MUST include the standardized `data.block_mutation` payload and audit artifact metadata

#### Scenario: Flat bridge block write returns standardized mutation contract
- **WHEN** a flat bridge block write command completes
- **THEN** the JSON result MUST include the standardized `data.block_mutation` payload and audit artifact metadata
