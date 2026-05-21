## Why

`FUNCTION_TREE.md` E-07 still marks provider replay coverage as partial because several query capabilities have no deterministic fixture-backed replay path. `transaction.stock_transaction_data_by_date` already has live manager and CLI entrypoints, but replay mode cannot yet prove this by-date transaction contract offline without live TongDaXin runtime access.

## What Changes

- Add a built-in successful replay fixture for `transaction.stock_transaction_data_by_date`.
- Register the fixture in the provider replay catalog and default sync replay fixture map.
- Mark the query discovery metadata for `transaction.stock_transaction_data_by_date` as replay-supported.
- Route `TdxApiManager(provider_mode="replay").transaction.stock_transaction_data_by_date(...)` through replay dispatch without live fallback.
- Allow nested `api stock-transaction-data-by-date --provider-mode replay` and flat `tdx-data-stock-transaction-by-date --provider-mode replay` to use the replay manager path.
- Update `FUNCTION_TREE.md` E-07 with explicit status, evidence, and boundaries for this newly covered capability.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-replay-fixtures`: add a representative `transaction.stock_transaction_data_by_date` query fixture.
- `tdx-provider-replay-mode`: add default fixture-backed replay execution for `transaction.stock_transaction_data_by_date`.
- `tdx-api-management`: route the manager by-date stock transaction query through replay dispatch in replay mode.
- `tdx-api-cli-entry`: expose nested and flat CLI replay entrypoints for the by-date stock transaction query.

## Impact

- Affected code: `tdxquant/replay_fixtures.py`, `tdxquant/replay_provider.py`, `tdxquant/query_contract.py`, `tdxquant/api/manager.py`, `tdxquant/cli.py`.
- Affected fixtures: `tdxquant/fixtures/provider/` including the runtime capabilities sample.
- Affected tests: provider fixture, replay provider, and CLI tests.
- Affected documentation/register: `FUNCTION_TREE.md` remains the single feature registry.
