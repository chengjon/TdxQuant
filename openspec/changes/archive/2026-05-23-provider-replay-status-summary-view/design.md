## Context

Provider replay status is a read-only boundary report over a configured fixture-backed HTTP replay service. It can optionally probe health, watch-status, watch-events, and watch-stream endpoints, and it already derives `runtime.probe_summary` from those probe objects.

## Goals / Non-Goals

**Goals:**

- Expose a compact `summary_view` for `provider-replay status --view summary`.
- Preserve the detailed status payload for default callers.
- Reuse existing `runtime.probe_summary` rather than recomputing probe health.

**Non-Goals:**

- Do not start a provider replay HTTP server.
- Do not add daemon start/stop/restart lifecycle controls.
- Do not hide or replace the detailed status payload for default `--view detailed`.

## Decisions

- Add a `--view` parser option with `detailed` default and `summary` opt-in, matching the bridge watch-status view pattern.
- Store the compact projection in `Result.data["summary_view"]` while keeping `Result.data["status"]` available. This avoids breaking callers that already consume the detailed status payload.
- Include lifecycle mode, managed-lifecycle booleans, runtime observation booleans, probe summary, and boundaries in the summary.

## Risks / Trade-offs

- The summary duplicates a subset of detailed status fields. This is intentional so machine callers can use a smaller stable projection.
- The view depends on `probe_summary`; if no probes were requested it reports the existing `not_requested` rollup instead of inferring runtime health.
