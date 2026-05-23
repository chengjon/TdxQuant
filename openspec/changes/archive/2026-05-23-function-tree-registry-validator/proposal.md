# Add FUNCTION_TREE Registry Validator

## Why

`FUNCTION_TREE.md` is the single feature registry for the project. The registry
format is currently checked with ad hoc scripts during maintenance. A committed
validator makes the contract repeatable: every feature row must have an explicit
status, evidence, and boundary, and the repository must not grow a competing
`ROADMAP.md`.

## What Changes

- Add `scripts/validate_function_tree_registry.py`.
- Validate feature-row status values, duplicate ids, evidence cells, boundary
  cells, and root `ROADMAP.md` absence.
- Add focused tests for valid registry parsing and failure cases.
- Update `FUNCTION_TREE.md` A-08 as OpenSpec/registry lifecycle evidence while
  keeping its boundary explicit.

## Out of Scope

- Proving runtime behavior for any feature node.
- Interpreting evidence paths as executed tests.
- Replacing OpenSpec validation.
- Adding a second roadmap or planning document.

## Impact

- Affected spec: `tdx-function-tree-registry`
- Affected docs: `FUNCTION_TREE.md`
- Affected scripts/tests: `scripts/validate_function_tree_registry.py`,
  `tests/test_function_tree_registry.py`
