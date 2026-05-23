# Validate OpenSpec Evidence In FUNCTION_TREE

## Why

`FUNCTION_TREE.md` uses OpenSpec change ids as part of its evidence column. The
registry already validates row shape, status, evidence, boundary, and the absence
of a competing `ROADMAP.md`; it should also reject stale or misspelled OpenSpec
evidence ids so the feature registry does not point at non-existent design
records.

## What Changes

- Extend `scripts/validate_function_tree_registry.py` to parse `OpenSpec
  \`change-id\`` references in feature rows.
- Require each referenced change id to exist either as an active change or as an
  archived change directory.
- Add tests for archived evidence, active evidence, and missing evidence ids.
- Update `FUNCTION_TREE.md` A-08 evidence/boundary.

## Out of Scope

- Proving that OpenSpec evidence implies runtime availability.
- Requiring every row to cite OpenSpec.
- Replacing `openspec validate --all --strict`.

## Impact

- Affected spec: `tdx-function-tree-registry`
- Affected script/tests: `scripts/validate_function_tree_registry.py`,
  `tests/test_function_tree_registry.py`
- Affected registry: `FUNCTION_TREE.md`
