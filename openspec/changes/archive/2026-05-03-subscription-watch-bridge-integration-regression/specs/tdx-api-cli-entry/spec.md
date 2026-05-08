## ADDED Requirements

### Requirement: Query API CLI SHALL expose bridge remote-control read commands for subscription-watch control planes
The system SHALL expose remote-control CLI read commands for the worker bridge control plane and keep them as transport-only JSON pass-through entrypoints.

#### Scenario: Caller invokes bridge health
- **WHEN** a caller invokes `tdxquant bridge health`
- **THEN** the CLI MUST dispatch the call through the master-side bridge registry/client
- **AND** stdout MUST print the resulting JSON payload unchanged

#### Scenario: Caller invokes bridge watch-list or watch-artifacts
- **WHEN** a caller invokes `tdxquant bridge watch-list` or `tdxquant bridge watch-artifacts`
- **THEN** the CLI MUST dispatch the call through the master-side bridge registry/client
- **AND** stdout MUST print the resulting JSON payload unchanged

#### Scenario: Caller invokes bridge watch-events or watch-logs with tail
- **WHEN** a caller invokes `tdxquant bridge watch-events --tail <n>` or `tdxquant bridge watch-logs --tail <n>`
- **THEN** the CLI MUST pass the tail parameter through the master-side bridge registry/client route
- **AND** stdout MUST print the resulting JSON payload unchanged

#### Scenario: Bridge remote-control CLI preserves bridge error payload
- **WHEN** the master-side bridge client returns a bridge failure payload with `ok=false`
- **THEN** the CLI MUST print that JSON payload unchanged
- **AND** it MUST return a failing exit code without rewriting the bridge `result` or `error` fields

#### Scenario: Bridge watch-status remains an active-snapshot reader
- **WHEN** a caller invokes `tdxquant bridge watch-status`
- **THEN** the CLI MUST return the current controller-projected active snapshot for that worker
- **AND** it MUST NOT reinterpret the command as a historical `run_id` lookup interface
