## Context

TdxQuant already ships a stable provider-facing contract surface for synchronous JSON results, capability discovery, block mutation governance, subscription event rows, and `subscription-watch` run artifacts. It also now ships a curated replay fixture bundle plus loader helpers. What is missing is an execution mode that makes those fixtures behave like a provider instead of just static sample files.

The main architectural constraint is that the current Python and CLI entrypoints are already the public integration surface. Adding a second, replay-only API surface would fragment contract tests and make upstream integrations validate a different path than production callers use. The design therefore needs to let the current manager and CLI entrypoints switch execution source while preserving their existing output contracts.

The second constraint is safety. Replay mode must never silently fall through to live Windows runtime access. Upstream tests need deterministic offline behavior, and a mistaken replay invocation cannot be allowed to mutate a real TongDaXin environment.

## Goals / Non-Goals

**Goals:**
- Add a manager-level provider mode switch so supported capabilities can run in `live` or `replay` mode through the same public entrypoints.
- Support built-in fixture names, explicit fixture file paths, and default fixture selection by capability.
- Materialize `subscription-watch` replay runs as completed run artifact bundles using the existing artifact contract.
- Keep current provider result envelopes, manager metadata, CLI exit semantics, and task result contracts stable.
- Enforce strict no-live-fallback behavior when replay mode is enabled.

**Non-Goals:**
- No HTTP, SSE, or external transport server.
- No replay support for every query capability in the repository; this package covers the selected high-value integration contracts only.
- No simulation of long-lived runtime subscription sessions, heartbeats, or delayed event playback.
- No daemon/process-control plane for `subscription-watch`.

## Decisions

### 1. Use manager-level provider mode instead of replay-only entrypoints

The replay switch will live at `TdxApiManager` construction time and be forwarded through current CLI entrypoints. This keeps contract tests and upstream integrations on the same public surface as live mode. The alternative, a separate `replay ...` CLI tree or a replay-only Python facade, would reduce immediate implementation complexity but would validate the wrong code path.

This decision also keeps domain APIs simple: they do not need to become independently aware of profile loading, fixture lookup, or CLI parsing. The manager layer can decide whether a capability call dispatches to live domain code or to replay-provider helpers.

### 2. Introduce a dedicated replay-provider helper layer

Replay-mode logic will be centralized in a new helper module rather than spread across bridge functions. That helper layer will own:
- capability-to-default-fixture mapping
- built-in fixture lookup
- custom fixture path loading and validation
- replay result normalization for synchronous JSON capabilities
- `subscription-watch` run artifact materialization

This keeps live bridge code free of replay branches and reduces the chance of accidental live runtime access when replay mode is active.

### 3. Support both default fixture selection and explicit overrides

Replay mode will support three fixture selection paths:
- automatic default built-in fixture by capability
- explicit built-in fixture name
- explicit JSON/JSONL fixture path

Python will additionally support a capability-keyed replay fixture map so one manager instance can answer multiple capabilities from different fixtures in a single test run. The alternative, forcing every call site to pass an explicit fixture every time, would make test setup noisy and would underuse the curated fixture bundle already in the repo.

### 4. Treat `subscription-watch` replay as artifact materialization, not simulated runtime

Replay mode for `task subscription-watch` will not emulate a live callback loop. Instead it will immediately write a completed `run_id` directory containing canonical `events.jsonl`, `status.json`, `summary.json`, and `manifest.json`, using either the built-in fixture bundle or a caller-supplied manifest/directory source.

This is the right abstraction for current needs because the task contract is file-oriented. Simulating delays, polling loops, or Ctrl+C behavior would add complexity without improving offline contract validation.

### 5. Enforce explicit no-live-fallback behavior

When replay mode is enabled:
- unsupported capabilities must fail deterministically
- missing fixture mappings must fail deterministically
- invalid fixture payloads must fail deterministically
- no replay path may call live Windows bridge/runtime code

The alternative, silent fallback to live mode, would make offline tests nondeterministic and unsafe.

## Risks / Trade-offs

- **[Partial coverage only]** → Mitigation: scope the first package to the most integration-critical capabilities and make unsupported replay explicit instead of pretending full coverage exists.
- **[Manager layer becomes a dispatch hub]** → Mitigation: keep replay resolution in a dedicated helper module and only let the manager choose between live and replay execution.
- **[Custom fixture path variability can weaken contracts]** → Mitigation: validate custom fixture payload shape against the same capability expectations used by built-in fixtures and fail early on malformed input.
- **[Subscription-watch replay artifacts may diverge from live artifacts over time]** → Mitigation: reuse the same run-artifact builders already used by the live task path and cover replay materialization with dedicated tests.

## Migration Plan

1. Add replay-provider helper module and default fixture mapping.
2. Extend `TdxApiManager` construction/configuration to carry replay mode and fixture selectors.
3. Route supported synchronous capabilities through replay helpers when replay mode is active.
4. Extend CLI entrypoints with replay flags and preserve existing live defaults.
5. Add `subscription-watch` replay materialization through the existing task contract.
6. Add fixture, manager, CLI, and task coverage proving no-live-fallback behavior.

Rollback is straightforward because replay mode is additive and live mode remains the default. If needed, the new provider-mode flags and manager options can be removed without altering live bridge semantics.

## Open Questions

- None for this package. HTTP/SSE transport replay, daemonized watch control, and live subscription session replay are intentionally deferred to later changes.
