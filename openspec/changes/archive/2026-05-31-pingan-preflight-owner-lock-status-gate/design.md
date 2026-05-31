## Context

`TdxTradeManager.pingan.lifecycle_owner_lock(...)` already supports explicit `status/acquire/release` operations for a caller-provided local statefile and token. `trade preflight` currently reports provider/broker ownership and safety gate evidence, but not the local owner lock state that later lifecycle work depends on.

## Goals / Non-Goals

**Goals:**

- Allow preflight callers to opt into a read-only lifecycle owner lock status check.
- Return stable summary fields for configuration, lock state, staleness, statefile/lock presence, owner token match, PID diagnostics, and side-effect flags.
- Preserve preflight's non-side-effecting contract.
- Keep D-07/D-08 partial in `FUNCTION_TREE.md`.

**Non-Goals:**

- No acquire/release behavior from `trade preflight`.
- No start/stop/restart/kill/supervise/backoff.
- No order submission, catalog workflow execution, broker readiness claim, or live/manual acceptance claim.
- No promotion of D-07/D-08 to `[已实现]`.

## Decisions

- Reuse the existing PingAn lifecycle owner lock status logic instead of adding a second parser for the statefile format. This keeps PID diagnostics and stale detection consistent with the explicit owner-lock CLI.
- Make the preflight owner lock inputs optional. When omitted, the summary is `configured=false` and `status=not_configured`; existing preflight callers keep working.
- Place the summary under `promotion_gate_status.lifecycle_owner_lock_status`. It is promotion evidence, but it remains bounded as local lifecycle statefile evidence, not a completed desktop lifecycle gate.

## Risks / Trade-offs

- A preflight result with `status=owned` could be misread as real desktop process ownership. Mitigation: include `pid_ownership_claimed=false`, `side_effect_level=none`, and a boundary string in the summary, specs, and FUNCTION_TREE.
- Optional inputs can be partially provided. Mitigation: report `configured=false` unless both statefile path and owner token are present; do not fail the whole trade preflight for absent optional lifecycle inputs.
