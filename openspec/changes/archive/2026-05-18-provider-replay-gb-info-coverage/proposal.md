# provider-replay-gb-info-coverage

## Why

E-07 remains partial because each provider replay capability must be backed by explicit fixtures, default mapping, and tests. After stock-info, more-info, and cb-info, `meta.gb_info` is the next adjacent query with existing live manager/API/flat CLI entrypoints but no fixture-backed replay path.

## What Changes

- Add a built-in `meta.gb_info` provider replay fixture with hardened query metadata.
- Add `meta.gb_info` to synchronous replay default fixture resolution and query discovery replay metadata.
- Route `TdxApiManager.meta.gb_info(...)` through fixture-backed replay mode.
- Allow `api gb-info --provider-mode replay` and `tdx-data-gb-info --provider-mode replay` to use the manager replay path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one additional metadata query.
- Live `gb_info` behavior is unchanged.
- Unregistered edge capabilities remain explicitly unsupported in replay mode.

