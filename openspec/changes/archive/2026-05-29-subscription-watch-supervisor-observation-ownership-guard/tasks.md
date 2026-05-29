## 1. Specification

- [x] 1.1 Add proposal, design, spec delta, and tasks for supervisor observation ownership guard.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing controller test proving supervisor tick observation does not attach to a different active run.
- [x] 2.2 Add failing controller test proving supervisor run observation does not attach to a different active run.

## 3. Implementation

- [x] 3.1 Add optional expected-run ownership guard to supervisor tick observation persistence.
- [x] 3.2 Add optional expected-run ownership guard to supervisor run observation persistence.
- [x] 3.3 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused pytest for subscription background control.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change and rerun verification.
