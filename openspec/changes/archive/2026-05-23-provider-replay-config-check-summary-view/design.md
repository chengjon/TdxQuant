## Context

The provider replay CLI already exposes three foreground-oriented actions:
`serve`, `config-check`, and `status`. The existing `status --view summary`
path summarizes lifecycle and probe state while explicitly stating that daemon
start/stop management is unsupported. `config-check` is even narrower: it only
loads and summarizes configuration, but it does not currently have an explicit
summary view that documents those runtime boundaries.

## Goals / Non-Goals

- Provide a compact machine-readable summary for `provider-replay config-check --view summary`.
- Preserve the existing detailed config payload and default output shape.
- Make the summary boundary explicit: no socket opened, no probes requested, no daemon lifecycle management.
- Do not introduce daemon start/stop, restart/backoff, process supervision, or runtime observation.
- Do not expose bearer token values in any output.

## Decisions

- Add `--view detailed|summary` to `config-check`, defaulting to `detailed`.
  - Rationale: this mirrors the existing `status --view` contract and keeps older callers unchanged.
  - Alternative considered: always add the summary view. That would change all config-check payloads, so it is avoided.
- Attach `summary_view` beside the existing `config` data only when summary is requested.
  - Rationale: this keeps detailed machine output intact while giving registry/catalog users a stable compact surface.
  - Alternative considered: replace the payload with only summary data. That would remove detailed config fields from summary callers.
- Keep the summary derived from the loaded config and fixed command semantics.
  - Rationale: `config-check` intentionally does not run probes or inspect a live process.

## Risks / Trade-offs

- Summary consumers may mistake config validity for a running service. Mitigation: include explicit `serve_started: false`, `probe_requested: false`, and boundary strings.
- The CLI parser is a broad fan-out entry point. Mitigation: keep the change additive and cover parser plus dispatch behavior with focused tests.

## Migration Plan

No migration is required. Existing `provider-replay config-check --config <path>` callers continue to receive the existing detailed config payload.

## Open Questions

None.
