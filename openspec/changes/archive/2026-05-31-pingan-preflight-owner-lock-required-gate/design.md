## Context

The prior preflight owner-lock status gate reports local statefile status under `promotion_gate_status.lifecycle_owner_lock_status`. The next useful step is to let callers make that read-only status a blocking preflight requirement without performing lifecycle control.

## Goals / Non-Goals

**Goals:**

- Add an opt-in preflight requirement that passes only when status is `owned`, the current owner token matches the requested owner token, and the lock is not stale.
- Surface stable fields describing whether the requirement was evaluated and why it passed or failed.
- Keep the default preflight path backward compatible when the flag is omitted.

**Non-Goals:**

- No owner lock acquire/release from preflight.
- No real PingAn process ownership claim.
- No start/stop/restart/kill/supervise/backoff.
- No order execution or D-07/D-08 status promotion.

## Decisions

- Implement the requirement inside the existing `lifecycle_owner_lock_status` summary so callers can inspect one object for both observed status and gate result.
- Make missing lifecycle inputs a blocking condition only when `require_lifecycle_owner_lock=true`; otherwise they remain `not_configured` informational status.
- Mark preflight result as failed-style when the requirement fails, using `ErrorCode.INVALID_REQUEST` only if no earlier check already produced a more specific failure code.

## Risks / Trade-offs

- Required owner lock can block preflight based on local state that is not real broker readiness. Mitigation: fields and boundaries explicitly state this is local statefile evidence only.
- Existing callers might discover new keys in the summary. Mitigation: defaults are non-blocking, and added keys are additive.
