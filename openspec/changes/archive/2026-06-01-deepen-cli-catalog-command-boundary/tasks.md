## 1. Red Tests

- [x] 1.1 Add a public CLI parser/handler test that proves `catalog list` still returns summary discovery fields without execution.
- [x] 1.2 Add a public CLI parser/handler test that proves `catalog plan` or `catalog preview` keeps non-execution provenance and constraints.
- [x] 1.3 Add a public CLI parser/handler test that proves `catalog validate` uses registry validation without dispatching catalog execution.

## 2. Boundary Implementation

- [x] 2.1 Introduce a catalog-specific CLI command boundary module.
- [x] 2.2 Route catalog parser registration through the catalog boundary while preserving the top-level `tdxquant.cli` entrypoint.
- [x] 2.3 Route catalog subcommand handling through the catalog boundary while preserving current list/plan/preview/validate/run behavior.
- [x] 2.4 Move catalog-specific helpers that can be moved without broad CLI import cycles.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` evidence and boundary for the catalog/CLI architecture boundary.
- [x] 3.2 Run focused catalog CLI tests.
- [x] 3.3 Run `openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Run `python scripts/validate_function_tree_registry.py`.
- [x] 3.6 Archive the OpenSpec change and repeat verification.
