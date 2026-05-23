## Why

D-08 still records Ping An submit-once as partial because `side=sell` is visible at the CLI/task boundary, but the lower path is still a compatibility route through `pingan.sell`. That is truthful, but it leaves audit identity and idempotency evidence split: buy submit-once records `buy_submit_once`, while sell submit-once records ordinary `sell`.

The next small step is to give sell submit-once a dedicated manager/task/gateway identity while still using the existing sell desktop automation flow underneath. This makes the registry evidence sharper without implying a new broker engine or broader exception coverage.

## What Changes

- Add a dedicated `TdxTradeManager.pingan.sell_submit_once` manager method that reuses the existing sell desktop flow but records `sell_submit_once` as method/audit/idempotency identity.
- Route submit-once sell requests from the Ping An desktop trader gateway and task layer through that dedicated manager method.
- Preserve existing `trade submit-once --side sell` and `task trade-submit-once --side sell` UX, safety controls, and buy defaults.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary to reflect the new dedicated sell-submit-once identity without overclaiming full production coverage.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-management`: Ping An sell submit-once has a dedicated manager/audit/idempotency identity.
- `tdx-securities-trader-gateway`: submit-once sell requests route through the dedicated sell-submit-once manager path.
- `tdx-task-management`: task-level `side=sell` submit-once routes through the dedicated sell-submit-once manager path.

## Impact

- Affected code: `tdxquant/trade/manager.py`, `tdxquant/trader/adapters/pingan_desktop.py`, `tdxquant/api/task.py`.
- Affected tests: `tests/test_trade_manager.py`, `tests/test_pingan_trader_gateway.py`, `tests/test_api_manager.py`.
- Documentation: `FUNCTION_TREE.md`.
- Dependencies: none.
