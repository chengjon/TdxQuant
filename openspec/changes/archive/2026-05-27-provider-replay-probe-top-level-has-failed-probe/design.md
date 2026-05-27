# Design: Provider Replay Probe Top-Level Has Failed Probe

## Context

E-06 remains `[部分实现]`: provider replay exposes read-only replay/status metadata, but it is not a production daemon lifecycle manager.
The top-level probe summary now has compact presence flags for requested, not-requested, healthy, and error-sample states.
Failed probe presence is still only available as a nested `outcome_summary.has_failed_probe` or by comparing `failed_count`.

## Design

Expose top-level `runtime.probe_summary.has_failed_probe` as `bool(failed_count)`.
The field must match `outcome_summary.has_failed_probe`, remain consistent with `failed_count > 0`, and must not alter `request_summary`, `health_summary`, `outcome_summary`, probe ordering, probe execution, or degraded/healthy classification.

Tests cover:

- no-probe-request status reports `false`;
- degraded requested probes report `true`;
- CLI summary view preserves the field.

## Non-Goals

- No new provider replay endpoints or probes.
- No socket start, process management, scheduler, restart/backoff, or daemon lifecycle control.
- No provider mutation or write capability.
- No readiness claim; this only reports whether existing normalized probe results include at least one failed requested probe.
