# Tasks

## 1. Contract

- [x] Add OpenSpec deltas for block sync write-policy task/catalog exposure.

## 2. Tests

- [x] Add failing parser/dispatch tests for `task block-sync --write-policy`.
- [x] Add failing preset/catalog tests for the safe dry-run block sync entry.

## 3. Implementation

- [x] Thread `write_policy` through API manager, task manager, bridge, and CLI block sync paths.
- [x] Register the block sync task default profile.
- [x] Add `plan-zxg-block-sync-merge` task preset and catalog entry.

## 4. Registry / Verification

- [x] Update `FUNCTION_TREE.md` E-04 with status, evidence, and boundary.
- [x] Run focused tests.
- [x] Run OpenSpec validation.
- [x] Run `git diff --check`.
