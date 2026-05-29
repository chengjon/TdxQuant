## Context

The diagnostics view is built from an already-reduced summary view plus the detailed status payload for selected compact observations. The previous slice added `status_summary.lifecycle_readiness` in detailed and summary payloads. This change lets diagnostics consumers see the same lifecycle readiness gate under `diagnostics.lifecycle_readiness`.

## Goals / Non-Goals

**Goals:**

- Copy a compact, stable subset of `status_summary.lifecycle_readiness` into `diagnostics.lifecycle_readiness`.
- Keep CLI and HTTP diagnostics behavior aligned because both use the shared diagnostics builder.
- Preserve read-only semantics and avoid calling lifecycle APIs while building diagnostics.

**Non-Goals:**

- Do not recompute readiness from raw statefile, PID, lock, daemon state, or control payload in diagnostics.
- Do not call `restart_preflight()`, `start()`, `stop()`, `restart()`, supervisor tick/run, daemon control, probes, or signal processes.
- Do not claim provider readiness, broker readiness, trading readiness, production lifecycle health, or complete long-run governance.

## Decisions

- Use `status_summary.lifecycle_readiness` as the source of truth.
  - Rationale: the readiness rules already live in the canonical status summary; diagnostics should not duplicate or diverge from them.
  - Alternative considered: recompute diagnostics readiness from `status_payload`. Rejected because it would create two interpretations and risk extra raw-data exposure.

- Preserve only compact scalar/map fields.
  - Rationale: diagnostics should remain operator-friendly and should not expose raw statefile content, owner tokens, commands, settings, or full control payloads.

## Risks / Trade-offs

- [Risk] Diagnostics may omit lifecycle readiness if a caller builds diagnostics from an older summary payload.
  - Mitigation: omit the field when absent rather than synthesizing from raw payload; older clients keep working.
- [Risk] Operators may treat readiness as health.
  - Mitigation: preserve the boundary string and update `FUNCTION_TREE.md` to state this is not health/readiness proof for live provider or broker.
