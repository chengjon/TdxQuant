# Tasks

## 1. Spec

- [x] Add FUNCTION_TREE registry validator requirement and scenarios.

## 2. Tests

- [x] Cover the current `FUNCTION_TREE.md` passing validation.
- [x] Cover missing evidence or boundary failures.
- [x] Cover duplicate ids, unsupported status, unsafe pending rows, and
  competing `ROADMAP.md` failures.

## 3. Implementation

- [x] Add `scripts/validate_function_tree_registry.py`.
- [x] Keep validator output compact and deterministic.

## 4. Registry And Verification

- [x] Update `FUNCTION_TREE.md` A-08 evidence and boundary text.
- [x] Run focused pytest, script validation, OpenSpec validation, diff check,
  registry validation, and GitNexus change detection.
