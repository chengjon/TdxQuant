# tdx-worker-bridge-http-control-plane Specification

## Purpose
TBD - created by archiving change subscription-watch-bridge-integration-regression. Update Purpose after archive.
## Requirements
### Requirement: Worker bridge HTTP control plane SHALL preserve transport boundaries and controller state projection
The system SHALL keep the worker bridge as a transport/control-plane shell that projects controller state, enforces auth and source allowlists, and avoids inventing bridge-only runtime states.

#### Scenario: Watch status projects controller state verbatim
- **WHEN** a caller invokes `GET /bridge/v1/watch/status`
- **THEN** the bridge MUST return the controller `status()` payload as the bridge `result`
- **AND** resilience fields such as `reconnect_count`, `degraded_since`, and `last_error` MUST survive the HTTP layer unchanged

#### Scenario: Health uses control-only read even if run status artifacts are malformed
- **WHEN** the current run `status.json` is malformed but worker-local control state is readable
- **THEN** `GET /bridge/v1/health` MUST still return bridge-online success
- **AND** the health payload MUST be derived from control-only state instead of failing on run-status parsing

#### Scenario: Active run fallback resolves from control-only state
- **WHEN** a caller requests `watch/artifacts`, `watch/events`, or `watch/logs` without an explicit `run_id`
- **THEN** the bridge MUST resolve the active `run_id` from the controller control-state view
- **AND** the fallback MUST NOT require a parseable current `status.json`

#### Scenario: Missing or invalid bearer token is rejected before controller reads
- **WHEN** a caller omits the required bearer token or provides the wrong bearer token
- **THEN** the bridge MUST return `UNAUTHORIZED`
- **AND** it MUST reject the request before invoking controller reads or watch lifecycle logic

#### Scenario: Source IP outside allowlist is rejected before controller reads
- **WHEN** a request arrives from an IP not listed in `master_allowlist`
- **THEN** the bridge MUST return `FORBIDDEN_SOURCE`
- **AND** it MUST reject the request before invoking controller reads or watch lifecycle logic

### Requirement: Master-side bridge clients SHALL normalize transport failures without rewriting worker error payloads
The system SHALL keep master-side registry/client calls transport-scoped by preserving worker JSON error payloads and normalizing malformed or unreachable success responses into stable client failures.

#### Scenario: HTTP error body JSON is preserved verbatim
- **WHEN** a worker bridge returns a non-2xx HTTP response containing a JSON bridge failure envelope
- **THEN** the master-side client MUST return that JSON payload unchanged

#### Scenario: Invalid success payload becomes a stable transport failure
- **WHEN** a worker bridge returns a 2xx response whose body is invalid UTF-8, invalid JSON, or a non-object JSON payload
- **THEN** the master-side client MUST raise a stable transport failure instead of misclassifying it as a watch task/runtime failure

#### Scenario: Connection refused becomes a stable transport failure
- **WHEN** a master-side client cannot connect to a worker bridge because the socket is refused
- **THEN** the client MUST return a stable transport-failure message that normalizes the failure as `connection refused`

