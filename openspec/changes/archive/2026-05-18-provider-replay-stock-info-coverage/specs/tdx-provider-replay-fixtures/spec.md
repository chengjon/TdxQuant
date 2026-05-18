# tdx-provider-replay-fixtures Delta

## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a stock-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.stock_info` sample for offline stock metadata query validation.

#### Scenario: Consumer enumerates the stock-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-stock-info-success`
- **AND** that descriptor MUST identify capability `market.stock_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the stock-info fixture
- **WHEN** a caller loads `market-stock-info-success`
- **THEN** the fixture MUST contain capability `market.stock_info`
- **AND** the fixture data MUST preserve representative stock-info rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
