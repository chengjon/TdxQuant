## ADDED Requirements

### Requirement: Provider replay mode SHALL serve sector transaction range through default fixture-backed execution
Replay mode SHALL serve `transaction.sector_transaction_data` through deterministic fixture-backed execution while preserving live behavior in live mode.

#### Scenario: Replay mode resolves default sector transaction range fixture
- **WHEN** a caller invokes `transaction.sector_transaction_data` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `transaction-sector-transaction-data-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime sector transaction range code
