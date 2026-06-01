## Context

`TdxTradeManager.pingan.confirm_current` resolves profile-derived inputs and builds three execution-module inputs inline:

- `PingAnConfirmCurrentRejectionContext`
- `PingAnConfirmCurrentDispatchContext`
- `PingAnConfirmCurrentExecutionRequest`

It also constructs and augments the confirm-current boundary risk gate. These are preparation responsibilities, not the UI dispatch itself.

## Design

Add `PingAnConfirmCurrentExecutionPreparation` in `tdxquant/trade/pingan_execution.py`:

- `request`
- `risk_gate`
- `profile_options`
- `rejection_context`
- `dispatch_context`

Add `TdxTradeManager._prepare_pingan_confirm_current_execution(...)` that:

1. resolves effective profile options
2. resolves lookup mode and optional timeout overrides
3. builds the base confirm boundary risk gate
4. applies broker-readiness and lifecycle owner-lock guards
5. builds rejection and dispatch contexts
6. builds the confirm-current execution request

`confirm_current` uses the prepared object, while keeping the nested desktop `run()` body in the manager because it still owns UI lookup/click adapter calls.

## Non-Goals

- No movement of confirm-current UI lookup/click/result-dialog logic into the execution module.
- No change to `execute_pingan_confirm_current` behavior.
- No change to public CLI/task/catalog arguments or registry.
- No live broker readiness or production trading readiness evidence.
