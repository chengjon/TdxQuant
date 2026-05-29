## Context

The project already has an opt-in diagnostics view derived from summary rollups and detailed status. The latest slices added lifecycle readiness to both summary and diagnostics. A runbook view should not introduce a new source of truth; it should package the existing diagnostics signals into an operator-facing checklist.

## Goals / Non-Goals

**Goals:**

- Add `bridge watch-status --view runbook` and HTTP `watch/status?view=runbook`.
- Build a `runbook` object from the same reduced diagnostics payload that already avoids raw control/watch payloads.
- Provide deterministic fields for automation: `schema_version`, `decision`, `check_count`, `blocking_check_count`, `manual_review_required`, `checks`, and `boundary`.

**Non-Goals:**

- Do not execute `start`, `stop`, `restart`, `restart_preflight`, supervisor tick/run, daemon control, probes, signals, or backoff scheduling.
- Do not prove live provider availability, broker readiness, trading readiness, production lifecycle health, or complete long-run governance.
- Do not create a workflow builder, catalog entry, task/report execution path, or daemon policy.

## Decisions

- Build runbook from diagnostics view.
  - Rationale: diagnostics already combines summary, lifecycle readiness, restartability, backoff, ownership, and supervisor status without raw payload exposure.
  - Alternative considered: build runbook directly from detailed status. Rejected because it could duplicate diagnostics logic and increase raw-data exposure risk.

- Keep checklist items compact and deterministic.
  - Rationale: consumers should be able to assert the presence of known check codes and counts without parsing prose.

- Use conservative status mapping.
  - Any blocked lifecycle readiness, manual review requirement, mismatch, stale component, or active restart backoff produces a non-ready runbook decision.

## Risks / Trade-offs

- [Risk] The runbook can look like an operational authority instead of a report.
  - Mitigation: include an explicit read-only boundary and document in `FUNCTION_TREE.md` that it does not execute actions or prove health.
- [Risk] More view modes can confuse users.
  - Mitigation: `runbook` is opt-in and reuses the same watch-status endpoint/command rather than creating a separate control command.
