# Tasks: Provider Replay Probe Status Key Counts

## 1. OpenSpec

- [x] 1.1 Add OpenSpec proposal, design, tasks, and provider replay service delta for probe status key counts.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add provider replay status assertions for `status_key_count`.
- [x] 2.2 Add provider replay status assertions for `requested_status_key_count` and `failed_status_key_count`.

## 3. Implementation

- [x] 3.1 Derive probe summary status key-count fields from existing status count maps.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming probe execution, health/readiness proof, socket startup, provider mutation, or lifecycle management.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.
