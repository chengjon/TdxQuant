## Why

`FUNCTION_TREE.md` E-07 still marks provider replay coverage as partial because `market.market_snapshot` has live manager and CLI entrypoints but no deterministic fixture-backed replay path. This leaves `api market-snapshot` and `tdx-data-market-snapshot` unable to validate their provider result contract offline.

## What Changes

- Add a built-in successful replay fixture for `market.market_snapshot`.
- Register the fixture in the provider replay catalog and default sync replay fixture map.
- Mark the query discovery metadata for `market.market_snapshot` as replay-supported.
- Route `TdxApiManager(provider_mode="replay").market.market_snapshot(...)` through replay dispatch without live fallback.
- Allow nested `api market-snapshot --provider-mode replay` and flat `tdx-data-market-snapshot --provider-mode replay` to use the replay manager path.
- Update `FUNCTION_TREE.md` E-07 with explicit evidence and boundaries for this newly covered capability.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add a representative `market.market_snapshot` query fixture.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for `market.market_snapshot`.
- `tdx-api-management`: route the manager market-snapshot query through replay dispatch in replay mode.
- `tdx-api-cli-entry`: expose nested and flat CLI replay entrypoints for the market-snapshot query.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/query_contract.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/` including the runtime capabilities sample.
- Affected tests: provider fixture, replay provider, and CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
