## Context

Provider replay mode is strict and fixture-backed. `market.full_tick` is the only remaining query contract in the current registry without replay support. It has a manager method and nested `api full-tick` command, but no flat `tdx-data-*` command exists today.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for `market.full_tick`.
- Preserve existing live behavior and nested API argument shape.
- Preserve the hardened `data.query_meta` contract, including symbol selector and requested fields.
- Make `api full-tick` use the replay manager path only when `--provider-mode replay` is explicit.
- Update `FUNCTION_TREE.md` E-07 to state the current query-contract replay coverage boundary precisely.

**Non-Goals:**
- Do not add a new flat `tdx-data-full-tick` command.
- Do not alter live TongDaXin bridge behavior.
- Do not introduce runtime network or Windows dependencies into fixture loading.
- Do not claim replay support for future provider capabilities that are not yet registered in the query contract registry.

## Decisions

- Add one built-in JSON fixture named `market-full-tick-success`.
  - Alternative considered: reuse `market-snapshot-success`. Rejected because full-tick and snapshot are separate query contracts and entrypoints.
- Use the same manager replay dispatch path as the other E-07 query replay slices.
  - Alternative considered: direct nested CLI replay handling. Rejected because manager, replay provider, and runtime capability discovery must agree.
- Close E-07 only for the current query-contract registry.
  - Alternative considered: keep E-07 partial indefinitely. Rejected because the remaining known query-contract gap is explicitly resolved here; future capabilities can reopen or add new registry nodes.

## Risks / Trade-offs

- [Risk] Readers may infer a flat `tdx-data-full-tick` command exists. -> Mitigation: keep evidence scoped to `api full-tick` and state the non-goal explicitly.
- [Risk] Nested API replay might accidentally fall through to the live bridge. -> Mitigation: add a manager test that patches the live full-tick bridge path to fail if invoked.
- [Risk] Runtime capability fixture counts may drift. -> Mitigation: update summary counts and query metadata alongside tests.
