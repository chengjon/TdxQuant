## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for governance evaluation summary.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add subscription background summary coverage for `governance.evaluation_summary`.
- [x] 2.2 Add CLI summary coverage projecting `evaluation_summary` without full governance actions.
- [x] 2.3 Add HTTP summary coverage projecting `evaluation_summary` without full governance actions.

## 3. Implementation

- [x] 3.1 Add governance evaluation rollup derived from heartbeat/watermark/reconnect staleness.
- [x] 3.2 Project `evaluation_summary` through bridge watch-status CLI summary view.
- [x] 3.3 Project `evaluation_summary` through worker bridge HTTP summary view.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundaries.
- [x] 4.2 Run focused tests, OpenSpec validation, function-tree validation, and whitespace checks.
- [x] 4.3 Archive the OpenSpec change and re-run verification before committing.
