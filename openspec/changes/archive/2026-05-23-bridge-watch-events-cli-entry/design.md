## Context

The bridge control plane already has worker-local HTTP endpoints for watch events and watch event streams. `bridge_registry.py` can call those routes from a master registry, but the `bridge` CLI exposes only control/status-style commands. Adding CLI entries closes the operator-facing read-only inspection gap without changing event contracts.

## Goals / Non-Goals

**Goals:**
- Expose watch event JSON through `bridge watch-events`.
- Expose watch event SSE text through `bridge watch-events-stream`.
- Forward existing route parameters (`run_id`, `tail`, `from`, `follow`, `heartbeat_seconds`) without changing defaults.
- Keep JSON and raw SSE output behavior distinct.

**Non-Goals:**
- No live multi-worker scheduler.
- No event schema change.
- No worker registry schema change.
- No start/stop lifecycle changes.

## Decisions

1. Print SSE stream output as raw text.
   - Rationale: The registry helper returns text/event-stream frames, and wrapping them in JSON would change the caller-facing stream shape.
   - Alternative considered: emit JSON with a `text` field. That would make the CLI less useful for tools expecting SSE framing.

2. Keep the commands under the existing `bridge` namespace.
   - Rationale: These are master-to-worker bridge operations using the same registry and worker selection arguments.
   - Alternative considered: add provider-replay commands. That would mix live bridge worker inspection with fixture replay service concerns.

## Risks / Trade-offs

- [Risk] Users may treat a finite raw SSE snapshot as a managed long-running stream. -> Boundary text states the CLI proxies the existing read-only route and does not add scheduling.
- [Risk] Raw text output differs from `_emit_bridge_payload`. -> Tests cover stdout behavior for the stream command.
