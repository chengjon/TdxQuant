# Add FUNCTION_TREE Validator JSON Report

## Why

`FUNCTION_TREE.md` is the single feature registry, and the validator is now part of the A-08 lifecycle evidence. Its current text output is suitable for humans, but downstream CI and agent loops need a stable machine-readable report so they can consume row counts, status counts, and validation errors without parsing prose.

## What Changes

- Add `--json` to `scripts/validate_function_tree_registry.py`.
- Emit a stable JSON report for both successful and failed validation.
- Preserve the default compact text output and exit-code behavior.
- Update A-08 in `FUNCTION_TREE.md` to cite the JSON report as validator evidence without implying feature availability.

## Impact

- Affected spec: `tdx-function-tree-registry`
- Affected code: `scripts/validate_function_tree_registry.py`
- Affected tests: `tests/test_function_tree_registry.py`
- Boundary: the JSON report summarizes validation only; it still does not execute evidence paths, expand globs, or prove that cited features are usable.
