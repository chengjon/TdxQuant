## Why

`FUNCTION_TREE.md` E-12 still records the trade audit index as partial because the current cross-ledger query is exact-key only. Operators can inspect joined rows, but they cannot quickly see how the filtered audit set distributes across broker, method, and status without doing external aggregation.

## What Changes

- Add a read-only aggregation summary to `query_trade_audit_cross_ledger(...)`.
- Aggregate the filtered audit set by `status`, `method`, `broker`, and combined `broker/method/status` dimensions.
- Preserve existing exact-key rows, join rules, filters, cache behavior, and ledger immutability.
- Update `FUNCTION_TREE.md` E-12 with explicit evidence and boundaries.

## Non-Goals

- No PnL, amount, quantity, or price aggregation.
- No fuzzy joining or mutation of audit files, submission ledgers, task ledgers, or caches.
- No live broker/provider capability.
- No new CLI command in this slice.

