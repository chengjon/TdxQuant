## Context

D-07 ordinary buy now uses the same internal PingAn execution seam as D-08 submit-once paths. Ordinary sell still duplicates the same policy inline:

1. evaluate idempotency before dispatch,
2. evaluate risk, lifecycle owner-lock, and broker-readiness gates,
3. stop before desktop dispatch for duplicate/conflict/rejected-gate outcomes,
4. dispatch through `run_pingan_sell_fast` only after gates pass,
5. finalize result metadata through `_finalize_result`.

This change moves only ordinary sell onto the existing seam.

## Goals

- Build a `PingAnExecutionRequest` with `method="sell"` and `timing_label="pingan.sell"`.
- Preserve effective profile metadata and pass it through the request.
- Preserve caller safety inputs: `submission_key`, `max_price`, lifecycle owner-lock parameters, and broker-readiness requirement.
- Preserve the current `run_pingan_sell_fast` desktop dispatch callback and all arguments passed to it.
- Keep the public `TdxTradeManager.pingan.sell(...)` interface unchanged.

## Non-Goals

- Do not migrate `confirm_current`; it remains a separate D-07 slice.
- Do not introduce new desktop primitives, workflow builders, catalog entries, task presets, or CLI parameters.
- Do not claim live broker readiness or production trading readiness.

## Compatibility

The public method signature stays unchanged. Successful, duplicate, conflict, and rejected-risk results continue to pass through `_finalize_result` with `method="sell"`, timing metadata, request context, idempotency data, risk gate data, and artifact handling.

## Validation

Validation focuses on the manager boundary:

- A new focused test patches `execute_pingan_order` and `run_pingan_sell_fast`, calls `manager.pingan.sell(...)`, and asserts the normalized request identity and pre-dispatch seam delegation.
- Existing PingAn manager, execution seam, and trader gateway tests continue to cover prior behavior.

