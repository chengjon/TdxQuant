## Context

TdxQuant already has two separate pieces:

- `tdxquant.replay_provider` can resolve built-in or caller-supplied replay fixtures and return provider-contract-compatible results without live runtime access.
- `tdxquant.bridge_http` exposes worker-local subscription-watch status, events, and SSE stream frames over a small HTTP control plane.

The missing layer is an offline transport surface that lets upstream integrations test HTTP and SSE parsing against replay assets without starting a real TongDaXin runtime, a live bridge controller, or a subprocess-based CLI replay path.

## Goals / Non-Goals

**Goals:**

- Add a minimal HTTP replay service backed only by replay fixtures.
- Mirror the bridge-style subscription-watch read paths that transport clients need: health, fixture catalog, synchronous replay result, watch status, watch events, and watch SSE stream.
- Support deterministic delayed playback metadata for event streams while keeping immediate playback as the default.
- Preserve strict no-live-fallback replay behavior.

**Non-Goals:**

- No new business provider capability.
- No replacement for `bridge_http` live worker control.
- No change to existing CLI subprocess replay flags or semantics.
- No real timing loop is required for the first slice; delayed playback is represented by deterministic frame metadata and ordering.

## Decisions

1. Add an independent `tdxquant.provider_transport_replay` module.
   - Rationale: replay transport should not become another runtime source of truth inside the live bridge controller.
   - The module can still reuse stable helpers from `replay_provider`, `replay_fixtures`, and `bridge_http` frame shapes.

2. Use `http.server.ThreadingHTTPServer`, matching `bridge_http`.
   - Rationale: avoids adding FastAPI/aiohttp dependencies and keeps tests using the same standard-library client pattern already used by bridge HTTP tests.

3. Keep the fake provider read-only.
   - Rationale: replay fixtures are contract and regression assets; they must not be mistaken for a live mutable provider.
   - Start/stop/mutation endpoints remain out of scope.

4. Model delayed playback as fixture-backed frame annotations.
   - Rationale: deterministic tests can assert frame order, cursors, and planned delay without sleeping or creating a long-running scheduler.
   - Each SSE frame can carry `playback` metadata such as `mode`, `delay_ms`, and `planned_emit_after_ms`.

## Risks / Trade-offs

- A replay HTTP service could be mistaken for live availability. Mitigation: every envelope and frame carries `provider_mode: replay`, and `FUNCTION_TREE.md` keeps replay as a boundary asset rather than live capability evidence.
- Sharing code with the live bridge can blur responsibilities. Mitigation: only share inert frame encoding/projection helpers or duplicate small local projection code; do not call the live background controller.
- Delayed playback without real wall-clock delays is less realistic. Mitigation: first slice targets transport regression determinism; real scheduled playback can be added later if needed.

## Migration

No migration is required. Existing replay provider, CLI replay, bridge HTTP, and fixtures remain compatible. The new service is additive and opt-in.

## Open Questions

- Whether later slices should add an executable CLI wrapper for the HTTP replay service.
- Whether real-time delayed playback should be added after deterministic delayed playback metadata proves useful.
