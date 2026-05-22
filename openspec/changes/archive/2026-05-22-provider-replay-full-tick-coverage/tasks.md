## 1. Tests

- [x] 1.1 Add failing fixture and runtime capability metadata tests for `market.full_tick`.
- [x] 1.2 Add failing replay provider and manager tests proving replay uses the default fixture without live calls.
- [x] 1.3 Add failing nested API replay tests for full-tick.

## 2. Implementation

- [x] 2.1 Add the full-tick fixture and fixture descriptor/default replay mapping.
- [x] 2.2 Mark the capability replay-supported in query discovery and runtime capabilities metadata.
- [x] 2.3 Route the manager method and nested API replay entrypoint through fixture-backed replay dispatch.
- [x] 2.4 Update `FUNCTION_TREE.md` E-07 evidence and boundary.

## 3. Verification

- [x] 3.1 Run focused pytest for replay fixtures, replay provider, and API CLI.
- [x] 3.2 Run OpenSpec strict validation, `git diff --check`, and the FUNCTION_TREE registry validator.
- [x] 3.3 Archive the OpenSpec change, rerun verification, and commit the completed slice.
