## ADDED Requirements

### Requirement: Worker bridge HTTP control plane SHALL remain separate from provider transport replay service
The system SHALL keep live bridge control-plane behavior separate from fixture-backed provider transport replay behavior.

#### Scenario: Replay service mirrors only read-only transport contracts
- **WHEN** provider transport replay implements bridge-style subscription-watch HTTP or SSE shapes
- **THEN** it MUST mirror only read-only status, event, and stream response contracts
- **AND** it MUST NOT claim live bridge lifecycle control such as starting or stopping a worker run

#### Scenario: Live bridge endpoints remain backed by worker-local controller state
- **WHEN** callers use existing `/bridge/v1/*` endpoints
- **THEN** those endpoints MUST continue to derive responses from worker-local controller state and run artifacts
- **AND** they MUST NOT silently switch to provider transport replay fixtures
