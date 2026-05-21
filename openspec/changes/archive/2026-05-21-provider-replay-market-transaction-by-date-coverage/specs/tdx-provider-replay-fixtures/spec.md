## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a market transaction by-date query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.market_transaction_data_by_date` sample for offline by-date market transaction query validation.

#### Scenario: Consumer enumerates the market transaction by-date fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-market-transaction-data-by-date-success`
- **AND** that descriptor MUST identify capability `transaction.market_transaction_data_by_date`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the market transaction by-date fixture
- **WHEN** a caller loads `transaction-market-transaction-data-by-date-success`
- **THEN** the fixture MUST contain capability `transaction.market_transaction_data_by_date`
- **AND** the fixture data MUST preserve representative market transaction by-date rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested fields and date selector
