## Why

`FUNCTION_TREE.md` E-07 still has a small set of query contracts that are not replay-supported. `meta.sector_list` is already exposed by the manager and CLI, but replay mode cannot yet validate the sector-list metadata contract offline.

## What Changes

- Add a built-in successful replay fixture for `meta.sector_list`.
- Register the fixture in the provider replay catalog and default sync replay fixture map.
- Mark the query discovery metadata for `meta.sector_list` as replay-supported.
- Route `TdxApiManager(provider_mode="replay").meta.sector_list(...)` through replay dispatch without live fallback.
- Allow nested `api sector-list --provider-mode replay` and flat `tdx-data-sector-list --provider-mode replay` to use the replay manager path.
- Update `FUNCTION_TREE.md` E-07 with explicit evidence and boundaries for this newly covered capability.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add a representative `meta.sector_list` query fixture.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for `meta.sector_list`.
- `tdx-api-management`: route the manager sector-list query through replay dispatch in replay mode.
- `tdx-api-cli-entry`: expose nested and flat CLI replay entrypoints for the sector-list query.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/query_contract.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/` including the runtime capabilities sample.
- Affected tests: provider fixture, replay provider, and CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
