# provider-replay-ipo-info-coverage

## Why

E-07 remains partial because provider replay support is only truthful when each capability has explicit fixtures, default mapping, and tests. After adding `meta.gb_info`, `meta.ipo_info` is the next remaining metadata query with live manager/API/flat CLI entrypoints but no fixture-backed replay path.

## What Changes

- Add a built-in `meta.ipo_info` provider replay fixture with hardened query metadata.
- Add `meta.ipo_info` to synchronous replay default fixture resolution and query discovery replay metadata.
- Route `TdxApiManager.meta.ipo_info(...)` through fixture-backed replay mode.
- Allow `api ipo-info --provider-mode replay` and `tdx-data-ipo-info --provider-mode replay` to use the manager replay path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial if other edge capabilities remain outside replay coverage.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one additional metadata query.
- Live `ipo_info` behavior is unchanged.
- Unregistered edge capabilities remain explicitly unsupported in replay mode.

