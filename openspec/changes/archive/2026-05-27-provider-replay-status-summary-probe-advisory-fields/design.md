# provider replay status summary probe advisory fields design

## Context

The detailed provider replay status payload contains the full `runtime.probe_summary`, and the summary view already copies that object. However, `summary_view.status_summary` is the stable first-screen object for a compact CLI/API response, and it currently exposes only requested/failed probe counts.

## Design

In `_build_provider_replay_status_summary_view()`, read `probe_summary.advisory_summary` when present. Add these fields to `status_summary`:

- `probe_status`: advisory `status`, falling back to `probe_summary.status`.
- `probe_request_coverage_status`: advisory `request_coverage_status`, falling back to `probe_summary.request_coverage_status`.
- `has_problem_probe`: advisory `has_problem_probe`, falling back to `probe_summary.has_problem_probe`.
- `primary_problem_probe`: advisory `primary_problem_probe`, falling back to `probe_summary.primary_problem_probe`.

The projection does not call any probe function. It only reads the already-built status payload. The copied `probe_summary` remains available for detailed inspection.

## Boundaries

- This change is read-only summary projection.
- It does not execute extra probes or make unrequested endpoints observable.
- It does not start, stop, restart, daemonize, schedule, supervise, or back off provider replay.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.
- It does not expose full probe payloads, endpoint response bodies, tokens, allowlist members, or fixture paths.

