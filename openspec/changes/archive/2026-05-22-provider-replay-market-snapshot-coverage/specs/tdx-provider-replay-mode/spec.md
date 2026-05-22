## ADDED Requirements

### Requirement: Provider replay mode SHALL serve market-snapshot through default fixture-backed execution
Replay mode SHALL serve `market.market_snapshot` through deterministic fixture-backed execution while preserving live behavior in live mode.

#### Scenario: Replay mode resolves default market-snapshot fixture
- **WHEN** a caller invokes `market.market_snapshot` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `market-market-snapshot-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime market-snapshot code
