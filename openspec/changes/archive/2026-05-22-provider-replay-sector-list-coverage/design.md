## Context

Provider replay mode is strict and fixture-backed. `meta.sector_list` is one of the remaining query contracts not present in `_QUERY_REPLAY_SUPPORTED_CAPABILITIES`. It has manager and CLI entrypoints, and its query shape is simple: no selectors and `list_type` as a query parameter.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `meta.sector_list`.
- Preserve existing live behavior and CLI argument shape.
- Preserve the hardened `data.query_meta` contract, including `list_type`.
- Make nested `api` and flat `tdx-data-*` entrypoints use the replay manager path only when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` E-07 without implying all remaining query contracts are complete.

**Non-Goals:**
- Do not add replay coverage for `market.full_tick` or `market.market_snapshot`.
- Do not alter live TongDaXin bridge behavior.
- Do not introduce runtime network or Windows dependencies into fixture loading.

## Decisions

- Add one built-in JSON fixture named `meta-sector-list-success`.
  - Alternative considered: reuse `meta-sector-stocks-success`. Rejected because sector-list and sector-stocks have different selectors and payload meaning.
- Use the same manager replay dispatch path as the other E-07 query replay slices.
  - Alternative considered: CLI-only replay handling. Rejected because manager, CLI, replay provider, and runtime capability discovery must agree.
- Keep E-07 as `[部分实现]`.
  - Alternative considered: mark E-07 complete after this slice. Rejected because `market.full_tick` and `market.market_snapshot` remain uncovered.

## Risks / Trade-offs

- [Risk] Readers may infer all meta queries are replay-supported. -> Mitigation: name only `meta.sector_list` in evidence and keep E-07 partial.
- [Risk] Flat CLI replay might accidentally fall through to the live bridge. -> Mitigation: add a test that patches the live flat bridge to fail if invoked.
- [Risk] Runtime capability fixture counts may drift. -> Mitigation: update summary counts and query metadata alongside tests.
