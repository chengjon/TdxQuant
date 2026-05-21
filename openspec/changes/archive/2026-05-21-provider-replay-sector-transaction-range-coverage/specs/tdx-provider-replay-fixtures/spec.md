## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a sector transaction range query sample
The provider replay fixture bundle SHALL include a representative synchronous `transaction.sector_transaction_data` sample for offline sector transaction range query validation.

#### Scenario: Consumer enumerates the sector transaction range fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `transaction-sector-transaction-data-success`
- **AND** that descriptor MUST identify capability `transaction.sector_transaction_data`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the sector transaction range fixture
- **WHEN** a caller loads `transaction-sector-transaction-data-success`
- **THEN** the fixture MUST contain capability `transaction.sector_transaction_data`
- **AND** the fixture data MUST preserve representative sector transaction range rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve requested symbols, requested fields, and date range
