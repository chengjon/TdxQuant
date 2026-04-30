## Why

当前桌面交易主线已经有稳定买入流程、状态回填和事件日志，但还缺少第一版明确的安全治理契约。上层调用者和日常操作者都需要在真正触发桌面副作用前拿到一致的风险门、请求关联键和结果安全分级。

## What Changes

- Add first-slice desktop trade safety hardening for stable Ping An buy and submit-once workflows.
- Add optional `submission_key` correlation support to `TdxTradeManager` stable workflows and preserve it in result/state/event artifacts.
- Add a pre-trade risk gate that rejects invalid orders before desktop side effects and supports an optional caller `max_price` ceiling.
- Add stable `data.trade_safety` metadata to desktop trade results, including stability grade, side-effect grade, submission key, and risk-gate summary.
- Extend `trade buy`, `trade submit-once`, `trade run`, `pingan-buy`, and `pingan-buy-submit-once` CLI entrypoints with safety-control flags.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-safety`: Defines the first provider-style safety contract for stable desktop trading workflows, including safety metadata, correlation keys, and pre-trade rejection semantics.

### Modified Capabilities
- `tdx-desktop-trading-management`: Adds safety-governed behavior to stable `TdxTradeManager` desktop trade workflows and persisted trading artifacts.
- `tdx-desktop-trading-cli-entry`: Adds stable safety-control arguments to the nested and flat desktop trade CLI entrypoints.

## Impact

- Affected code:
  - `tdxquant/trade/manager.py`
  - `tdxquant/trade/context.py`
  - `tdxquant/cli.py`
  - `tests/test_trade_manager.py`
  - `tests/test_api_cli.py`
- Affected runtime artifacts:
  - `runtime/pingan-last-order.json`
  - `runtime/pingan-order-events.jsonl`
- Affected docs:
  - trade function map / next-steps documentation
