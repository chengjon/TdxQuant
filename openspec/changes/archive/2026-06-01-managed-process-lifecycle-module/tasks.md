## 1. Red Tests

- [x] 1.1 Add focused tests for shared managed lifecycle PID liveness, ownership diagnostics, provenance, and restart backoff projection.
- [x] 1.2 Add provider replay test asserting managed lifecycle provenance in ownership diagnostics.
- [x] 1.3 Add subscription watch background test asserting managed lifecycle provenance in statefile ownership diagnostics.
- [x] 1.4 Run focused tests and confirm they fail before implementation.

## 2. Implementation

- [x] 2.1 Add `tdxquant/managed_lifecycle.py` with shared primitives.
- [x] 2.2 Wire provider replay process liveness and ownership diagnostics through the shared module.
- [x] 2.3 Wire subscription watch PID parsing, liveness, and statefile ownership projection through the shared module.
- [x] 2.4 Preserve existing public CLI behavior, persisted file formats, and status field compatibility.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16 evidence and boundary with shared lifecycle module evidence.
- [x] 3.2 Run focused pytest for managed lifecycle, provider replay, and subscription watch background.
- [x] 3.3 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.4 Archive the OpenSpec change.
- [x] 3.5 Re-run verification after archive.
- [x] 3.6 Commit only this slice.
