# tdx-provider-replay-fixtures Delta

## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include a cb-info query sample
The provider replay fixture bundle SHALL include a representative synchronous `market.cb_info` sample for offline convertible-bond metadata validation.

#### Scenario: Consumer enumerates the cb-info fixture
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the catalog MUST include `market-cb-info-success`
- **AND** that descriptor MUST identify capability `market.cb_info`
- **AND** the descriptor MUST use JSON format

#### Scenario: Consumer loads the cb-info fixture
- **WHEN** a caller loads `market-cb-info-success`
- **THEN** the fixture MUST contain capability `market.cb_info`
- **AND** the fixture data MUST preserve representative convertible-bond metadata rows
- **AND** the fixture data MUST preserve hardened query metadata under `data.query_meta`
