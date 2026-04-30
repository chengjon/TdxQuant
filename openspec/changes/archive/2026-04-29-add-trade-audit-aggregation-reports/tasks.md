## 1. Spec

- [x] 1.1 Add `tdx-task-trade-audit-daily-report` capability spec
- [x] 1.2 Add `tdx-task-trade-audit-period-report` capability spec
- [x] 1.3 Update `tdx-task-management` for audit aggregation workflows
- [x] 1.4 Update `tdx-report-cli-entry` for audit daily/period commands

## 2. Tests

- [x] 2.1 Add task-manager tests for trade audit daily/period reports
- [x] 2.2 Add CLI parser and dispatch tests for trade audit daily/period reports

## 3. Implementation

- [x] 3.1 Implement trade audit aggregation helpers in `tdxquant/api/task.py`
- [x] 3.2 Add `TdxTaskManager.trade_audit_daily_report(...)`
- [x] 3.3 Add `TdxTaskManager.trade_audit_period_report(...)`
- [x] 3.4 Add CLI commands and default profile mappings for audit daily/period reports

## 4. Docs and Validation

- [x] 4.1 Update trade audit docs and project maps
- [x] 4.2 Validate targeted tests and compile
- [x] 4.3 Validate and archive the OpenSpec change
