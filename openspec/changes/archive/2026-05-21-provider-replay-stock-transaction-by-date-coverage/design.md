## Context

Provider replay mode is intentionally strict: a replay request must resolve to a deterministic fixture-backed result or fail without falling back to live Windows runtime code. Recent E-07 slices added replay coverage for several `market.*` and `meta.*` capabilities. `transaction.stock_transaction_data_by_date` has an existing live manager method and CLI parsers, but it is absent from the replay fixture registry, default replay mapping, replay-supported query metadata, API replay allowlist, and flat command replay dispatch.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `transaction.stock_transaction_data_by_date`.
- Preserve the existing live behavior and public argument shape.
- Keep replay output contract-equivalent to live manager query results by preserving `data.query_meta`.
- Make nested `api` and flat `tdx-data-*` entrypoints use the same replay manager path when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` so E-07 evidence names this capability without implying complete transaction replay coverage.

**Non-Goals:**
- Do not add replay coverage for `transaction.market_transaction_data_by_date`, sector transaction by-date queries, or other transaction variants.
- Do not change live TongDaXin bridge behavior or field normalization.
- Do not introduce runtime network or Windows dependencies into fixture loading.

## Decisions

- Add one built-in JSON fixture named `transaction-stock-transaction-data-by-date-success` for this single capability.
  - Alternative considered: reuse the existing non-by-date stock transaction fixture. Rejected because the by-date contract carries a `date` selector and must prove the by-date `query_meta` shape.
- Register the capability in the same replay dispatch path used by the recent stock-info, gp-one, and divid-factors slices.
  - Alternative considered: add CLI-only fixture handling. Rejected because manager, API CLI, flat CLI, and runtime capability discovery should all agree on the replay boundary.
- Keep `FUNCTION_TREE.md` E-07 as `[部分实现]`.
  - Alternative considered: mark E-07 complete after this slice. Rejected because other transaction by-date capabilities and long-tail replay coverage remain outside this change.

## Risks / Trade-offs

- [Risk] A new fixture can make readers infer all transaction by-date queries are replay-supported. → Mitigation: name only `transaction.stock_transaction_data_by_date` in specs and `FUNCTION_TREE.md` evidence, and leave other by-date transaction variants in the boundary.
- [Risk] Flat CLI replay could accidentally continue through the live bridge. → Mitigation: add a focused test that patches the live flat bridge to fail if invoked.
- [Risk] Runtime capability counts can drift as fixtures are added. → Mitigation: update the runtime capabilities fixture and tests together with the descriptor.
