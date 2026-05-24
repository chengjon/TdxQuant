# Change: Provider Replay Probe Error Summary

## Why

`provider-replay status` already rolls probe status into counts and target lists. When one or more probe targets are unhealthy, operators still need a compact failure-class rollup without inspecting each raw probe object or treating the fake provider as lifecycle-managed.

## What Changes

- Add `runtime.probe_summary.error_code_counts`, derived from requested probe objects that include an `error_code`.
- Preserve the existing `summary_view.probe_summary` projection by carrying the additive count map through unchanged.
- Keep the result read-only and observational: no socket start, daemon lifecycle, reconnect, restart, or scheduler behavior changes.

## Out of Scope

- No new probe endpoints or network behavior.
- No daemon start/stop or process management.
- No exposure of secret tokens, allowlist members, or full fixture path provenance.
