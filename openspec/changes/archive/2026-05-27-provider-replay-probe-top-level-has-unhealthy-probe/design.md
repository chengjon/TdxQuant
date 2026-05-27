# Design: Provider Replay Probe Top-Level Has Unhealthy Probe

## Context

E-06 remains `[部分实现]`: provider replay exposes read-only replay/status metadata, but it is not a production daemon lifecycle manager.
The top-level probe summary now has compact presence flags for requested, not-requested, healthy, failed, and error-sample states.
Unhealthy probe presence is still only available as nested `outcome_summary.has_unhealthy_probe` or by inspecting `unhealthy_count`/`unhealthy`.

## Design

Expose top-level `runtime.probe_summary.has_unhealthy_probe` as `bool(unhealthy)`.
The field must match `outcome_summary.has_unhealthy_probe`, remain consistent with `unhealthy_count > 0`, and must not alter `request_summary`, `health_summary`, `outcome_summary`, probe ordering, probe execution, or degraded/healthy classification.

Tests cover:

- no-probe-request status reports `false`;
- degraded unhealthy probes report `true`;
- CLI summary view preserves the field.

## Non-Goals

- No new provider replay endpoints or probes.
- No socket start, process management, scheduler, restart/backoff, or daemon lifecycle control.
- No provider mutation or write capability.
- No readiness claim; this only reports whether existing normalized probe results include at least one unhealthy probe.
