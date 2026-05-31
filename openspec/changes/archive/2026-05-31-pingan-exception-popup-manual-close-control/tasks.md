## 1. Tests

- [x] 1.1 Add a trade manager regression proving inspect reports exception popup evidence without clicking or writing trade artifacts.
- [x] 1.2 Add a trade manager regression proving close requires explicit confirmation before clicking.
- [x] 1.3 Add a trade manager regression proving confirmed close clicks only a recognized exception popup confirm control and records no retry/recovery/resubmission.
- [x] 1.4 Add CLI parser/dispatch coverage for `trade exception-popup` inspect and confirmed close arguments.
- [x] 1.5 Add FUNCTION_TREE registry coverage proving D-07/D-08 remain `[部分实现]` with explicit evidence and boundaries.

## 2. Implementation

- [x] 2.1 Add `TdxTradeManager.pingan.exception_popup(...)` using existing dialog lookup, exception detection, and click helpers.
- [x] 2.2 Add stable `trade exception-popup` CLI parser and dispatch path.
- [x] 2.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without claiming implementation status.

## 3. Verification

- [x] 3.1 Run focused pytest for trade manager, CLI, and FUNCTION_TREE registry coverage.
- [x] 3.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
