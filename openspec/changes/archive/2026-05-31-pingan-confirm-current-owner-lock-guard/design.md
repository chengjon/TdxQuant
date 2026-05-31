## Context

PingAn order submission paths already accept `require_lifecycle_owner_lock` and related owner-lock options. `confirm_current` is also side-effecting because it advances the currently visible confirmation dialog, but it currently only checks the dialog boundary and does not participate in the owner-lock guard.

The existing owner-lock helper returns a normalized risk-gate check. Reusing it keeps confirm-current aligned with buy/sell/submit-once while avoiding a new lifecycle controller in the task or CLI layers.

## Goals / Non-Goals

**Goals:**

- Add an opt-in owner-lock requirement to `TdxTradeManager.pingan.confirm_current(...)`.
- Forward guard options through stable `trade confirm-current` and `task trade-confirm-current` paths.
- Preserve current default behavior when guard options are omitted.
- Register the evidence as D-07 partial safety coverage.

**Non-Goals:**

- No owner-lock acquire/release in confirm-current.
- No supervisor, restart/backoff, process ownership, or broker readiness changes.
- No live PingAn acceptance claim and no D-07 status promotion.

## Decisions

- Reuse `_apply_pingan_lifecycle_owner_lock_required_guard(...)` for confirm-current.
  - Rationale: this is the established guard behavior for PingAn order submission paths.
  - Alternative considered: add a separate confirm-only lock helper. Rejected because it would duplicate the risk-gate shape and create a second source of owner-lock semantics.

- Evaluate the owner-lock requirement before dialog lookup/click.
  - Rationale: if the caller explicitly requires lifecycle ownership, the workflow must fail before advancing the current confirmation dialog.
  - Alternative considered: attach the guard status after execution as metadata only. Rejected because it would not protect the side-effecting action.

- Keep task and CLI layers as pass-through only.
  - Rationale: lifecycle control belongs to the PingAn manager owner-lock primitive, not to command dispatch wrappers.
  - Alternative considered: have `task trade-confirm-current` acquire a lock. Rejected because it would change ownership semantics and blur operator responsibility.

## Risks / Trade-offs

- [Risk] Confirm-current lacks order fields, so a rejected guard cannot use the generic order risk rejection payload. -> Mitigation: return a confirm-current-specific invalid request result with the same `lifecycle_owner_lock_required_status` embedded in `risk_gate`, then attach standard trade metadata.
- [Risk] Users may confuse this with full lifecycle management. -> Mitigation: FUNCTION_TREE and specs explicitly state this is an opt-in guard only and D-07 remains `[部分实现]`.
