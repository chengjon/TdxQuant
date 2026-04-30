## 1. Spec

- [x] 1.1 Add `tdx-task-trade-audit-lookup` capability spec
- [x] 1.2 Update `tdx-task-management` for audit lookup workflow
- [x] 1.3 Update `tdx-report-cli-entry` for `report audit-lookup`

## 2. Tests

- [x] 2.1 Add task-manager tests for trade audit lookup
- [x] 2.2 Add CLI parser and dispatch tests for trade audit lookup

## 3. Implementation

- [x] 3.1 Implement audit directory scan/load/filter helpers in `tdxquant/api/task.py`
- [x] 3.2 Add `TdxTaskManager.trade_audit_lookup(...)`
- [x] 3.3 Add CLI commands for `task trade-audit-lookup` and `report audit-lookup`
- [x] 3.4 Add task/report default profile mappings and task profile entry

## 4. Docs and Validation

- [x] 4.1 Update function map and next-steps docs
- [x] 4.2 Validate targeted tests and compile
- [x] 4.3 Validate and archive the OpenSpec change
