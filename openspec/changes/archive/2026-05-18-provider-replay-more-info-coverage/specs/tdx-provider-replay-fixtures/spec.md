# tdx-provider-replay-fixtures Delta

## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a more-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.more_info` sample for offline extended stock metadata validation.

#### Scenario: Consumer enumerates the more-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-more-info-success`
- **AND** that descriptor MUST identify capability `market.more_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the more-info fixture
- **WHEN** a caller loads `market-more-info-success`
- **THEN** the fixture MUST contain capability `market.more_info`
- **AND** the fixture data MUST preserve representative extended stock metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
