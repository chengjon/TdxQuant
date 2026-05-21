## Context

Provider replay mode is strict and fixture-backed. The previous E-07 slice added replay coverage for `transaction.stock_transaction_data_by_date`. `transaction.market_transaction_data_by_date` has a similar live manager/CLI surface, but it has no fixture descriptor, default replay mapping, replay-supported query metadata, nested API replay allowlist entry, or flat command replay dispatch.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `transaction.market_transaction_data_by_date`.
- Preserve existing live behavior and CLI argument shape.
- Preserve the hardened `data.query_meta` contract for the by-date market transaction query.
- Make nested `api` and flat `tdx-data-*` entrypoints use the replay manager path only when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` E-07 without implying full transaction replay coverage.

**Non-Goals:**
- Do not add replay coverage for sector transaction by-date queries or other transaction variants.
- Do not alter live TongDaXin bridge behavior.
- Do not introduce runtime network or Windows dependencies into fixture loading.

## Decisions

- Add one built-in JSON fixture named `transaction-market-transaction-data-by-date-success`.
  - Alternative considered: reuse `transaction-market-transaction-data-success`. Rejected because the by-date query must prove a `date` selector instead of a `date_range` selector.
- Use the same manager replay dispatch path as existing fixture-backed query capabilities.
  - Alternative considered: handle the fixture only in CLI. Rejected because manager, CLI, replay provider, and runtime capability discovery must agree.
- Keep E-07 as `[部分实现]`.
  - Alternative considered: mark E-07 complete after this slice. Rejected because sector transaction variants and other edge capabilities remain uncovered.

## Risks / Trade-offs

- [Risk] Readers may infer all transaction by-date queries are replay-supported. -> Mitigation: name only `transaction.market_transaction_data_by_date` in evidence and keep sector transaction variants in the boundary.
- [Risk] Flat CLI replay might accidentally fall through to the live bridge. -> Mitigation: add a test that patches the live flat bridge to fail if invoked.
- [Risk] Runtime capability fixture counts may drift. -> Mitigation: update summary counts and query metadata alongside tests.
