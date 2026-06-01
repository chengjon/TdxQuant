## Context

B-16 is currently marked implemented for explicit operator-managed subscription watch lifecycle control and diagnostics. The previous lifecycle hardening slice introduced `tdxquant.managed_lifecycle` for PID liveness, process ownership, provenance, and restart/backoff projection. Two lifecycle-adjacent lock paths still own their `fcntl.flock` details locally:

- provider replay lifecycle statefile writes use a sibling `.lock` file.
- subscription watch background control and supervisor code uses control/supervisor lock files.

This slice deepens the shared lifecycle module by moving local file lock primitives behind a small reusable interface, while preserving adapter behavior.

## Goals / Non-Goals

**Goals:**
- Provide a small shared primitive for local non-blocking file lock acquire/release.
- Return stable lock diagnostics for acquired, blocked, and released outcomes.
- Keep existing provider replay statefile and subscription watch control/supervisor behavior compatible.
- Cover the primitive and adapter use with focused tests.
- Update `FUNCTION_TREE.md` with evidence and boundaries.

**Non-Goals:**
- No distributed lock implementation.
- No cross-platform guarantee beyond the existing local `fcntl` advisory lock behavior.
- No change to daemon lifecycle public commands or HTTP routes.
- No automatic production recovery claim.
- No PingAn trade provider lifecycle or D-07/D-08 migration.

## Decisions

- Use the existing `tdxquant.managed_lifecycle` module instead of a new package. This keeps lifecycle primitives in one place and avoids another competing abstraction.
- Model lock acquisition as a small dataclass containing the path, handle, acquired flag, reason code, and diagnostics. This lets adapters preserve handle-based behavior while tests can assert stable diagnostics.
- Keep non-blocking local lock strategies as the only supported mode for this slice. Provider replay retains its exclusive lockfile sentinel, subscription watch retains its advisory `flock` control files, and both share diagnostics/provenance. Adding blocking/timeouts would broaden behavior unnecessarily.
- Let provider replay and subscription watch keep their existing public output shapes. The shared primitive is an internal consolidation unless an existing response already exposes lock status.

## Risks / Trade-offs

- Local file locks are process coordination, not distributed consensus. Mitigation: document this as local lifecycle state/control file protection only.
- Refactoring lock handling can accidentally change lock release behavior. Mitigation: preserve adapter tests for held-lock and release paths.
- Adding diagnostics could tempt overclaiming readiness. Mitigation: keep `FUNCTION_TREE.md` boundary explicit that shared locks do not prove provider availability, broker readiness, trade readiness, or automatic recovery.
