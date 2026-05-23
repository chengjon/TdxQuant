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

### Requirement: Worker bridge HTTP control plane SHALL expose a read-only subscription event stream
The system SHALL expose a read-only subscription event-stream endpoint that lets remote callers observe canonical subscription-watch updates without polling `watch/events`.

#### Scenario: Event stream endpoint enforces existing bridge auth boundaries
- **WHEN** a caller requests `GET /bridge/v1/watch/events/stream`
- **THEN** the bridge MUST enforce the same bearer-token and source-allowlist preconditions as other `/bridge/v1` endpoints
- **AND** unauthorized or forbidden callers MUST be rejected before controller state or run artifacts are read

#### Scenario: Event stream resolves active run when no run_id is supplied
- **WHEN** a caller requests the stream endpoint without a `run_id`
- **THEN** the bridge MUST resolve the active run from worker-local controller state
- **AND** the bridge MUST NOT require a parseable current `status.json` solely to resolve that active run

#### Scenario: Event stream preserves polling endpoints unchanged
- **WHEN** the stream endpoint is added
- **THEN** existing `watch/status`, `watch/events`, `watch/artifacts`, `watch/logs`, and `health` endpoints MUST keep their current request and response semantics

### Requirement: Worker bridge HTTP control plane SHALL stream machine-readable SSE frames
The system SHALL deliver stream updates as Server-Sent Events frames whose data payloads are JSON objects derived from canonical subscription-watch artifacts and controller state.

#### Scenario: Quote frame wraps a canonical event row
- **WHEN** the stream emits a subscription quote update
- **THEN** the SSE frame MUST include a stable `id`
- **AND** the frame `event` type MUST identify the frame as a quote update
- **AND** the JSON `data` object MUST include `schema_version`, `transport`, `run_id`, `cursor`, `frame_type`, `emitted_at`, and `event`
- **AND** `data.event` MUST preserve the normalized subscription event row read from canonical event artifacts

#### Scenario: Status and heartbeat frames expose runtime state without inventing bridge-only state
- **WHEN** the stream emits status, heartbeat, or terminal frames
- **THEN** the JSON `data` object MUST include `status`
- **AND** the status projection MUST preserve runtime states such as `running`, `reconnecting`, and `degraded`
- **AND** reconnect fields such as `reconnect_count`, `last_disconnect_at`, `last_reconnect_at`, `next_reconnect_at`, `degraded_since`, and `last_error` MUST be projected from canonical run artifacts or controller state

#### Scenario: Terminal frame closes a followed run
- **WHEN** the observed run reaches a terminal state
- **THEN** the stream MUST emit a terminal frame with the final status projection
- **AND** the bridge MAY close the HTTP response after the terminal frame

### Requirement: Worker bridge HTTP control plane SHALL support stable stream resume cursors
The system SHALL support stable stream resume semantics so clients can reconnect without receiving duplicate quote frames.

#### Scenario: Caller resumes after a delivered event id
- **WHEN** a caller supplies `Last-Event-ID` or an explicit cursor query parameter
- **THEN** the stream MUST resume after the supplied cursor when retained artifacts still contain the requested position
- **AND** the stream MUST avoid replaying the already acknowledged quote frame

#### Scenario: Caller requests an unavailable cursor
- **WHEN** a caller supplies a cursor older than retained artifacts or otherwise unavailable
- **THEN** the bridge MUST return a stable transport error
- **AND** the bridge MUST NOT silently replay from an arbitrary newer or older position

### Requirement: Worker bridge HTTP control plane SHALL remain separate from provider transport replay service
The system SHALL keep live bridge control-plane behavior separate from fixture-backed provider transport replay behavior.

#### Scenario: Replay service mirrors only read-only transport contracts
- **WHEN** provider transport replay implements bridge-style subscription-watch HTTP or SSE shapes
- **THEN** it MUST mirror only read-only status, event, and stream response contracts
- **AND** it MUST NOT claim live bridge lifecycle control such as starting or stopping a worker run

#### Scenario: Live bridge endpoints remain backed by worker-local controller state
- **WHEN** callers use existing `/bridge/v1/*` endpoints
- **THEN** those endpoints MUST continue to derive responses from worker-local controller state and run artifacts
- **AND** they MUST NOT silently switch to provider transport replay fixtures

### Requirement: Worker bridge watch-status SHALL expose an opt-in HTTP summary view

The worker bridge HTTP control plane SHALL allow callers to request a compact
read-only summary projection from `GET /bridge/v1/watch/status` without changing
the default detailed response or lifecycle behavior.

#### Scenario: Caller omits watch-status view

- **WHEN** a caller requests `GET /bridge/v1/watch/status` without a `view` query parameter
- **THEN** the bridge MUST return the existing detailed controller status payload
- **AND** the bridge MUST continue forwarding explicit heartbeat and watermark stale thresholds

#### Scenario: Caller requests watch-status summary view

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=summary`
- **THEN** the bridge MUST call the existing controller status path once
- **AND** the bridge MUST return a compact success envelope with `result.mode=summary`
- **AND** the result MUST include the worker id, status, selected `status_summary` fields, and advisory `governance.action_summary` when present

#### Scenario: Caller requests unsupported watch-status view

- **WHEN** a caller requests `GET /bridge/v1/watch/status` with an unsupported `view` value
- **THEN** the bridge MUST reject the request as invalid before writing a success response
- **AND** the bridge MUST NOT start, stop, restart, reconnect, back off, or change event-stream behavior

