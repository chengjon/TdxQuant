## ADDED Requirements

### Requirement: PingAn promotion readiness manifests SHALL remain non-executing

The evidence manifest input SHALL only select existing evidence artifacts for the read-only rollup and SHALL NOT trigger broker, desktop, trade, report, catalog, or lifecycle workflow execution.

#### Scenario: Manifest input does not execute workflows

- **WHEN** a caller provides an evidence manifest
- **THEN** the task SHALL still report non-executing rollup semantics
- **AND** it SHALL not refresh source evidence or submit orders.

