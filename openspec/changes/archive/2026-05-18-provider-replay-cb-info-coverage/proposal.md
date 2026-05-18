# provider-replay-cb-info-coverage

## Why

E-07 remains partial because each provider replay capability must be backed by explicit fixtures, default mapping, and tests. After stock-info and more-info, `market.cb_info` is the next adjacent market metadata query with existing live manager/API/flat CLI entrypoints but no replay fixture-backed path.

## What Changes

- Add a built-in `market.cb_info` provider replay fixture with hardened query metadata.
- Add `market.cb_info` to synchronous replay default fixture resolution and query discovery replay metadata.
- Route `TdxApiManager.market.cb_info(...)` through fixture-backed replay mode.
- Allow `api cb-info --provider-mode replay` and `tdx-data-cb-info --provider-mode replay` to use the manager replay path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one additional market metadata query.
- Live `cb_info` behavior is unchanged.
- Unregistered edge capabilities remain explicitly unsupported in replay mode.
