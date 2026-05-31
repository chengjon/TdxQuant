## Context

`submit_ready` is a split-step PingAn workflow that fills/submits the order entry path up to the manual confirmation boundary. It is not a final confirmation, but it still has desktop side effects and should respect the same opt-in lifecycle owner-lock requirement as the other side-effecting PingAn paths.

The existing owner-lock requirement helper already produces the normalized risk-gate status used by buy/sell/submit_once/confirm_current. Reusing it keeps this slice small and consistent.

## Goals / Non-Goals

**Goals:**

- Add an opt-in owner-lock requirement to `TdxTradeManager.pingan.submit_ready(...)`.
- Forward guard options through stable `trade submit-ready` and `task trade-submit-ready` paths.
- Preserve current default behavior when guard options are omitted.
- Register the evidence as D-07 partial safety coverage.

**Non-Goals:**

- No owner-lock acquire/release in submit-ready.
- No supervisor, restart/backoff, process ownership, or broker readiness changes.
- No live PingAn acceptance claim and no D-07 status promotion.

## Decisions

- Reuse `_apply_pingan_lifecycle_owner_lock_required_guard(...)` for submit-ready.
  - Rationale: the same local owner-lock requirement semantics should apply across PingAn desktop side-effecting paths.
  - Alternative considered: add a submit-ready-specific guard shape. Rejected because it would duplicate owner-lock status semantics.

- Evaluate the owner-lock requirement before `run_pingan_hid_submit_probe(...)`.
  - Rationale: if the caller explicitly requires lifecycle ownership, the workflow must fail before any HID submit probe can advance the desktop state.
  - Alternative considered: attach owner-lock status after the probe. Rejected because it would not guard the side effect.

- Keep task and CLI layers as pass-through only.
  - Rationale: lifecycle control belongs to the PingAn manager owner-lock primitive, not to command dispatch wrappers.
  - Alternative considered: have task submit-ready acquire a lock. Rejected because it would change ownership semantics and blur operator responsibility.

## Risks / Trade-offs

- [Risk] Users may confuse submit-ready guard coverage with full order lifecycle readiness. -> Mitigation: FUNCTION_TREE and specs explicitly state this is opt-in pre-probe guard evidence only and D-07 remains `[部分实现]`.
- [Risk] The rejected result has no order audit artifact because no desktop action occurs. -> Mitigation: attach standard trade metadata and trade safety metadata with `side_effect_level=none`.
