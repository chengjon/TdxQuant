# Design: Provider Replay Probe Has Problem Probe

## Context

E-06 remains `[部分实现]`: provider replay exposes read-only replay/status metadata, but it is not a production daemon lifecycle manager.
The top-level probe summary already exposes `primary_problem_probe` plus explicit failed/unhealthy/error-sample presence flags.
A direct `has_problem_probe` flag makes the primary problem hint easier to consume without reinterpreting nullability.

## Design

Expose top-level `runtime.probe_summary.has_problem_probe` as `bool(primary_problem_probe)`.
The field must remain consistent with `primary_problem_probe is not None` and must not alter `request_summary`, `health_summary`, `outcome_summary`, probe ordering, probe execution, sample selection, or degraded/healthy classification.

Tests cover:

- no-probe-request status reports `false`;
- degraded requested probes report `true`;
- all requested mixed probe results report `true`;
- CLI summary view preserves the field.

## Non-Goals

- No new provider replay endpoints or probes.
- No socket start, process management, scheduler, restart/backoff, or daemon lifecycle control.
- No provider mutation or write capability.
- No readiness claim; this only reports whether existing normalized metadata selected a primary problem probe.
