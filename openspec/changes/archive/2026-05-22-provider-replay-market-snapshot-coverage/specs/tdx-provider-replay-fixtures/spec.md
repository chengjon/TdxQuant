## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a market-snapshot query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.market_snapshot` sample for offline market-snapshot query validation.

#### Scenario: Consumer enumerates the market-snapshot fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-market-snapshot-success`
- **AND** that descriptor MUST identify capability `market.market_snapshot`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the market-snapshot fixture
- **WHEN** a caller loads `market-market-snapshot-success`
- **THEN** the fixture MUST contain capability `market.market_snapshot`
- **AND** the fixture data MUST preserve representative market-snapshot rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
- **AND** the query metadata MUST preserve the requested symbol and requested fields
