## ADDED Requirements

### Requirement: Provider replay mode SHALL serve full-tick through default fixture-backed execution
Replay mode SHALL serve `market.full_tick` through deterministic fixture-backed execution while preserving live behavior in live mode.

#### Scenario: Replay mode resolves default full-tick fixture
- **WHEN** a caller invokes `market.full_tick` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `market-full-tick-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime full-tick code
