## ADDED Requirements

### Requirement: Provider replay mode SHALL serve stock transaction by-date through default fixture-backed execution
Replay mode SHALL serve `transaction.stock_transaction_data_by_date` through deterministic fixture-backed execution while preserving live behavior in live mode.

#### Scenario: Replay mode resolves default stock transaction by-date fixture
- **WHEN** a caller invokes `transaction.stock_transaction_data_by_date` in replay mode without an explicit fixture override
- **THEN** the system MUST resolve `transaction-stock-transaction-data-by-date-success`
- **AND** the returned result MUST include replay source metadata identifying that fixture
- **AND** the system MUST NOT invoke live Windows runtime stock transaction by-date code
