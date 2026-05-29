## Context

B-16/E-09 has been advanced through additive read-only status projections. The controller already has local statefile ownership diagnostics, restart preflight evidence, and supervisor daemon status. These signals are useful together but currently require consumers to inspect several separate objects and apply their own interpretation.

This change adds one compact readiness read model. It keeps the existing pattern of deriving summary fields from data already available during `SubscriptionWatchBackgroundController.status()`, then allow-listing the result in CLI and HTTP summary views.

## Goals / Non-Goals

**Goals:**

- Produce a stable `status_summary.lifecycle_readiness` object with `ready`, `decision`, `reason_codes`, selected input statuses, and an explicit boundary.
- Include the projection in detailed status and preserve it in CLI/HTTP summary view.
- Make the projection deterministic and testable without starting processes or requiring a live provider.

**Non-Goals:**

- Do not execute `start`, `stop`, `restart`, `supervisor_tick`, `supervisor_run`, daemon control, probes, or backoff scheduling.
- Do not prove live provider availability, broker readiness, PID ownership beyond existing local evidence, or production lifecycle health.
- Do not mark B-16/E-09 as `[已实现]`.

## Decisions

- Derive readiness inside `build_subscription_watch_status_summary()`.
  - Rationale: this keeps the field part of the canonical status summary and lets CLI/HTTP views copy it like other summary projections.
  - Alternative considered: build readiness in CLI/HTTP only. Rejected because it would duplicate interpretation and leave direct status without the field.

- Use conservative readiness rules.
  - `ready=true` only when restart preflight is ready, statefile ownership is owned/active with matching PID evidence, and no supervisor daemon state indicates blocked control.
  - Missing or non-ready evidence yields `ready=false` with reason codes rather than optimistic defaults.
  - Rationale: this avoids overstating lifecycle readiness from partial data.

- Include only compact inputs and reason codes.
  - Rationale: summary view should not expose raw statefile content, owner tokens, commands, settings, full control payloads, or full arrays.

## Risks / Trade-offs

- [Risk] The conservative gate may report blocked in cases where an operator could still manually recover the system.
  - Mitigation: expose reason codes and input statuses so the operator can see which evidence is missing.
- [Risk] Readiness could be confused with actual health.
  - Mitigation: include a boundary string and update `FUNCTION_TREE.md` to state that this is not provider readiness, broker readiness, or lifecycle control.
- [Risk] More summary fields can expand the already large B-16/E-09 registry entry.
  - Mitigation: add one concise supplemental registration line and keep the node status `[部分实现]`.
