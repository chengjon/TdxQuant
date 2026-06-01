## Context

D-07 covers PingAn buy/sell/confirm-current desktop trading. Recent D-08 work extracted an internal execution seam for submit-once paths. That seam centralizes the common policy order:

1. evaluate idempotency and safety gates before desktop dispatch,
2. stop before desktop dispatch for duplicate/conflict/risk/lifecycle/broker-readiness rejection,
3. run the caller-provided desktop dispatch callback only after gates pass,
4. finalize the result with the manager's existing audit and artifact metadata.

The ordinary `buy` path in `tdxquant/trade/manager.py` still implements that same policy inline. This change moves only the ordinary buy path onto the existing seam.

## Goals

- Build a `PingAnExecutionRequest` with `method="buy"` and `timing_label="pingan.buy"`.
- Preserve the existing effective profile and pass it to the request so finalize metadata remains stable.
- Preserve all existing caller safety inputs: `submission_key`, `max_price`, lifecycle owner-lock parameters, and broker-readiness requirement.
- Preserve the current desktop dispatch callback and all arguments passed to `run_pingan_buy_fast`.
- Keep the public `TdxTradeManager.pingan.buy(...)` interface unchanged.

## Non-Goals

- Do not migrate `sell` or `confirm_current`; each should remain its own OpenSpec slice.
- Do not introduce new desktop primitives, workflow builders, catalog entries, task presets, or CLI parameters.
- Do not claim live broker readiness or production trading readiness.

## Compatibility

The public method signature stays unchanged. Successful, duplicate, conflict, and rejected-risk results continue to pass through `_finalize_result` with `method="buy"`, existing timing metadata, request context, idempotency data, risk gate data, and artifact handling.

## Validation

Validation focuses on the manager boundary:

- A new focused test patches `execute_pingan_order` and `run_pingan_buy_fast`, calls `manager.pingan.buy(...)`, and asserts the normalized request identity and pre-dispatch seam delegation.
- Existing PingAn manager, execution seam, and trader gateway tests continue to cover prior behavior.

