## 1. Specification

- [x] 1.1 Add proposal, design, spec deltas, and tasks for supervisor-tick observation.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing controller tests for compact supervisor-tick observation persistence.
- [x] 2.2 Add failing bridge diagnostics test for `last_supervisor_tick_observation` projection.

## 3. Implementation

- [x] 3.1 Implement compact supervisor-tick observation builder and best-effort persistence.
- [x] 3.2 Project latest supervisor-tick observation in diagnostics view.
- [x] 3.3 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused pytest for subscription background and bridge diagnostics.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change and rerun verification.
