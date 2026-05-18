# provider-replay-more-info-coverage

## Why

E-07 remains partially implemented after stock-info replay coverage because adjacent market metadata capabilities still have live manager/CLI entrypoints but no fixture-backed replay support. `market.more_info` is the next narrow query contract to cover: it shares the same explicit symbol and requested-field semantics as `market.stock_info`, but must be registered and tested independently so readers do not assume all market metadata queries are replay-supported.

## What Changes

- Add a built-in `market.more_info` provider replay fixture with hardened query metadata.
- Add `market.more_info` to synchronous replay default fixture resolution and query discovery replay metadata.
- Route `TdxApiManager.market.more_info(...)` through fixture-backed replay mode.
- Allow `api more-info --provider-mode replay` and `tdx-data-more-info --provider-mode replay` to use the manager replay path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one additional provider-facing market metadata query.
- Live `more_info` behavior is unchanged.
- Replay support remains explicitly per capability; unregistered edge queries continue to fail without live fallback.
