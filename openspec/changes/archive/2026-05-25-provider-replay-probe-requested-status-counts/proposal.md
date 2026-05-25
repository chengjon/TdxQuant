## Why

E-06 fake provider status already exposes `probe_summary.status_counts`, but that map includes unrequested probes. Maintainers who run a narrow probe need a compact way to see the status distribution of only the probes that were actually requested.

Adding `requested_status_counts` separates requested probe outcomes from skipped probe targets without changing probe execution or daemon lifecycle behavior.

## What Changes

- Add additive `runtime.probe_summary.requested_status_counts` to provider replay status.
- Derive the counts only from normalized probe objects whose status is not `not_requested`.
- Preserve existing probe execution, status, error, target-list, and lifecycle behavior.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary.

## Non-Goals

- No new probe endpoints.
- No automatic socket startup, daemon supervision, restart, scheduler, or live provider behavior.
- No replacement of existing `status_counts`, target lists, or compact error samples.

