## Context

`TdxTradeManager.pingan.buy`, `buy_submit_once`, `sell`, and `sell_submit_once` each prepare the same order execution inputs before calling `execute_pingan_order`. The desktop dispatch lambda remains method-specific, but the preparation sequence is method-parameterized and can be centralized.

## Design

Add `PingAnOrderExecutionPreparation` in `tdxquant/trade/pingan_execution.py`:

- `request: PingAnExecutionRequest`
- `idempotency: dict[str, Any]`
- `risk_gate: dict[str, Any]`
- `profile_options: dict[str, Any]`
- `handlers: PingAnOrderExecutionHandlers`

Add `TdxTradeManager._prepare_pingan_order_execution(...)` that:

1. resolves the effective profile
2. evaluates submission idempotency for `broker=pingan` and the provided method
3. evaluates `max_price` risk gate
4. applies broker-readiness guard
5. applies lifecycle owner-lock guard
6. builds the request and handler bundle
7. returns the preparation object

Order callsites use `prepared.profile_options` for dispatch options and pass `prepared.request`, `prepared.idempotency`, `prepared.risk_gate`, and `prepared.handlers` to `execute_pingan_order`.

## Non-Goals

- No movement of UIA/HID desktop dispatch into the execution module.
- No change to `execute_pingan_order` behavior.
- No change to CLI/task/catalog arguments or registry.
- No new broker readiness or production trading readiness evidence.
