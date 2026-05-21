## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a stock transaction by-date query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.stock_transaction_data_by_date` sample for offline by-date stock transaction query validation.

#### Scenario: Consumer enumerates the stock transaction by-date fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-stock-transaction-data-by-date-success`
- **AND** that descriptor MUST identify capability `transaction.stock_transaction_data_by_date`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the stock transaction by-date fixture
- **WHEN** a caller loads `transaction-stock-transaction-data-by-date-success`
- **THEN** the fixture MUST contain capability `transaction.stock_transaction_data_by_date`
- **AND** the fixture data MUST preserve representative stock transaction by-date rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested symbols, requested fields, and date selector
