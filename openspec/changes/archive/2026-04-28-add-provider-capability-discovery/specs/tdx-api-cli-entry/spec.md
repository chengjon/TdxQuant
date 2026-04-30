## ADDED Requirements

### Requirement: Query API CLI SHALL provide nested api commands for provider discovery diagnostics
The system SHALL expose provider capability discovery and diagnostics through nested `api` commands that dispatch through `TdxApiManager.runtime`.

#### Scenario: Caller invokes nested api capabilities command
- **WHEN** a caller invokes `api capabilities`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.capabilities(...)`

#### Scenario: Caller invokes nested api health or doctor command
- **WHEN** a caller invokes `api health` or `api doctor`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.health(...)` or `TdxApiManager.runtime.doctor(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for provider discovery diagnostics
The system SHALL expose flat bridge-oriented commands for provider capability discovery and diagnostics so bridge-oriented callers can consume the same formal contract without going through the manager layer.

#### Scenario: Caller invokes flat capability discovery bridge command
- **WHEN** a caller invokes `tdx-capabilities`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for provider capability discovery

#### Scenario: Caller invokes flat health or doctor bridge command
- **WHEN** a caller invokes `tdx-health` or `tdx-doctor`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for provider health or doctor diagnostics
