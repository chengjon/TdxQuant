## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a sector transaction by-date query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.sector_transaction_data_by_date` sample for offline by-date sector transaction query validation.

#### Scenario: Consumer enumerates the sector transaction by-date fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-sector-transaction-data-by-date-success`
- **AND** that descriptor MUST identify capability `transaction.sector_transaction_data_by_date`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the sector transaction by-date fixture
- **WHEN** a caller loads `transaction-sector-transaction-data-by-date-success`
- **THEN** the fixture MUST contain capability `transaction.sector_transaction_data_by_date`
- **AND** the fixture data MUST preserve representative sector transaction by-date rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve requested symbols, requested fields, and date selector
