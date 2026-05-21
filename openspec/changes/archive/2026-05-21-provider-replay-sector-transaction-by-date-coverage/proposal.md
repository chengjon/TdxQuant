## Why

`FUNCTION_TREE.md` E-07 still has transaction-sector replay gaps after covering stock and market by-date transaction queries. `transaction.sector_transaction_data_by_date` has live manager and CLI entrypoints, but replay mode cannot yet validate its by-date sector transaction contract offline.

## What Changes

- Add a built-in successful replay fixture for `transaction.sector_transaction_data_by_date`.
- Register the fixture in the provider replay catalog and default sync replay fixture map.
- Mark the query discovery metadata for `transaction.sector_transaction_data_by_date` as replay-supported.
- Route `TdxApiManager(provider_mode="replay").transaction.sector_transaction_data_by_date(...)` through replay dispatch without live fallback.
- Allow nested `api sector-transaction-data-by-date --provider-mode replay` and flat `tdx-data-sector-transaction-by-date --provider-mode replay` to use the replay manager path.
- Update `FUNCTION_TREE.md` E-07 with explicit evidence and boundaries for this newly covered capability.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add a representative `transaction.sector_transaction_data_by_date` query fixture.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for `transaction.sector_transaction_data_by_date`.
- `tdx-api-management`: route the manager by-date sector transaction query through replay dispatch in replay mode.
- `tdx-api-cli-entry`: expose nested and flat CLI replay entrypoints for the by-date sector transaction query.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/query_contract.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/` including the runtime capabilities sample.
- Affected tests: provider fixture, replay provider, and CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
