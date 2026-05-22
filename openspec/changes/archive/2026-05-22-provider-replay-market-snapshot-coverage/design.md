## Context

Provider replay mode is strict and fixture-backed. `market.market_snapshot` is a distinct query contract from the already replay-backed `market.snapshot`: it maps to the TongDaXin `get_market_snapshot` path and has its own manager method, nested API command, and flat CLI command.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `market.market_snapshot`.
- Preserve existing live behavior and CLI argument shape.
- Preserve the hardened `data.query_meta` contract, including symbol selector and requested fields.
- Make nested `api` and flat `tdx-data-*` entrypoints use the replay manager path only when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` E-07 without implying all remaining query contracts are complete.

**Non-Goals:**
- Do not add replay coverage for `market.full_tick`.
- Do not merge or rename the existing `market.snapshot` fixture.
- Do not alter live TongDaXin bridge behavior.
- Do not introduce runtime network or Windows dependencies into fixture loading.

## Decisions

- Add one built-in JSON fixture named `market-market-snapshot-success`.
  - Alternative considered: reuse `market-snapshot-success`. Rejected because `market.snapshot` and `market.market_snapshot` are separate capabilities and entrypoints.
- Use the same manager replay dispatch path as the other E-07 query replay slices.
  - Alternative considered: CLI-only replay handling. Rejected because manager, CLI, replay provider, and runtime capability discovery must agree.
- Keep E-07 as `[部分实现]`.
  - Alternative considered: mark E-07 complete after this slice. Rejected because `market.full_tick` remains uncovered.

## Risks / Trade-offs

- [Risk] Readers may confuse `market.snapshot` and `market.market_snapshot`. -> Mitigation: name both the fixture and FUNCTION_TREE evidence with the full `market.market_snapshot` capability.
- [Risk] Flat CLI replay might accidentally fall through to the live bridge. -> Mitigation: add a test that patches the live flat bridge to fail if invoked.
- [Risk] Runtime capability fixture counts may drift. -> Mitigation: update summary counts and query metadata alongside tests.
