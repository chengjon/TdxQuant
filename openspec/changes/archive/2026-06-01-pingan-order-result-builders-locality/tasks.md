## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for PingAn order result-builder locality.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Test

- [x] 2.1 Add direct tests for order duplicate/conflict/risk rejection builder helpers.
- [x] 2.2 Run the focused new tests and confirm they fail before the helpers exist.

## 3. Implementation

- [x] 3.1 Add `PingAnOrderResultContext` and order result builder helpers to `pingan_execution.py`.
- [x] 3.2 Route order handler construction through the module-level builders.
- [x] 3.3 Route submit-ready risk rejection through the same risk rejection builder.
- [x] 3.4 Remove redundant manager private result builder methods/imports.
- [x] 3.5 Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
