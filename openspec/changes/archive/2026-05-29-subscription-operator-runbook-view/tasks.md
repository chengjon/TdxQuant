## 1. Tests

- [x] 1.1 Add CLI parser coverage for `bridge watch-status --view runbook`.
- [x] 1.2 Add focused CLI runbook-view coverage for read-only checklist output.
- [x] 1.3 Add focused HTTP runbook-view coverage for read-only checklist output.

## 2. Implementation

- [x] 2.1 Add a shared operator runbook builder derived from diagnostics view.
- [x] 2.2 Wire CLI `watch-status --view runbook`.
- [x] 2.3 Wire HTTP `watch/status?view=runbook`.

## 3. Registry and Validation

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence/boundary for operator runbook view.
- [x] 3.2 Run focused pytest for HTTP/CLI watch-status view coverage.
- [x] 3.3 Run `openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Run `python scripts/validate_function_tree_registry.py`.
