## 1. Spec

- [x] Add the `tdx-function-tree-registry` delta spec for explicit local evidence path validation.
- [x] Validate the OpenSpec change before implementation.

## 2. Tests

- [x] Add validator tests for existing local evidence paths, missing local evidence paths, and ignored non-literal evidence.

## 3. Implementation

- [x] Extend `scripts/validate_function_tree_registry.py` with conservative local evidence path extraction and existence checks.

## 4. Registry And Verification

- [x] Update `FUNCTION_TREE.md` A-08 evidence/boundary for local path existence validation.
- [x] Run focused tests, registry validation, OpenSpec validation, and whitespace checks.
- [x] Archive the OpenSpec change and rerun verification.
