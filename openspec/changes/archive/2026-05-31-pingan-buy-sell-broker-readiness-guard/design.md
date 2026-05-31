# Design

## Behavior

The buy/sell manager methods will reuse the existing PingAn broker readiness helper that returns a normalized `broker_readiness_required_status`. The guard remains opt-in:

- `require_broker_readiness=false`: preserve current buy/sell behavior.
- `require_broker_readiness=true` and broker health OK: keep the risk gate passed and continue to desktop execution.
- `require_broker_readiness=true` and broker health failed: mark the risk gate failed, return a trade risk rejection result, and do not call desktop buy/sell automation.

The rejection is a pre-desktop-dispatch safety gate. It may still pass through the existing risk rejection finalization path so metadata remains consistent with other risk-gate rejections.

## Entry Points

Task entrypoints will add the optional argument and forward it to `TdxTradeManager.pingan.buy/sell(...)`; the task layer does not evaluate broker health itself.

CLI entrypoints will expose:

- `trade buy --require-broker-readiness`
- `trade sell --require-broker-readiness`
- `task trade-buy --require-broker-readiness`
- `task trade-sell --require-broker-readiness`

If direct `trade buy/sell` routes through the gateway layer, the gateway must carry the option to the PingAn manager without changing default behavior.

## Evidence And Boundary

`FUNCTION_TREE.md` D-07 remains `[部分实现]`. The row will cite the OpenSpec change and tests, and its boundary will explicitly state that this is only an opt-in broker runtime health guard for buy/sell desktop dispatch. It does not implement long-running lifecycle management, restart/backoff, retry/recovery, order resubmission, live acceptance, or production readiness.
