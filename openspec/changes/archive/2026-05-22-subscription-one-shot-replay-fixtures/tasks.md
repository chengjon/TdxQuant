## 1. Tests

- [x] 1.1 Add failing fixture tests for one-shot subscription replay samples.
- [x] 1.2 Add failing replay provider and manager tests proving replay uses fixtures without live session calls.
- [x] 1.3 Add failing CLI replay tests for `api subscription-subscribe/unsubscribe/list --provider-mode replay`.

## 2. Implementation

- [x] 2.1 Add one-shot subscription fixtures and fixture descriptors/default replay mapping.
- [x] 2.2 Add manager-level one-shot subscription methods with live and replay paths.
- [x] 2.3 Allow one-shot subscription API commands in explicit replay mode.
- [x] 2.4 Update `FUNCTION_TREE.md` E-01 evidence and boundary without claiming long-running watch governance.

## 3. Verification

- [x] 3.1 Run focused pytest for replay fixtures, replay provider, API manager, and API CLI.
- [x] 3.2 Run OpenSpec strict validation, `git diff --check`, and the FUNCTION_TREE registry validator.
- [x] 3.3 Archive the OpenSpec change, rerun verification, and commit the completed slice.
