## Why

`FUNCTION_TREE.md` E-07 still marks provider replay coverage as partial, and `market.full_tick` is the remaining query contract that is not replay-supported. It already has a manager and nested API entrypoint, but cannot validate its full-tick provider result contract offline.

## What Changes

- Add a built-in successful replay fixture for `market.full_tick`.
- Register the fixture in the provider replay catalog and default sync replay fixture map.
- Mark the query discovery metadata for `market.full_tick` as replay-supported.
- Route `TdxApiManager(provider_mode="replay").market.full_tick(...)` through replay dispatch without live fallback.
- Allow nested `api full-tick --provider-mode replay` to use the replay manager path.
- Update `FUNCTION_TREE.md` E-07 with explicit evidence and boundaries for the completed current query-contract replay set.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add a representative `market.full_tick` query fixture.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for `market.full_tick`.
- `tdx-api-management`: route the manager full-tick query through replay dispatch in replay mode.
- `tdx-api-cli-entry`: expose the nested API replay entrypoint for the full-tick query.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/query_contract.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/` including the runtime capabilities sample.
- Affected tests: provider fixture, replay provider, and CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
