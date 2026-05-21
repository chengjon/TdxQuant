## Context

Provider replay mode is strict and fixture-backed. The previous E-07 transaction slices covered by-date stock, market, and sector queries. `transaction.sector_transaction_data` is the remaining sector transaction range query with symbol and date-range selectors, but it lacks a fixture descriptor, default replay mapping, replay-supported query metadata, API replay allowlist entry, flat command replay arguments, and flat replay dispatch.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `transaction.sector_transaction_data`.
- Preserve existing live behavior and CLI argument shape.
- Preserve the hardened `data.query_meta` contract, including requested symbols, requested fields, and date range.
- Make nested `api` and flat `tdx-data-*` entrypoints use the replay manager path only when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` E-07 without implying full replay coverage for every remaining transaction capability.

**Non-Goals:**
- Do not add replay coverage for any other transaction, formula, block, subscription, or trading capability.
- Do not alter live TongDaXin bridge behavior.
- Do not introduce runtime network or Windows dependencies into fixture loading.

## Decisions

- Add one built-in JSON fixture named `transaction-sector-transaction-data-success`.
  - Alternative considered: reuse the by-date sector transaction fixture. Rejected because the range query must prove a `date_range` selector and separate entrypoints.
- Use the same manager replay dispatch path as the other E-07 replay slices.
  - Alternative considered: CLI-only replay handling. Rejected because manager, CLI, replay provider, and runtime capability discovery must agree.
- Keep E-07 as `[部分实现]`.
  - Alternative considered: mark E-07 complete after this slice. Rejected because other long-tail replay capabilities remain uncovered.

## Risks / Trade-offs

- [Risk] Readers may infer all transaction queries are replay-supported. -> Mitigation: name only `transaction.sector_transaction_data` in evidence and keep E-07 partial.
- [Risk] Flat CLI replay might accidentally fall through to the live bridge. -> Mitigation: add a test that patches the live flat bridge to fail if invoked.
- [Risk] Runtime capability fixture counts may drift. -> Mitigation: update summary counts and query metadata alongside tests.
