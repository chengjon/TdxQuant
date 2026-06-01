## ADDED Requirements

### Requirement: Desktop trading management SHALL keep PingAn order result builders inside the execution module
The desktop trading management layer SHALL keep PingAn order duplicate, submission-key conflict, and risk-rejection result builders in the PingAn execution module while preserving existing manager behavior.

#### Scenario: Order result builders remain internal and non-executing

- **WHEN** PingAn order execution needs duplicate, submission-key conflict, or risk-rejection results
- **THEN** the result shape SHOULD be built by internal helpers in `tdxquant/trade/pingan_execution.py`
- **AND** manager callsites SHOULD route through those helpers rather than private manager-owned result builder methods
- **AND** the change MUST preserve existing order dispatch, idempotency, risk gate, finalize, audit, and request-context behavior
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, desktop primitive, live readiness, or production trading behavior

