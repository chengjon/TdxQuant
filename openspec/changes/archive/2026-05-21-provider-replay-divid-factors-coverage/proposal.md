# provider-replay-divid-factors-coverage

## Why

E-07 remains partial because provider replay support is only truthful when each capability has explicit fixtures, default mapping, and tests. After adding `meta.gp_one_data`, `meta.divid_factors` is the next metadata query with live manager/API/flat CLI entrypoints but no fixture-backed replay path.

## What Changes

- Add a built-in `meta.divid_factors` provider replay fixture with hardened query metadata.
- Add `meta.divid_factors` to synchronous replay default fixture resolution and query discovery replay metadata.
- Route `TdxApiManager.meta.divid_factors(...)` through fixture-backed replay mode.
- Allow `api divid-factors --provider-mode replay` and `tdx-data-divid-factors --provider-mode replay` to use the manager replay path.
- Update `FUNCTION_TREE.md` E-07 evidence and boundary while keeping the node partial if other edge capabilities remain outside replay coverage.

## Capabilities

### Modified Capabilities

- `tdx-provider-replay-fixtures`
- `tdx-provider-replay-mode`
- `tdx-api-management`
- `tdx-api-cli-entry`

## Impact

- Offline replay coverage expands by one additional metadata query.
- Live `divid_factors` behavior is unchanged.
- Unregistered edge capabilities remain explicitly unsupported in replay mode.

