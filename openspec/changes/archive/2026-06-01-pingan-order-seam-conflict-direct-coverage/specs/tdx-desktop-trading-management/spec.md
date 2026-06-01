## ADDED Requirements

### Requirement: Desktop trading management SHALL directly verify PingAn order seam submission-key conflict behavior
The desktop trading management test suite SHALL directly verify the internal PingAn order seam behavior for `reject_conflict` idempotency decisions.

#### Scenario: Direct order seam conflict coverage remains non-public

- **WHEN** direct seam coverage is added for `execute_pingan_order`
- **THEN** the tests MUST assert that `reject_conflict` uses the conflict result builder without desktop dispatch
- **AND** finalize MUST receive conflict risk-gate metadata, not-applicable timing, normalized request context, and the original idempotency payload
- **AND** the change MUST NOT introduce public CLI, task, catalog, API, workflow builder, or desktop primitive behavior

