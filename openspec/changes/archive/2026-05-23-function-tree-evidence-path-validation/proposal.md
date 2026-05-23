## Why

`FUNCTION_TREE.md` is now the single feature registry, but its evidence column can still cite local files or directories that no longer exist. The registry validator should catch obvious stale local evidence without interpreting free-form descriptions or claiming that cited code has been executed.

## What Changes

- Extend the FUNCTION_TREE registry validator to check explicit local evidence paths in feature rows.
- Treat only conservative, literal path references as checkable evidence so prose, globs, code symbols, and command examples are not misclassified.
- Report missing evidence paths with the feature row id and path.
- Keep validation scoped to existence checks; it does not prove runtime behavior or feature availability.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-function-tree-registry`: validate explicit local evidence paths cited in `FUNCTION_TREE.md` feature rows.

## Impact

- Affected spec: `tdx-function-tree-registry`
- Affected script/tests: `scripts/validate_function_tree_registry.py`, `tests/test_function_tree_registry.py`
- Affected registry: `FUNCTION_TREE.md`
