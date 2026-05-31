## ADDED Requirements

### Requirement: PingAn artifact provenance gate SHALL remain non-executing

The PingAn artifact provenance gate SHALL validate metadata only and SHALL NOT execute workflows.

#### Scenario: Artifact provenance validation has no runtime side effects

- **GIVEN** a caller requests PingAn promotion readiness rollup
- **WHEN** artifact provenance status is built
- **THEN** broker, desktop, trade, report, task, catalog, and bundle workflows SHALL NOT be executed by the provenance check
- **AND** `order_submitted` SHALL remain `false`
- **AND** `control_dispatch_executed` SHALL remain `false`
- **AND** artifact provenance SHALL NOT prove production readiness by itself.
