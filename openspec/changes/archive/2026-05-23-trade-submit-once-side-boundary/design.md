## Context

`trade submit-once` currently creates a `SecurityOrderRequest` with `OrderSide.BUY`. The lower `PingAnDesktopTraderGateway` already has a compatibility branch where `execution_mode=submit_once` plus `side=sell` calls the existing Ping An sell workflow and labels the adapter step as submit-once-compatible. The task layer, however, calls `TdxTradeManager.pingan.buy_submit_once` directly and has no side selector.

## Goals / Non-Goals

**Goals:**

- Make stable submit-once entrypoints explicit about order side.
- Keep default behavior unchanged as `side=buy`.
- Make `side=sell` visible as a compatibility route through the existing sell chain.

**Non-Goals:**

- No new underlying `run_pingan_sell_submit_once` or dedicated manager method.
- No change to legacy `pingan-buy-submit-once`; it remains buy-only by name.
- No expansion to other brokers, order types, or exception dialogs.

## Decisions

- Add `--side {buy,sell}` to nested `trade submit-once` and task submit-once paths.
  - Rationale: `side` is already the domain model used by `SecurityOrderRequest`; exposing it avoids invented command names.
  - Alternative considered: create a new `trade sell-submit-once` command. That would imply a dedicated implementation that does not exist.
- Add `side` to `TdxTaskManager.trade_submit_once`.
  - Rationale: task presets and task CLI should share the same explicit boundary as the nested trade CLI.
  - Alternative considered: keep task buy-only. That would leave the feature tree evidence split and incomplete at the task layer.
- Route task `side=sell` to `trade_manager.pingan.sell`.
  - Rationale: this matches the existing adapter compatibility route and keeps the boundary truthful.

## Risks / Trade-offs

- `side=sell` may be mistaken for a dedicated sell-submit-once engine -> mitigate by recording `side` in task input and by updating FUNCTION_TREE boundary text.
- More arguments on submit-once paths -> keep default `buy` so existing presets and callers remain compatible.
