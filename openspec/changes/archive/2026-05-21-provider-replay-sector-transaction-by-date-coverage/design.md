## Context

Provider replay mode is strict and fixture-backed. Recent E-07 slices added replay coverage for by-date stock and market transaction queries. `transaction.sector_transaction_data_by_date` is the remaining by-date transaction query with a stock/sector symbol selector, but it lacks a fixture descriptor, default replay mapping, replay-supported query metadata, API replay allowlist entry, and flat command replay dispatch.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `transaction.sector_transaction_data_by_date`.
- Preserve existing live behavior and CLI argument shape.
- Preserve the hardened `data.query_meta` contract, including requested symbols, requested fields, and date selector.
- Make nested `api` and flat `tdx-data-*` entrypoints use the replay manager path only when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` E-07 without implying full transaction replay coverage.

**Non-Goals:**
- Do not add replay coverage for sector transaction range queries or other transaction variants.
- Do not alter live TongDaXin bridge behavior.
- Do not introduce runtime network or Windows dependencies into fixture loading.

## Decisions

- Add one built-in JSON fixture named `transaction-sector-transaction-data-by-date-success`.
  - Alternative considered: reuse the stock transaction by-date fixture. Rejected because sector transaction uses a distinct capability name and should prove its own selector/query metadata.
- Use the same manager replay dispatch path as the other E-07 replay slices.
  - Alternative considered: CLI-only replay handling. Rejected because manager, CLI, replay provider, and runtime capability discovery must agree.
- Keep E-07 as `[部分实现]`.
  - Alternative considered: mark E-07 complete after this slice. Rejected because sector transaction range and other long-tail replay capabilities remain uncovered.

## Risks / Trade-offs

- [Risk] Readers may infer all sector transaction queries are replay-supported. -> Mitigation: name only `transaction.sector_transaction_data_by_date` in evidence and keep range variants in the boundary.
- [Risk] Flat CLI replay might accidentally fall through to the live bridge. -> Mitigation: add a test that patches the live flat bridge to fail if invoked.
- [Risk] Runtime capability fixture counts may drift. -> Mitigation: update summary counts and query metadata alongside tests.
