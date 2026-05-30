## Context

D-07/D-08 promotion gates are ordered. The previous provider/safety gate status covers ownership and pre-trade safeguards, while desktop lifecycle still needs evidence for dialog readiness, result popup handling, exception popup boundaries, timeout/retry behavior, and process/window ownership. The code already has `dialog_readiness`, including confirm dialog lookup, result dialog lookup, and result confirm-button lookup.

## Goals / Non-Goals

**Goals:**

- Add a normalized desktop lifecycle gate status to `dialog_readiness`.
- Keep the status read-only and non-writing.
- Make covered and remaining lifecycle areas mechanically inspectable.

**Non-Goals:**

- Do not implement new order submission, confirmation, result-popup closing, exception-popup handling, or retry orchestration.
- Do not claim D-07/D-08 `[已实现]`.
- Do not add live/manual acceptance evidence.

## Decisions

- Attach the status to `dialog_readiness`, because that method already owns passive confirm/result dialog probes and timeout inputs.
- Keep `desktop_lifecycle_gate_status.status` as `partial` even when requested visible dialogs are found. This prevents a single readonly probe from implying full lifecycle coverage.
- Represent missing areas in `remaining_lifecycle_gates` rather than hiding them in prose. This keeps FUNCTION_TREE evidence and tests aligned.

## Risks / Trade-offs

- [Risk] The gate status could be mistaken for full lifecycle readiness. -> Include `execution_mode=readonly_dialog_readiness`, `side_effect_level=none`, and remaining lifecycle gates.
- [Risk] Process/window ownership is only declared by inputs here. -> Mark it as `declared` and keep real process/window lifecycle ownership as a remaining gate.
- [Risk] Existing dialog checks can return degraded/passive results. -> Preserve existing `overall_status` behavior and derive lifecycle status from the same checks.
