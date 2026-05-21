## Why

`FUNCTION_TREE.md` E-07 still marks provider replay coverage as partial because transaction-sector range queries remain uncovered after the by-date slices. `transaction.sector_transaction_data` already has live manager and CLI entrypoints, but replay mode cannot yet validate its range query contract offline.

## What Changes

- Add a built-in successful replay fixture for `transaction.sector_transaction_data`.
- Register the fixture in the provider replay catalog and default sync replay fixture map.
- Mark the query discovery metadata for `transaction.sector_transaction_data` as replay-supported.
- Route `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data(...)` through replay dispatch without live fallback.
- Allow nested `api sector-transaction-data --provider-mode replay` and flat `tdx-data-sector-transaction --provider-mode replay` to use the replay manager path.
- Update `FUNCTION_TREE.md` E-07 with explicit evidence and boundaries for this newly covered capability.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add a representative `transaction.sector_transaction_data` query fixture.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for `transaction.sector_transaction_data`.
- `tdx-api-management`: route the manager sector transaction range query through replay dispatch in replay mode.
- `tdx-api-cli-entry`: expose nested and flat CLI replay entrypoints for the sector transaction range query.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/query_contract.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/` including the runtime capabilities sample.
- Affected tests: provider fixture, replay provider, and CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
