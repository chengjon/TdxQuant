# Design

## Behavior

Submit-once will reuse the existing PingAn broker readiness guard helper used by the buy/sell and confirm-current safety paths:

- `require_broker_readiness=false`: preserve existing submit-once behavior.
- `require_broker_readiness=true` and broker health OK: keep the risk gate passed and continue to submit-once desktop execution.
- `require_broker_readiness=true` and broker health failed: mark the risk gate failed, return a trade risk rejection result, and do not call the submit-once desktop automation path.

The rejection is a pre-desktop-dispatch safety gate. It uses the existing trade risk rejection/finalization path so metadata stays consistent with other risk-gate rejections.

## Entry Points

Task entrypoint `TdxTaskManager.trade_submit_once(...)` will add the optional argument and forward it to the side-specific PingAn manager method. The task layer must not evaluate broker health.

CLI entrypoints will expose:

- `trade submit-once --require-broker-readiness`
- `task trade-submit-once --require-broker-readiness`

Direct `trade submit-once` routes through `PingAnDesktopTraderGateway(execution_mode="submit_once")`, so the gateway must carry the option to `buy_submit_once` or `sell_submit_once` without changing default behavior.

## Evidence And Boundary

`FUNCTION_TREE.md` D-08 remains `[部分实现]`. The row will cite the OpenSpec change, CLI/task options, manager methods, and tests. The boundary will explicitly state that this is only an opt-in broker runtime health guard for submit-once desktop dispatch, not lifecycle control, restart/backoff, retry/recovery/resubmission, process ownership, live/manual acceptance, or production trading readiness.
