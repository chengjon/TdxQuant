## Context

Lifecycle readiness currently appends `lifecycle_controller`, `supervisor_loop`, and `operator_opt_in_control` to missing requirements unconditionally. After managed lifecycle status summary, those requirements can be proven from `lifecycle.control_summary` and `lifecycle.supervision_summary` without executing lifecycle control.

## Goals / Non-Goals

**Goals:**

- Count lifecycle controller, supervisor loop, and operator opt-in control as satisfied when detailed status reports `operator_opt_in_available`.
- Keep valid statefile and owned process identity as separate readiness requirements.
- Report ready only when all requirements are satisfied.

**Non-Goals:**

- No lifecycle dispatch.
- No new process inspection behavior beyond existing `--include-ownership-check` / `--inspect-process-identity`.
- No real TongDaXin provider, broker, workflow, or write readiness claim.

## Decisions

- Derive static lifecycle capability readiness from `build_provider_transport_replay_status(config)`, which is already built before readiness.
- Keep `control_allowed` tied to owned process diagnostics as well as static lifecycle capability availability.
- Preserve `boundary=read_only_lifecycle_readiness; no_control_dispatch` even when `ready=true`.

## Risks / Trade-offs

- [Risk] `ready=true` could be mistaken for a started provider. -> Mitigation: keep dispatch flags false, keep runtime probes separate, and update FUNCTION_TREE boundary language.
