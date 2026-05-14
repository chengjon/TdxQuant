## Context

The current subscription stack has three stable layers:

- foreground `subscription-watch` run artifacts: `events.jsonl`, `status.json`, `summary.json`, `manifest.json`
- worker-local single-active background control
- worker bridge HTTP control plane for `watch-start`, `watch-stop`, `watch-status`, `watch/list`, `watch/artifacts`, `watch/events`, `watch/logs`, and `health`

The missing layer is a transport contract that lets a remote caller observe event updates without repeatedly polling. The first transport should be read-only and should project existing artifacts and controller state instead of becoming a second runtime state machine.

## Decisions

### 1. Add event-stream as a bridge read transport

The first endpoint is a read-only stream endpoint under the existing bridge namespace:

- `GET /bridge/v1/watch/events/stream`

It MUST reuse the same bearer-token and source-allowlist preconditions as the existing bridge endpoints.

### 2. Use SSE framing, but keep payload JSON machine-readable

The transport SHOULD use Server-Sent Events framing for HTTP compatibility:

```text
id: <cursor>
event: <frame_type>
data: <json object>
```

Frame `data` MUST be JSON. The bridge may internally build frames from JSONL artifact rows, but callers consume the transport as SSE frames.

### 3. Stream frames are projections, not a new event schema

The stream MUST preserve the normalized subscription event row under `data.event` for quote-update frames. Transport-only fields belong outside that row:

- `schema_version`
- `transport`
- `run_id`
- `cursor`
- `frame_type`
- `status`
- `reconnect`
- `event`

This avoids rewriting the canonical provider event-row schema while still making transport state visible.

### 4. Status and heartbeat frames carry reconnect summaries

The stream MUST be able to emit non-quote frames:

- `status`: current run state projection, including `running`, `reconnecting`, `degraded`, and terminal states.
- `heartbeat`: liveness frame emitted when no quote rows are available within the configured interval.
- `terminal`: final status projection before the stream closes when the observed run reaches a terminal state.

Reconnect fields are projected from `status.json` and controller state rather than invented by the bridge.

### 5. Resume uses stable cursors

The stream MUST support a resume cursor through `Last-Event-ID` or an explicit query parameter. The cursor maps to the last delivered canonical event sequence or a bridge-generated status/heartbeat cursor.

If the requested cursor is older than retained artifacts, the endpoint MUST return a stable transport error instead of silently replaying from an arbitrary position.

### 6. Reconnect metadata is additive

Existing event rows already include `reconnect_metadata`. This change may populate that object with additive fields for events observed after reconnect/degraded transitions, such as:

- `reconnect_count`
- `session_generation`
- `last_disconnect_at`
- `last_reconnect_at`
- `degraded_since`

Callers MUST continue to tolerate `{}` for old rows and rows without reconnect context.

## Contract Surface

### Stream query parameters

- `run_id` optional; default resolves from the active controller state.
- `from` optional cursor; alternative to `Last-Event-ID`.
- `follow` optional boolean; default `true`.
- `heartbeat_seconds` optional bounded heartbeat interval.

### Stream frame JSON

Every frame data object MUST include:

- `schema_version`
- `transport`
- `run_id`
- `cursor`
- `frame_type`
- `emitted_at`

Quote frames MUST include `event`.

Status, heartbeat, and terminal frames MUST include `status` and SHOULD include `reconnect`.

## Risks / Trade-offs

- SSE is easier for HTTP clients than raw chunked JSONL, but needs focused tests for framing, cursor resume, and heartbeat behavior.
- Bridge projection must not create a second source of truth; frames must be derived from canonical artifacts and controller state.
- Reconnect metadata is additive to avoid breaking older fixtures and existing event consumers.

## Migration Plan

1. Add a transport contract document for the bridge stream endpoint.
2. Add stream frame builders and parser-friendly tests.
3. Add route handling with existing auth and allowlist checks.
4. Add cursor/resume behavior over canonical event rows.
5. Add status/heartbeat/terminal frame projection.
6. Add representative stream fixtures and replay catalog entries.

Rollback strategy:

- Keep existing `watch/events` polling endpoint unchanged.
- Disable or remove only the stream route if transport framing causes regressions.
- Existing foreground/background subscription artifacts remain compatible.

