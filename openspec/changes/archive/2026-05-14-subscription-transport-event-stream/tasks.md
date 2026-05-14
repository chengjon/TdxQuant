## 1. Transport contract and route

- [x] 1.1 Document the `GET /bridge/v1/watch/events/stream` contract, query parameters, frame types, and auth/allowlist preconditions.
- [x] 1.2 Add a worker bridge route that reuses existing bearer-token and `master_allowlist` checks.
- [x] 1.3 Keep existing `watch/events`, `watch/status`, worker registry, and auth semantics unchanged.

## 2. Stream frame projection

- [x] 2.1 Add stream frame builders for quote, status, heartbeat, and terminal frames.
- [x] 2.2 Preserve normalized subscription rows under `data.event` without rewriting the canonical event-row schema.
- [x] 2.3 Project reconnect/degraded status fields from canonical run artifacts and controller state.
- [x] 2.4 Support `Last-Event-ID` and explicit cursor resume semantics.

## 3. Reconnect metadata

- [x] 3.1 Refine additive `reconnect_metadata` fields for events observed after reconnect/degraded transitions.
- [x] 3.2 Preserve compatibility with existing rows where `reconnect_metadata` is `{}`.
- [x] 3.3 Lock reconnect metadata behavior with focused subscription event tests.

## 4. Fixtures and replay

- [x] 4.1 Add representative stream transport fixture frames for running, reconnecting, degraded, heartbeat, and terminal projections.
- [x] 4.2 Register the new transport fixtures in the provider replay fixture catalog.
- [x] 4.3 Keep existing completed subscription-watch fixtures compatible.

## 5. Verification

- [x] 5.1 Add focused bridge HTTP tests for auth, allowlist, status projection, frame formatting, and cursor resume.
- [x] 5.2 Add focused replay fixture tests for the stream transport samples.
- [x] 5.3 Run focused subscription/bridge/replay tests and `openspec validate subscription-transport-event-stream --type change --strict`.
