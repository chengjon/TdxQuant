## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and command catalog delta for sample truncation metadata.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add catalog validate coverage for detailed `task_report_bundle_sample_limit` and `task_report_bundle_sample_truncated`.
- [x] 2.2 Add catalog validate summary coverage for the same bounded sample metadata.

## 3. Implementation

- [x] 3.1 Add stable sample limit and truncation metadata to catalog validation results.
- [x] 3.2 Project the metadata through `catalog validate --view summary` without adding full entry or bundle rows.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-11 evidence and boundary text.
- [x] 4.2 Run focused tests, OpenSpec validation, function-tree validation, and whitespace checks.
- [x] 4.3 Archive the OpenSpec change and re-run verification before committing.
