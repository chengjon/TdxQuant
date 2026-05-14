## ADDED Requirements

### Requirement: Provider replay mode SHALL keep transport replay strict and fixture-backed
The system SHALL treat transport replay execution as a replay-only path backed by explicit fixture data.

#### Scenario: Transport replay never falls back to live runtime
- **WHEN** a transport replay request cannot resolve a required fixture
- **THEN** the system MUST return a stable replay error
- **AND** it MUST NOT invoke live TongDaXin runtime code

#### Scenario: Transport replay identifies replay source metadata
- **WHEN** a replay HTTP response or replay SSE frame is emitted
- **THEN** the payload MUST include replay source metadata sufficient to distinguish built-in fixtures from caller-supplied fixture paths
