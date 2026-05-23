# Tasks

## 1. Spec

- [x] Add command-catalog validation requirement and scenarios.

## 2. Tests

- [x] Cover parser support for `catalog validate`.
- [x] Cover successful validation of all fixed catalog entries and bundles.
- [x] Cover label-filtered validation of task/report follow-up bundles.
- [x] Cover invalid selected targets returning `INVALID_REQUEST`.

## 3. Implementation

- [x] Add `catalog validate` parser branch.
- [x] Add non-execution validation helper reusing existing catalog resolvers.
- [x] Include task/report bundle coverage counts.

## 4. Registry And Verification

- [x] Update `FUNCTION_TREE.md` E-11 evidence and boundary text.
- [x] Run focused pytest, OpenSpec validation, diff check, registry validation,
  and GitNexus change detection.
