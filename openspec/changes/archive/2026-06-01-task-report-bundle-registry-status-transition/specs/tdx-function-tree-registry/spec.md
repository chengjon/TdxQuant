## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL record E-11 task/report bundle registry as implemented

`FUNCTION_TREE.md` SHALL mark E-11 as `[已实现]` only when a read-only catalog validation artifact records the fixed task/report bundle registry coverage and non-execution boundary.

#### Scenario: E-11 is transitioned with catalog registry evidence

- **GIVEN** `catalog validate --kind bundle --label followup --view summary` validates the fixed runtime bundle registry without execution
- **WHEN** E-11 records the final task/report bundle registry status artifact
- **THEN** E-11 SHALL have status `[已实现]`
- **AND** evidence SHALL mention `runtime/catalog-evidence/e11-task-report-bundle-registry-status.json`
- **AND** evidence SHALL mention `task_report_bundle_count`
- **AND** evidence SHALL mention `task-report-bundle-registry-status-transition`
- **AND** the boundary SHALL state that E-11 is fixed runtime JSON discovery/validation/planning, not arbitrary workflow building or execution.
