## 1. Tests

- [x] 1.1 Add failing trade audit index tests for broker/method/status count aggregation.
- [x] 1.2 Add failing tests proving aggregation is computed before row `limit` is applied.
- [x] 1.3 Add failing tests for unknown dimension handling.

## 2. Implementation

- [x] 2.1 Add deterministic count aggregation helpers in `tdxquant/trade_audit_index.py`.
- [x] 2.2 Include aggregation in `query_trade_audit_cross_ledger(...)` without changing existing rows or join rules.
- [x] 2.3 Update `FUNCTION_TREE.md` E-12 evidence and boundary without claiming PnL/amount aggregation.

## 3. Verification

- [x] 3.1 Run focused pytest for trade audit index and API CLI coverage.
- [x] 3.2 Run OpenSpec strict validation, `git diff --check`, and the FUNCTION_TREE registry validator.
- [x] 3.3 Archive the OpenSpec change, rerun verification, and commit the completed slice.
