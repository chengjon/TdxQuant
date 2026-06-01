## ADDED Requirements

### Requirement: Desktop trading management SHALL route PingAn order execution through an internal execution seam
The desktop trading management layer SHALL provide an internal PingAn order execution seam that accepts a normalized order request, preserves public method identity, applies caller-provided gate decisions before desktop dispatch, and returns the existing manager result shape. The public `TdxTradeManager.pingan.*` methods MUST remain the supported caller interface.

#### Scenario: Buy submit-once uses the internal execution seam
- **WHEN** a caller executes `TdxTradeManager.pingan.buy_submit_once(...)`
- **THEN** the manager MUST route the normalized buy submit-once request through the internal PingAn execution seam before desktop dispatch
- **AND** the public result MUST preserve existing audit, idempotency, safety, lifecycle, and artifact fields

#### Scenario: Rejected gate stops before desktop dispatch
- **WHEN** a normalized PingAn execution request has a failed idempotency, safety, lifecycle owner, or broker-readiness gate
- **THEN** the internal execution seam MUST return the existing rejected manager result shape without invoking the desktop dispatch callback

#### Scenario: Public contract remains stable
- **WHEN** callers use existing PingAn manager, CLI, task, or catalog entry points
- **THEN** no new public parameter, command, catalog entry, desktop primitive, or live execution guarantee is introduced by the internal module extraction
