# provider-replay-stock-info-coverage

## Why

`FUNCTION_TREE.md` tracks E-07 `wider capability replay coverage` as partially implemented: replay fixtures exist for core runtime, market, meta, financial, transaction, block, and subscription paths, but edge query capabilities still require explicit samples, contracts, and tests before they can be treated as offline replay-supported.

`market.stock_info` is a useful next vertical slice because the manager and CLI already expose live stock-info query entrypoints, but replay mode currently has no built-in fixture/default mapping for that capability and must not silently fall back to live Windows runtime code.

## What Changes

- Add a built-in `market.stock_info` provider replay fixture that preserves the hardened query metadata shape.
- Add `market.stock_info` to synchronous replay default fixture resolution.
- Route `TdxApiManager.market.stock_info(...)` through fixture-backed replay mode when `provider_mode="replay"`.
- Allow the nested `api stock-info --provider-mode replay` and flat `tdx-data-stock-info --provider-mode replay` entrypoints to use the same fixture-backed path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one provider-facing query capability.
- Live stock-info behavior is unchanged.
- Replay mode remains explicit and fixture-backed; unsupported capabilities still fail without live fallback.
