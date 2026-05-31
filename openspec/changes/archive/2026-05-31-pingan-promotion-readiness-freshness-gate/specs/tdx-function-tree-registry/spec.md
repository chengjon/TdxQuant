## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL record evidence freshness guarding without status promotion

FUNCTION_TREE SHALL register the PingAn promotion readiness freshness gate as a read-only evidence guard and SHALL NOT treat it as implemented trading capability.

#### Scenario: Freshness guard is visible but non-promoting

- **WHEN** the freshness gate is added to the tree evidence
- **THEN** the D-07/D-08 rows SHALL keep their `[部分实现]` status
- **AND** their boundary text SHALL mention stale evidence rejection
- **AND** the tree SHALL not imply promotion to `[已实现]`.

