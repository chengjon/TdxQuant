## ADDED Requirements

### Requirement: PingAn trade management SHALL expose read-only execution acceptance evidence

PingAn desktop trading management SHALL expose a read-only acceptance evidence summary for the implemented D-07 and D-08 trade execution surface.

#### Scenario: Acceptance evidence summary covers implemented trade surfaces without execution

- **WHEN** a caller requests PingAn trade execution acceptance evidence
- **THEN** the result MUST identify target nodes `D-07` and `D-08`
- **AND** it MUST enumerate the covered buy, sell, confirm-current, and submit-once trade surfaces
- **AND** it MUST expose explicit false side-effect flags for trade dispatch, order submission, workflow dispatch, desktop automation, process control, and status transition.

#### Scenario: Acceptance evidence summary remains a bounded review aid

- **WHEN** the acceptance evidence summary is returned
- **THEN** the payload MUST state that it is read-only evidence for manual/operator review
- **AND** it MUST NOT claim broker readiness, production readiness, live/manual acceptance completion, or automatic FUNCTION_TREE status transition.
