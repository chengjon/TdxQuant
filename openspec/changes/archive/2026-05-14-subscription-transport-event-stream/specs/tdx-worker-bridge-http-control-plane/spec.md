## ADDED Requirements

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

