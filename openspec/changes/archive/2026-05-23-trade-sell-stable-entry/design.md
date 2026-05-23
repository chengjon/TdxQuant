## Context

`TdxTradeManager.pingan.sell` and `PingAnDesktopTraderGateway.place_order(side=sell)` already exist. The stable nested CLI layer has `trade buy`, `trade submit-once`, and confirm/readiness commands, while task management has `trade_buy` and `trade_submit_once` but no first-class `trade_sell`.

## Goals / Non-Goals

**Goals:**

- Make Ping An sell discoverable through stable `trade sell` and `task trade-sell` entrypoints.
- Reuse existing sell manager behavior and trade service/store contracts.
- Preserve `submission_key`, `max_price`, refresh controls, and artifact propagation.

**Non-Goals:**

- No new broker adapter or sell execution engine.
- No new exception-dialog coverage.
- No change to buy, submit-once, or confirm-current behavior.

## Decisions

- Implement `trade sell` by mirroring `trade buy` with `OrderSide.SELL`.
  - Rationale: the trade service already owns stable order request creation and result compatibility.
  - Alternative considered: call `TdxTradeManager.pingan.sell` directly from CLI. That would diverge from the current stable `trade buy` command path.
- Implement `TdxTaskManager.trade_sell` by mirroring `trade_buy` and delegating to `self.trade_manager.pingan.sell`.
  - Rationale: task workflows already use manager methods directly and handle optional environment refresh.
- Keep D-07 partial after this change.
  - Rationale: stable sell entrypoints improve daily usability, but do not prove all broker windows, order types, and exception dialogs are covered.

## Risks / Trade-offs

- Sell is live-side-effecting -> keep existing safety controls and do not add presets that would execute without explicit operator arguments.
- Some users may expect multi-broker sell -> keep FUNCTION_TREE boundary scoped to Ping An desktop automation.
