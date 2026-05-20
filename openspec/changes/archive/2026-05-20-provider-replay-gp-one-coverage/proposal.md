# provider-replay-gp-one-coverage

## Why

E-07 remains partial because provider replay support is only truthful when each capability has explicit fixtures, default mapping, and tests. After adding `meta.gb_info` and `meta.ipo_info`, `meta.gp_one_data` is the next metadata query with live manager/API/flat CLI entrypoints but no fixture-backed replay path.

## What Changes

- Add a built-in `meta.gp_one_data` provider replay fixture with hardened query metadata.
- Add `meta.gp_one_data` to synchronous replay default fixture resolution and query discovery replay metadata.
- Route `TdxApiManager.meta.gp_one_data(...)` through fixture-backed replay mode.
- Allow `api gp-one --provider-mode replay` and `tdx-data-gp-one --provider-mode replay` to use the manager replay path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial if other edge capabilities remain outside replay coverage.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one additional metadata query.
- Live `gp_one_data` behavior is unchanged.
- Unregistered edge capabilities remain explicitly unsupported in replay mode.

