## Context

PingAn `dialog_readiness` now exposes passive exception popup lookup evidence. That lookup is intentionally not handling: it does not close popups, press buttons, retry, recover, or resubmit. Consumers need a stable status object that makes this boundary explicit and machine-readable.

## Goals / Non-Goals

**Goals:**

- Add `exception_popup_handling_status` to `desktop_lifecycle_gate_status`.
- Derive manual-required status from `exception_popup_lookup.detail.exception_detected`.
- Keep `exception_popup_handling` in `remaining_lifecycle_gates` until actual handling exists.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not close exception/result popups.
- Do not click confirmation controls.
- Do not retry, recover, or resubmit orders.
- Do not write order state, submission ledger, or audit artifacts from dialog readiness.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Represent handling as a top-level `desktop_lifecycle_gate_status.exception_popup_handling_status` object, not as a new health check. This avoids changing readiness pass/fail semantics.
- Use `status=manual_required` when exception-like text is detected, `status=not_triggered` when lookup reports no exception, and `status=unknown` when lookup is skipped or unavailable.
- Include false execution flags (`close_executed`, `confirm_click_executed`, `recovery_executed`, `retry_executed`, `resubmission_executed`) to prevent consumers from inferring side effects.

## Risks / Trade-offs

- [Risk] A lookup heuristic can misclassify popup text. -> The handling status references lookup status and matched keywords; it does not claim recovery.
- [Risk] Consumers could treat the status as implemented handling. -> The status explicitly reports `handling_available=false` and FUNCTION_TREE records the boundary.
