## Context

The replay HTTP server writes SSE responses with `Content-Length`, so a passive probe can safely request `/provider/v1/replay/watch/events/stream?playback=immediate` and read the finite response body.

This remains separate from real subscription streaming or daemon lifecycle management. It only validates that the already-running replay service can produce SSE-like frames from fixtures.

## Goals / Non-Goals

**Goals:**

- Probe `/provider/v1/replay/watch/events/stream?playback=immediate`.
- Report normalized probe status under `runtime.watch_stream_probe`.
- Keep runtime observation opt-in and passive.
- Preserve all no-daemon-management boundaries.

**Non-Goals:**

- No long-lived stream client.
- No delayed playback validation.
- No event payload contract changes.
- No service start/stop/restart or scheduler management.

## Decisions

- Treat a `text/event-stream` HTTP 200 response with at least one `data:` frame as healthy.
  - Rationale: this proves the SSE surface is reachable without coupling the probe to every frame payload detail.
- Use the existing `--probe-timeout`.
  - Rationale: all provider replay status probes should have consistent timeout control.
- Keep `watch_stream_probe` separate from `watch_events_probe`.
  - Rationale: JSON events and SSE frames are separate surfaces and can fail independently.

## Risks / Trade-offs

- The probe reads the whole finite SSE response.
  - Mitigation: replay stream responses include `Content-Length` and immediate playback by default; the probe remains opt-in.
- Operators may treat this as production stream supervision.
  - Mitigation: `FUNCTION_TREE.md`, specs, and lifecycle status keep the no-daemon/no-restart boundary explicit.
