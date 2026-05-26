# Tasks: Provider Replay Probe Error Key Counts

## 1. OpenSpec

- [x] 1.1 Add OpenSpec proposal, design, tasks, and provider replay service delta for probe error key counts.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add provider replay status assertions for `error_code_key_count` and `failed_error_code_key_count`.
- [x] 2.2 Add provider replay status assertions for `error_sample_status_key_count` and `error_sample_probe_key_count`.

## 3. Implementation

- [x] 3.1 Derive probe summary error key-count fields from existing error-code and error-sample count maps.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming probe execution, full error payload exposure, failure coverage, health/readiness proof, socket startup, provider mutation, or lifecycle management.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.
