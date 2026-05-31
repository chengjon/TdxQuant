## ADDED Requirements

### Requirement: PingAn promotion readiness rollup SHALL not execute trading workflows

PingAn promotion readiness rollup SHALL aggregate existing evidence only and SHALL NOT run broker, desktop, task/report, catalog, or trade execution workflows.

#### Scenario: Rollup does not promote implemented status

- **WHEN** the rollup reports `status=complete`
- **THEN** that result SHALL remain evidence for a later status transition
- **AND** it SHALL NOT modify `FUNCTION_TREE.md`
- **AND** it SHALL NOT submit orders, control the desktop, start/stop processes, or claim production readiness.

#### Scenario: Rollup keeps source boundaries

- **WHEN** the rollup includes a complete gate
- **THEN** the rollup SHALL identify the evidence source kind
- **AND** the rollup SHALL keep boundary text stating that source files can be stale or operator-provided.
