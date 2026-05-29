## 1. Specification

- [x] 1.1 Add proposal, design, spec delta, and tasks for supervisor daemon lifecycle scaffold.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing controller test for supervisor daemon start writing owned state and pid files.
- [x] 2.2 Add failing controller test for read-only supervisor daemon status.
- [x] 2.3 Add failing controller test for owner-token guarded supervisor daemon stop.

## 3. Implementation

- [x] 3.1 Add separate supervisor daemon paths and statefile helpers.
- [x] 3.2 Implement controller start/status/stop methods and daemon command builder.
- [x] 3.3 Add a minimal supervisor daemon runner module.
- [x] 3.4 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused pytest for subscription background control.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change and rerun verification.
