## ADDED Requirements

### Requirement: PingAn promotion evidence contract SHALL remain non-executing

The PingAn evidence provenance gate SHALL validate only source artifact schemas and SHALL NOT execute workflows.

#### Scenario: Evidence contract validation has no runtime side effects

- **GIVEN** a caller requests PingAn promotion readiness rollup
- **WHEN** the evidence contract status is built
- **THEN** broker, desktop, trade, report, task, catalog, and bundle workflows SHALL NOT be executed by the contract check
- **AND** `order_submitted` SHALL remain `false`
- **AND** `control_dispatch_executed` SHALL remain `false`
- **AND** the contract SHALL NOT prove production readiness by itself.
